#!/usr/bin/env python3
"""Validate every note of every skill (skills/*/).

Errors (exit 1):
  - missing/invalid frontmatter; missing required fields (id, title, domain, summary)
  - knowledge-base server fields (tools/kb_meta.py): type, owner, updated, review_by, source, confidentiality
    missing; type/source/confidentiality outside the allowed values; updated/review_by not YYYY-MM-DD
  - id != file name, id without the '<domain>-' prefix, duplicate id anywhere in the repo
  - `area` different from the note's folder name
  - wikilink to an id that does not exist in the repo
  - cross-skill wikilink to a skill not listed in the note's `requires` (skills must stay self-contained)
  - relative markdown link that leaves the repo or points to a missing file
  - `see`/`uses`/`implements`/`depends_on` items that are not wikilinks
  - unbalanced ``` fences (a split code block)
  - Python block that fails ast.parse (after dedent); YAML block that fails to parse (needs PyYAML);
    XML block (launch files, behavior trees) that is not well-formed
  - SKILL.md: name != folder, missing/oversized (>1024) description, missing INDEX markers,
    broken or cross-skill wikilinks
  - a link with credentials or a signed token (AWSAccessKeyId=, X-Amz-Signature=, Signature=, token=) or a
    Windows user path (C:\\Users\\...) in a note or SKILL.md
  - an ID of a "## Real ... (fix)" section of reports/version_audit*.md that no note cites (the fix never
    reached the notes); a report without that section is a WARNING (its fixes are not checked)
Warnings: > MAX_TOKENS (≈ chars/4 without the knowledge-base fields), summary > 20 words, audience not dev|students,
  learn/ note not audience: students, SKILL.md description > 200 chars or body > 2500 tokens,
  generated indexes out of date, review_by date passed (the server reports the note as overdue),
  knowledge-base fields out of date (python tools/kb_meta.py --check; needs git), pyflakes findings in
  complete Python programs (only if pyflakes is installed; a block is "complete" when it has an import and
  def main / __main__).

Optional checks:
  --forbidden FILE  one term per line ('#' = comment): any text file of the repo (.md, .yaml, .yml, .txt:
                    notes, SKILL.md, README, reports...) containing a term (case-insensitive) is an ERROR.
                    Keep the file outside the repo when the terms themselves must not be published.
  Unlabelled code blocks (WARNING): a block without a language that looks like Python, a params YAML or XML
  is never parsed; label it (```python, ```yaml, ```xml; logs and trees: ```text).
  Launch/YAML names (WARNING): a params YAML whose node key matches an executable launched in the same skill
  under a different name is never applied (ROS 2 matches params by node name).

Usage: python tools/validate.py [--strict] [--brief] [--forbidden FILE]
  --strict  warnings also fail
  --brief   print the summary, the errors and the warnings grouped by kind (one line)
"""
import ast
import datetime
import re
import sys
import textwrap
from pathlib import Path
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from notes_lib import (ROOT, RELATION_FIELDS, as_list, discover_skills,  # noqa: E402
                       load_notes, parse_frontmatter, strip_code, tokens_estimate, wikilinks)
from kb_meta import KB_FIELDS, KB_VALUES, parse_date, split_kb  # noqa: E402

REQUIRED = ('id', 'title', 'domain', 'summary')
MAX_TOKENS = 1000
MAX_SUMMARY_WORDS = 20
MAX_DESC = 200                 # project rule for SKILL.md descriptions
MAX_DESC_HARD = 1024           # Claude skill limit
MAX_SKILL_BODY_TOKENS = 2500
MD_LINK_RE = re.compile(r'(?<!!)\[[^\]\n]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
FENCE_RE = re.compile(r'^\s*```', re.M)
PY_BLOCK_RE = re.compile(r'^\s*```(?:python|py)\s*\n(.*?)^\s*```', re.S | re.M | re.I)
YAML_BLOCK_RE = re.compile(r'^\s*```ya?ml\s*\n(.*?)^\s*```', re.S | re.M | re.I)
XML_BLOCK_RE = re.compile(r'^\s*```xml\s*\n(.*?)^\s*```', re.S | re.M | re.I)
OPEN_FENCE_RE = re.compile(r'^\s*```(.*)$')
LOOKS_LIKE_CODE_RE = re.compile(r'^\s*(?:import \w|from [\w.]+ import |def \w+\(|class \w+[(:])|ros__parameters:'
                                r'|^\s*<\?xml|^\s*<(?:launch|root|package|library|BehaviorTree)\b', re.M)
SECRET_RE = re.compile(r'AWSAccessKeyId=|X-Amz-(?:Signature|Credential)=|[?&](?:Signature|token)=|'
                       r'\b[A-Za-z]:\\+Users\\+', re.I)
TEXT_SUFFIXES = {'.md', '.yaml', '.yml', '.txt'}
SKIP_DIRS = {'.git', 'dist', '.venv', '__pycache__', '.obsidian', '.trash'}
FIX_SECTION_RE = re.compile(r'^## Real .*\(fix\)\s*$(.*?)(?=^## |\Z)', re.S | re.M)
AUDIT_ID_RE = re.compile(r'^\| *((?:[A-Z0-9]+-)?V\d{2,3}) *\|', re.M)
LINK_ITEM_RE = re.compile(r'^\[\[[^\]]+\]\]$')
COMPLETE_PY_RE = re.compile(r'^(?:import|from)\s', re.M)


def fenced_blocks(body):
    """[(language, code)] of the ``` blocks of a note, paired line by line (opening fence, closing fence)."""
    blocks, lang, cur = [], None, []
    for line in body.splitlines():
        m = OPEN_FENCE_RE.match(line)
        if m and lang is None:
            lang, cur = m.group(1).strip().lower(), []
        elif m:
            blocks.append((lang, '\n'.join(cur)))
            lang = None
        elif lang is not None:
            cur.append(line)
    return blocks


def pyflakes_messages(code):
    """Return pyflakes findings for a code string, or None if pyflakes is not installed."""
    try:
        from pyflakes.api import check
        from pyflakes.reporter import Reporter
    except ImportError:
        return None
    import io
    out, err = io.StringIO(), io.StringIO()
    check(code, 'block', Reporter(out, err))
    return [line.split(':', 2)[-1].strip() for line in (out.getvalue() + err.getvalue()).splitlines() if line]


def yaml_error(code):
    """Return the YAML parse error for a code string, '' if it parses, None without PyYAML."""
    try:
        import yaml
    except ImportError:
        return None
    try:
        list(yaml.safe_load_all(code))
        return ''
    except yaml.YAMLError as e:
        return str(e).splitlines()[0]


def launched_nodes(body):
    """(names, executables) of launch_ros Node(...) calls with literal arguments in Python blocks.
    names holds 'name' and 'namespace/name'; a non-literal namespace adds the bare name only."""
    names, exes = set(), set()
    for block in PY_BLOCK_RE.findall(body):
        try:
            tree = ast.parse(textwrap.dedent(block))
        except SyntaxError:
            continue
        for call in ast.walk(tree):
            if not isinstance(call, ast.Call):
                continue
            func = call.func.attr if isinstance(call.func, ast.Attribute) else getattr(call.func, 'id', '')
            if func not in ('Node', 'LifecycleNode'):
                continue
            kw = {k.arg: k.value.value for k in call.keywords
                  if isinstance(k.value, ast.Constant) and isinstance(k.value.value, str)}
            if 'executable' in kw:
                exes.add(kw['executable'])
            if 'name' in kw:
                names.add(kw['name'])
                if 'namespace' in kw:
                    names.add(f"{kw['namespace'].strip('/')}/{kw['name']}")
    return names, exes


def yaml_node_keys(body):
    """Node keys of params YAML blocks: 'node' or 'ns/node' (nested form), the ones holding ros__parameters."""
    try:
        import yaml
    except ImportError:
        return set()
    keys = set()
    for block in YAML_BLOCK_RE.findall(body):
        try:
            docs = list(yaml.safe_load_all(textwrap.dedent(block)))
        except yaml.YAMLError:
            continue
        for doc in docs:
            if not isinstance(doc, dict):
                continue
            for k, v in doc.items():
                if not isinstance(v, dict) or str(k).startswith('/**'):
                    continue
                if 'ros__parameters' in v:
                    keys.add(str(k).strip('/'))
                for k2, v2 in v.items():
                    if isinstance(v2, dict) and 'ros__parameters' in v2:
                        keys.add(f'{str(k).strip("/")}/{k2}')
    return keys


def main(argv):
    strict = '--strict' in argv
    brief = '--brief' in argv
    forbidden = []
    if '--forbidden' in argv:
        path = Path(argv[argv.index('--forbidden') + 1])
        forbidden = sorted({t.strip().lower() for t in path.read_text(encoding='utf-8').splitlines()
                            if t.strip() and not t.startswith('#')})
    skills = discover_skills()
    notes = load_notes()
    errors, warnings = [], []
    unlinted = 0                                   # complete Python programs not checked (no pyflakes)
    unparsed_yaml = 0                              # YAML blocks not checked (no PyYAML)
    by_id = {}
    for n in notes:
        nid = n['fm'].get('id')
        if nid:
            if nid in by_id:
                errors.append(f"{n['repo_rel']}: duplicate id '{nid}' (also {by_id[nid]['repo_rel']})")
            else:
                by_id[nid] = n

    for n in notes:
        where, fm = n['repo_rel'], n['fm']
        if n['fm_error']:
            errors.append(f'{where}: {n["fm_error"]}')
            continue
        for k in REQUIRED:
            if not fm.get(k):
                errors.append(f'{where}: missing required field `{k}`')
        for k in KB_FIELDS:                           # knowledge-base server fields
            v = fm.get(k)
            if v is None or v == '':
                errors.append(f'{where}: missing knowledge-base field `{k}` (run python tools/kb_meta.py)')
            elif k in KB_VALUES and v not in KB_VALUES[k]:
                errors.append(f"{where}: {k} '{v}' not in {'|'.join(KB_VALUES[k])}")
            elif k in ('updated', 'review_by') and parse_date(str(v)) is None:
                errors.append(f"{where}: {k} '{v}' is not a YYYY-MM-DD date")
        due = parse_date(str(fm.get('review_by', '')))
        if due and due < datetime.date.today():
            warnings.append(f'{where}: review_by {due} has passed (overdue: review the note, then kb_meta.py)')
        nid, domain = fm.get('id'), fm.get('domain')
        if nid and nid != n['path'].stem:
            errors.append(f"{where}: id '{nid}' != file name '{n['path'].stem}'")
        if nid and domain and not str(nid).startswith(f'{domain}-'):
            errors.append(f"{where}: id '{nid}' lacks the domain prefix '{domain}-'")
        area = fm.get('area')
        if area and area != n['path'].parent.name:
            errors.append(f"{where}: area '{area}' != folder '{n['path'].parent.name}'")
        for field in RELATION_FIELDS:
            for item in as_list(fm.get(field)):
                if not LINK_ITEM_RE.match(str(item)):
                    errors.append(f'{where}: `{field}` item {item!r} is not a [[wikilink]]')

        requires = {str(r) for r in as_list(fm.get('requires'))}
        for target in wikilinks(n['text']):
            t = by_id.get(target)
            if t is None:
                errors.append(f'{where}: broken wikilink [[{target}]]')
            elif t['skill'] != n['skill'] and t['skill'] not in requires:
                errors.append(f"{where}: links to [[{target}]] in skill '{t['skill']}' "
                              f"which is not in `requires` (skills must stay self-contained)")

        for href in MD_LINK_RE.findall(strip_code(n['body'])):
            if re.match(r'^(https?:|mailto:|#)', href):
                continue
            target = (n['path'].parent / href.split('#', 1)[0]).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f'{where}: markdown link leaves the repo: {href}')
                continue
            if not target.exists():
                errors.append(f'{where}: markdown link to missing file: {href}')

        if len(FENCE_RE.findall(n['body'])) % 2:
            errors.append(f'{where}: unbalanced ``` fences (split code block)')
        for block in PY_BLOCK_RE.findall(n['body']):
            code = textwrap.dedent(block)
            try:
                ast.parse(code)
            except SyntaxError as e:
                errors.append(f'{where}: Python block does not parse (line {e.lineno}: {e.msg})')
                continue
            if COMPLETE_PY_RE.search(code) and ('def main' in code or "__name__ == '__main__'" in code):
                msgs = pyflakes_messages(code)
                if msgs is None:
                    unlinted += 1
                for msg in msgs or []:
                    warnings.append(f'{where}: pyflakes: {msg}')
        for block in YAML_BLOCK_RE.findall(n['body']):
            err = yaml_error(textwrap.dedent(block))
            if err is None:
                unparsed_yaml += 1
            if err:
                errors.append(f'{where}: YAML block does not parse ({err})')
        for block in XML_BLOCK_RE.findall(n['body']):
            code = textwrap.dedent(block).strip()
            try:
                ElementTree.fromstring(code)
            except ElementTree.ParseError as e:
                try:                                  # fragment of sibling elements (e.g. package.xml lines)
                    ElementTree.fromstring(f'<fragment>{code}</fragment>')
                except ElementTree.ParseError:
                    errors.append(f'{where}: XML block is not well-formed ({e})')

        for lang, block in fenced_blocks(n['body']):
            if not lang and LOOKS_LIKE_CODE_RE.search(block):
                warnings.append(f'{where}: code block without a language looks like Python/YAML/XML '
                                f'(not parsed): label it')
        m = SECRET_RE.search(n['text'])
        if m:
            errors.append(f'{where}: signed link or local user path ({m.group(0)}): remove it')

        tok = tokens_estimate(split_kb(n['text'])[0])     # the six fixed knowledge-base lines do not count
        if tok > MAX_TOKENS:
            warnings.append(f'{where}: ~{tok} tokens (> {MAX_TOKENS})')
        words = len(str(fm.get('summary', '')).split())
        if words > MAX_SUMMARY_WORDS:
            warnings.append(f'{where}: summary has {words} words (> {MAX_SUMMARY_WORDS})')
        aud = fm.get('audience')
        if aud and aud not in ('dev', 'students'):
            warnings.append(f"{where}: audience '{aud}' not in dev|students")
        if n['path'].parent.name == 'learn' and aud != 'students':
            warnings.append(f'{where}: learn/ note should have audience: students')

    for skill in skills:                              # params YAML key vs launched node name
        in_skill = [n for n in notes if n['skill'] == skill and not n['fm_error']]
        names, exes = set(), set()
        for n in in_skill:
            a, b = launched_nodes(n['body'])
            names |= a
            exes |= b
        for n in in_skill:
            for key in sorted(yaml_node_keys(n['body'])):
                base = key.rsplit('/', 1)[-1]
                if key not in names and base not in names and base in exes:
                    warnings.append(f"{n['repo_rel']}: params key '{key}' matches executable '{base}', but no node "
                                    f"is launched with that name in this skill (the YAML would be ignored)")

    for skill, spath in skills.items():
        skill_md = spath / 'SKILL.md'
        where = skill_md.relative_to(ROOT).as_posix()
        text = skill_md.read_text(encoding='utf-8')
        fm, body, err = parse_frontmatter(text)
        if err:
            errors.append(f'{where}: {err}')
            continue
        if fm.get('name') != skill:
            errors.append(f"{where}: name '{fm.get('name')}' != folder '{skill}'")
        desc = str(fm.get('description', ''))
        if not desc:
            errors.append(f'{where}: missing description')
        elif len(desc) > MAX_DESC_HARD:
            errors.append(f'{where}: description has {len(desc)} chars (> {MAX_DESC_HARD})')
        elif len(desc) > MAX_DESC:
            warnings.append(f'{where}: description has {len(desc)} chars (> {MAX_DESC})')
        if '<!-- INDEX:START -->' not in text or '<!-- INDEX:END -->' not in text:
            errors.append(f'{where}: missing INDEX markers')
        for target in wikilinks(body):
            t = by_id.get(target)
            if t is None:
                errors.append(f'{where}: broken wikilink [[{target}]]')
            elif t['skill'] != skill:
                errors.append(f"{where}: links to [[{target}]] in another skill ('{t['skill']}')")
        if tokens_estimate(body) > MAX_SKILL_BODY_TOKENS:
            warnings.append(f'{where}: body ~{tokens_estimate(body)} tokens (> {MAX_SKILL_BODY_TOKENS})')
        m = SECRET_RE.search(text)
        if m:
            errors.append(f'{where}: signed link or local user path ({m.group(0)}): remove it')

    cited = '\n'.join(n['text'] for n in notes)       # every audit fix must reach a note (version_notes)
    for report in sorted((ROOT / 'reports').glob('version_audit*.md')):
        where = report.relative_to(ROOT).as_posix()
        sections = FIX_SECTION_RE.findall(report.read_text(encoding='utf-8'))
        if not sections:
            warnings.append(f"{where}: no '## Real ... (fix)' section: its fixes are not checked against the notes")
        for aid in sorted({i for s in sections for i in AUDIT_ID_RE.findall(s)}):
            if not re.search(rf'(?<![\w-]){re.escape(aid)}(?!\d)', cited):
                errors.append(f'{where}: fix {aid} is cited by no note (add it to the version_notes of the '
                              f'note that carries the correction)')

    if forbidden:                                      # every text file of the repo, not only the notes
        for path in sorted(ROOT.rglob('*')):
            rel = path.relative_to(ROOT)
            if path.suffix not in TEXT_SUFFIXES or any(p in SKIP_DIRS for p in rel.parts) or not path.is_file():
                continue
            low = path.read_text(encoding='utf-8', errors='replace').lower()
            hits = [term for term in forbidden if term in low]
            if hits:
                errors.append(f'{rel.as_posix()}: contains forbidden terms ({", ".join(hits)})')

    try:
        import build_index
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            if build_index.main(['--check']) != 0:
                warnings.append('generated indexes are out of date: run python tools/build_index.py')
    except SystemExit as e:
        warnings.append(f'index check skipped: {e}')
    try:
        import kb_meta
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            if kb_meta.main(['--check']) != 0:
                warnings.append('knowledge-base fields out of date (an edited note keeps an old `updated`): '
                                'run python tools/kb_meta.py')
    except SystemExit as e:
        warnings.append(f'knowledge-base freshness check skipped: {e}')

    print(f'skills: {len(skills)} ({", ".join(skills)}) | notes: {len(notes)} | '
          f'errors: {len(errors)} | warnings: {len(warnings)}'
          + (f' | NOT CHECKED: {unparsed_yaml} YAML blocks and the params-YAML/node-name check'
             ' (python -m pip install -r requirements.txt)' if unparsed_yaml else '')
          + (f' | NOT CHECKED: {unlinted} Python programs (python -m pip install -r requirements.txt)'
             if unlinted else ''))
    for e in errors:
        print(f'ERROR   {e}')
    if brief and warnings:                         # rare kinds in full, frequent kinds as one count
        kinds = {}
        for w in warnings:
            kind = re.sub(r'^[^:]+: ', '', w)
            kind = re.sub(r"'[^']*'", 'X', re.sub(r'~?\d[\d,.]*', 'N', kind))[:70]
            kinds.setdefault(kind, []).append(w)
        for kind, ws in sorted(kinds.items(), key=lambda x: len(x[1])):
            if len(ws) <= 3:
                for w in ws:
                    print(f'WARNING {w}')
            else:
                print(f'WARNING {len(ws)} x {kind}')
    else:
        for w in warnings:
            print(f'WARNING {w}')
    return 1 if errors or (strict and warnings) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

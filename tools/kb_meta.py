#!/usr/bin/env python3
"""Add and refresh the knowledge-base fields of every note (skills/*/), for the knowledge-base MCP server.

Fields (inserted right after `id:`, in this order):
  type: reference              objective|segment|process|metric|idea|decision|roadmap_item|spec|system|
                               repo|interface|tech_debt|reference (notes under skills/ are `reference`)
  owner: <OWNER>               who maintains the note
  updated: YYYY-MM-DD          last content change
  review_by: YYYY-MM-DD        after this date the server reports the note as overdue
  source: manual               manual|gitlab|generated
  confidentiality: internal    internal|restricted

Rules (needs git; run it before every commit, from any folder):
  - a missing field gets its default; values that are present are kept;
  - a note whose content changed since the last commit (the six fields ignored), or a new note:
    updated = today, review_by = at least today + REVIEW_DAYS;
  - a committed, unchanged note without `updated` gets the date of its last commit; without `review_by`,
    today + REVIEW_DAYS;
  - an `updated` or `review_by` that is not a YYYY-MM-DD date counts as missing (reported).
Files that need no change are not rewritten. tools/validate.py reports missing or invalid fields as errors.

Usage: python tools/kb_meta.py [--check] [--today YYYY-MM-DD]
  --check  write nothing; list the notes that would change and exit 1 if there is any
"""
import datetime
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from notes_lib import ROOT, discover_skills, iter_note_files  # noqa: E402

# Defaults of this repo: edit them when the tools are copied to another repo.
OWNER = 'equipo-ros2'
CONFIDENTIALITY = 'internal'     # internal | restricted (restricted never goes to a shareable repo)
REVIEW_DAYS = 180

KB_FIELDS = ('type', 'owner', 'updated', 'review_by', 'source', 'confidentiality')
KB_VALUES = {
    'type': ('objective', 'segment', 'process', 'metric', 'idea', 'decision', 'roadmap_item', 'spec',
             'system', 'repo', 'interface', 'tech_debt', 'reference'),
    'source': ('manual', 'gitlab', 'generated'),
    'confidentiality': ('internal', 'restricted'),
}
FM_RE = re.compile(r'\A(---\n)(.*?\n)(---\n)', re.S)
KB_LINE_RE = re.compile(r'^(%s):[ \t]*(.*?)[ \t]*$' % '|'.join(KB_FIELDS))
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def parse_date(value):
    """date for a YYYY-MM-DD string (quotes allowed), else None."""
    value = value.strip().strip('"\'')
    if not DATE_RE.match(value):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def split_kb(text):
    """(text without the knowledge-base lines of the frontmatter, {field: raw value})."""
    text = text.replace('\r\n', '\n')
    m = FM_RE.match(text)
    if not m:
        return text, {}
    kept, values = [], {}
    for line in m.group(2).splitlines(keepends=True):
        km = KB_LINE_RE.match(line.rstrip('\n'))
        if km:
            values.setdefault(km.group(1), km.group(2))   # a repeated field keeps its first value
        else:
            kept.append(line)
    return m.group(1) + ''.join(kept) + m.group(3) + text[m.end():], values


def with_kb(stripped, values):
    """Insert the fields after the `id:` line (or at the top of the frontmatter)."""
    m = FM_RE.match(stripped)
    lines = m.group(2).splitlines(keepends=True)
    at = next((i + 1 for i, line in enumerate(lines) if line.startswith('id:')), 0)
    block = [f'{k}: {values[k]}\n' for k in KB_FIELDS]
    return m.group(1) + ''.join(lines[:at] + block + lines[at:]) + m.group(3) + stripped[m.end():]


def git(*args):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or f'git {args[0]} failed')
    return r.stdout


def git_state():
    """(paths changed or new since HEAD, paths in HEAD, {path: date of its last commit})."""
    top = Path(git('rev-parse', '--show-toplevel').strip())
    if top.resolve() != ROOT.resolve():
        raise RuntimeError(f'the repository root is {top}, not {ROOT}')
    has_head = subprocess.run(['git', 'rev-parse', '--verify', '-q', 'HEAD'], cwd=ROOT,
                              capture_output=True).returncode == 0
    changed = set(git('ls-files', '--others', '--exclude-standard', '--', 'skills').splitlines())
    in_head, last = set(), {}
    if has_head:
        changed |= set(git('diff', '--name-only', 'HEAD', '--', 'skills').splitlines())
        in_head = set(git('ls-tree', '-r', '--name-only', 'HEAD', '--', 'skills').splitlines())
        day = None
        for line in git('log', '--format=@%cs', '--name-only', '--', 'skills').splitlines():
            if line.startswith('@'):
                day = line[1:]
            elif line:
                last.setdefault(line, day)
    return changed, in_head, last


def main(argv):
    check = '--check' in argv
    today = datetime.date.today()
    if '--today' in argv:
        today = datetime.date.fromisoformat(argv[argv.index('--today') + 1])
    try:
        changed, in_head, last = git_state()
    except (OSError, RuntimeError) as e:
        sys.exit(f'kb_meta.py needs git and a git repository ({e})')

    review = (today + datetime.timedelta(days=REVIEW_DAYS)).isoformat()
    defaults = {'type': 'reference', 'owner': OWNER, 'source': 'manual', 'confidentiality': CONFIDENTIALITY}
    notes = added = refreshed = bad_dates = 0
    to_change = []
    for spath in discover_skills().values():
        for p in iter_note_files(spath):
            notes += 1
            rel = p.relative_to(ROOT).as_posix()
            text = p.read_text(encoding='utf-8')
            stripped, values = split_kb(text)
            if not FM_RE.match(stripped):
                continue                                  # validate.py reports the missing frontmatter
            new = dict(values)
            for k, v in defaults.items():
                if not new.get(k):
                    new[k] = v
            for k in ('updated', 'review_by'):
                if new.get(k) and parse_date(new[k]) is None:
                    bad_dates += 1
                    new[k] = ''
            content_changed = rel in changed and (
                rel not in in_head or stripped != split_kb(git('show', f'HEAD:{rel}'))[0])
            if content_changed:
                new['updated'] = today.isoformat()
                if not new.get('review_by') or parse_date(new['review_by']).isoformat() < review:
                    new['review_by'] = review
            else:
                if not new.get('updated'):
                    new['updated'] = last.get(rel) or today.isoformat()
                if not new.get('review_by'):
                    new['review_by'] = review
            for k in ('updated', 'review_by'):
                new[k] = parse_date(new[k]).isoformat()
            out = with_kb(stripped, new)
            if out == text.replace('\r\n', '\n'):
                continue
            to_change.append(rel)
            added += sum(1 for k in KB_FIELDS if k not in values)
            refreshed += int(content_changed and values.get('updated') != new['updated'])
            if not check:
                p.write_text(out, encoding='utf-8', newline='\n')

    verb = 'would change' if check else 'changed'
    print(f'notes: {notes} | {verb}: {len(to_change)} | fields added: {added} | '
          f'updated set to {today.isoformat()}: {refreshed} | invalid dates replaced: {bad_dates}')
    if check:
        for rel in to_change:
            print(f'OUTDATED {rel}')
        return 1 if to_change else 0
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

"""Shared helpers for the repo tools: skill discovery, note loading, frontmatter, wikilinks.

Works for any number of skills: a skill is a directory skills/<name>/ that contains SKILL.md.
A note is any .md file inside a skill except SKILL.md and generated _index.md files.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / 'skills'
REPORTS_DIR = ROOT / 'reports'
EXCLUDED_NAMES = {'SKILL.md', '_index.md'}
EXCLUDED_DIRS = {'.obsidian', '.trash', '.git', '__pycache__'}

FM_RE = re.compile(r'\A---\r?\n(.*?)\r?\n---\r?\n', re.S)
WIKILINK_RE = re.compile(r'\[\[([^\]|#\n]+)(?:[#|][^\]\n]*)?\]\]')
RELATION_FIELDS = ('see', 'uses', 'implements', 'depends_on')


def discover_skills():
    """Return {skill_name: skill_path} for every skills/<name>/SKILL.md."""
    if not SKILLS_DIR.is_dir():
        return {}
    return {p.parent.name: p.parent for p in sorted(SKILLS_DIR.glob('*/SKILL.md'))}


def iter_note_files(skill_path):
    for p in sorted(skill_path.rglob('*.md')):
        if p.name in EXCLUDED_NAMES or any(part in EXCLUDED_DIRS for part in p.parts):
            continue
        yield p


def _parse_scalar(v):
    v = v.strip()
    if v.startswith('[') and v.endswith(']'):
        inner = v[1:-1].strip()
        return [_parse_scalar(x) for x in _split_list(inner)] if inner else []
    if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'':
        return v[1:-1]
    if v in ('true', 'false'):
        return v == 'true'
    if re.fullmatch(r'-?\d+', v):
        return int(v)
    return v


def _split_list(s):
    out, depth, quote, cur = [], 0, None, ''
    for ch in s:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
        elif ch in '"\'':
            quote, cur = ch, cur + ch
        elif ch == '[':
            depth, cur = depth + 1, cur + ch
        elif ch == ']':
            depth, cur = depth - 1, cur + ch
        elif ch == ',' and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return out


def parse_yaml_subset(text):
    """Minimal YAML for frontmatter (key: scalar, key: [a, b], key:\\n  - item). Used if PyYAML is absent."""
    data, key = {}, None
    for raw in text.splitlines():
        line = raw.split(' #', 1)[0].rstrip() if not raw.lstrip().startswith(('"', "'")) else raw.rstrip()
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        m = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', line)
        if m and not raw.startswith((' ', '\t')):
            key, val = m.group(1), m.group(2)
            data[key] = _parse_scalar(val) if val else []
        elif key and line.strip().startswith('- '):
            data.setdefault(key, [])
            if not isinstance(data[key], list):
                data[key] = []
            data[key].append(_parse_scalar(line.strip()[2:]))
    return data


def parse_frontmatter(text):
    """Return (frontmatter_dict_or_None, body, error_message_or_None)."""
    m = FM_RE.match(text)
    if not m:
        return None, text, 'no YAML frontmatter'
    raw = m.group(1)
    try:
        import yaml  # optional dependency
        data = yaml.safe_load(raw) or {}
    except ImportError:
        data = parse_yaml_subset(raw)
    except Exception as e:  # yaml.YAMLError
        return None, text[m.end():], f'invalid YAML: {e}'
    if not isinstance(data, dict):
        return None, text[m.end():], 'frontmatter is not a mapping'
    return data, text[m.end():], None


def load_notes():
    """Load every note of every skill. Returns a list of dicts."""
    notes = []
    for skill, spath in discover_skills().items():
        for p in iter_note_files(spath):
            text = p.read_text(encoding='utf-8')
            fm, body, err = parse_frontmatter(text)
            notes.append({
                'skill': skill, 'skill_path': spath, 'path': p,
                'rel': p.relative_to(spath).as_posix(),
                'repo_rel': p.relative_to(ROOT).as_posix(),
                'text': text, 'fm': fm or {}, 'body': body, 'fm_error': err,
            })
    return notes


def strip_code(text):
    """Remove fenced blocks and inline code (Obsidian does not treat [[...]] there as links)."""
    text = re.sub(r'^\s*```.*?^\s*```', '', text, flags=re.S | re.M)
    return re.sub(r'`[^`\n]*`', '', text)


def wikilinks(text):
    """Wikilink targets outside code spans/blocks."""
    return [m.strip() for m in WIKILINK_RE.findall(strip_code(text))]


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def tokens_estimate(text):
    return len(text) // 4

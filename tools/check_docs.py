"""Offline checks for public documentation repositories. Python 3.10+, stdlib only."""
import argparse
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

IGNORED_DIRECTORIES = {'.git', '.venv', 'venv', 'node_modules', '__pycache__'}
INLINE_LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+["\'][^\n]*["\'])?\s*\)')
REFERENCE_LINK = re.compile(r'^\s{0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)', re.MULTILINE)


class ImageSources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'img':
            self.sources.extend(value for key, value in attrs if key.lower() == 'src' and value)


def outside(path, root):
    try:
        path.relative_to(root)
        return False
    except ValueError:
        return True


def prose_only(text):
    """Remove fenced and inline examples; return prose plus fence status."""
    lines = []
    fence_character = None
    fence_length = 0
    for line in text.splitlines():
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
        if fence_character:
            if (marker and marker[1][0] == fence_character
                    and len(marker[1]) >= fence_length and not marker[2].strip()):
                fence_character = None
            continue
        if marker:
            fence_character, fence_length = marker[1][0], len(marker[1])
            continue
        lines.append(re.sub(r'(`+).*?\1', '', line))
    return '\n'.join(lines), fence_character is not None


def check_link(target, source, root):
    target = target.strip('<>')
    try:
        parts = urlsplit(target)
    except ValueError:
        return f'{source.relative_to(root)}: Invalid link target {target}'
    if parts.scheme or parts.netloc or not parts.path:
        return None
    decoded = unquote(parts.path)
    path = ((root / decoded.lstrip('/')) if decoded.startswith('/')
            else source.parent / decoded).resolve()
    if outside(path, root):
        return f'{source.relative_to(root)}: Link outside repository: {target}'
    if not path.exists():
        return f'{source.relative_to(root)}: Missing local link: {target}'
    return None


def check_svg(text, source, root):
    label = source.relative_to(root)
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
        return [f'{label}: SVG document/entity declarations are unsupported']
    try:
        element = ET.fromstring(text)
    except ET.ParseError as error:
        return [f'{label}: Invalid SVG: {error}']
    if element.tag.split('}')[-1] != 'svg':
        return [f'{label}: Invalid SVG root element']
    errors = []
    for node in element.iter():
        if node.tag.split('}')[-1].lower() in {'script', 'foreignobject'}:
            errors.append(f'{label}: Active SVG content is unsupported')
        for attribute, value in node.attrib.items():
            name = attribute.split('}')[-1].lower()
            if name.startswith('on'):
                errors.append(f'{label}: Active SVG content is unsupported')
            if name == 'href' and value and not value.startswith('#'):
                errors.append(f'{label}: External SVG reference is unsupported')
    if re.search(r'url\(\s*["\']?(?:https?:|//|data:|file:)', text, re.IGNORECASE):
        errors.append(f'{label}: External SVG reference is unsupported')
    return errors


def check_repository(root):
    root = Path(root).resolve()
    if not root.is_dir():
        return [f'Repository directory does not exist: {root}']
    errors = []
    for folder, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = [name for name in directories if name not in IGNORED_DIRECTORIES]
        for name in sorted(filenames):
            source = Path(folder) / name
            if source.suffix.lower() not in {'.md', '.svg', '.json'}:
                continue
            if outside(source.resolve(), root):
                errors.append(f'{source.relative_to(root)}: File outside repository')
                continue
            try:
                text = source.read_text(encoding='utf-8-sig')
            except (OSError, UnicodeError) as error:
                errors.append(f'{source.relative_to(root)}: Cannot read UTF-8 document: {error}')
                continue
            extension = source.suffix.lower()
            if extension == '.md':
                prose, unclosed = prose_only(text)
                if unclosed:
                    errors.append(f'{source.relative_to(root)}: Unclosed code fence')
                targets = [match[1] for match in INLINE_LINK.finditer(prose)]
                targets.extend(match[1] for match in REFERENCE_LINK.finditer(prose))
                images = ImageSources()
                images.feed(prose)
                targets.extend(images.sources)
                for target in targets:
                    error = check_link(target, source, root)
                    if error:
                        errors.append(error)
            elif extension == '.svg':
                errors.extend(check_svg(text, source, root))
            else:
                try:
                    json.loads(text)
                except json.JSONDecodeError as error:
                    errors.append(f'{source.relative_to(root)}: Invalid JSON: {error}')
    return sorted(set(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Documentation repository to check')
    args = parser.parse_args()
    errors = check_repository(args.root)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f'Documentation checks failed: {len(errors)} error(s)', file=sys.stderr)
        return 1
    print('Documentation checks passed (offline; remote URLs and fragment targets are not verified).')
    return 0


if __name__ == '__main__':
    sys.exit(main())

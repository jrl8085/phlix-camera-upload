#!/usr/bin/env python3
"""Checks that the translated documents in docs/<language>/ still match the English ones.

usage: python3 scripts/check-translations.py            (all languages)
       python3 scripts/check-translations.py --bars     (rewrites the language bar of every file)

README.md, NETWORKING.md and SECURITY.md in English are the source. Each translation:
- starts with the language bar: every language in the same order, its own in bold;
- holds the same fenced code blocks as the English, byte for byte and in the same order
  (commands, the Compose text and settings are never translated);
- has the same number of headings at each level, so no section was left out;
- links only to files that exist.

When the English documents change, the translations have to follow; this script says
which file fell behind and how. CI runs it as a warning: a release is never held up by it.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = ('README.md', 'NETWORKING.md', 'SECURITY.md')
LANGUAGES = [('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français'), ('es', 'Español'), ('it', 'Italiano'),
             ('pt-BR', 'Português (Brasil)'), ('nl', 'Nederlands'), ('sv', 'Svenska'), ('da', 'Dansk'),
             ('nb', 'Norsk bokmål'), ('fi', 'Suomi'), ('pl', 'Polski'), ('ja', '日本語'), ('ko', '한국어'),
             ('zh-Hans', '简体中文'), ('zh-Hant', '繁體中文')]
FENCE = re.compile(r'^(```|~~~)')
LINK = re.compile(r'\]\(([^)#\s]+)(?:#[^)]*)?\)')


def path(code, doc):
    return os.path.join(ROOT, doc) if code == 'en' else os.path.join(ROOT, 'docs', code, doc)


def bar(code, doc):
    parts = []
    for other, name in LANGUAGES:
        if other == code:
            parts.append(f'**{name}**')
            continue
        target = path(other, doc)
        here = os.path.dirname(path(code, doc))
        parts.append(f'[{name}]({os.path.relpath(target, here)})')
    return ' · '.join(parts)


def code_blocks(text):
    blocks, current = [], None
    for line in text.splitlines():
        if FENCE.match(line.strip()):
            if current is None:
                current = [line]
            else:
                current.append(line)
                blocks.append('\n'.join(current))
                current = None
        elif current is not None:
            current.append(line)
    return blocks


def outline(text):
    counts, inside = {}, False
    for line in text.splitlines():
        if FENCE.match(line.strip()):
            inside = not inside
            continue
        match = re.match(r'^(#{1,6}) ', line)
        if match and not inside:
            counts[len(match.group(1))] = counts.get(len(match.group(1)), 0) + 1
    return counts


def rewrite_bars():
    for code, _ in LANGUAGES:
        for doc in DOCS:
            file = path(code, doc)
            if not os.path.exists(file):
                continue
            with open(file, encoding='utf-8') as f:
                lines = f.read().split('\n')
            if lines and '](' in lines[0] and ' · ' in lines[0]:
                lines[0] = bar(code, doc)
            else:
                lines[:0] = [bar(code, doc), '']
            with open(file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
    print('language bars written')


def main():
    if '--bars' in sys.argv:
        rewrite_bars()
        return
    problems = []
    for doc in DOCS:
        with open(path('en', doc), encoding='utf-8') as f:
            english = f.read()
        if english.split('\n', 1)[0] != bar('en', doc):
            problems.append(f'{doc}: the English language bar is missing or out of date (run with --bars)')
        source_blocks, source_outline = code_blocks(english), outline(english)
        for code, _ in LANGUAGES[1:]:
            file = path(code, doc)
            name = os.path.relpath(file, ROOT)
            if not os.path.exists(file):
                problems.append(f'{name}: missing')
                continue
            with open(file, encoding='utf-8') as f:
                text = f.read()
            if text.split('\n', 1)[0] != bar(code, doc):
                problems.append(f'{name}: the language bar differs (run with --bars)')
            blocks = code_blocks(text)
            if blocks != source_blocks:
                changed = next((i for i, (a, b) in enumerate(zip(blocks, source_blocks)) if a != b), min(len(blocks), len(source_blocks)))
                problems.append(f'{name}: code block {changed + 1} differs from the English '
                                f'({len(blocks)} blocks here, {len(source_blocks)} in English)')
            if outline(text) != source_outline:
                problems.append(f'{name}: headings {outline(text)} where the English has {source_outline}')
            for target in LINK.findall(text):
                if re.match(r'^[a-z]+:', target):
                    continue
                if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(file), target))):
                    problems.append(f'{name}: the link to {target} leads nowhere')
    if problems:
        print('The translations need updating:')
        for problem in problems:
            print('  ' + problem)
        sys.exit(1)
    print(f'The translations agree with the English documents ({len(LANGUAGES) - 1} languages).')


if __name__ == '__main__':
    main()

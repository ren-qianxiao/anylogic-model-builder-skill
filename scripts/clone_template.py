# -*- coding: utf-8 -*-
"""Copy an official AnyLogic example and rename the model.

Only the model display name is changed; structure and IDs stay intact so the
result is guaranteed to load. Use this as the base for later parameter edits.
"""
import argparse
import os
import re
import xml.etree.ElementTree as ET

NAME_CDATA = re.compile(
    r'(<Model>\s*<Id>[^<]*</Id>\s*<Name><!\[CDATA\[)(.*?)(\]\]></Name>)', re.S)
NAME_PLAIN = re.compile(
    r'(<Model>\s*<Id>[^<]*</Id>\s*<Name>)([^<]*)(</Name>)', re.S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--dst', required=True)
    ap.add_argument('--name', required=True)
    args = ap.parse_args()

    text = open(args.src, encoding='utf-8').read()
    if NAME_CDATA.search(text):
        new_text = NAME_CDATA.sub(lambda m: m.group(1) + args.name + m.group(3), text, count=1)
    elif NAME_PLAIN.search(text):
        new_text = NAME_PLAIN.sub(lambda m: m.group(1) + args.name + m.group(3), text, count=1)
    else:
        raise SystemExit('could not locate <Model>/<Name> in source')

    os.makedirs(os.path.dirname(os.path.abspath(args.dst)), exist_ok=True)
    with open(args.dst, 'w', encoding='utf-8') as f:
        f.write(new_text)

    # self-check: output parses and carries the new name
    root = ET.parse(args.dst).getroot()
    got = root.find('.//Model/Name')
    assert got is not None and (got.text or '').strip() == args.name, 'rename failed'
    print('written', args.dst)


if __name__ == '__main__':
    main()

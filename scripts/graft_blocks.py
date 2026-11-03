# -*- coding: utf-8 -*-
"""Graft blocks from one AnyLogic .alp into another, verbatim.

Copies the selected EmbeddedObject blocks, the Connectors between them, and the
TargetLines they reference, then rewrites ids/names/package/coordinates. The
block XML itself is never rebuilt, only retagged, so the structure stays exactly
as AnyLogic generated it.

Example:
  python graft_blocks.py \
    --example "Areas with Restrictions for Pedestrians.alp" \
    --target "AndonWarehouse44.alp" \
    --out "AndonWarehouse45.alp" \
    --blocks pedSource,pedGoTo,pedSink,pedSettings \
    --pkg-target warehouse_conveyor \
    --offset-x 140 --offset-y -380
"""
import argparse
import os
import re
import xml.etree.ElementTree as ET

BASE_ID = 1770000000000
_counter = [0]


def nid():
    _counter[0] += 1
    return str(BASE_ID + _counter[0])


def read(path):
    return open(path, encoding='utf-8').read()


def extract(text, tag, ident):
    i = text.index(f'<Id>{ident}</Id>')
    start = text.rindex(f'<{tag}>', 0, i)
    end = text.index(f'</{tag}>', i) + len(f'</{tag}>')
    return text[start:end]


def block_info(root):
    out = {}
    for e in root.iter('EmbeddedObject'):
        name = e.findtext('Name')
        aoc = e.find('ActiveObjectClass')
        if name and aoc is not None:
            out[name] = (e, aoc.findtext('ClassName'))
    return out


def referenced_lines(root, block_names):
    """TargetLine names referenced by any selected block's locationLine."""
    lines = set()
    for e in root.iter('EmbeddedObject'):
        if e.findtext('Name') not in block_names:
            continue
        params = e.find('Parameters')
        if params is None:
            continue
        for prm in params:
            if prm.findtext('Name') == 'locationLine':
                v = prm.find('Value')
                if v is not None:
                    code = v.findtext('Code')
                    if code:
                        lines.add(code)
    return lines


def relevant_connectors(root, block_names):
    out = []
    for c in root.iter('Connector'):
        se = c.find('SourceEmbeddedObjectReference')
        te = c.find('TargetEmbeddedObjectReference')
        if se is None or te is None:
            continue
        s, t = se.findtext('ItemName'), te.findtext('ItemName')
        if s in block_names and t in block_names:
            out.append(c)
    return out


def retag(xml, old_id, old_name, new_name, dx, dy, pkg_from, pkg_to):
    xml = xml.replace(f'<Id>{old_id}</Id>', f'<Id>{nid()}</Id>', 1)
    xml = xml.replace(f'<Name><![CDATA[{old_name}]]></Name>',
                      f'<Name><![CDATA[{new_name}]]></Name>', 1)
    # shift only the first X/Y pair (the element position, not Label children)
    m = re.search(r'<X>(-?\d+)</X>\s*<Y>(-?\d+)</Y>', xml)
    if m:
        x, y = int(m.group(1)) + dx, int(m.group(2)) + dy
        xml = xml[:m.start()] + f'<X>{x}</X><Y>{y}</Y>' + xml[m.end():]
    if pkg_from and pkg_to:
        xml = xml.replace(pkg_from, pkg_to)
    return xml


def connector_block(xml, src_item, src_port, tgt_item, tgt_port, name, pkg_from, pkg_to):
    xml = xml.replace(f'<Id>{xml.split("<Id>")[1].split("</Id>")[0]}</Id>',
                      f'<Id>{nid()}</Id>', 1)
    xml = re.sub(r'<Name><!\[CDATA\[[^\]]*\]\]></Name>',
                 f'<Name><![CDATA[{name}]]></Name>', xml, count=1)
    # Source side
    xml = re.sub(r'(<SourceEmbeddedObjectReference>.*?<ItemName><!\[CDATA\[)[^\]]*(\]\]></ItemName>)',
                 lambda m: m.group(1) + src_item + m.group(2), xml, count=1, flags=re.S)
    xml = re.sub(r'(<SourceConnectableItemReference>.*?<ItemName><!\[CDATA\[)[^\]]*(\]\]></ItemName>)',
                 lambda m: m.group(1) + src_port + m.group(2), xml, count=1, flags=re.S)
    # Target side
    xml = re.sub(r'(<TargetEmbeddedObjectReference>.*?<ItemName><!\[CDATA\[)[^\]]*(\]\]></ItemName>)',
                 lambda m: m.group(1) + tgt_item + m.group(2), xml, count=1, flags=re.S)
    xml = re.sub(r'(<TargetConnectableItemReference>.*?<ItemName><!\[CDATA\[)[^\]]*(\]\]></ItemName>)',
                 lambda m: m.group(1) + tgt_port + m.group(2), xml, count=1, flags=re.S)
    if pkg_from and pkg_to:
        xml = xml.replace(pkg_from, pkg_to)
    return xml


def check_refs(root):
    names = {e.findtext('Name') for e in root.iter() if e.findtext('Name')}
    bad = []
    for c in root.iter('Connector'):
        for ref in ('SourceEmbeddedObjectReference', 'TargetEmbeddedObjectReference'):
            x = c.find(ref)
            if x is not None:
                item = x.findtext('ItemName')
                if item and item not in names:
                    bad.append((c.findtext('Name'), item))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--example', required=True)
    ap.add_argument('--target', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--blocks', required=True, help='comma separated block names')
    ap.add_argument('--pkg-target', required=True)
    ap.add_argument('--offset-x', type=int, default=0)
    ap.add_argument('--offset-y', type=int, default=0)
    args = ap.parse_args()

    wanted = [b.strip() for b in args.blocks.split(',') if b.strip()]
    ex_text = read(args.example)
    ex_root = ET.parse(args.example).getroot()
    info = block_info(ex_root)
    missing = [b for b in wanted if b not in info]
    if missing:
        raise SystemExit('blocks not found: ' + ', '.join(missing))

    pkg_from = ex_root.find('.//Model/JavaPackageName').text
    pkg_to = args.pkg_target

    pieces = []
    for name in wanted:
        elem, cls = info[name]
        xml = extract(ex_text, 'EmbeddedObject', elem.findtext('Id'))
        pieces.append(retag(xml, elem.findtext('Id'), name, name,
                            args.offset_x, args.offset_y, pkg_from, pkg_to))

    for line_name in referenced_lines(ex_root, set(wanted)):
        found = None
        for t in ex_root.iter('TargetLine'):
            if t.findtext('Name') == line_name:
                found = t
                break
        if found is None:
            continue
        xml = extract(ex_text, 'TargetLine', found.findtext('Id'))
        pieces.append(retag(xml, found.findtext('Id'), line_name, line_name,
                            args.offset_x, args.offset_y, pkg_from, pkg_to))

    for c in relevant_connectors(ex_root, set(wanted)):
        src = c.find('SourceEmbeddedObjectReference').findtext('ItemName')
        tgt = c.find('TargetEmbeddedObjectReference').findtext('ItemName')
        sp = c.find('SourceConnectableItemReference').findtext('ItemName')
        tp = c.find('TargetConnectableItemReference').findtext('ItemName')
        xml = extract(ex_text, 'Connector', c.findtext('Id'))
        pieces.append(connector_block(xml, src, sp, tgt, tp,
                                      c.findtext('Name'), pkg_from, pkg_to))

    text = read(args.target)
    main_pos = text.index('<Name><![CDATA[Main]]></Name>')
    level_start = text.index('<Level>', main_pos)
    level_end = text.index('</Level>', main_pos)
    pres_close = text.rindex('</Presentation>', level_start, level_end)
    payload = '\n' + '\n'.join(pieces) + '\n'
    text = text[:pres_close] + payload + text[pres_close:]

    # library references from the example, minus ones the target already has
    target_libs = {lr.findtext('LibraryName') for lr in ET.parse(args.target).getroot().iter('RequiredLibraryReference')}
    libs = ''
    for lr in ex_root.iter('RequiredLibraryReference'):
        n = lr.findtext('LibraryName')
        if n and n not in target_libs:
            libs += (f'\t<RequiredLibraryReference>\n\t\t<LibraryName><![CDATA[{n}]]></LibraryName>\n'
                     f'\t\t<VersionMajor>1</VersionMajor>\n\t\t<VersionMinor>0</VersionMinor>\n'
                     f'\t\t<VersionBuild>0</VersionBuild>\n\t</RequiredLibraryReference>\n')
    if libs:
        text = text.replace('</Model>', libs + '</Model>', 1)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8', newline='') as f:
        f.write(text)

    root = ET.parse(args.out).getroot()
    bad = check_refs(root)
    print('written:', args.out)
    print('blocks grafted:', len(wanted), 'connectors:', len(relevant_connectors(ex_root, set(wanted))))
    print('dangling refs:', len(bad))
    if bad:
        for b in bad[:10]:
            print('  ', b)


if __name__ == '__main__':
    main()

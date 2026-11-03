# -*- coding: utf-8 -*-
"""Print a structural summary of an AnyLogic .alp file."""
import argparse
import collections
import sys
import xml.etree.ElementTree as ET


def summarize(path):
    root = ET.parse(path).getroot()
    model = root.find('.//Model')
    if model is None:
        raise SystemExit('not an AnyLogic .alp: missing <Model>')

    name = model.findtext('Name') or '?'
    pkg = model.findtext('JavaPackageName') or '?'
    version = root.attrib.get('AnyLogicVersion', '?')

    classes = []
    for ac in root.iter('ActiveObjectClass'):
        cls_name = ac.findtext('Name') or '?'
        blocks = collections.Counter()
        for eo in ac.iter('EmbeddedObject'):
            aoc = eo.find('ActiveObjectClass')
            if aoc is not None:
                blocks[aoc.findtext('ClassName') or '?'] += 1
        connectors = len(list(ac.iter('Connector')))
        lines = len(list(ac.iter('TargetLine')))
        figures = len(list(ac.iter('Figure3D')))
        classes.append((cls_name, blocks, connectors, lines, figures))

    experiments = [(e.tag, e.findtext('Name') or '?') for e in root.iter()
                   if e.tag.endswith('Experiment')]

    return name, pkg, version, classes, experiments


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('alp')
    args = ap.parse_args()

    name, pkg, version, classes, experiments = summarize(args.alp)
    print(f'Model: {name}')
    print(f'Package: {pkg}')
    print(f'AnyLogic: {version}')
    print(f'Experiments: {", ".join(n for _, n in experiments) or "none"}')
    for cls, blocks, conn, lines, figs in classes:
        print(f'\n[ActiveObjectClass] {cls}')
        print(f'  blocks={sum(blocks.values())} connectors={conn} targetLines={lines} figures3D={figs}')
        for k, v in blocks.most_common(12):
            print(f'    {k} x{v}')
    assert name and pkg, 'incomplete parse'
    print('\nlist endpoint', file=sys.stderr)


if __name__ == '__main__':
    main()

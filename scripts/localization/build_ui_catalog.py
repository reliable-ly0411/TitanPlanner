#!/usr/bin/env python3
"""将审阅过的界面词典编译为标准 .NET 卫星资源，不访问网络。"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]


def catalog():
    values = {}
    for name in ('ui-translations.json', 'code-translations.json'):
        values.update(json.loads((ROOT / 'localization/zh-Hans' / name).read_text(encoding='utf-8')))
    return values


def resource(values):
    root = ET.Element('root')
    for name, value in (
        ('resmimetype', 'text/microsoft-resx'), ('version', '2.0'),
        ('reader', 'System.Resources.ResXResourceReader, System.Windows.Forms, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089'),
        ('writer', 'System.Resources.ResXResourceWriter, System.Windows.Forms, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089'),
    ):
        ET.SubElement(ET.SubElement(root, 'resheader', name=name), 'value').text = value
    for english, chinese in sorted(values.items()):
        # RESX 编译器会忽略键名大小写；哈希键区分 Arm/ARM 等不同源文。
        key = hashlib.sha256(english.encode('utf-8')).hexdigest()
        item = ET.SubElement(root, 'data', name=key)
        item.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        ET.SubElement(item, 'value').text = chinese
        ET.SubElement(item, 'comment').text = json.dumps(english, ensure_ascii=False)
    ET.indent(root)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    entries = catalog()
    for name, values in (('UiText.resx', {}), ('UiText.zh-Hans.resx', {}), ('UiText.zh-CN.resx', entries)):
        path = ROOT / 'ExtLibs/Utilities/Resources' / name
        expected = resource(values)
        if args.check:
            if not path.exists() or path.read_bytes() != expected:
                raise SystemExit(f'资源需要重新生成：{path.relative_to(ROOT)}')
        else:
            path.write_bytes(expected)
    print(f'UI 字典：{len(entries)} 条；' + ('检查通过' if args.check else '资源已生成'))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""离线检查汉化词典、格式占位符、链接与生成资源。"""
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from build_ui_catalog import ROOT, catalog


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'重复词条：{key}')
        result[key] = value
    return result


def main():
    for path in (ROOT / 'localization/zh-Hans').glob('*translations.json'):
        json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    placeholders = re.compile(r'(?<!\{)\{[^{}]+\}(?!\})')
    urls = re.compile(r'https?://[^\s;\]）)]+')
    errors = []
    entries = catalog()
    for english, chinese in entries.items():
        if sorted(placeholders.findall(english)) != sorted(placeholders.findall(chinese)):
            errors.append(f'占位符不一致：{english!r}')
        if urls.findall(english) != urls.findall(chinese):
            errors.append(f'链接不一致：{english!r}')
        if not chinese.strip():
            errors.append(f'空译文：{english!r}')
    # 资源键使用稳定哈希，检查 .NET 不区分大小写的资源名规则。
    resources = ROOT / 'ExtLibs/Utilities/Resources/UiText.zh-Hans.resx'
    names = [e.get('name').casefold() for e in ET.parse(resources).findall('data')]
    if len(names) != len(set(names)) or len(names) != len(entries):
        errors.append('卫星资源存在重复或缺失词条')
    # 验证所有中文 RESX 的 XML 结构，而非仅检查新增文件。
    count = 0
    for path in ROOT.rglob('*.zh-Hans.resx'):
        if 'mono' in path.parts or 'obj' in path.parts or 'bin' in path.parts:
            continue
        ET.parse(path)
        count += 1
    if errors:
        raise SystemExit('\n'.join(errors))
    for script in ('build_ui_catalog.py', 'update_zh_hans.py'):
        subprocess.run([sys.executable, str(Path(__file__).with_name(script)), '--check'], check=True)
    print(f'验证通过：{len(entries)} 条翻译，{count} 个简体中文资源文件；占位符和链接完整。')


if __name__ == '__main__':
    main()

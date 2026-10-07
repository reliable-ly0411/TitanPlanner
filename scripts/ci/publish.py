#!/usr/bin/env python3
"""Publish only the exact artifact validated by this workflow; never replace a release."""
import hashlib
import json
import os
from pathlib import Path
import re
from upstream import git, promote, run

sha, base = os.environ['BUILD_SHA'], os.environ['BASE_SHA']
if not all(re.fullmatch(r'[0-9a-f]{40}', value) for value in (sha, base)):
    raise RuntimeError('Invalid commit SHA')
root = Path('release')
metadata = json.loads((root / 'build-info.json').read_text())
expected_name = f'TitanPlanner-zh2-{sha[:12]}-windows.zip'
if metadata['commit'] != sha or metadata['archive'] != expected_name:
    raise RuntimeError('Artifact commit does not match validated candidate')
archive = root / expected_name
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
if digest != metadata['sha256'] or (root / 'SHA256SUMS').read_text().strip() != f'{digest}  {expected_name}':
    raise RuntimeError('Artifact hash mismatch')
if os.environ.get('CANDIDATE_BRANCH'):
    git('fetch', 'origin', os.environ['CANDIDATE_BRANCH'])
promote(base, sha)
repo = os.environ['GITHUB_REPOSITORY']
tag = 'zh2-' + sha[:12]
exists = run('gh', 'release', 'view', tag, '--repo', repo, '--json', 'url', check=False)
if exists.returncode == 0:
    refs = git('ls-remote', 'origin', 'refs/tags/' + tag, 'refs/tags/' + tag + '^{}').splitlines()
    target = next((line.split()[0] for line in refs if line.endswith('^{}')), refs[0].split()[0] if refs else '')
    if target != sha:
        raise RuntimeError('Existing release tag points to another commit; refusing to overwrite it')
    print('Release already exists; immutable assets retained: ' + exists.stdout)
else:
    notes = root / 'release-notes.md'
    notes.write_text('自动构建的 Windows 便携版（测试版）。\n\n'
                     '- 保留“中文(简体)”与增强“中文(简体)2”，选择后重启生效。\n'
                     '- 已通过中文资源、翻译运行、Windows 控件及离线回归测试、Release/Debug 构建和依赖漏洞检查。\n'
                     '- 解压完整 ZIP 后启动 MissionPlanner.exe；不要仅复制 EXE。\n'
                     '- 包含 SHA256SUMS 校验文件。未签名；真实飞控、飞行、高 DPI 与所有外部服务尚需实机验收。\n\n'
                     f'构建提交：`{sha}`\n', encoding='utf-8')
    print(run('gh', 'release', 'create', tag, str(archive), str(root / 'SHA256SUMS'), str(root / 'build-info.json'),
              '--repo', repo, '--target', sha, '--title', 'TitanPlanner 中文双版本 ' + sha[:12],
              '--prerelease', '--notes-file', str(notes)).stdout)

#!/usr/bin/env python3
"""Publish a complete verified terrain pack without changing the app's latest release."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from package import HGT_BYTES, read_plan, sha256_file


def gh(*args, payload=None, check=True):
    result = subprocess.run(['gh', *args], input=None if payload is None else json.dumps(payload),
                            text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr)
    return result


def api(endpoint, method='GET', payload=None):
    args = ['api', endpoint, '--method', method]
    if payload is not None:
        args += ['--input', '-']
    return json.loads(gh(*args, payload=payload).stdout)


def validate_bundle(root, config, selected):
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    if manifest['tag'] != config['tag'] or manifest['actual_tile_count'] != len(selected):
        raise ValueError('Manifest release or count mismatch')
    if [t['tile'] for t in manifest['tiles']] != selected:
        raise ValueError('Missing or duplicate tiles in manifest')
    if any(t['hgt_bytes'] != HGT_BYTES for t in manifest['tiles']):
        raise ValueError('Non-30m tile in manifest')
    files = {a['name']: a['sha256'] for a in manifest['parts']}
    if sum(a['tile_count'] for a in manifest['parts']) != len(selected):
        raise ValueError('Part counts do not cover all tiles')
    files.update({n: sha256_file(root / n) for n in ['manifest.json', 'INSTALL.zh-CN.txt']})
    expected_checksums = ''.join(f'{h}  {n}\n' for n, h in files.items())
    if (root / 'SHA256SUMS').read_text() != expected_checksums:
        raise ValueError('SHA256SUMS does not match manifest')
    for name, digest in files.items():
        if Path(name).name != name or sha256_file(root / name) != digest:
            raise ValueError('Release asset integrity failure: ' + name)
    files['SHA256SUMS'] = sha256_file(root / 'SHA256SUMS')
    return manifest, files


def publish(root):
    config, selected = read_plan('data/terrain/request.json', 'data/terrain/china-tiles.txt')
    manifest, files = validate_bundle(root, config, selected)
    repo, sha = os.environ['GITHUB_REPOSITORY'], os.environ['GITHUB_SHA']
    if repo != 'reliable-ly0411/TitanPlanner-zh-CN' or manifest['build_commit'] != sha:
        raise ValueError('Unexpected repository or build commit')
    endpoint = f'repos/{repo}/releases'
    found = gh('api', endpoint + '/tags/' + config['tag'], check=False)
    notes = (f"官方来源：中国区 1 角秒（约 30 米）HGT 离线包，共 {len(selected)} 个图幅。\n\n"
             "下载全部 part*.zip，分别解压到同一个临时目录；按 INSTALL.zh-CN.txt 安装。每个 ZIP 都可独立解压。\n\n"
             "覆盖按 MFE 中国区包的 1166 个图幅名称确定，仅复用覆盖清单，不含 MFE 高程值。"
             "官方缺少的 4 个图幅为 N18E111、N20E108、N20E111、N27E122；旧包中这四幅也全部是 -9999 无效值。"
             "此处“完整”指清单内所有官方可用图幅均已收录，不是国界裁切或全部海岛完整性承诺。\n\n"
             "来源：https://terrain.ardupilot.org/SRTM1/ 。保留下载到的 HGT 原始字节，逐幅验证 ZIP CRC、"
             "3601×3601 尺寸、SHA-256，并对重打包文件完整回读验证。解压后约 28.1 GiB。\n\n"
             "Credit: JAXA ALOS World 3D (AW3D30), as attributed by ArduPilot; distribution/conversion: ArduPilot. "
             "数据许可与限制见 https://earth.jaxa.jp/en/data/policy/ 。上游产品版本未独立鉴定。\n\n"
             "这是地形数据包，不是 TitanPlanner 程序更新；HGT 不能直接作为飞控 APM/TERRAIN 的 DAT 使用。"
             "校验通过证明传输和打包完整，不代表实地高程或飞行验证。\n\n"
             f"打包提交：`{sha}`\n快照开始时间：{manifest['snapshot_started_utc']}\n")
    if found.returncode == 0:
        release = json.loads(found.stdout)
        if not release['draft'] or release['target_commitish'] != sha:
            raise ValueError('Existing release is published or belongs to another commit; refusing to overwrite')
    else:
        if '404' not in found.stderr:
            raise RuntimeError(found.stderr)
        release = api(endpoint, 'POST', {'tag_name': config['tag'], 'target_commitish': sha,
                                         'name': config['title'], 'body': notes, 'draft': True,
                                         'prerelease': False, 'make_latest': 'false'})
    assets = {a['name']: a for a in release['assets']}
    if set(assets) - set(files):
        raise ValueError('Unexpected assets in existing draft; refusing to overwrite')
    for name, digest in files.items():
        if name in assets:
            if assets[name].get('digest') != 'sha256:' + digest:
                raise ValueError('Existing draft asset differs: ' + name)
            continue
        gh('release', 'upload', config['tag'], str(root / name), '--repo', repo)
        print('Uploaded ' + name, flush=True)
    release = api(endpoint + '/' + str(release['id']))
    assets = {a['name']: a for a in release['assets']}
    if set(assets) != set(files):
        raise ValueError('Remote asset set incomplete')
    for name, digest in files.items():
        a = assets[name]
        if a['state'] != 'uploaded' or a['size'] != (root / name).stat().st_size or a.get('digest') != 'sha256:' + digest:
            raise ValueError('Remote asset size/SHA256 verification failed: ' + name)
    result = api(endpoint + '/' + str(release['id']), 'PATCH',
                 {'draft': False, 'make_latest': 'false', 'body': notes})
    print('Published: ' + result['html_url'], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory', type=Path)
    publish(p.parse_args().directory)

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


def release_context():
    config, selected = read_plan('data/terrain/request.json', 'data/terrain/china-tiles.txt')
    repo, sha = os.environ['GITHUB_REPOSITORY'], os.environ['GITHUB_SHA']
    if repo != 'reliable-ly0411/TitanPlanner-zh-CN':
        raise ValueError('Unexpected repository')
    return config, selected, repo, sha


def optional_api(endpoint):
    found = gh('api', endpoint, check=False)
    if found.returncode == 0:
        return json.loads(found.stdout)
    if '404' not in found.stderr:
        raise RuntimeError(found.stderr)
    return None


def find_release(repo, tag):
    # The by-tag endpoint only returns published releases. Listing includes drafts.
    pages = json.loads(gh('api', f'repos/{repo}/releases?per_page=100', '--paginate', '--slurp').stdout)
    matches = [release for page in pages for release in page if release['tag_name'] == tag]
    if len(matches) > 1:
        raise ValueError('Multiple releases for the same tag')
    return matches[0] if matches else None


def require_draft(release, sha):
    if not release['draft'] or release['target_commitish'] != sha:
        raise ValueError('Existing release is published or belongs to another commit; refusing to overwrite')


def prepare():
    """Freeze the tag and verify release permissions before the long download."""
    config, _, repo, sha = release_context()
    endpoint = f'repos/{repo}'
    release = find_release(repo, config['tag'])
    if release:
        require_draft(release, sha)
    tag = optional_api(endpoint + '/git/ref/tags/' + config['tag'])
    if tag:
        if tag['object']['type'] != 'commit' or tag['object']['sha'] != sha:
            raise ValueError('Existing tag belongs to another commit; refusing to move it')
    else:
        api(endpoint + '/git/refs', 'POST', {'ref': 'refs/tags/' + config['tag'], 'sha': sha})
    if not release:
        release = api(endpoint + '/releases', 'POST',
                      {'tag_name': config['tag'], 'target_commitish': sha,
                       'name': config['title'], 'body': 'Preparing terrain data; not yet verified or published.',
                       'draft': True, 'prerelease': False, 'make_latest': 'false'})
    require_draft(release, sha)
    # Exercise the exact lookup and upload paths now, before spending time downloading.
    confirmed = find_release(repo, config['tag'])
    if not confirmed or confirmed['id'] != release['id']:
        raise ValueError('Created draft cannot be found by the publisher')
    require_draft(confirmed, sha)
    notes = Path('data/terrain/INSTALL.zh-CN.txt')
    assets = {a['name']: a for a in confirmed['assets']}
    if notes.name not in assets:
        gh('release', 'upload', config['tag'], str(notes), '--repo', repo)
    confirmed = api(endpoint + '/releases/' + str(release['id']))
    uploaded = next(a for a in confirmed['assets'] if a['name'] == notes.name)
    if uploaded.get('digest') != 'sha256:' + sha256_file(notes) or uploaded['size'] != notes.stat().st_size:
        raise ValueError('Preflight upload hash/size mismatch')
    print('Prepared draft and verified test upload: ' + release['html_url'], flush=True)


def publish(root):
    config, selected, repo, sha = release_context()
    manifest, files = validate_bundle(root, config, selected)
    if manifest['build_commit'] != sha:
        raise ValueError('Unexpected repository or build commit')
    endpoint = f'repos/{repo}/releases'
    release = find_release(repo, config['tag'])
    if not release:
        raise ValueError('Prepared draft missing; run --prepare before downloading')
    require_draft(release, sha)
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
    p.add_argument('directory', type=Path, nargs='?')
    p.add_argument('--prepare', action='store_true')
    args = p.parse_args()
    if args.prepare and args.directory is None:
        prepare()
    elif args.directory is not None and not args.prepare:
        publish(args.directory)
    else:
        p.error('choose --prepare or a bundle directory')

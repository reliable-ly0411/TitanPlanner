#!/usr/bin/env python3
"""Package a clean Windows build and verify both languages, excluding local state."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

EXCLUDED_DIRS = {'logs', 'gmapcache', 'srtm', '.git', 'testresults'}
EXCLUDED_NAMES = {'config.xml', 'profile.txt', 'custom.config.xml'}


def package(source, destination, sha):
    source, destination = Path(source), Path(destination)
    if destination.resolve().is_relative_to(source.resolve()):
        raise ValueError('Package destination must be outside the build directory')
    required = ['MissionPlanner.exe', 'MissionPlanner.exe.config', 'MissionPlanner.Utilities.dll',
                'zh-Hans/MissionPlanner.resources.dll', 'zh-CN/MissionPlanner.resources.dll',
                'zh-CN/MissionPlanner.Utilities.resources.dll', 'ProDotNetZip.dll', 'x64/libSkiaSharp.dll', 'x86/libSkiaSharp.dll']
    missing = [name for name in required if not (source / name).is_file()]
    if missing:
        raise ValueError('Incomplete Windows build: ' + ', '.join(missing))
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f'TitanPlanner-zh2-{sha[:12]}-windows.zip'
    files = []
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(source.rglob('*')):
            if not path.is_file():
                continue
            relative = path.relative_to(source)
            lower = relative.as_posix().lower()
            if set(part.lower() for part in relative.parts) & EXCLUDED_DIRS:
                continue
            if path.name.lower() in EXCLUDED_NAMES or path.name.lower().startswith('config_') or lower.endswith(('.log', '.tlog', '.binlog')):
                continue
            # Obsolete vulnerable ZIP assemblies must never survive incremental builds.
            if path.name.lower() in {'dotnetzip.dll', 'ionic.zip.dll', 'ionic.zip.netstandard.dll'}:
                raise ValueError('Stale vulnerable ZIP assembly in output: ' + str(relative))
            z.write(path, relative.as_posix())
            files.append({'path': relative.as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        z.writestr('BUILD-INFO.json', json.dumps({'commit': sha, 'languages': ['中文(简体)', '中文(简体)2'], 'files': files}, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None or not set(required).issubset(z.namelist()):
            raise ValueError('Package round-trip verification failed')
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (destination / 'SHA256SUMS').write_text(f'{digest}  {archive.name}\n', encoding='ascii')
    (destination / 'build-info.json').write_text(json.dumps({'commit': sha, 'archive': archive.name, 'sha256': digest, 'file_count': len(files)}, indent=2)+'\n')
    print(f'Verified {archive.name}: {len(files)} files, SHA-256 {digest}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source'); parser.add_argument('destination'); parser.add_argument('sha')
    args = parser.parse_args()
    package(args.source, args.destination, args.sha)

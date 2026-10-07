#!/usr/bin/env python3
"""Exercise install, repair and uninstall in an ephemeral Windows CI runner."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile
from release_artifacts import verify_manifest


def smoke(root, sha, results):
    if os.name != 'nt' or os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Installer smoke test is restricted to disposable GitHub Windows runners')
    root, results = Path(root).resolve(), Path(results).resolve()
    results.mkdir(parents=True, exist_ok=True)
    archive, installer = verify_manifest(root, sha)
    installed = Path(os.environ['LOCALAPPDATA'])/'Programs'/'TitanPlanner-zh-CN'
    shortcut = Path(os.environ['APPDATA'])/'Microsoft'/'Windows'/'Start Menu'/'Programs'/'TitanPlanner-zh-CN'/'TitanPlanner-zh-CN.lnk'
    if installed.exists() or shortcut.exists():
        raise RuntimeError('Refusing to alter a pre-existing installation')
    def msi(operation, name):
        run = subprocess.run(['msiexec.exe', operation, str(installer), '/qn', '/norestart', '/L*v', str(results/(name+'.log'))])
        if run.returncode not in (0, 3010):
            raise RuntimeError(f'MSI {name} failed: {run.returncode}; see verbose log')
    def compare():
        with zipfile.ZipFile(archive) as z:
            for name in z.namelist():
                path = installed/name
                if not path.is_file() or hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(z.read(name)).digest():
                    raise RuntimeError('Installed payload differs from ZIP: '+name)
    msi('/i', 'msi-install')
    try:
        compare()
        if not shortcut.is_file():
            raise RuntimeError('Start menu shortcut missing')
        config = installed/'config.xml'
        log = installed/'logs'/'personal.tlog'
        log.parent.mkdir(exist_ok=True)
        config.write_bytes(b'personal configuration preserved')
        log.write_bytes(b'personal flight log preserved')
        (installed/'MissionPlanner.exe').unlink()
        msi('/fa', 'msi-repair')
        compare()
    finally:
        msi('/x', 'msi-uninstall')
    if (installed/'MissionPlanner.exe').exists() or shortcut.exists():
        raise RuntimeError('Uninstall left a program/shortcut behind')
    if config.read_bytes() != b'personal configuration preserved' or log.read_bytes() != b'personal flight log preserved':
        raise RuntimeError('Uninstall modified personal data')
    result = {'commit': sha, 'install': 'passed', 'payload_matches_zip': True,
              'repair': 'passed', 'uninstall': 'passed', 'personal_config_and_logs_preserved': True}
    (results/'msi-smoke.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    smoke(*sys.argv[1:])

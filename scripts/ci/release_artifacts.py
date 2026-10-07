"""Hash and require the complete ZIP/MSI pair before publishing."""
import hashlib
import json
from pathlib import Path
import re


def artifact_names(sha):
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Invalid commit SHA')
    return [f'TitanPlanner-zh2-{sha[:12]}-windows.{ext}' for ext in ('zip', 'msi')]


def write_manifest(root, sha, **extra):
    root = Path(root)
    entries = [{'name': name, 'sha256': hashlib.sha256((root/name).read_bytes()).hexdigest(),
                'size': (root/name).stat().st_size} for name in artifact_names(sha)]
    (root/'build-info.json').write_text(json.dumps({'commit': sha, 'artifacts': entries, **extra}, indent=2)+'\n', encoding='utf-8')
    (root/'SHA256SUMS').write_text(''.join(f"{e['sha256']}  {e['name']}\n" for e in entries), encoding='ascii')


def verify_manifest(root, sha):
    root = Path(root)
    data = json.loads((root/'build-info.json').read_text(encoding='utf-8'))
    entries = data.get('artifacts', [])
    if data['commit'] != sha or [e['name'] for e in entries] != artifact_names(sha):
        raise ValueError('Release must contain exactly the validated ZIP and MSI')
    for e in entries:
        path = root/e['name']
        if path.stat().st_size != e['size'] or hashlib.sha256(path.read_bytes()).hexdigest() != e['sha256']:
            raise ValueError('Artifact hash/size mismatch: ' + e['name'])
    if (root/'SHA256SUMS').read_text(encoding='ascii') != ''.join(f"{e['sha256']}  {e['name']}\n" for e in entries):
        raise ValueError('Checksum manifest mismatch')
    return [root/e['name'] for e in entries]

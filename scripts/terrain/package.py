#!/usr/bin/env python3
"""Download the official HGT bytes, validate them, and create bounded ZIP parts."""
import argparse
from array import array
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile

HGT_BYTES = 3601 * 3601 * 2
BASE = 'https://terrain.ardupilot.org/SRTM1/'
MAX_PART = 1_800_000_000
TILE = re.compile(r'N\d{2}E\d{3}')


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def validate_tile(tile, payload):
    if not TILE.fullmatch(tile):
        raise ValueError('Invalid tile name')
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        if z.namelist() != [tile + '.hgt']:
            raise ValueError(f'{tile}: unexpected ZIP members')
        entry = z.infolist()[0]
        if entry.file_size != HGT_BYTES:
            raise ValueError(f'{tile}: expected 3601x3601 signed int16 HGT')
        data = z.read(entry)  # ZIP CRC is checked here.
    if len(data) != HGT_BYTES:
        raise ValueError(f'{tile}: truncated HGT')
    values = array('h')
    values.frombytes(data)
    if sys.byteorder == 'little':
        values.byteswap()
    voids = values.count(-32768)
    legacy_invalid = values.count(-9999)
    if voids + legacy_invalid == len(values):
        raise ValueError(f'{tile}: entirely invalid elevation tile')
    return data, {
        'tile': tile, 'hgt_bytes': len(data),
        'hgt_sha256': hashlib.sha256(data).hexdigest(),
        'source_zip_bytes': len(payload),
        'source_zip_sha256': hashlib.sha256(payload).hexdigest(),
        'void_minus32768_nodes': voids,
        'invalid_minus9999_nodes': legacy_invalid,
    }


def download(tile):
    url = BASE + tile + '.hgt.zip'
    for attempt in range(5):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'TitanPlanner-terrain-packager/1.0'})
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = response.read(HGT_BYTES + 1024 * 1024 + 1)
                if len(payload) > HGT_BYTES + 1024 * 1024:
                    raise ValueError('Unexpectedly large upstream ZIP')
                metadata = dict(source_url=url, source_last_modified=response.headers.get('Last-Modified'),
                                source_etag=response.headers.get('ETag'),
                                retrieved_at_utc=datetime.now(timezone.utc).isoformat())
            data, record = validate_tile(tile, payload)
            record.update(metadata)
            return data, record
        except (OSError, ValueError, zipfile.BadZipFile, urllib.error.URLError):
            if attempt == 4:
                raise
            time.sleep(min(2 ** attempt, 16))


def ordered_downloads(tiles, workers):
    # Keep at most `workers` downloaded tiles in memory, including completed futures.
    with ThreadPoolExecutor(max_workers=workers) as executor:
        iterator = iter(tiles)
        pending = deque()
        for _ in range(workers):
            tile = next(iterator, None)
            if tile:
                pending.append(executor.submit(download, tile))
        while pending:
            yield pending.popleft().result()
            tile = next(iterator, None)
            if tile:
                pending.append(executor.submit(download, tile))


def read_plan(config_path, tiles_path):
    config = json.loads(Path(config_path).read_text(encoding='utf-8'))
    tiles = Path(tiles_path).read_text().splitlines()
    if config['source_base'] != BASE:
        raise ValueError('This packager only accepts the official MP SRTM1 source')
    if len(tiles) != config['requested_tiles'] or tiles != sorted(set(tiles)):
        raise ValueError('Incomplete, unsorted or duplicate coverage list')
    if not all(TILE.fullmatch(t) for t in tiles):
        raise ValueError('Invalid tile in coverage list')
    if not set(config['excluded']) <= set(tiles):
        raise ValueError('Excluded tiles are outside the requested coverage')
    selected = [t for t in tiles if t not in config['excluded']]
    if len(selected) != config['available_tiles']:
        raise ValueError('Unexpected available tile count')
    return config, selected


def preflight(config, tiles):
    with urllib.request.urlopen(BASE, timeout=90) as response:
        index = response.read().decode('utf-8')
    available = set(re.findall(r'href="(N\d{2}E\d{3})\.hgt\.zip"', index))
    if set(tiles) - available:
        raise ValueError('Upstream missing requested tiles: ' + str(sorted(set(tiles) - available)))
    for tile in config['excluded']:
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE + tile + '.hgt.zip', method='HEAD'), timeout=45):
                pass
        except urllib.error.HTTPError as error:
            if error.code == 404:
                continue
            raise
        raise ValueError(f'{tile} became available; review the coverage plan before publishing')
    return hashlib.sha256(index.encode()).hexdigest()


def verify_part(path, records):
    expected = {'srtm/' + r['tile'] + '.hgt': r for r in records}
    with zipfile.ZipFile(path) as z:
        actual = [name for name in z.namelist() if name.startswith('srtm/')]
        if len(actual) != len(expected) or set(actual) != set(expected):
            raise ValueError('Package tile coverage mismatch')
        for name in z.namelist():
            payload = z.read(name)  # Verify all CRCs, including package notes.
            if name in expected:
                if len(payload) != HGT_BYTES or hashlib.sha256(payload).hexdigest() != expected[name]['hgt_sha256']:
                    raise ValueError('HGT changed during packaging: ' + name)
    if path.stat().st_size >= MAX_PART:
        raise ValueError('Release asset exceeds the part limit')
    return {'name': path.name, 'bytes': path.stat().st_size,
            'sha256': sha256_file(path), 'tile_count': len(records),
            'first_tile': records[0]['tile'], 'last_tile': records[-1]['tile']}


def build(config, tiles, output, notes, workers=4, source_index_sha256=None):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError('Output directory must be empty; previous verified releases are never overwritten')
    stamp = datetime.now(timezone.utc)
    zip_date = (stamp.year, stamp.month, stamp.day, stamp.hour, stamp.minute, stamp.second)
    all_records, assets, part_records = [], [], []
    archive = None
    path = None
    try:
        for number, (data, record) in enumerate(ordered_downloads(tiles, workers), 1):
            # Reserve the worst-case next HGT size and ample ZIP overhead.
            if archive and archive.fp.tell() + HGT_BYTES + 1_000_000 >= MAX_PART:
                archive.close()
                assets.append(verify_part(path, part_records))
                archive, part_records = None, []
            if archive is None:
                name = f"{config['tag']}-part{len(assets) + 1:02d}.zip"
                path = output / name
                archive = zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6)
                archive.writestr('INSTALL.zh-CN.txt', notes)
            name = 'srtm/' + record['tile'] + '.hgt'
            info = zipfile.ZipInfo(name, date_time=zip_date)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=6)
            record['package'] = path.name
            all_records.append(record)
            part_records.append(record)
            print(f"{number}/{len(tiles)} {record['tile']} sha256={record['hgt_sha256']}", flush=True)
        if archive:
            archive.close()
            assets.append(verify_part(path, part_records))
            archive = None
    finally:
        if archive:
            archive.close()
    if [r['tile'] for r in all_records] != tiles:
        raise ValueError('Incomplete download: refusing to produce a release manifest')
    manifest = dict(config, snapshot_started_utc=stamp.isoformat(),
                    source_index_sha256=source_index_sha256,
                    build_commit=__import__('os').environ.get('GITHUB_SHA'),
                    actual_tile_count=len(all_records),
                    uncompressed_hgt_bytes=len(all_records) * HGT_BYTES,
                    grid_shape=[3601, 3601], horizontal_spacing_arcseconds=1,
                    zip_timestamp_policy='Packaging time, to avoid MP deleting newly fetched files with pre-2026-03-01 ZIP timestamps. Original HTTP Last-Modified retained per tile.',
                    parts=assets, tiles=all_records)
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (output / 'INSTALL.zh-CN.txt').write_text(notes, encoding='utf-8')
    checksums = [(a['sha256'], a['name']) for a in assets]
    checksums.extend((sha256_file(output / n), n) for n in ['manifest.json', 'INSTALL.zh-CN.txt'])
    (output / 'SHA256SUMS').write_text(''.join(f'{h}  {n}\n' for h, n in checksums))
    print(json.dumps({'tiles': len(all_records), 'parts': len(assets),
                      'compressed_bytes': sum(a['bytes'] for a in assets)}, indent=2), flush=True)
    return manifest


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', default='data/terrain/request.json')
    p.add_argument('--tiles', default='data/terrain/china-tiles.txt')
    p.add_argument('--notes', default='data/terrain/INSTALL.zh-CN.txt')
    p.add_argument('--output', required=True)
    p.add_argument('--workers', type=int, default=4, choices=range(1, 9))
    args = p.parse_args()
    config, tiles = read_plan(args.config, args.tiles)
    index_sha = preflight(config, tiles)
    build(config, tiles, args.output, Path(args.notes).read_text(encoding='utf-8'), args.workers, index_sha)

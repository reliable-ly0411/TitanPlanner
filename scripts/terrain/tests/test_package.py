import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import package
import publish


def zipped(name, data, compression=zipfile.ZIP_DEFLATED):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=compression) as z:
        z.writestr(name, data)
    return out.getvalue()


class SourceTests(unittest.TestCase):
    def test_rejects_90m_source_without_resampling(self):
        payload = zipped('N30E103.hgt', b'\0' * (1201 * 1201 * 2))
        with self.assertRaisesRegex(ValueError, '3601x3601'):
            package.validate_tile('N30E103', payload)

    def test_rejects_wrong_filename_and_extra_members(self):
        for name in ['../N30E103.hgt', 'N30E104.hgt']:
            with self.assertRaisesRegex(ValueError, 'unexpected ZIP members'):
                package.validate_tile('N30E103', zipped(name, b'abcd'))

    def test_zip_crc_detects_network_corruption(self):
        data = b'\x00\x01\x00\x02'
        payload = bytearray(zipped('N30E103.hgt', data, zipfile.ZIP_STORED))
        payload[payload.index(data)] ^= 1
        with patch.object(package, 'HGT_BYTES', 4):
            with self.assertRaises(zipfile.BadZipFile):
                package.validate_tile('N30E103', payload)

    def test_all_invalid_tiles_are_not_published_as_terrain(self):
        for data in [b'\x80\x00' * 2, b'\xd8\xf1' * 2]:
            with patch.object(package, 'HGT_BYTES', 4):
                with self.assertRaisesRegex(ValueError, 'entirely invalid'):
                    package.validate_tile('N30E103', zipped('N30E103.hgt', data))

    def test_partial_void_count_and_big_endian_values(self):
        data = b'\x80\x00\x00\x64'
        with patch.object(package, 'HGT_BYTES', 4):
            result, record = package.validate_tile('N30E103', zipped('N30E103.hgt', data))
        self.assertEqual(data, result)
        self.assertEqual(1, record['void_minus32768_nodes'])
        self.assertEqual(hashlib.sha256(data).hexdigest(), record['hgt_sha256'])


class BundleTests(unittest.TestCase):
    def test_parts_roundtrip_and_incomplete_manifest_blocks_publication(self):
        tiles = ['N30E103', 'N30E104']
        data = b'\x00\x01\x00\x02'
        records = [(data, {'tile': t, 'hgt_bytes': 4, 'hgt_sha256': hashlib.sha256(data).hexdigest()}) for t in tiles]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'out'
            config = {'tag': 'terrain-test', 'available_tiles': 2}
            with patch.object(package, 'HGT_BYTES', 4), patch.object(package, 'MAX_PART', 1_000_008), \
                 patch.object(package, 'ordered_downloads', return_value=iter(records)):
                m = package.build(config, tiles, root, 'credit and installation')
                self.assertEqual(2, len(m['parts']))
                for part in m['parts']:
                    with zipfile.ZipFile(root / part['name']) as z:
                        hgt = [n for n in z.namelist() if n.endswith('.hgt')][0]
                        self.assertEqual(data, z.read(hgt))
                        self.assertGreaterEqual(z.getinfo(hgt).date_time[:3], (2026, 3, 1))
                with patch.object(publish, 'HGT_BYTES', 4):
                    publish.validate_bundle(root, config, tiles)
                    m['tiles'].pop()
                    (root / 'manifest.json').write_text(json.dumps(m))
                    with self.assertRaisesRegex(ValueError, 'Missing or duplicate'):
                        publish.validate_bundle(root, config, tiles)

    def test_repackaged_valid_crc_cannot_hide_changed_elevation_bytes(self):
        data = b'\x00\x01\x00\x02'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'bad.zip'
            path.write_bytes(zipped('srtm/N30E103.hgt', b'\x00\x03\x00\x04'))
            with patch.object(package, 'HGT_BYTES', 4):
                with self.assertRaisesRegex(ValueError, 'HGT changed'):
                    package.verify_part(path, [{'tile': 'N30E103', 'hgt_sha256': hashlib.sha256(data).hexdigest()}])

    def test_full_coverage_has_exactly_four_documented_exclusions(self):
        root = Path(__file__).resolve().parents[3]
        config, selected = package.read_plan(root / 'data/terrain/request.json', root / 'data/terrain/china-tiles.txt')
        self.assertEqual(1162, len(selected))
        self.assertEqual({'N18E111', 'N20E108', 'N20E111', 'N27E122'}, set(config['excluded']))


if __name__ == '__main__':
    unittest.main()

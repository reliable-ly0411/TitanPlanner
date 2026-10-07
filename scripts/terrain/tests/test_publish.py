import json
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import publish


class PrepareTests(unittest.TestCase):
    config = {'tag': 'terrain-test', 'title': 'Terrain'}
    sha = 'a' * 40

    def draft(self):
        return {'id': 123, 'draft': True, 'target_commitish': self.sha, 'html_url': 'draft', 'assets': []}

    def verified_upload(self):
        result = self.draft()
        notes = Path('data/terrain/INSTALL.zh-CN.txt')
        result['assets'] = [{'name': notes.name, 'digest': 'sha256:' + publish.sha256_file(notes), 'size': notes.stat().st_size}]
        return result

    def run_prepare(self, tag=None, responses=None, saved=None):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / 'release-state.json'
            if saved:
                state.write_text(json.dumps(saved))
            with patch.object(publish, 'release_context', return_value=(self.config, [], 'owner/repo', self.sha)), \
                 patch.object(publish, 'state_path', return_value=state), \
                 patch.object(publish, 'optional_api', return_value=tag), \
                 patch.object(publish, 'api', side_effect=responses) as api, \
                 patch.object(publish, 'upload_asset') as upload:
                publish.prepare()
                return api.call_args_list, upload.call_args_list, json.loads(state.read_text())

    def test_preflight_and_upload_use_persisted_release_id(self):
        calls, uploads, saved = self.run_prepare(responses=[{}, self.draft(), self.draft(), self.verified_upload()])
        self.assertEqual(saved, {'id': 123, 'tag': self.config['tag'], 'sha': self.sha})
        self.assertTrue(calls[0].args[0].endswith('/git/refs'))
        self.assertTrue(calls[1].args[2]['draft'])
        self.assertEqual(calls[1].args[2]['make_latest'], 'false')
        self.assertTrue(calls[2].args[0].endswith('/releases/123'))
        self.assertEqual(uploads[0].args[1], 123)

    def test_wrong_uploaded_hash_fails_preflight(self):
        bad = self.verified_upload(); bad['assets'][0]['digest'] = 'sha256:wrong'
        with self.assertRaisesRegex(ValueError, 'hash/size'):
            self.run_prepare(responses=[{}, self.draft(), self.draft(), bad])

    def test_existing_published_release_is_never_modified(self):
        published = self.draft(); published['draft'] = False
        with self.assertRaisesRegex(ValueError, 'published'):
            self.run_prepare(responses=[published], saved={'id':123,'tag':self.config['tag'],'sha':self.sha})

    def test_existing_tag_is_never_moved(self):
        with self.assertRaisesRegex(ValueError, 'refusing to move'):
            self.run_prepare(tag={'object': {'type': 'commit', 'sha': 'b' * 40}}, responses=[])

    def test_permission_failure_stops_prepare(self):
        with self.assertRaisesRegex(RuntimeError, '403'):
            self.run_prepare(responses=[RuntimeError('403')])

    def test_wrong_saved_build_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'does not match'):
            self.run_prepare(saved={'id':123,'tag':self.config['tag'],'sha':'b'*40})

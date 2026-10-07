import json
import subprocess
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import publish


class PrepareTests(unittest.TestCase):
    config = {'tag': 'terrain-test', 'title': 'Terrain'}
    sha = 'a' * 40

    def run_prepare(self, release, tag, api_responses, confirmed=None):
        with patch.object(publish, 'release_context', return_value=(self.config, [], 'owner/repo', self.sha)), \
             patch.object(publish, 'find_release', side_effect=[release, confirmed]), \
             patch.object(publish, 'optional_api', return_value=tag), \
             patch.object(publish, 'api', side_effect=api_responses) as api, \
             patch.object(publish, 'gh') as gh:
            publish.prepare()
            return api.call_args_list, gh.call_args_list

    def draft(self):
        return {'id': 123, 'draft': True, 'target_commitish': self.sha, 'html_url': 'draft', 'assets': []}

    def verified_upload(self):
        notes = Path('data/terrain/INSTALL.zh-CN.txt')
        return {'assets': [{'name': notes.name, 'digest': 'sha256:' + publish.sha256_file(notes), 'size': notes.stat().st_size}]}

    def test_draft_lookup_includes_paginated_unpublished_releases(self):
        draft = dict(self.draft(), tag_name='terrain-test')
        result = subprocess.CompletedProcess([], 0, json.dumps([[{'tag_name': 'other'}], [draft]]), '')
        with patch.object(publish, 'gh', return_value=result) as gh:
            self.assertEqual(publish.find_release('owner/repo', 'terrain-test'), draft)
            self.assertIn('--paginate', gh.call_args.args)
            self.assertNotIn('/tags/', gh.call_args.args[1])

    def test_tag_draft_lookup_and_real_upload_are_checked_before_download(self):
        draft = self.draft()
        calls, uploads = self.run_prepare(None, None, [{}, draft, self.verified_upload()], draft)
        self.assertTrue(calls[0].args[0].endswith('/git/refs'))
        self.assertEqual(calls[0].args[2]['sha'], self.sha)
        self.assertTrue(calls[1].args[2]['draft'])
        self.assertEqual(calls[1].args[2]['make_latest'], 'false')
        self.assertEqual(uploads[0].args[:2], ('release', 'upload'))

    def test_missing_draft_after_creation_fails_preflight(self):
        with self.assertRaisesRegex(ValueError, 'cannot be found'):
            self.run_prepare(None, None, [{}, self.draft()], None)

    def test_wrong_uploaded_hash_fails_preflight(self):
        bad = self.verified_upload(); bad['assets'][0]['digest'] = 'sha256:wrong'
        with self.assertRaisesRegex(ValueError, 'hash/size'):
            self.run_prepare(None, None, [{}, self.draft(), bad], self.draft())

    def test_existing_published_release_is_never_modified(self):
        with self.assertRaisesRegex(ValueError, 'published'):
            self.run_prepare({'draft': False, 'target_commitish': self.sha}, None, [])

    def test_existing_tag_is_never_moved(self):
        with self.assertRaisesRegex(ValueError, 'refusing to move'):
            self.run_prepare(None, {'object': {'type': 'commit', 'sha': 'b' * 40}}, [])

    def test_permission_failure_stops_prepare(self):
        with self.assertRaisesRegex(RuntimeError, '403'):
            self.run_prepare(None, None, [RuntimeError('403')])

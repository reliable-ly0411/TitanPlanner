import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import publish


class PrepareTests(unittest.TestCase):
    config = {'tag': 'terrain-test', 'title': 'Terrain'}
    sha = 'a' * 40

    def run_prepare(self, existing, responses):
        with patch.object(publish, 'release_context', return_value=(self.config, [], 'owner/repo', self.sha)), \
             patch.object(publish, 'optional_api', side_effect=existing), \
             patch.object(publish, 'api', side_effect=responses) as api:
            publish.prepare()
            return api.call_args_list

    def test_tag_is_fixed_before_draft_creation(self):
        draft = {'draft': True, 'target_commitish': self.sha, 'html_url': 'draft'}
        calls = self.run_prepare([None, None], [{}, draft])
        self.assertTrue(calls[0].args[0].endswith('/git/refs'))
        self.assertEqual(calls[0].args[2]['sha'], self.sha)
        self.assertTrue(calls[1].args[0].endswith('/releases'))
        self.assertTrue(calls[1].args[2]['draft'])
        self.assertEqual(calls[1].args[2]['make_latest'], 'false')

    def test_existing_published_release_is_never_modified(self):
        with self.assertRaisesRegex(ValueError, 'published'):
            self.run_prepare([{'draft': False, 'target_commitish': self.sha}], [])

    def test_existing_tag_is_never_moved(self):
        with self.assertRaisesRegex(ValueError, 'refusing to move'):
            self.run_prepare([None, {'object': {'type': 'commit', 'sha': 'b' * 40}}], [])

    def test_permission_failure_stops_prepare(self):
        with self.assertRaisesRegex(RuntimeError, '403'):
            self.run_prepare([None, None], [RuntimeError('403')])

    def test_matching_tag_and_draft_can_resume(self):
        draft = {'draft': True, 'target_commitish': self.sha, 'html_url': 'draft'}
        calls = self.run_prepare([draft, {'object': {'type': 'commit', 'sha': self.sha}}], [])
        self.assertEqual(calls, [])

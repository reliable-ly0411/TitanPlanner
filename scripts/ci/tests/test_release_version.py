import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_artifacts import application_version, artifact_names, release_tag, validate_version, write_manifest, verify_manifest


class ReleaseVersionTests(unittest.TestCase):
    def test_application_version_ignores_dependency_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'Properties').mkdir()
            (root/'MissionPlanner.csproj').write_text('<Project><PropertyGroup><Version>1.3.83</Version></PropertyGroup><ItemGroup><PackageReference><Version>9.9.9</Version></PackageReference></ItemGroup></Project>')
            source = root/'Properties'/'AssemblyInfo.cs'
            source.write_text('[assembly: AssemblyFileVersion("1.3.83.0")]')
            self.assertEqual('1.3.83', application_version(root))
            source.write_text('[assembly: AssemblyFileVersion("1.3.84")]')
            with self.assertRaises(ValueError): application_version(root)

    def test_names_and_tags_use_validated_version_and_commit(self):
        sha = 'a'*40
        self.assertEqual(['TitanPlanner-zh-CN-v1.3.83-aaaaaaaaaaaa-windows.zip', 'TitanPlanner-zh-CN-v1.3.83-aaaaaaaaaaaa-windows.msi'], artifact_names(sha, '1.3.83'))
        self.assertEqual('v1.3.83-zh2-aaaaaaaaaaaa', release_tag(sha, '1.3.83'))
        for value in (None, '', '../1.3.83', '1.3', '1.3.*', '01.3.83', '1.3.83;cmd', '1.3.83\n'):
            with self.assertRaises(ValueError): validate_version(value)

    def test_manifest_version_change_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); sha = 'a'*40
            for name in artifact_names(sha, '1.3.83'): (root/name).write_bytes(b'test')
            write_manifest(root, sha, '1.3.83')
            manifest = json.loads((root/'build-info.json').read_text())
            self.assertEqual('1.3.83', manifest['version'])
            manifest['version'] = '1.3.84'
            (root/'build-info.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError): verify_manifest(root, sha)

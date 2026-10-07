#!/usr/bin/env python3
"""Build a per-user x64 MSI from the exact verified ZIP payload using WiX 3.14."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import uuid
import xml.etree.ElementTree as ET
import zipfile
from release_artifacts import application_version, artifact_names, write_manifest

NS = 'http://schemas.microsoft.com/wix/2006/wi'
UPGRADE = uuid.UUID('bb2c699d-2579-4dd8-8d05-4fce1a09d78a')
ET.register_namespace('', NS)


def add(parent, tag, **attrs):
    return ET.SubElement(parent, '{'+NS+'}'+tag, attrs)


def identifier(prefix, path):
    return prefix + hashlib.sha256(path.casefold().encode()).hexdigest()[:32]


def msi_version(run_number):
    if not 1 <= run_number < 256 * 65536:
        raise ValueError('Build number exceeds MSI version range')
    return f'1.{run_number // 65536}.{run_number % 65536}'


def author(payload, sha, version):
    root = ET.Element('{'+NS+'}Wix')
    product = add(root, 'Product', Id=str(uuid.uuid5(UPGRADE, sha)), Name='TitanPlanner-zh-CN',
                  Language='2052', Codepage='936', Version=version, Manufacturer='TitanPlanner-zh-CN contributors', UpgradeCode=str(UPGRADE))
    add(product, 'Package', InstallerVersion='500', Compressed='yes', InstallScope='perUser', Platform='x64', SummaryCodepage='936')
    add(product, 'MajorUpgrade', Schedule='afterInstallInitialize', DowngradeErrorMessage='已安装更新版本的 TitanPlanner-zh-CN。')
    add(product, 'MediaTemplate', EmbedCab='yes', CompressionLevel='high')
    add(product, 'Property', Id='ARPCOMMENTS', Value='保留原版中文，新增中文(简体)2；卸载保留个人配置和日志。')
    add(product, 'Property', Id='ARPURLINFOABOUT', Value='https://github.com/reliable-ly0411/TitanPlanner-zh-CN')
    add(product, 'Property', Id='ARPPRODUCTICON', Value='AppIcon')
    add(product, 'Icon', Id='AppIcon', SourceFile=str(payload/'MissionPlanner.exe'))
    net = add(product, 'Property', Id='NETFRAMEWORKRELEASE')
    add(net, 'RegistrySearch', Id='FindNetFramework', Root='HKLM', Key=r'SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full', Name='Release', Type='raw', Win64='yes')
    add(product, 'Condition', Message='需要 64 位 Windows 和 .NET Framework 4.7.2 或更新版本。').text = 'Installed OR (VersionNT64 AND NETFRAMEWORKRELEASE >= "#461808")'
    target = add(product, 'Directory', Id='TARGETDIR', Name='SourceDir')
    local = add(target, 'Directory', Id='LocalAppDataFolder')
    programs = add(local, 'Directory', Id='UserPrograms', Name='Programs')
    install = add(programs, 'Directory', Id='INSTALLFOLDER', Name='TitanPlanner-zh-CN')
    menu = add(target, 'Directory', Id='ProgramMenuFolder')
    app_menu = add(menu, 'Directory', Id='AppMenu', Name='TitanPlanner-zh-CN')
    feature = add(product, 'Feature', Id='Complete', Title='TitanPlanner-zh-CN', Level='1')
    directories = {'': install}
    def directory(relative):
        if relative not in directories:
            path = PurePosixPath(relative)
            parent = '' if str(path.parent) == '.' else str(path.parent)
            directories[relative] = add(directory(parent), 'Directory', Id=identifier('D', relative), Name=path.name)
        return directories[relative]
    for path in sorted(payload.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(payload).as_posix()
        parent = str(PurePosixPath(rel).parent)
        comp_id = identifier('C', rel)
        comp = add(directory('' if parent == '.' else parent), 'Component', Id=comp_id, Guid=str(uuid.uuid5(UPGRADE, rel.casefold())), Win64='yes')
        add(comp, 'File', Id=identifier('F', rel), Name=path.name, Source=str(path))
        add(comp, 'RegistryValue', Root='HKCU', Key=r'Software\TitanPlanner-zh-CN\Installer', Name=comp_id, Type='integer', Value='1', KeyPath='yes')
        add(feature, 'ComponentRef', Id=comp_id)
    # Remove only empty directories; never delete application-created settings/logs.
    for rel, node in directories.items():
        cid = identifier('R', rel)
        comp = add(node, 'Component', Id=cid, Guid=str(uuid.uuid5(UPGRADE, 'dir:'+rel.casefold())), Win64='yes')
        add(comp, 'RemoveFolder', Id=cid, On='uninstall')
        add(comp, 'RegistryValue', Root='HKCU', Key=r'Software\TitanPlanner-zh-CN\Installer', Name=cid, Type='integer', Value='1', KeyPath='yes')
        add(feature, 'ComponentRef', Id=cid)
    shortcut = add(app_menu, 'Component', Id='StartMenuShortcut', Guid=str(uuid.uuid5(UPGRADE, 'startmenu')), Win64='yes')
    add(shortcut, 'Shortcut', Id='Launch', Name='TitanPlanner-zh-CN', Target='[INSTALLFOLDER]MissionPlanner.exe', WorkingDirectory='INSTALLFOLDER', Icon='AppIcon')
    add(shortcut, 'RemoveFolder', Id='RemoveAppMenu', On='uninstall')
    add(shortcut, 'RemoveFolder', Id='RemoveUserPrograms', Directory='UserPrograms', On='uninstall')
    add(shortcut, 'RegistryValue', Root='HKCU', Key=r'Software\TitanPlanner-zh-CN\Installer', Name='shortcut', Type='integer', Value='1', KeyPath='yes')
    add(feature, 'ComponentRef', Id='StartMenuShortcut')
    add(product, 'UIRef', Id='WixUI_Minimal')
    add(product, 'WixVariable', Id='WixUILicenseRtf', Value=str(Path('Msi/licence.rtf').resolve()))
    ET.indent(root)
    return ET.ElementTree(root)


def build(root, sha, run_number, work):
    root, work = Path(root).resolve(), Path(work).resolve()
    work.mkdir(parents=True, exist_ok=False)
    payload = work/'payload'
    app_version = application_version()
    names = artifact_names(sha, app_version)
    with zipfile.ZipFile(root/names[0]) as z:
        for name in z.namelist():
            p = PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
                raise ValueError('Unsafe ZIP path')
        z.extractall(payload)
    info = json.loads((payload/'BUILD-INFO.json').read_text(encoding='utf-8'))
    if info['commit'] != sha or info.get('version') != app_version:
        raise ValueError('ZIP commit/version mismatch')
    for entry in info['files']:
        if hashlib.sha256((payload/entry['path']).read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('ZIP payload hash mismatch')
    version = msi_version(run_number)
    source = work/'Product.wxs'
    author(payload, sha, version).write(source, encoding='utf-8', xml_declaration=True)
    wix = Path(os.environ['WIX'])/'bin'
    subprocess.run([str(wix/'candle.exe'), '-nologo', '-arch', 'x64', '-out', str(work/'Product.wixobj'), str(source)], check=True)
    subprocess.run([str(wix/'light.exe'), '-nologo', '-ext', 'WixUIExtension', '-cultures:zh-cn', '-out', str(root/names[1]), str(work/'Product.wixobj')], check=True)
    # Debug symbols are CI diagnostics, not distributable release assets.
    symbols = root/Path(names[1]).with_suffix('.wixpdb')
    if symbols.exists():
        symbols.replace(work/symbols.name)
    write_manifest(root, sha, app_version, msi_version=version, file_count=len(info['files']))
    print(f'Built and validated MSI {names[1]} ({version}); payload shared with ZIP')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('release'); parser.add_argument('sha'); parser.add_argument('run_number', type=int); parser.add_argument('work')
    args = parser.parse_args()
    build(args.release, args.sha, args.run_number, args.work)

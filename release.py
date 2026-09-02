#!/usr/bin/env python3
"""Build a DooFree repository release.

Everything Kodi needs has to agree or the update stays invisible: the version in
the addon manifest, the version in the repository index, the checksum of that
index, and a zip whose name matches. Doing that by hand is how a release ends up
half-published, so this script does all of it from one source of truth - the
addon manifest.

    ./release.py                     rebuild the current version
    ./release.py --bump patch        5.3.1 -> 5.3.2
    ./release.py --bump minor        5.3.1 -> 5.4.0
    ./release.py --bump major        5.3.1 -> 6.0.0
    ./release.py --version 6.1.0     set it exactly
    ./release.py --news "..."        replace the release note as well
    ./release.py --check             verify the release on disk, change nothing

Nothing is committed or pushed; that stays a deliberate act.
"""

import argparse
import hashlib
import os
import re
import shutil
import sys
import zipfile
from xml.dom import minidom

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(ROOT, 'repo')
ADDON_ID = 'plugin.video.doofree'

# Files that must never end up in a published zip.
EXCLUDE_NAMES = {'.DS_Store', '.gitignore', 'Thumbs.db'}
EXCLUDE_DIRS = {'__pycache__', '.git', '.idea'}
EXCLUDE_SUFFIXES = ('.pyc', '.pyo', '.orig', '.rej')

# Copied into the addon at build time so the fallback cannot drift from the
# configuration the repository serves.
CONFIG_SOURCE = os.path.join(REPO, 'config', 'doofree.json')
CONFIG_BUNDLED = os.path.join(REPO, ADDON_ID, 'resources', 'data', 'channels.json')


def fail(message):
    print('error: %s' % message, file=sys.stderr)
    sys.exit(1)


def addon_dirs():
    """Every addon folder in the repository, in a stable order."""
    found = []
    for name in sorted(os.listdir(REPO)):
        manifest = os.path.join(REPO, name, 'addon.xml')
        if os.path.isfile(manifest):
            found.append((name, manifest))
    if not found:
        fail('no addon manifests found under %s' % REPO)
    return found


def read_version(manifest):
    text = open(manifest, encoding='utf-8').read()
    match = re.search(r'<addon\b[^>]*\bversion="([^"]+)"', text)
    if not match:
        fail('no version attribute in %s' % manifest)
    return match.group(1)


def bump(version, part):
    numbers = version.split('.')
    if len(numbers) != 3 or not all(n.isdigit() for n in numbers):
        fail('cannot bump a non numeric version: %s' % version)
    major, minor, patch = (int(n) for n in numbers)
    if part == 'major':
        return '%d.0.0' % (major + 1)
    if part == 'minor':
        return '%d.%d.0' % (major, minor + 1)
    return '%d.%d.%d' % (major, minor, patch + 1)


def set_version(manifest, version):
    text = open(manifest, encoding='utf-8').read()
    updated = re.sub(r'(<addon\b[^>]*\bversion=")[^"]+(")',
                     lambda m: m.group(1) + version + m.group(2), text, count=1)
    open(manifest, 'w', encoding='utf-8').write(updated)


def set_news(manifest, news):
    text = open(manifest, encoding='utf-8').read()
    if '<news>' not in text:
        fail('no news element in %s' % manifest)
    body = '\n'.join('            ' + line for line in news.splitlines())
    updated = re.sub(r'<news>.*?</news>', '<news>\n%s\n        </news>' % body,
                     text, count=1, flags=re.DOTALL)
    open(manifest, 'w', encoding='utf-8').write(updated)


def write_index():
    """Rebuild addons.xml from the manifests so the two cannot disagree."""
    entries = []
    for name, manifest in addon_dirs():
        body = open(manifest, encoding='utf-8').read()
        body = re.sub(r'^<\?xml[^>]*\?>\s*', '', body).strip()
        entries.append('\n'.join(('    ' + line) if line.strip() else line
                                 for line in body.splitlines()))

    index = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n%s\n</addons>\n' % \
            '\n'.join(entries)
    path = os.path.join(REPO, 'addons.xml')
    open(path, 'w', encoding='utf-8').write(index)
    return path


def write_checksum(index_path):
    """Write the md5 of the index, with no trailing newline - Kodi is fussy."""
    digest = hashlib.md5(open(index_path, 'rb').read()).hexdigest()
    path = index_path + '.md5'
    with open(path, 'w', encoding='utf-8') as handle:
        handle.write(digest)
    return digest


def skip(path_parts, filename):
    if any(part in EXCLUDE_DIRS for part in path_parts):
        return True
    if filename in EXCLUDE_NAMES:
        return True
    return filename.endswith(EXCLUDE_SUFFIXES)


def build_zip(addon_name, version):
    source = os.path.join(REPO, addon_name)
    target_dir = os.path.join(REPO, 'zips', addon_name)
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, '%s-%s.zip' % (addon_name, version))

    if os.path.exists(target):
        os.remove(target)

    written = 0
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder, dirs, files in os.walk(source):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
            relative = os.path.relpath(folder, REPO)
            parts = relative.split(os.sep)
            for filename in sorted(files):
                if skip(parts, filename):
                    continue
                archive.write(os.path.join(folder, filename),
                              os.path.join(relative, filename))
                written += 1
    return target, written


def sync_bundled_config():
    """Ship the served configuration as the addon's offline fallback."""
    if not os.path.isfile(CONFIG_SOURCE):
        return False
    os.makedirs(os.path.dirname(CONFIG_BUNDLED), exist_ok=True)
    shutil.copyfile(CONFIG_SOURCE, CONFIG_BUNDLED)
    return True


def check():
    """Verify what is on disk without changing anything."""
    problems = []
    index_path = os.path.join(REPO, 'addons.xml')

    try:
        published = {node.getAttribute('id'): node.getAttribute('version')
                     for node in minidom.parse(index_path).getElementsByTagName('addon')}
    except Exception as error:
        return ['addons.xml does not parse: %s' % error]

    for name, manifest in addon_dirs():
        version = read_version(manifest)
        if published.get(name) != version:
            problems.append('%s is %s in the manifest but %s in addons.xml'
                            % (name, version, published.get(name) or 'absent'))
        archive = os.path.join(REPO, 'zips', name, '%s-%s.zip' % (name, version))
        if not os.path.isfile(archive):
            problems.append('missing zip %s' % os.path.relpath(archive, ROOT))
        elif zipfile.ZipFile(archive).testzip() is not None:
            problems.append('corrupt zip %s' % os.path.relpath(archive, ROOT))

    digest = hashlib.md5(open(index_path, 'rb').read()).hexdigest()
    published = open(index_path + '.md5', encoding='utf-8').read().strip()
    if digest != published:
        problems.append('addons.xml.md5 does not match addons.xml')

    if os.path.isfile(CONFIG_SOURCE):
        served = open(CONFIG_SOURCE, encoding='utf-8').read()
        bundled = open(CONFIG_BUNDLED, encoding='utf-8').read() if os.path.isfile(CONFIG_BUNDLED) else None
        if served != bundled:
            problems.append('bundled channels.json differs from the served config')

    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--bump', choices=['major', 'minor', 'patch'],
                        help='raise the version of the plugin before building')
    parser.add_argument('--version', help='set the plugin version exactly')
    parser.add_argument('--news', help='replace the release note in the manifest')
    parser.add_argument('--check', action='store_true',
                        help='verify the release on disk and change nothing')
    args = parser.parse_args()

    if args.check:
        problems = check()
        for problem in problems:
            print('  %s' % problem)
        print('release is %s' % ('inconsistent' if problems else 'consistent'))
        return 1 if problems else 0

    if args.bump and args.version:
        fail('use either --bump or --version, not both')

    manifest = os.path.join(REPO, ADDON_ID, 'addon.xml')
    version = read_version(manifest)

    if args.version:
        version = args.version
    elif args.bump:
        version = bump(version, args.bump)

    if args.version or args.bump:
        set_version(manifest, version)
    if args.news:
        set_news(manifest, args.news)

    if sync_bundled_config():
        print('config    bundled fallback synced from repo/config/doofree.json')

    index_path = write_index()
    digest = write_checksum(index_path)

    for name, addon_manifest in addon_dirs():
        addon_version = read_version(addon_manifest)
        target, count = build_zip(name, addon_version)
        print('zip       %s (%d files)' % (os.path.relpath(target, ROOT), count))

    print('index     %s' % os.path.relpath(index_path, ROOT))
    print('checksum  %s' % digest)
    print('version   %s %s' % (ADDON_ID, version))

    problems = check()
    for problem in problems:
        print('  %s' % problem)
    print('release is %s' % ('inconsistent' if problems else 'consistent'))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())

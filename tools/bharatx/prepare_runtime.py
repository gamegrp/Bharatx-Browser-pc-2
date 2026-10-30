"""Prepare the pinned Gecko source for the standard upstream artifact build."""
# SPDX-License-Identifier: MPL-2.0
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]

def git_apply(runtime: Path, patch: Path) -> None:
    reverse = subprocess.run(['git', 'apply', '--reverse', '--check', str(patch)], cwd=runtime, capture_output=True)
    if reverse.returncode == 0:
        print('Already applied:', patch.name)
        return
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=runtime, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=runtime, check=True)
    print('Applied:', patch.name)

def prepare(runtime: Path) -> None:
    lock = json.loads((ROOT / 'floorp-runtime.lock.json').read_text())
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=runtime, text=True).strip()
    if actual != lock['source']['commit']: raise ValueError('Runtime source revision does not match the lock')
    if ROOT != runtime / 'noraneko':
        raise ValueError('Place this project in the runtime/noraneko directory before preparing')
    upstream_names = set()
    for patch in sorted((runtime / '.github/patches/upstream').glob('*.patch')):
        git_apply(runtime, patch)
        upstream_names.add(patch.name)
    for patch in sorted((ROOT / '.github/patches/floorp-runtime/common').glob('*.patch')):
        # The pinned runtime already ships and applies a same-named patch
        # (e.g. macos-app-shim-pwa-input-and-compositor.patch). Re-applying our
        # older local copy conflicts with it, so the upstream one wins.
        if patch.name in upstream_names:
            print('Skipped (provided by pinned runtime):', patch.name)
            continue
        git_apply(runtime, patch)
    icons = runtime / 'browser/components/shell/icons'
    icons.mkdir(parents=True, exist_ok=True)
    for source in (ROOT / 'static/gecko/custom-app-icons').glob('*.png'):
        shutil.copy2(source, icons / source.name)
    for patch in sorted((ROOT / '.github/patches/floorp-runtime').glob('*.patch')):
        if not patch.name.endswith('-tests.patch'): git_apply(runtime, patch)

    branding = runtime / 'browser/branding/bharatx'
    base = runtime / '.github/assets/branding/floorp-official'
    if not base.is_dir(): base = runtime / 'browser/branding/unofficial'
    shutil.copytree(base, branding, dirs_exist_ok=True)
    # Reuse the complete branding layout and replace only product values/assets.
    for p in branding.rglob('*'):
        if not p.is_file(): continue
        if p.suffix == '.ico': shutil.copy2(ROOT/'branding/BharatXBrowser.ico',p)
        elif p.suffix == '.png': shutil.copy2(ROOT/'branding/BharatXBrowser.png',p)
        elif p.suffix in {'.ftl','.properties','.dtd','.css','.sh','.txt'}:
            text=p.read_text()
            text=''.join(line if re.search(r'copyright|trademark|license|SPDX',line,re.I)
                else re.sub(r'\b(?:Ablaze )?Floorp(?: Browser)?\b','BharatX Browser',line).replace('Noraneko','BharatX Browser')
                for line in text.splitlines(keepends=True))
            p.write_text(text)
    (branding/'configure.sh').write_text('''# SPDX-License-Identifier: MPL-2.0
MOZ_APP_DISPLAYNAME="BharatX Browser"
MOZ_APP_NAME="floorp"
MOZ_APP_VENDOR="Nitai Studio"
MOZ_APP_REMOTINGNAME="bharatx-browser"
''')
    locale=branding/'locales/en-US';locale.mkdir(parents=True,exist_ok=True)
    # Retain the original license header on branding files when one exists.
    ftl=locale/'brand.ftl'
    header=''.join(line+'\n' for line in ftl.read_text().splitlines() if line.startswith('#')) if ftl.exists() else '# SPDX-License-Identifier: MPL-2.0\n'
    ftl.write_text(header+'''\n-brand-shorter-name = BharatX Browser
-brand-short-name = BharatX Browser
-brand-shortcut-name = BharatX Browser
-brand-full-name = BharatX Browser
-brand-product-name = BharatX Browser
-vendor-short-name = Nitai Studio
trademarkInfo = BharatX Browser branding by Nitai Studio.
''')
    prop=locale/'brand.properties'
    header=''.join(line+'\n' for line in prop.read_text().splitlines() if line.startswith('#')) if prop.exists() else '# SPDX-License-Identifier: MPL-2.0\n'
    prop.write_text(header+'\nbrandShorterName=BharatX Browser\nbrandShortName=BharatX Browser\nbrandFullName=BharatX Browser\nvendorShortName=Nitai Studio\n')
    for n in ['about-logo.png','about-logo@2x.png','icon32.png','icon64.png','icon128.png']:
        target=branding/'content'/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'branding/BharatXBrowser.png',target)

    candidates=[runtime/'.github/workflows/mozconfigs/windows-x86_64.mozconfig',runtime/'.github/workflows/mozconfigs/win64.mozconfig']
    original=next((p for p in candidates if p.is_file()),None)
    if original is None: raise FileNotFoundError('The locked runtime has no Windows artifact mozconfig')
    config=original.read_text()
    removed=['--with-branding=','--with-version-file-path=','--enable-update-channel=','--enable-unverified-updates','--disable-updater','--enable-chrome-format=']
    config='\n'.join(line for line in config.splitlines() if not any(flag in line for flag in removed))
    gecko_version=(runtime/'browser/config/version.txt').read_text().strip()
    gecko_display=(runtime/'browser/config/version_display.txt').read_text().strip()
    versions=ROOT/'static/gecko/config/autogenerated';versions.mkdir(parents=True,exist_ok=True)
    (versions/'version.txt').write_text('1.36.0@'+gecko_version+'\n')
    (versions/'version_display.txt').write_text('1.36.0@'+gecko_display+'\n')
    config+='''
ac_add_options --with-branding=browser/branding/bharatx
ac_add_options --with-version-file-path=noraneko/static/gecko/config/autogenerated
ac_add_options --enable-release
ac_add_options --disable-tests
ac_add_options --enable-artifact-builds
ac_add_options --enable-chrome-format=flat
ac_add_options --enable-update-channel=bharatx-store
mk_add_options MOZ_OBJDIR=./obj-artifact-build-output
'''
    (runtime/'mozconfig').write_text(config)
    print('Prepared pinned runtime source and BharatX branding')

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('runtime',type=Path)
    prepare(p.parse_args().runtime.resolve())

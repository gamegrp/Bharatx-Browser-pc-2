"""Apply the project's post-mach patches to the complete flat runtime output."""
# SPDX-License-Identifier: MPL-2.0
import argparse
from pathlib import Path
import shutil
import subprocess
import zipfile
from prepare_runtime import git_apply

ROOT=Path(__file__).resolve().parents[2]

# Same mapping as tools/src/injector.ts: chrome sub-directory -> project directory.
CHROME_MOUNTS=[
    ('content','bridge/loader-features/_dist'),('startup','bridge/startup/_dist'),
    ('skin','browser-features/skin'),('resource','bridge/loader-modules/_dist'),
    ('pages-newtab','browser-features/pages-newtab/_dist'),
    ('pages-settings','browser-features/pages-settings/_dist'),
    ('pages-welcome','browser-features/pages-welcome/_dist'),
    ('pages-notes','browser-features/pages-notes/_dist'),
    ('pages-modal-child','browser-features/pages-modal-child/_dist'),
    ('pages-profile-manager','browser-features/pages-profile-manager/_dist'),
    ('pages-aboutDialog','browser-features/pages-aboutDialog/_dist'),
]
CHROME_MANIFEST="""content noraneko content/ contentaccessible=yes
content noraneko-startup startup/ contentaccessible=yes
content noraneko-skin skin/ contentaccessible=yes
resource noraneko resource/ contentaccessible=yes
content noraneko-pages-aboutdialog pages-aboutDialog/ contentaccessible=yes
override chrome://browser/content/aboutDialog.xhtml chrome://noraneko-pages-aboutdialog/content/aboutDialog.html
content noraneko-newtab pages-newtab/ contentaccessible=yes
content noraneko-welcome pages-welcome/ contentaccessible=yes
content noraneko-notes pages-notes/ contentaccessible=yes
content noraneko-modal-child pages-modal-child/ contentaccessible=yes
content noraneko-settings pages-settings/ contentaccessible=yes
content noraneko-profile-manager pages-profile-manager/ contentaccessible=yes
"""

def noraneko_registered(payload: Path) -> bool:
    """True when the runtime build already registers chrome://noraneko-startup."""
    for manifest in payload.rglob('*.manifest'):
        try:
            if 'noraneko-startup' in manifest.read_text(errors='ignore'):return True
        except OSError:pass
    for archive in payload.rglob('omni.ja'):
        try:
            with zipfile.ZipFile(archive) as z:
                if any(n.endswith('chrome_root.js') for n in z.namelist()):return True
        except (zipfile.BadZipFile,OSError):pass
    return False

def register_noraneko(payload: Path) -> None:
    """Ship the production frontend and register its chrome:// URLs.

    The artifact build does not process the project's moz.build/jar.mn files, so
    chrome://noraneko-startup/content/chrome_root.js would never resolve and the
    browser would start without any BharatX features.
    """
    if noraneko_registered(payload):
        print('Noraneko chrome content already registered by the runtime build');return
    target=payload/'noraneko'
    if target.exists():shutil.rmtree(target)
    target.mkdir(parents=True)
    for subdir,source in CHROME_MOUNTS:
        source_dir=ROOT/source
        if not source_dir.is_dir():
            raise FileNotFoundError(f'Production frontend output is missing: {source}')
        shutil.copytree(source_dir,target/subdir,symlinks=False,
            ignore=shutil.ignore_patterns('node_modules','moz.build','jar.mn'))
    if not (target/'startup/chrome_root.js').is_file():
        raise FileNotFoundError('chrome_root.js was not produced by the startup build')
    (target/'noraneko.manifest').write_text(CHROME_MANIFEST,encoding='utf-8')
    root_manifest=payload/'chrome.manifest'
    entry='manifest noraneko/noraneko.manifest'
    existing=root_manifest.read_text(encoding='utf-8') if root_manifest.is_file() else ''
    if entry not in existing:
        root_manifest.write_text(existing.rstrip('\n')+('\n' if existing else '')+entry+'\n',encoding='utf-8')
    print('Registered Noraneko chrome content in',root_manifest)

def finalize(payload: Path) -> None:
    # Mach dist files may be links to build inputs; materialize before patching.
    temporary=payload.with_name(payload.name+'-bharatx-materialized')
    if temporary.exists():raise FileExistsError(temporary)
    shutil.copytree(payload,temporary,symlinks=False)
    original=payload.with_name(payload.name+'-before-materialize')
    if original.exists():raise FileExistsError(original)
    payload.rename(original);temporary.rename(payload)
    shutil.rmtree(original)
    for patch in sorted((ROOT/'tools/patches').glob('*.patch')):
        if patch.name.endswith(('.linux.patch','.darwin.patch')):continue
        command=['git','apply','--directory',str(payload),'--unsafe-paths']
        already=subprocess.run(command+['--reverse','--check',str(patch)],cwd=ROOT,capture_output=True)
        if already.returncode==0:continue
        subprocess.run(command+['--check',str(patch)],cwd=ROOT,check=True)
        subprocess.run(command+[str(patch)],cwd=ROOT,check=True)
    buildid=ROOT/'_dist/buildid2'
    if not buildid.is_file():raise FileNotFoundError('Missing production build identifier')
    shutil.copy2(buildid,payload/'browser/buildid2')
    preferences=payload/'browser/defaults/preferences/firefox.js'
    if not preferences.is_file():raise FileNotFoundError('Runtime preferences file is missing')
    subprocess.run(['bash',str(ROOT/'static/gecko/pref/override.sh'),str(preferences)],cwd=ROOT,check=True)
    register_noraneko(payload)
    print('Finalized Windows artifact and production defaults')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('payload',type=Path)
    finalize(p.parse_args().payload.resolve())

"""Apply the project's post-mach patches to the complete flat runtime output."""
# SPDX-License-Identifier: MPL-2.0
import argparse
from pathlib import Path
import shutil
import subprocess
from prepare_runtime import git_apply

ROOT=Path(__file__).resolve().parents[2]

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
    print('Finalized Windows artifact and production defaults')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('payload',type=Path)
    finalize(p.parse_args().payload.resolve())

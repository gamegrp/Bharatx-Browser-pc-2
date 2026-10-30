"""Download the exact public native artifact recorded in the supplied lock."""
# SPDX-License-Identifier: MPL-2.0
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[2]

def fetch(destination: Path) -> Path:
    lock = json.loads((ROOT / 'floorp-runtime.lock.json').read_text())
    entry = next(x for x in lock['artifacts'] if x['platform'] == 'windows' and x['architecture'] == 'x86_64')
    asset = entry['asset']
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and hashlib.file_digest(destination.open('rb'), 'sha256').hexdigest() == asset['sha256']:
        return destination
    url = f"https://github.com/{lock['source']['repository']}/releases/download/{lock['source']['ref']}/{asset['name']}"
    request = urllib.request.Request(url, headers={'User-Agent': 'BharatXBrowser-Build/1.36.0'})
    temporary = destination.with_suffix('.download')
    try:
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open('wb') as out:
            while chunk := response.read(1024 * 1024): out.write(chunk)
        if temporary.stat().st_size != asset['size']:
            raise ValueError('Runtime size differs from the locked artifact')
        with temporary.open('rb') as stream: digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if digest != asset['sha256']: raise ValueError('Runtime SHA-256 check failed')
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    print('Verified native artifact:', destination.name)
    return destination

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=Path)
    fetch(parser.parse_args().destination.resolve())

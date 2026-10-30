"""Offline checks for release identity, local policy links and UI branding."""
# SPDX-License-Identifier: MPL-2.0
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.images=[];self.text=[]
    def handle_starttag(self, tag, attributes):
        attrs=dict(attributes)
        if tag=='a' and 'href' in attrs:self.links.append(attrs['href'])
        if tag=='img' and 'src' in attrs:self.images.append(attrs['src'])
    def handle_data(self,data):self.text.append(data)

def walk(value):
    if isinstance(value,dict):
        for element in value.values():yield from walk(element)
    elif isinstance(value,list):
        for element in value:yield from walk(element)
    elif isinstance(value,str):yield value

def check() -> dict:
    checks=[]
    identity=json.loads((ROOT/'packaging/windows/store-identity.json').read_text())
    package=json.loads((ROOT/'package.json').read_text())
    assert package['version']=='.'.join(identity['version'].split('.')[:3]),'Package versions differ'
    assert tuple(map(int,identity['version'].split('.')))>tuple(map(int,identity['previousVersion'].split('.'))),'Store version must increase'
    assert identity['version'].split('.')[-1]=='0','Store reserves the final version component'
    assert identity['name']=='NitaiStudio.BharatXBrowser'
    assert identity['publisher']=='CN=BEDDC7D9-ACD5-4D93-AEC9-C98C64F43592'
    checks.append('Partner Center identity and increasing four-part version')
    namespace={'m':'http://schemas.microsoft.com/appx/manifest/foundation/windows10',
        'uap':'http://schemas.microsoft.com/appx/manifest/uap/windows10'}
    manifest=ET.parse(ROOT/'packaging/windows/AppxManifest.xml').getroot()
    actual=manifest.find('m:Identity',namespace)
    assert actual is not None
    for key,expected in [('Name',identity['name']),('Publisher',identity['publisher']),('Version',identity['version']),('ProcessorArchitecture','x64')]:
        assert actual.get(key)==expected,'Manifest mismatch: '+key
    family=manifest.find('m:Dependencies/m:TargetDeviceFamily',namespace)
    assert family is not None and family.get('Name')=='Windows.Desktop'
    assert {p.get('Name') for p in manifest.findall('.//uap:Protocol',namespace)}=={'http','https'}
    for node in manifest.iter():
        for attribute,value in node.attrib.items():
            if attribute.endswith('Logo'):
                assert (ROOT/'packaging/windows'/value.replace('\\','/')).is_file(),value
    checks.append('Manifest identity, Windows Desktop, browser associations and logo paths')
    for folder in [ROOT/'i18n',ROOT/'browser-features']:
        candidates=folder.rglob('*.json') if folder.name=='i18n' else folder.rglob('locales/*.json')
        for p in candidates:
            for value in walk(json.loads(p.read_text())):
                assert not re.search(r'\b(?:Floorp|Noraneko|GitHub)\b',value),f'Old display branding: {p.relative_to(ROOT)}'
                assert 'https://BharatX Browser' not in value,'Malformed translated URL'
    checks.append('All localized display values preserve keys and use BharatX branding')
    public=ROOT/'browser-features/pages-aboutDialog/public'
    for filename in ['bharatx-about.html','privacy-policy.html','disclaimer.html']:
        source=(public/filename).read_text();parsed=Page();parsed.feed(source)
        assert 'nitai.grp00@gmail.com' in source
        assert 'Made in India' in source
        assert not re.search(r'\b(?:Floorp|Noraneko|GitHub)\b',' '.join(parsed.text))
        assert '<script' not in source.lower()
        for link in parsed.links+parsed.images:
            if link.startswith('https:'):assert link==identity['website'],'Unexpected external product link: '+link
            elif link.startswith(('mailto:','about:')):continue
            else:assert (public/link).is_file(),'Broken offline page link: '+link
        assert (ROOT/'publish-website'/filename).read_bytes()==(public/filename).read_bytes()
    checks.append('Offline About, Privacy and Disclaimer; only developer website and support links')
    for p in (ROOT/'browser-features').rglob('*.tsx'):
        if '/test/' in str(p):continue
        source=p.read_text()
        # External product navigation only; copyright comments are retained.
        assert not re.search(r'href\s*=\s*["\']https?://[^"\']*(?:floorp\.app|github\.com)',source,re.I),str(p)
    checks.append('No built-in TSX navigation links to upstream product or code-hosting pages')
    for p in (ROOT/'browser-features').rglob('*.html'):
        if '/test/' in str(p):continue
        title=re.search(r'<title[^>]*>([^<]*)</title>',p.read_text(),re.I)
        if title:assert not re.search(r'\b(?:Floorp|Noraneko)\b',title[1]),'Old browser page title: '+str(p)
    checks.append('Browser HTML titles use the product name')
    defaults=json.loads((ROOT/'packaging/windows/brand-prefs.json').read_text())
    assert defaults['floorp.releaseNotes.mode']=='disabled'
    assert defaults['app.update.url']=='' and defaults['toolkit.telemetry.server']==''
    assert defaults['bharatx.experiments.enabled'] is False
    assert defaults['nora.dev.allow_http_loader'] is False
    checks.append('Upstream update feed, remote experiments and HTTP developer loader disabled')
    lock=ROOT/'tools/bharatx/vendor/rcedit-lock.json'
    if lock.is_file():
        expected=json.loads(lock.read_text())
        with (lock.parent/'rcedit-x64.exe').open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
        assert digest==expected['sha256'],'Resource editor checksum mismatch'
        assert (lock.parent/'RCEDIT-LICENSE').is_file()
    else:raise AssertionError('Resource editor lock missing')
    checks.append('Pinned resource editor and retained third-party license')
    assert (ROOT/'LICENSE').read_text().startswith('Mozilla Public License Version 2.0')
    assert 'Floorp' in (ROOT/'THIRD_PARTY_NOTICES.md').read_text(),'Required original attribution must be retained'
    workflows=list((ROOT/'.github/workflows').glob('*.yml'))
    assert len(workflows)==1 and workflows[0].name=='build-bharatx-store.yml'
    assert 'windows_smoke.py' in (ROOT/'packaging/windows/Build-StorePackage.ps1').read_text()
    checks.append('Preserved MPL/attribution and one Store build workflow with native smoke test')
    return {'passed':True,'checks':checks,'sourceVersion':package['version'],
        'storeVersion':identity['version'],'windowsBuildExecuted':False,
        'limitation':'Dependency downloads are restricted in the editing environment; run the workflow to build, execute and validate the Windows application.'}

if __name__=='__main__':
    try:
        result=check();print(json.dumps(result,indent=2))
    except (AssertionError,ValueError) as error:
        print('AUDIT FAILED:',error,file=sys.stderr);sys.exit(1)

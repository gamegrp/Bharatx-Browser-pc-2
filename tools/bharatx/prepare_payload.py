"""Brand an artifact-build dist/bin tree before Windows MSIX packaging.

This transforms the complete mach output. It does not claim to compile Gecko.
Original engine licenses and copyright headers are preserved.
"""
# SPDX-License-Identifier: MPL-2.0
import argparse
import configparser
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]

def replace_constant(text: str, name: str, value: object, required: bool = True) -> str:
    # Preprocessed runtime JS may have //#line comments between key and value.
    pattern = r'(\b' + re.escape(name) + r':\s*(?://[^\n]*\n\s*)*)(?:"[^"\n]*"|true|false)'
    output, count = re.subn(pattern, lambda m: m[1] + json.dumps(value), text)
    if required and count != 1: raise ValueError(f'Unexpected runtime constant: {name} ({count})')
    return output

def replace_display_lines(text: str) -> str:
    output=[]
    for line in text.splitlines(keepends=True):
        stripped=line.lstrip()
        if stripped.startswith(('#','//','/*','*','<!--')) or re.search(r'copyright|trademark|licensed|license notice',line,re.I):
            output.append(line);continue
        # Do not rename Fluent keys, preferences or other internal API names.
        if '=' in line:
            left,right=line.split('=',1)
            right=re.sub(r'\b(?:Ablaze )?Floorp(?: Browser)?\b','BharatX Browser',right)
            right=re.sub(r'\bNoraneko\b','BharatX Browser',right)
            line=left+'='+right
        output.append(line)
    return ''.join(output)

def prepare(source: Path, output: Path) -> None:
    if output.exists(): raise FileExistsError(f'Output already exists: {output}')
    if not (source/'xul.dll').is_file(): raise ValueError('Missing Windows x64 xul.dll')
    if not (source/'browser/chrome/browser/content/browser/browser.xhtml').is_file():
        raise ValueError('Expected a flat, complete mach artifact build')
    shutil.copytree(source,output,symlinks=False)
    entry=next((output/n for n in ['floorp.exe','noraneko.exe','firefox.exe','BharatXCore.exe'] if (output/n).exists()),None)
    if entry is None: raise FileNotFoundError('The native browser executable is missing')
    if entry.name!='BharatXCore.exe':entry.rename(output/'BharatXCore.exe')

    for p in output.rglob('*'):
        if not p.is_file() or p.suffix not in {'.ftl','.properties','.dtd'} or 'license' in p.name.lower():continue
        original=p.read_text(encoding='utf-8')
        replaced=replace_display_lines(original)
        if replaced!=original:p.write_text(replaced,encoding='utf-8')

    branding=output/'browser/chrome/browser/content/branding'
    if not branding.is_dir():raise FileNotFoundError('Runtime branding directory is missing')
    for p in branding.glob('*.png'):shutil.copy2(ROOT/'branding/BharatXBrowser.png',p)
    import base64
    data=base64.b64encode((ROOT/'branding/BharatXBrowser.png').read_bytes()).decode()
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128"><image width="128" height="128" href="data:image/png;base64,{data}"/></svg>\n'
    for p in branding.glob('*.svg'):p.write_text(svg)
    for name in ['about-logo.png','about-logo@2x.png','icon64.png']:
        shutil.copy2(ROOT/'branding/BharatXBrowser.png',branding/name)
    for p in (output/'browser/VisualElements').glob('*.png'):
        shutil.copy2(ROOT/'branding/BharatXBrowser.png',p)

    constants=output/'modules/AppConstants.sys.mjs'
    text=constants.read_text()
    lock=json.loads((ROOT/'floorp-runtime.lock.json').read_text())
    engine=next(x['version'] for x in lock['artifacts'] if x['platform']=='windows')
    for name,value in {'MOZ_APP_NAME':'BharatXCore','MOZ_APP_BASENAME':'BharatXBrowser',
        'MOZ_APP_DISPLAYNAME_DO_NOT_USE':'BharatX Browser','MOZ_APP_VERSION':'1.36.0@'+engine,
        'MOZ_APP_VERSION_DISPLAY':'1.36.0@'+engine,'MOZ_UPDATER':False,'MOZ_NORMANDY':False,
        'MOZ_DATA_REPORTING':False,'MOZ_UPDATE_AGENT':False}.items():
        text=replace_constant(text,name,value)
    constants.write_text(text)

    # Keep the native Help menu on a valid local page. The matching source
    # change is maintained in the common runtime patch set as well.
    help_file=output/'browser/chrome/browser/content/browser/utilityOverlay.js'
    help_source=help_file.read_text()
    old_help='  var url = Services.urlFormatter.formatURLPref("app.support.baseURL");\n  return url + aHelpTopic;'
    if old_help in help_source:
        help_source=help_source.replace(old_help,'  // Product help is local in the Nitai Studio distribution.\n  return "about:bharatx";')
        help_file.write_text(help_source)
    elif 'return "about:bharatx";' not in help_source:
        raise ValueError('The native Help link implementation changed; update the runtime patch')

    # The shipped native runtime embeds upstream XREAppData. A dedicated launcher
    # always supplies -app and XUL_APP_FILE, so changing an ignored root ini is
    # never mistaken for a successful native identity change.
    ini=configparser.ConfigParser();ini.optionxform=str
    ini.read(output/'application.ini')
    ini['App']['Vendor']='Nitai Studio'
    ini['App']['Name']='BharatXBrowser'
    ini['App']['RemotingName']='bharatx-browser'
    ini['App']['Profile']='NitaiStudio/BharatXBrowser'
    # Engine compatibility is separate from the user-facing/store release number.
    ini['App']['Version']=engine
    ini['App']['CodeName']='BharatX Browser'
    ini['AppUpdate']={'URL':''}
    with (output/'browser/application.ini').open('w') as stream:ini.write(stream,space_around_delimiters=False)
    (output/'application.ini').unlink()
    prefs=json.loads((ROOT/'packaging/windows/brand-prefs.json').read_text())
    prefdir=output/'browser/defaults/preferences';prefdir.mkdir(parents=True,exist_ok=True)
    (prefdir/'bharatx.js').write_text('// BharatX Browser distribution defaults\n'+''.join(
        f'pref({json.dumps(k)}, {json.dumps(v)});\n' for k,v in prefs.items()))
    locked={key:{'Value':value,'Status':'locked'} for key,value in prefs.items()
        if key.startswith(('app.update.','datareporting.','toolkit.telemetry.','bharatx.experiments.'))
        or key in {'floorp.os.enabled','floorp.os.hidden','floorp.mcp.enabled','nora.dev.allow_http_loader','floorp.releaseNotes.mode','floorp.releaseNotes.choiceConfirmed'}}
    policies={'policies':{'DisableAppUpdate':True,'DisableTelemetry':True,'DisableFirefoxStudies':True,
        'DisableFeedbackCommands':True,'DisablePocket':True,'Preferences':locked}}
    distribution=output/'distribution';distribution.mkdir(exist_ok=True)
    (distribution/'policies.json').write_text(json.dumps(policies,indent=2)+'\n')
    for name in ['LICENSE','THIRD_PARTY_NOTICES.md']:shutil.copy2(ROOT/name,output/name)
    shutil.copytree(ROOT/'packaging/windows/Assets',output/'Assets',dirs_exist_ok=True)
    shutil.copy2(ROOT/'packaging/windows/AppxManifest.xml',output/'AppxManifest.xml')
    shutil.copy2(ROOT/'branding/BharatXBrowser.ico',output/'BharatXBrowser.ico')
    # MSIX handles uninstall/update; never install an upstream maintenance agent.
    for n in ['updater.exe','updater.ini','maintenanceservice.exe','maintenanceservice_installer.exe','default-browser-agent.exe','pingsender.exe']:
        (output/n).unlink(missing_ok=True)
    shutil.rmtree(output/'uninstall',ignore_errors=True)
    (output/'BharatXBrowser.VisualElementsManifest.xml').write_text('''<Application xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><VisualElements BackgroundColor="#101820" ShowNameOnSquare150x150Logo="on" ForegroundText="light" Square150x150Logo="Assets\\Square150x150Logo.png" Square70x70Logo="Assets\\Square44x44Logo.png" /></Application>''')
    for p in output.glob('*VisualElementsManifest.xml'):
        if p.name!='BharatXBrowser.VisualElementsManifest.xml':p.unlink()
    print('Prepared BharatX Browser payload:',output)

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();prepare(args.source.resolve(),args.output.resolve())

"""Run the real Windows browser and validate branding through Marionette.

No existing user profile is opened or modified. Used by the Store packaging job.
"""
# SPDX-License-Identifier: MPL-2.0
import os
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

class Marionette:
    def __init__(self, port: int):
        self.socket = socket.create_connection(('127.0.0.1',port),timeout=10)
        self.sequence=0
        self.receive()

    def receive(self):
        size=b''
        while True:
            char=self.socket.recv(1)
            if not char: raise RuntimeError('Marionette connection closed')
            if char==b':': break
            size+=char
        remaining=int(size);content=b''
        while remaining:
            part=self.socket.recv(remaining)
            if not part: raise RuntimeError('Incomplete Marionette response')
            remaining-=len(part);content+=part
        return json.loads(content)

    def command(self, name: str, data: dict):
        self.sequence+=1
        content=json.dumps([0,self.sequence,name,data]).encode()
        self.socket.sendall(str(len(content)).encode()+b':'+content)
        while True:
            message=self.receive()
            if isinstance(message,list) and message[0]==1 and message[1]==self.sequence:
                if message[2]:raise RuntimeError(json.dumps(message[2]))
                return message[3]

    def script(self, script: str):
        result=self.command('WebDriver:ExecuteScript',{'script':script,'args':[],
            'newSandbox':True,'sandbox':'default','filename':'bharatx-smoke','line':1})
        return result.get('value',result)

def smoke(payload: Path, report_file: Path) -> None:
    report={'passed':False,'checks':[]}
    browser=None;client=None
    profile_manager=tempfile.TemporaryDirectory(prefix="bharatx-smoke-")
    try:
        profile=Path(profile_manager.name)
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
        preferences={'marionette.port':port,'browser.shell.checkDefaultBrowser':False,
            'floorp.browser.welcome.page.shown':True,'browser.startup.page':0,
            'browser.startup.homepage_override.mstone':'ignore',
            'floorp.releaseNotes.mode':'disabled','floorp.releaseNotes.choiceConfirmed':True}
        (profile/'user.js').write_text(''.join(f'user_pref({json.dumps(k)},{json.dumps(v)});\n' for k,v in preferences.items()))
        browser=subprocess.Popen([str(payload/'BharatXBrowser.exe'),'--no-remote',
            '--profile',str(profile),'--headless','--marionette','--remote-allow-system-access','about:blank'],
            env={**os.environ,'MOZ_REMOTE_ALLOW_SYSTEM_ACCESS':'1'})
        deadline=time.monotonic()+90
        while time.monotonic()<deadline:
            if browser.poll() is not None and browser.returncode != 0:raise RuntimeError(f'Browser exited before connection: {browser.returncode}')
            try:client=Marionette(port);break
            except (ConnectionError,OSError):time.sleep(0.5)
        if client is None:raise RuntimeError('Browser did not expose Marionette in time')
        client.command('WebDriver:NewSession',{'capabilities':{'alwaysMatch':{'acceptInsecureCerts':False}}})
        client.command('Marionette:SetContext',{'value':'chrome'})
        while time.monotonic()<deadline:
            result=client.script('return {mode:Services.prefs.getStringPref(\"nora.startup.mode\",\"\"),name:Services.appinfo.name,vendor:Services.appinfo.vendor,loader:Services.prefs.getStringPref("nora.startup.loader",""),error:Services.prefs.getStringPref("nora.startup.error","")};')
            if result['error']:raise RuntimeError('Feature startup failed: '+result['error'])
            if result['loader']=='loaded':break
            time.sleep(0.5)
        if result['loader']!='loaded':raise RuntimeError('Production feature loader did not finish: '+json.dumps(result))
        if result['name']!='BharatXBrowser' or result['vendor']!='Nitai Studio':
            raise RuntimeError('Native XRE identity was not overridden: '+json.dumps(result))
        report['identity']=result;report['checks'].append('native identity and production startup')
        client.command('Marionette:SetContext',{'value':'content'})
        for address,expected in [('about:bharatx','Developed by Nitaistudio'),
            ('about:bharatx-privacy','Privacy Policy'),('about:bharatx-disclaimer','Disclaimer'),
            ('about:hub#/about/browser','nitai.grp00@gmail.com')]:
            client.command('WebDriver:Navigate',{'url':address})
            deadline_page=time.monotonic()+25
            while time.monotonic()<deadline_page:
                text=client.script('return document.body ? document.body.innerText : "";')
                if expected in text:break
                time.sleep(0.3)
            if expected not in text:raise RuntimeError('Page failed to render: '+address)
            if 'Floorp' in text or 'Noraneko' in text or 'GitHub' in text:
                raise RuntimeError('Upstream product branding is visible on '+address)
            report['checks'].append(address)
        report['passed']=True
    except Exception as error:
        report['error']=str(error)
        raise
    finally:
        if client:
            try:client.command('Marionette:Quit',{'flags':['eForceQuit']})
            except Exception:pass
            client.socket.close()
        if browser:
            try:browser.wait(timeout=10)
            except subprocess.TimeoutExpired:
                subprocess.run(['taskkill','/PID',str(browser.pid),'/T','/F'],capture_output=True)
        report_file.parent.mkdir(parents=True,exist_ok=True)
        report_file.write_text(json.dumps(report,indent=2)+'\n')
        profile_manager.cleanup()

if __name__=='__main__':
    smoke(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())

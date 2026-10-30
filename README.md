# BharatX Browser

**Version 1.36.0 · Microsoft Store package 1.36.0.0 · Windows x64**

Developed by **Nitaistudio** · **Made in India**

Support: **nitai.grp00@gmail.com**

Website: **https://www.trishabonlineservice.in/?m=1**

এই project-এ আপনার দেওয়া browser feature source, BharatX branding, স্থানীয়
About/Privacy/Disclaimer, supplied logo এবং Microsoft Store build setup আছে।
Gecko engine-এর source ও native artifact lock file অনুযায়ী build-এর সময় নেওয়া হয়।
এই source ZIP-টি সরাসরি Partner Center-এ upload করার package নয়।

## Microsoft Store build

1. ZIP extract করে `BharatXBrowser` folder-এর **ভেতরের সব files/folders**, hidden
   `.github` folder-সহ, আপনার repository-এর root-এ দিন।
2. Actions → **Build BharatX Browser for Microsoft Store** → **Run workflow** চালান।
3. Linux job production feature code ও pinned runtime দিয়ে Windows build বানায়।
   Windows job launcher compile করে, বাস্তবে browser চালিয়ে internal pages ও
   branding পরীক্ষা করে, তারপর Windows SDK দিয়ে package validation করে।
4. সব job সফল হলে **BharatXBrowser-Microsoft-Store-1.36.0.0-x64** artifact download করুন।
5. Partner Center → BharatX Browser → Start update → Packages-এ পাওয়া
   **BharatXBrowser-Store-x64-1.36.0.0.msixupload** অথবা `.msix` দিন।

এই workflow public pinned runtime ব্যবহার করে। Upstream publisher-এর PAT,
signing secrets বা private runtime repository প্রয়োজন হয় না। Source dependencies
download করার জন্য runner-এর internet access লাগবে। বড় runtime checkout-এর কারণে
প্রথম build-এ সময় লাগে; GitHub runner quota ও availability আপনার account-এর ওপর নির্ভর করে।

## Store identity

| Field | Value |
| --- | --- |
| Package Name | `NitaiStudio.BharatXBrowser` |
| Publisher | `CN=BEDDC7D9-ACD5-4D93-AEC9-C98C64F43592` |
| Publisher Display Name | `Nitai Studio` |
| Product display name | `BharatX Browser` |
| New package version | `1.36.0.0` |
| Previous screenshot version | `1.35.7.0` |
| Architecture | `x64` |
| Device family | Windows Desktop |

The identity is transcribed from the supplied Partner Center screenshot. The engine
compatibility version stays separate from the BharatX release number so addon
version checks are not lowered to 1.36. The dedicated native launcher uses the
custom XRE application file; editing the ignored root application.ini alone is
deliberately avoided. The native engine remains a precompiled locked artifact.

## Privacy policy for the Store listing

অ্যাপের About screen-এ Privacy Policy এবং Disclaimer offline পাওয়া যাবে।
Store listing-এ একটি public privacy-policy URL দরকার হলে `publish-website`-এর
`privacy-policy.html` ও `bharatx-logo.png` আপনার নিজের website-এ প্রকাশ করুন এবং
প্রকাশিত আসল URL ব্যবহার করুন। এই source update আপনার website-এ নিজে থেকে কিছু
publish করে না। `chrome://...` বা `about:...` address Store-এর public URL হিসেবে দেবেন না।

## What changed

- Product name, dialog, settings, welcome screens, new-tab logos and translated display strings use BharatX Browser.
- The supplied logo is used for app branding, Windows executable icons and Store tiles.
- About includes the support email, developer website, developer attribution and Made in India.
- Privacy and disclaimer pages use local content and no remote scripts or fonts.
- Product navigation to the upstream project, its social pages and code-hosting pages was removed.
- Upstream self-update, remote experiment startup and telemetry defaults are disabled;
  the Store edition receives Nitai Studio updates through Microsoft Store.
- Browser URL entry, search, web standards, extension services and technical build
  dependency addresses remain functional. Internal identifiers are retained to avoid
  breaking browser features. Required legal attributions are preserved.

## Source and licensing

`LICENSE`, source headers, font notices and `THIRD_PARTY_NOTICES.md` retain the
applicable third-party terms. Branding changes do not transfer ownership of the
upstream engine or code. An independent distribution can charge a price subject
to its licenses and Store terms; recipients retain rights granted by those licenses.

Keep the workflow's **BharatXBrowser-MPL-Source-1.36.0** artifact for the exact binary
you distribute and make the covered source available to recipients, including
modifications. The in-app notice directs source requests to your support email.
Download and preserve the source artifact before the runner's artifact retention
expires, then serve requests without charge or publish it on your own website.

`rcedit-x64.exe` is a pinned MIT-licensed build helper. Its license and checksum
are in `tools/bharatx/vendor`; it is not copied into the browser payload.

## Validation status

Offline identity, local-link, localization and source checks are available with:

```text
python tools/bharatx/audit.py
```

The editing environment could download and verify the locked native runtime but
could not install all frontend dependencies because registry access was denied.
Therefore **a complete browser build, Windows execution, makeappx validation and
Store certification were not completed here**. The included workflow executes the
Windows startup test and packaging validation and stops if they fail. Microsoft
makes the final Store certification decision. Review `docs/validation-report.json`
for the actual checks performed on this source delivery.

Before submitting the generated package, install a test-signed copy on a clean
Windows device and check browsing, downloads, addons, setting it as default,
relaunch, and update from the existing Store version. The Store upload itself
remains unsigned for Store signing; a raw unsigned package is not a sideload installer.

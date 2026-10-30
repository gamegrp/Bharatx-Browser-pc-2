[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$Payload,
  [string]$OutputDirectory = "out"
)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$Payload = (Resolve-Path $Payload).Path
$identity = Get-Content (Join-Path $PSScriptRoot "store-identity.json") -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$OutputDirectory = (Resolve-Path $OutputDirectory).Path

if (!(Test-Path (Join-Path $Payload "BharatXCore.exe"))) { throw "Prepared native payload is missing." }
if (!(Test-Path (Join-Path $Payload "browser/application.ini"))) { throw "The rebranded XRE application identity is missing." }

$compiler = Join-Path $env:WINDIR "Microsoft.NET/Framework64/v4.0.30319/csc.exe"
if (!(Test-Path $compiler)) { throw "The Windows .NET Framework C# compiler is required." }
$launcher = Join-Path $Payload "BharatXBrowser.exe"
& $compiler /nologo /target:winexe /platform:x64 /optimize+ /reference:System.Windows.Forms.dll "/win32icon:$(Join-Path $root 'branding/BharatXBrowser.ico')" "/out:$launcher" (Join-Path $PSScriptRoot "Launcher.cs")
if ($LASTEXITCODE -ne 0) { throw "Launcher compilation failed." }

$resourceEditor = Join-Path $root "tools/bharatx/vendor/rcedit-x64.exe"
$resourceLock = Get-Content (Join-Path $root "tools/bharatx/vendor/rcedit-lock.json") -Raw | ConvertFrom-Json
if ((Get-FileHash $resourceEditor -Algorithm SHA256).Hash.ToLowerInvariant() -ne $resourceLock.sha256) {
  throw "Resource editor checksum does not match its lock."
}
$core = Join-Path $Payload "BharatXCore.exe"
$oldCopyright = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($core).LegalCopyright
& $resourceEditor $core --set-icon (Join-Path $root "branding/BharatXBrowser.ico") `
  --set-version-string "ProductName" "BharatX Browser" `
  --set-version-string "FileDescription" "BharatX Browser" `
  --set-version-string "CompanyName" "Nitai Studio" `
  --set-version-string "InternalName" "BharatXCore" `
  --set-version-string "OriginalFilename" "BharatXCore.exe" `
  --set-version-string "LegalCopyright" "2026 Nitai Studio customizations. $oldCopyright" `
  --set-file-version $identity.version --set-product-version $identity.version
if ($LASTEXITCODE -ne 0) { throw "Native branding resource update failed." }

# Launch the actual Windows executable and test internal pages before packing.
& python (Join-Path $root "tools/bharatx/windows_smoke.py") $Payload (Join-Path $OutputDirectory "smoke-report.json")
if ($LASTEXITCODE -ne 0) { throw "Windows startup or branding smoke test failed." }

$sdkRoot = Join-Path ${env:ProgramFiles(x86)} "Windows Kits/10/bin"
$makeappx = Get-ChildItem "$sdkRoot/*/x64/makeappx.exe" | Sort-Object { [version]$_.Directory.Parent.Name } -Descending | Select-Object -First 1
if (!$makeappx) { throw "Install the Windows 10/11 SDK packaging tools (makeappx.exe)." }
$package = Join-Path $OutputDirectory "BharatXBrowser-Store-x64-$($identity.version).msix"
& $makeappx.FullName pack /d $Payload /p $package /o
if ($LASTEXITCODE -ne 0) { throw "MSIX validation or packing failed." }

Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead($package)
try {
  $manifestEntry = $archive.GetEntry("AppxManifest.xml")
  if (!$manifestEntry) { throw "The generated MSIX has no AppxManifest.xml." }
  $reader = [System.IO.StreamReader]::new($manifestEntry.Open())
  try { [xml]$manifest = $reader.ReadToEnd() } finally { $reader.Dispose() }
  if ($manifest.Package.Identity.Name -ne $identity.name -or
      $manifest.Package.Identity.Publisher -ne $identity.publisher -or
      $manifest.Package.Identity.Version -ne $identity.version) {
    throw "The generated MSIX identity does not match the Partner Center configuration."
  }
} finally { $archive.Dispose() }

# Store submissions use unsigned packages. Store supplies the distribution signature.
$uploadDirectory = Join-Path $OutputDirectory "upload-content"
New-Item -ItemType Directory -Force -Path $uploadDirectory | Out-Null
Copy-Item $package $uploadDirectory -Force
$upload = Join-Path $OutputDirectory "BharatXBrowser-Store-x64-$($identity.version).msixupload"
if (Test-Path $upload) { Remove-Item $upload }
[System.IO.Compression.ZipFile]::CreateFromDirectory($uploadDirectory, $upload)
Remove-Item $uploadDirectory -Recurse -Force
$hashes = @($package, $upload) | ForEach-Object {
  "{0}  {1}" -f (Get-FileHash $_ -Algorithm SHA256).Hash.ToLowerInvariant(), [System.IO.Path]::GetFileName($_)
}
$hashes | Set-Content (Join-Path $OutputDirectory "SHA256SUMS.txt")
Write-Host "Created Store packages: $package and $upload"

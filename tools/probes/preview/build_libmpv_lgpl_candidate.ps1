param(
    [Parameter(Mandatory = $true)]
    [string]$MpvSource,

    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$mpv = (Resolve-Path -LiteralPath $MpvSource).Path
$out = [System.IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Force -Path $out | Out-Null

function Stop-Harness([string]$Message) {
    Write-Host "HARNESS_FAILURE: $Message"
    exit 30
}

function Replace-Required {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Old,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$New,
        [int]$Expected = 1
    )

    $count = [regex]::Matches($Text, [regex]::Escape($Old)).Count
    if ($count -ne $Expected) {
        Stop-Harness "Expected $Expected occurrence(s) of '$Old', found $count. Upstream build script changed."
    }
    return $Text.Replace($Old, $New)
}

function Run-Native {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$ArgumentList,
        [Parameter(Mandatory = $true)][string]$Stdout,
        [Parameter(Mandatory = $true)][string]$Stderr,
        [string]$WorkingDirectory = $mpv
    )

    $p = Start-Process `
        -FilePath $FilePath `
        -ArgumentList $ArgumentList `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $Stdout `
        -RedirectStandardError $Stderr `
        -Wait `
        -PassThru `
        -NoNewWindow

    return $p.ExitCode
}

Write-Host "=== libmpv LGPL candidate builder ==="
Write-Host "mpv source: $mpv"
Write-Host "output: $out"

$tag = (git -C $mpv describe --tags --exact-match HEAD 2>$null).Trim()
if ($LASTEXITCODE -ne 0 -or $tag -ne "v0.41.0") {
    Stop-Harness "Expected exact mpv tag v0.41.0, observed '$tag'."
}
$mpvSha = (git -C $mpv rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { Stop-Harness "Could not resolve mpv HEAD." }

$upstreamScript = Join-Path $mpv "ci\build-win32.ps1"
if (-not (Test-Path -LiteralPath $upstreamScript)) {
    Stop-Harness "Missing upstream ci/build-win32.ps1."
}

$upstreamHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $upstreamScript).Hash.ToLowerInvariant()
$patchedScript = Join-Path $env:RUNNER_TEMP "mpv-build-win32-lgpl-v0.41.0.ps1"
$text = Get-Content -LiteralPath $upstreamScript -Raw

# Keep the upstream-supported Windows/Clang build route, but convert its normal
# GPL/full-player CI configuration into a benchmark-only shared libmpv LGPL candidate.
$text = Replace-Required $text '-Ddefault_library=static `' '-Ddefault_library=both `'
$text = Replace-Required $text '-Dlibmpv=true `' @'
-Dlibmpv=true `
    -Dcplayer=false `
    -Dbuild-date=false `
    -Dcplugins=disabled `
    -Dcdda=disabled `
    -Ddvbin=disabled `
    -Ddvdnav=disabled `
    -Djavascript=disabled `
    -Djpeg=disabled `
    -Dlcms2=disabled `
    -Dlibavdevice=disabled `
    -Dlibbluray=disabled `
    -Dlua=disabled `
    -Duchardet=disabled `
    -Dvapoursynth=disabled `
    -Dzimg=disabled `
    -Dwasapi=enabled `
    -Dd3d11=enabled `
    -Dd3d-hwaccel=enabled `
    -Dd3d9-hwaccel=disabled `
    -Ddirect3d=disabled `
    -Dshaderc=disabled `
    -Dspirv-cross=disabled `
    -Dwin32-smtc=disabled `
'@
$text = Replace-Required $text '-Dtests=true `' '-Dtests=false `'
$text = Replace-Required $text '-Dgpl=true `' '-Dgpl=false `'
$text = Replace-Required $text '-Dffmpeg:gpl=enabled `' '-Dffmpeg:gpl=disabled `'
$text = Replace-Required $text '-Dffmpeg:tests=enabled `' '-Dffmpeg:tests=disabled `'
$text = Replace-Required $text '-Dffmpeg:programs=enabled `' '-Dffmpeg:programs=disabled `'
$text = Replace-Required $text '-Dffmpeg:vulkan=auto `' '-Dffmpeg:vulkan=disabled `'
$text = Replace-Required $text '-Dffmpeg:libdav1d=enabled `' '-Dffmpeg:libdav1d=disabled `'
$text = Replace-Required $text '-Dffmpeg:libjxl=enabled `' '-Dffmpeg:libjxl=disabled `'
$text = Replace-Required $text '-Dffmpeg:libaom=enabled `' '-Dffmpeg:libaom=disabled `'
$text = Replace-Required $text '-Dlcms2:fastfloat=true `' ''
$text = Replace-Required $text '-Dlcms2:jpeg=disabled `' ''
$text = Replace-Required $text '-Dlcms2:tiff=disabled `' ''
$text = Replace-Required $text '-Dlibass:test=enabled `' '-Dlibass:test=disabled `'
$text = Replace-Required $text '-Dlibplacebo:lcms=enabled `' '-Dlibplacebo:lcms=disabled `'
$text = Replace-Required $text '-Dlibplacebo:shaderc=enabled `' '-Dlibplacebo:shaderc=disabled `'
$text = Replace-Required $text '-Dlibplacebo:vulkan=enabled `' '-Dlibplacebo:vulkan=disabled `'
$text = Replace-Required $text '-Dvulkan=enabled `' '-Dvulkan=disabled `'
$text = Replace-Required $text '-Djavascript=enabled `' '-Djavascript=disabled `'
$text = Replace-Required $text '-Dwin32-smtc=enabled `' '-Dwin32-smtc=disabled `'
$text = Replace-Required $text '-Dlua=luajit `' '-Dlua=disabled `'
$text = Replace-Required $text 'ninja -C build mpv.exe mpv.com libmpv.a' 'ninja -C build libmpv-2.dll'
$text = Replace-Required $text 'cp ./build/subprojects/vulkan-loader/vulkan.dll ./build/vulkan-1.dll' '# Vulkan intentionally disabled for this candidate.'
$text = Replace-Required $text 'cp ./etc/mpv-*.bat ./build' '# cplayer intentionally disabled; no launcher artifacts.'
$text = Replace-Required $text './build/mpv.com -v --no-config' '# libmpv DLL is validated below.'

# Pin the two always-required higher-level multimedia dependencies to stable tags
# instead of upstream CI's moving master branches. The FFmpeg Meson port stays on
# upstream's v0.41.0-tested meson-8.0 branch; its exact resolved commit is recorded.
$text = [regex]::Replace(
    $text,
    '(URL = "https://github\.com/libass/libass"\s+Revision = )"master"',
    '$1"0.17.5"',
    1
)
$text = [regex]::Replace(
    $text,
    '(URL = "https://code\.videolan\.org/videolan/libplacebo\.git"\s+Revision = )"master"',
    '$1"v7.360.1"',
    1
)

Set-Content -LiteralPath $patchedScript -Value $text -Encoding UTF8
$patchedHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $patchedScript).Hash.ToLowerInvariant()
Copy-Item -LiteralPath $patchedScript -Destination (Join-Path $out "patched-upstream-build-win32-lgpl.ps1") -Force

$buildArgsPath = Join-Path $out "candidate-policy.txt"
@"
mpv_tag=v0.41.0
mpv_sha=$mpvSha
mpv_gpl=false
ffmpeg_gpl=disabled
cplayer=false
libmpv=true
default_library=both
prefer_static=false
windows_video=d3d11 enabled
windows_hwdecode=d3d11va enabled
software_decode=FFmpeg native path retained
vulkan=disabled
lua=disabled
javascript=disabled
libarchive=disabled (upstream script)
libbluray=disabled
libass_pin=0.17.5
libplacebo_pin=v7.360.1
upstream_build_script_sha256=$upstreamHash
patched_build_script_sha256=$patchedHash
candidate_status=benchmark-only; not approved for product distribution
"@ | Set-Content -LiteralPath $buildArgsPath -Encoding UTF8

$buildStdout = Join-Path $out "build.stdout.log"
$buildStderr = Join-Path $out "build.stderr.log"

Push-Location $mpv
try {
    $exitCode = Run-Native `
        -FilePath "pwsh.exe" `
        -ArgumentList @("-NoLogo", "-NoProfile", "-File", $patchedScript) `
        -Stdout $buildStdout `
        -Stderr $buildStderr `
        -WorkingDirectory $mpv
} finally {
    Pop-Location
}

if (Test-Path -LiteralPath (Join-Path $mpv "build\meson-logs")) {
    Copy-Item -LiteralPath (Join-Path $mpv "build\meson-logs") -Destination (Join-Path $out "meson-logs") -Recurse -Force
}

if ($exitCode -ne 0) {
    Write-Host "CANDIDATE_BUILD_FAILURE: upstream-derived build exited $exitCode"
    Write-Host "=== stderr tail ==="
    if (Test-Path -LiteralPath $buildStderr) { Get-Content -LiteralPath $buildStderr -Tail 120 }
    exit 10
}

$buildDir = Join-Path $mpv "build"
$dll = Get-ChildItem -LiteralPath $buildDir -Recurse -File -Filter "libmpv-2.dll" | Select-Object -First 1
if ($null -eq $dll) { Stop-Harness "Build reported success but libmpv-2.dll was not found." }

$runtimeDir = Join-Path $out "runtime"
New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null
Copy-Item -LiteralPath $dll.FullName -Destination $runtimeDir -Force

$importLib = Get-ChildItem -LiteralPath $buildDir -Recurse -File | Where-Object { $_.Name -in @("mpv.lib", "libmpv.lib") } | Select-Object -First 1
if ($null -ne $importLib) { Copy-Item -LiteralPath $importLib.FullName -Destination $runtimeDir -Force }

$headersDir = Join-Path $out "include\mpv"
New-Item -ItemType Directory -Force -Path $headersDir | Out-Null
foreach ($header in @("client.h", "render.h", "render_gl.h", "stream_cb.h")) {
    $src = Join-Path $mpv "include\mpv\$header"
    if (Test-Path -LiteralPath $src) { Copy-Item -LiteralPath $src -Destination $headersDir -Force }
}

$dependentsPath = Join-Path $out "libmpv-dependents.txt"
$dumpbinStdErr = Join-Path $out "dumpbin.stderr.log"
$dumpCode = Run-Native -FilePath "dumpbin.exe" -ArgumentList @("/DEPENDENTS", $dll.FullName) -Stdout $dependentsPath -Stderr $dumpbinStdErr -WorkingDirectory $mpv
if ($dumpCode -ne 0) { Stop-Harness "dumpbin /DEPENDENTS failed with exit $dumpCode." }

# Bundle direct non-system DLL dependencies only when the build produced them.
$systemDlls = @(
    "kernel32.dll", "user32.dll", "gdi32.dll", "advapi32.dll", "ole32.dll", "oleaut32.dll",
    "shell32.dll", "shlwapi.dll", "comdlg32.dll", "comctl32.dll", "winmm.dll", "version.dll",
    "ws2_32.dll", "bcrypt.dll", "secur32.dll", "dwmapi.dll", "dxgi.dll", "d3d11.dll",
    "d3dcompiler_47.dll", "mfplat.dll", "mfuuid.dll", "propsys.dll", "avrt.dll", "ntdll.dll",
    "ucrtbase.dll", "vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll", "api-ms-win-core-libraryloader-l1-2-0.dll"
) | ForEach-Object { $_.ToLowerInvariant() }

$depText = Get-Content -LiteralPath $dependentsPath -Raw
$directDllNames = [regex]::Matches($depText, '(?im)^\s+([A-Za-z0-9_.+-]+\.dll)\s*$') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
$bundled = @()
$unresolved = @()
foreach ($name in $directDllNames) {
    if ($systemDlls -contains $name.ToLowerInvariant()) { continue }
    $found = Get-ChildItem -LiteralPath $buildDir -Recurse -File -Filter $name | Select-Object -First 1
    if ($null -ne $found) {
        Copy-Item -LiteralPath $found.FullName -Destination $runtimeDir -Force
        $bundled += $name
    } else {
        $unresolved += $name
    }
}

# Record Meson options as an auditable truth source.
$configureOut = Join-Path $out "meson-configure.txt"
$configureErr = Join-Path $out "meson-configure.stderr.log"
$configureCode = Run-Native -FilePath "meson.exe" -ArgumentList @("configure", $buildDir) -Stdout $configureOut -Stderr $configureErr -WorkingDirectory $mpv
if ($configureCode -ne 0) { Stop-Harness "meson configure audit failed." }

$introspectPath = Join-Path $out "meson-buildoptions.json"
$introspectErr = Join-Path $out "meson-introspect.stderr.log"
$introspectCode = Run-Native -FilePath "meson.exe" -ArgumentList @("introspect", "--buildoptions", $buildDir) -Stdout $introspectPath -Stderr $introspectErr -WorkingDirectory $mpv
if ($introspectCode -ne 0) { Stop-Harness "meson introspect audit failed." }

$options = Get-Content -LiteralPath $introspectPath -Raw | ConvertFrom-Json
$topGpl = $options | Where-Object { $_.name -eq "gpl" } | Select-Object -First 1
if ($null -eq $topGpl -or $topGpl.value -ne $false) {
    Stop-Harness "Meson introspection did not prove top-level gpl=false."
}
$preferStatic = $options | Where-Object { $_.name -eq "prefer_static" } | Select-Object -First 1
if ($null -eq $preferStatic -or $preferStatic.value -ne $false) {
    Stop-Harness "Meson introspection did not prove prefer_static=false."
}

# FFmpeg's generated config is the strongest local build proof that GPL/nonfree
# components were not enabled by the selected Meson subproject configuration.
$ffmpegConfigCandidates = Get-ChildItem -LiteralPath $buildDir -Recurse -File -Filter "config.h" | Where-Object {
    Select-String -LiteralPath $_.FullName -Pattern "CONFIG_GPL" -Quiet -ErrorAction SilentlyContinue
}
$ffmpegConfig = $ffmpegConfigCandidates | Select-Object -First 1
if ($null -eq $ffmpegConfig) { Stop-Harness "Could not find generated FFmpeg config.h containing CONFIG_GPL." }
$ffmpegAudit = Join-Path $out "ffmpeg-license-config.txt"
Select-String -LiteralPath $ffmpegConfig.FullName -Pattern "CONFIG_GPL|CONFIG_NONFREE|CONFIG_VERSION3" | ForEach-Object { $_.Line } | Set-Content -LiteralPath $ffmpegAudit -Encoding UTF8
$ffmpegConfigText = Get-Content -LiteralPath $ffmpegConfig.FullName -Raw
if ($ffmpegConfigText -match '#define\s+CONFIG_GPL\s+1') { Stop-Harness "FFmpeg CONFIG_GPL=1; candidate is not acceptable." }
if ($ffmpegConfigText -match '#define\s+CONFIG_NONFREE\s+1') { Stop-Harness "FFmpeg CONFIG_NONFREE=1; candidate is not redistributable." }

# Capture exact subproject revisions and license files. Moving branches may be used
# during this benchmark build, but their resolved SHAs become part of the evidence.
$subprojects = @()
$licenseRoot = Join-Path $out "licenses"
New-Item -ItemType Directory -Force -Path $licenseRoot | Out-Null
$subRoot = Join-Path $mpv "subprojects"
if (Test-Path -LiteralPath $subRoot) {
    foreach ($dir in Get-ChildItem -LiteralPath $subRoot -Directory) {
        $gitDir = Join-Path $dir.FullName ".git"
        if (-not (Test-Path -LiteralPath $gitDir)) { continue }
        $sha = (git -C $dir.FullName rev-parse HEAD 2>$null).Trim()
        $remote = (git -C $dir.FullName remote get-url origin 2>$null).Trim()
        $subprojects += [ordered]@{ name = $dir.Name; sha = $sha; remote = $remote }

        $dst = Join-Path $licenseRoot $dir.Name
        $copied = $false
        foreach ($f in Get-ChildItem -LiteralPath $dir.FullName -File -ErrorAction SilentlyContinue) {
            if ($f.Name -match '^(LICENSE|LICENCE|COPYING|COPYRIGHT|NOTICE)(\.|$|[-_])') {
                if (-not $copied) { New-Item -ItemType Directory -Force -Path $dst | Out-Null; $copied = $true }
                Copy-Item -LiteralPath $f.FullName -Destination $dst -Force
            }
        }
    }
}

$mpvLicenseDir = Join-Path $licenseRoot "mpv"
New-Item -ItemType Directory -Force -Path $mpvLicenseDir | Out-Null
foreach ($f in @("LICENSE.LGPL", "Copyright")) {
    $src = Join-Path $mpv $f
    if (Test-Path -LiteralPath $src) { Copy-Item -LiteralPath $src -Destination $mpvLicenseDir -Force }
}

$dllHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $dll.FullName).Hash.ToLowerInvariant()
$runtimeFiles = Get-ChildItem -LiteralPath $runtimeDir -File | ForEach-Object {
    [ordered]@{
        name = $_.Name
        size = $_.Length
        sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()
    }
}

$compiler = (& clang --version 2>&1 | Select-Object -First 1) -join ""
$mesonVersion = (& meson --version 2>&1 | Select-Object -First 1) -join ""

$provenance = [ordered]@{
    schema = "video-editing-agent-preview-libmpv-candidate/v1"
    purpose = "R0.12 Preview benchmark only"
    product_distribution_approved = $false
    mpv = [ordered]@{
        tag = $tag
        sha = $mpvSha
        license_mode = "LGPL-2.1-or-later via gpl=false"
        upstream_build_script_sha256 = $upstreamHash
        patched_build_script_sha256 = $patchedHash
    }
    build = [ordered]@{
        os = [Environment]::OSVersion.VersionString
        compiler = $compiler
        meson = $mesonVersion
        default_library = "both"
        prefer_static = $false
        cplayer = $false
        libmpv = $true
        gpl = $false
        ffmpeg_gpl = "disabled"
        ffmpeg_nonfree_proven_disabled = -not ($ffmpegConfigText -match '#define\s+CONFIG_NONFREE\s+1')
        d3d11 = "enabled"
        d3d11_hwaccel = "enabled"
        vulkan = "disabled"
    }
    artifact = [ordered]@{
        libmpv_dll_sha256 = $dllHash
        direct_dependencies = $directDllNames
        bundled_non_system_dependencies = $bundled
        unresolved_non_system_dependencies = $unresolved
        runtime_files = $runtimeFiles
    }
    subprojects = $subprojects
    limitations = @(
        "Benchmark candidate only; packaging/notices/source-offer obligations are not closed here.",
        "Subproject exact SHAs are recorded; moving upstream branches are not accepted as future production pins.",
        "A successful build does not by itself prove playback/control compatibility on the target Windows host."
    )
}
$provenance | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out "PROVENANCE.json") -Encoding UTF8

if ($unresolved.Count -gt 0) {
    Write-Host "CANDIDATE_PACKAGING_GAP: unresolved direct non-system DLL dependencies: $($unresolved -join ', ')"
    exit 11
}

Write-Host "LIBMPV LGPL CANDIDATE BUILD PASS"
Write-Host "mpv: $tag $mpvSha"
Write-Host "libmpv-2.dll SHA256: $dllHash"
Write-Host "artifact: $out"
exit 0

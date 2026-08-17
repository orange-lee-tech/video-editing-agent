$ErrorActionPreference = "Stop"

$version = "1.28.6"
$installer = Join-Path $env:RUNNER_TEMP "gstreamer-1.0-msvc-x86_64-$version.exe"
$runtimeRoot = Join-Path $env:RUNNER_TEMP "gstreamer-$version"
$url = "https://gstreamer.freedesktop.org/data/pkg/windows/$version/msvc/gstreamer-1.0-msvc-x86_64-$version.exe"
$expectedSha256 = "059251444D1267B486EBA390B18D25FED87E10315E72F757EC6C7E912FA746B5"

& curl.exe --fail --location --retry 2 --retry-delay 2 --output $installer $url
if ($LASTEXITCODE -ne 0) {
    throw "GStreamer installer download failed with exit code $LASTEXITCODE"
}

$actualSha256 = (Get-FileHash $installer -Algorithm SHA256).Hash
if ($actualSha256 -ne $expectedSha256) {
    throw "GStreamer installer SHA-256 mismatch: expected $expectedSha256, got $actualSha256"
}

$bytes = [System.IO.File]::ReadAllBytes($installer)
if ($bytes.Length -lt 2 -or $bytes[0] -ne 0x4D -or $bytes[1] -ne 0x5A) {
    throw "GStreamer installer is not a PE/MZ executable"
}

$arguments = @(
    "/CURRENTUSER",
    "/VERYSILENT",
    "/NORESTART",
    "/TYPE=runtime",
    "/DIR=$runtimeRoot"
)
$process = Start-Process -FilePath $installer -ArgumentList $arguments -Wait -PassThru
if ($process.ExitCode -ne 0) {
    throw "GStreamer installer failed with exit code $($process.ExitCode)"
}

$required = @(
    (Join-Path $runtimeRoot "bin\gstreamer-1.0-0.dll"),
    (Join-Path $runtimeRoot "bin\gstplay-1.0-0.dll"),
    (Join-Path $runtimeRoot "bin\gobject-2.0-0.dll"),
    (Join-Path $runtimeRoot "bin\glib-2.0-0.dll"),
    (Join-Path $runtimeRoot "lib\gstreamer-1.0")
)
foreach ($path in $required) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "GStreamer runtime component missing after install: $path"
    }
}

$gstLaunch = Join-Path $runtimeRoot "bin\gst-launch-1.0.exe"
if (-not (Test-Path -LiteralPath $gstLaunch -PathType Leaf)) {
    throw "gst-launch-1.0.exe missing after runtime install"
}
& $gstLaunch --version | Select-Object -First 2
if ($LASTEXITCODE -ne 0) {
    throw "GStreamer runtime version smoke failed"
}

if ([string]::IsNullOrWhiteSpace($env:GITHUB_ENV)) {
    throw "GITHUB_ENV is unavailable"
}
"GSTREAMER_PREVIEW_RUNTIME_ROOT=$runtimeRoot" | Out-File -FilePath $env:GITHUB_ENV -Encoding utf8 -Append
"GSTREAMER_PREVIEW_INSTALLER_SHA256=$actualSha256" | Out-File -FilePath $env:GITHUB_ENV -Encoding utf8 -Append
Write-Host "GStreamer private runtime ready: $runtimeRoot"

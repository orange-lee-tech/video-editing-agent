$ErrorActionPreference = "Stop"

$archive = Join-Path $env:RUNNER_TEMP "ffmpeg-8.1-full_build.zip"
$installRoot = Join-Path $env:RUNNER_TEMP "ffmpeg-8.1"
$url = "https://github.com/GyanD/codexffmpeg/releases/download/8.1/ffmpeg-8.1-full_build.zip"
$expectedSha256 = "587B1C37DE29C5003D01CF65DA10001BAC43A58B88E61AF0FC77C61DAFF04761"

Invoke-WebRequest -Uri $url -OutFile $archive
$actualSha256 = (Get-FileHash $archive -Algorithm SHA256).Hash
if ($actualSha256 -ne $expectedSha256) {
    throw "FFmpeg archive SHA-256 mismatch: expected $expectedSha256, got $actualSha256"
}

Expand-Archive -Path $archive -DestinationPath $installRoot -Force
$ffmpeg = Get-ChildItem -Path $installRoot -Recurse -Filter ffmpeg.exe | Select-Object -First 1
if ($null -eq $ffmpeg) {
    throw "ffmpeg.exe was not found after archive extraction"
}

if ([string]::IsNullOrWhiteSpace($env:GITHUB_PATH)) {
    throw "GITHUB_PATH is unavailable"
}

$ffmpeg.Directory.FullName | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append
& $ffmpeg.FullName -version | Select-Object -First 1

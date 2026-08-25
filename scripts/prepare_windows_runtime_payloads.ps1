param([string]$PayloadRoot = "build/runtime-payloads")

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Root = Join-Path $RepoRoot $PayloadRoot
$Cache = Join-Path $Root "cache"
$FfmpegArchive = Join-Path $Cache "ffmpeg-n8.1.2-44-g7c533d0f86-win64-lgpl-shared-8.1.zip"
$FfmpegExtract = Join-Path $Root "ffmpeg-extracted"
$FfmpegOwned = Join-Path $Root "ffmpeg-owned"
$TransNet = Join-Path $Root "transnet"
$Speech = Join-Path $Root "speech"
$SpeechOwned = Join-Path $Root "speech-owned"
$SpeechModel = Join-Path $Root "models/faster-whisper-base"
$SpeechProbe = Join-Path $Root "speech-probe.wav"
$PythonStdlib = Join-Path $Root "python-stdlib"

New-Item -ItemType Directory -Force -Path $Cache,$FfmpegOwned,$TransNet,$Speech,$SpeechModel | Out-Null
$PythonRoot = uv run python -c "import sys; print(sys.base_prefix)"
if ($LASTEXITCODE -ne 0) { throw "Pinned Python runtime discovery failed" }
New-Item -ItemType Directory -Force -Path $PythonStdlib | Out-Null
robocopy (Join-Path $PythonRoot "Lib") $PythonStdlib /E /XD site-packages __pycache__ test tests `
    /XF "*.pyc" /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Pinned Python standard library staging failed" }
robocopy (Join-Path $PythonRoot "DLLs") $PythonStdlib "*.pyd" "*.dll" `
    /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Pinned Python native standard library staging failed" }
if (-not (Test-Path -LiteralPath $FfmpegArchive)) {
    Invoke-WebRequest `
        -Uri "https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2026-08-20-13-45/ffmpeg-n8.1.2-44-g7c533d0f86-win64-lgpl-shared-8.1.zip" `
        -OutFile $FfmpegArchive
}
$ArchiveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $FfmpegArchive).Hash.ToLowerInvariant()
if ($ArchiveHash -ne "d311c8c7b86e06b54588e442652f963bae165bd4d8393e73cc9ebb445b025547") {
    throw "FFmpeg archive SHA-256 mismatch"
}
if (-not (Test-Path -LiteralPath $FfmpegExtract)) {
    Expand-Archive -LiteralPath $FfmpegArchive -DestinationPath $FfmpegExtract
}
$FfmpegRoot = Get-ChildItem -LiteralPath $FfmpegExtract -Directory | Select-Object -First 1
$FfmpegBin = Join-Path $FfmpegRoot.FullName "bin"
Copy-Item -LiteralPath (Join-Path $FfmpegBin "ffmpeg.exe") -Destination $FfmpegOwned -Force
Copy-Item -LiteralPath (Join-Path $FfmpegBin "ffprobe.exe") -Destination $FfmpegOwned -Force
Get-ChildItem -LiteralPath $FfmpegBin -Filter "*.dll" | Copy-Item -Destination $FfmpegOwned -Force
Copy-Item -LiteralPath (Join-Path $FfmpegRoot.FullName "LICENSE.txt") -Destination $FfmpegOwned -Force
$Configuration = (& (Join-Path $FfmpegOwned "ffmpeg.exe") -version | Select-String "^configuration:").Line
if ($Configuration -match "--enable-(gpl|nonfree)") {
    throw "FFmpeg configuration is not LGPL-only"
}

if (-not (Test-Path -LiteralPath (Join-Path $TransNet "transnetv2_pytorch"))) {
    # The locked CPU Torch wheel lives on PyTorch's dedicated CPU index. The
    # compile input records this source, but generated requirement locks do not
    # preserve index directives, so repeat the source explicitly at install time.
    uv pip install --target $TransNet --require-hashes `
        --extra-index-url "https://download.pytorch.org/whl/cpu" `
        --index-strategy unsafe-best-match `
        -r (Join-Path $RepoRoot "packaging/requirements-transnet-windows-cpu.lock")
    if ($LASTEXITCODE -ne 0) { throw "TransNet runtime installation failed" }
}
if (-not (Test-Path -LiteralPath (Join-Path $Speech "faster_whisper"))) {
    uv pip install --target $Speech --require-hashes `
        -r (Join-Path $RepoRoot "packaging/requirements-speech-windows-cpu.lock")
    if ($LASTEXITCODE -ne 0) { throw "Speech runtime installation failed" }
}
if (-not (Test-Path -LiteralPath (Join-Path $SpeechModel "model.bin"))) {
    $PreviousPythonPath = $env:PYTHONPATH
    try {
        $env:PYTHONPATH = $Speech
        uv run python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='Systran/faster-whisper-base', revision='ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66', local_dir=r'$SpeechModel')"
        if ($LASTEXITCODE -ne 0) { throw "Pinned speech model acquisition failed" }
    }
    finally {
        $env:PYTHONPATH = $PreviousPythonPath
    }
}

# PyAV's upstream Windows wheel carries a broad FFmpeg DLL set including GPL
# codecs. Keep the exact PyAV extension modules, but replace that native set
# with the already-approved LGPL-only FFmpeg 8.1 shared payload. PyAV 18.1.0
# supports FFmpeg 8.x and the compatibility is exercised below.
New-Item -ItemType Directory -Force -Path $SpeechOwned | Out-Null
robocopy $Speech $SpeechOwned /E /XD av.libs /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Speech runtime staging failed" }
$SpeechAvLibs = Join-Path $SpeechOwned "av.libs"
New-Item -ItemType Directory -Force -Path $SpeechAvLibs | Out-Null
$AvAliases = @{
    "avcodec-62.dll" = "avcodec-62-984de33114b7fa384296817dec999c9d.dll"
    "avdevice-62.dll" = "avdevice-62-bf7a3ffbb6a4b577f24a39ea98a958d5.dll"
    "avfilter-11.dll" = "avfilter-11-aef80fc767dc77e0319469b5bdcdf998.dll"
    "avformat-62.dll" = "avformat-62-b6d6bb16ff0b7753371e2d0b285c9dc0.dll"
    "avutil-60.dll" = "avutil-60-cc1777f859dcfd98b8019bdf459e774e.dll"
    "swresample-6.dll" = "swresample-6-0158536d5c4197d7d623445553ce9472.dll"
    "swscale-9.dll" = "swscale-9-0c9886c118598c54e159ef2267ff99f3.dll"
}
foreach ($Name in $AvAliases.Keys) {
    Copy-Item -LiteralPath (Join-Path $FfmpegOwned $Name) `
        -Destination (Join-Path $SpeechAvLibs $AvAliases[$Name]) -Force
}
Get-ChildItem -LiteralPath $FfmpegOwned -Filter "*.dll" |
    Copy-Item -Destination $SpeechAvLibs -Force

if (-not (Test-Path -LiteralPath $SpeechProbe)) {
    Add-Type -AssemblyName System.Speech
    $Synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
    try {
        $Synthesizer.SetOutputToWaveFile($SpeechProbe)
        $Synthesizer.Speak("This is a deterministic speech recognition test.")
    }
    finally {
        $Synthesizer.Dispose()
    }
}
$PreviousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = $SpeechOwned
    uv run python -c "import av; source=av.open(r'$SpeechProbe'); source.close()"
    if ($LASTEXITCODE -ne 0) { throw "LGPL-only PyAV compatibility probe failed" }
}
finally {
    $env:PYTHONPATH = $PreviousPythonPath
}
foreach ($OwnedRuntime in ($PythonStdlib, $TransNet, $SpeechOwned)) {
    $ResolvedRuntime = (Resolve-Path -LiteralPath $OwnedRuntime).Path
    if (-not $ResolvedRuntime.StartsWith((Resolve-Path -LiteralPath $Root).Path)) {
        throw "Refusing to clean generated caches outside the payload root"
    }
    Get-ChildItem -LiteralPath $ResolvedRuntime -Directory -Filter "__pycache__" -Recurse |
        Remove-Item -Recurse -Force
    Get-ChildItem -LiteralPath $ResolvedRuntime -File -Filter "*.pyc" -Recurse |
        Remove-Item -Force
}
Write-Host "Windows runtime payload preparation PASSED." -ForegroundColor Green

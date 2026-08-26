param(
    [Parameter(Mandatory = $true)]
    [string]$InstallerPath,
    [string]$EvidencePath = "build/installer/installer-smoke.json"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Installer = (Resolve-Path -LiteralPath $InstallerPath).Path
$Evidence = Join-Path $RepoRoot $EvidencePath
$RunId = [Guid]::NewGuid().ToString("N")
$InstallRoot = Join-Path $env:TEMP "VideoEditingAgent-Installer-Smoke-$RunId"
$Workspace = Join-Path $env:TEMP "VideoEditingAgent-Workspace-Smoke-$RunId"

function Invoke-CheckedProcess {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList
    )
    $Process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -Wait -PassThru
    if ($Process.ExitCode -ne 0) {
        throw "Process failed with exit code $($Process.ExitCode): $FilePath"
    }
}

try {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Evidence) | Out-Null

    Invoke-CheckedProcess $Installer @(
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/SP-",
        "/DIR=$InstallRoot",
        "/TYPE=full",
        "/COMPONENTS=core,editing",
        "/TASKS=!desktopicon"
    )

    $App = Join-Path $InstallRoot "VideoEditingAgent.exe"
    if (-not (Test-Path -LiteralPath $App -PathType Leaf)) {
        throw "Installed application executable is missing"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $InstallRoot "_internal\tools\ffmpeg.exe") -PathType Leaf)) {
        throw "Editing component did not install FFmpeg"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $InstallRoot "_internal\runtimes\transnet\transnetv2_pytorch\transnetv2-pytorch-weights.pth") -PathType Leaf)) {
        throw "Editing component did not install TransNetV2 weights"
    }
    if (Test-Path -LiteralPath (Join-Path $InstallRoot "_internal\runtimes\speech")) {
        throw "Deferred 2.0 speech runtime was unexpectedly installed in 1.0 smoke"
    }
    if (Test-Path -LiteralPath (Join-Path $InstallRoot "_internal\models\faster-whisper-base")) {
        throw "Deferred 2.0 speech model was unexpectedly installed in 1.0 smoke"
    }

    $env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE = "1"
    $env:VIDEO_EDITING_AGENT_SMOKE_WORKSPACE = $Workspace
    try {
        Invoke-CheckedProcess $App @()
    }
    finally {
        Remove-Item Env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE -ErrorAction SilentlyContinue
        Remove-Item Env:VIDEO_EDITING_AGENT_SMOKE_WORKSPACE -ErrorAction SilentlyContinue
    }

    $ProjectDb = Join-Path $Workspace "project.sqlite3"
    if (-not (Test-Path -LiteralPath $ProjectDb -PathType Leaf)) {
        throw "Installed launcher smoke did not create external Workspace project.sqlite3"
    }

    $Uninstaller = Get-ChildItem -LiteralPath $InstallRoot -Filter "unins*.exe" -File |
        Select-Object -First 1
    if ($null -eq $Uninstaller) {
        throw "Installed uninstaller was not found"
    }

    Invoke-CheckedProcess $Uninstaller.FullName @(
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART"
    )

    if (-not (Test-Path -LiteralPath $ProjectDb -PathType Leaf)) {
        throw "Uninstall incorrectly removed the external Project Workspace"
    }

    $Payload = [ordered]@{
        schema = "video-editing-agent-installer-smoke/v1"
        installer = $Installer
        install_root = $InstallRoot
        workspace = $Workspace
        install = "PASS"
        core_component = "PASS"
        editing_component = "PASS"
        deferred_speech_absent = "PASS"
        launcher = "PASS"
        workspace_external = "PASS"
        uninstall = "PASS"
        workspace_preserved_after_uninstall = "PASS"
    }
    $Payload | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 $Evidence
    Write-Host "Installer smoke PASSED." -ForegroundColor Green
    Write-Host "Evidence: $Evidence" -ForegroundColor Green
}
finally {
    Remove-Item Env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE -ErrorAction SilentlyContinue
    Remove-Item Env:VIDEO_EDITING_AGENT_SMOKE_WORKSPACE -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $InstallRoot) {
        Remove-Item -LiteralPath $InstallRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path -LiteralPath $Workspace) {
        Remove-Item -LiteralPath $Workspace -Recurse -Force -ErrorAction SilentlyContinue
    }
}

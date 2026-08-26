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

function Invoke-Setup {
    param(
        [string]$Type,
        [string]$Components
    )
    Invoke-CheckedProcess $Installer @(
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/SP-",
        "/DIR=$InstallRoot",
        "/TYPE=$Type",
        "/COMPONENTS=$Components",
        "/TASKS=!desktopicon"
    )
}

function Assert-DeferredSpeechAbsent {
    foreach ($Path in @(
        (Join-Path $InstallRoot "_internal\runtimes\speech"),
        (Join-Path $InstallRoot "_internal\models\faster-whisper-base")
    )) {
        if (Test-Path -LiteralPath $Path) {
            throw "Deferred 2.0 speech payload was unexpectedly installed: $Path"
        }
    }
}

function Assert-EditingAbsent {
    if (Test-Path -LiteralPath (Join-Path $InstallRoot "_internal\tools\ffmpeg.exe")) {
        throw "Planning-only installation unexpectedly contains FFmpeg"
    }
    if (Test-Path -LiteralPath (Join-Path $InstallRoot "_internal\runtimes\transnet")) {
        throw "Planning-only installation unexpectedly contains TransNet runtime"
    }
}

function Assert-EditingPresent {
    if (-not (Test-Path -LiteralPath (Join-Path $InstallRoot "_internal\tools\ffmpeg.exe") -PathType Leaf)) {
        throw "Full installation has no FFmpeg Editing payload"
    }
    $Weights = Join-Path $InstallRoot "_internal\runtimes\transnet\transnetv2_pytorch\transnetv2-pytorch-weights.pth"
    if (-not (Test-Path -LiteralPath $Weights -PathType Leaf)) {
        throw "Full installation has no reviewed TransNetV2 weights"
    }
}

function Invoke-LauncherSmoke {
    param([string]$App)
    $env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE = "1"
    $env:VIDEO_EDITING_AGENT_SMOKE_WORKSPACE = $Workspace
    try {
        Invoke-CheckedProcess $App @()
    }
    finally {
        Remove-Item Env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE -ErrorAction SilentlyContinue
        Remove-Item Env:VIDEO_EDITING_AGENT_SMOKE_WORKSPACE -ErrorAction SilentlyContinue
    }
}

try {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Evidence) | Out-Null

    # First install the smallest ordinary-user choice. Planning-only must not silently
    # acquire the heavy Editing runtime merely because the product also supports Editing.
    Invoke-Setup -Type "planning" -Components "core"

    $App = Join-Path $InstallRoot "VideoEditingAgent.exe"
    if (-not (Test-Path -LiteralPath $App -PathType Leaf)) {
        throw "Planning-only installation has no application executable"
    }
    Assert-EditingAbsent
    Assert-DeferredSpeechAbsent
    Invoke-LauncherSmoke $App

    $ProjectDb = Join-Path $Workspace "project.sqlite3"
    if (-not (Test-Path -LiteralPath $ProjectDb -PathType Leaf)) {
        throw "Installed launcher smoke did not create external Workspace project.sqlite3"
    }

    # Re-run Setup into the same app-owned directory and expand the installation to Full.
    # This exercises the real upgrade/reconfiguration path without touching user Workspace data.
    Invoke-Setup -Type "full" -Components "core,editing"
    Assert-EditingPresent
    Assert-DeferredSpeechAbsent
    if (-not (Test-Path -LiteralPath $ProjectDb -PathType Leaf)) {
        throw "Planning-to-Full upgrade removed the external Project Workspace"
    }
    Invoke-LauncherSmoke $App

    # Same-version Full setup is the repair path. It must be idempotent for app-owned files
    # and preserve the external Workspace.
    Invoke-Setup -Type "full" -Components "core,editing"
    Assert-EditingPresent
    Assert-DeferredSpeechAbsent
    if (-not (Test-Path -LiteralPath $ProjectDb -PathType Leaf)) {
        throw "Repair removed the external Project Workspace"
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

    if (Test-Path -LiteralPath $App -PathType Leaf) {
        throw "Uninstall left the application executable installed"
    }
    if (-not (Test-Path -LiteralPath $ProjectDb -PathType Leaf)) {
        throw "Uninstall incorrectly removed the external Project Workspace"
    }

    $Payload = [ordered]@{
        schema = "video-editing-agent-installer-smoke/v2"
        installer = $Installer
        install_root = $InstallRoot
        workspace = $Workspace
        planning_only_install = "PASS"
        planning_only_editing_runtime_absent = "PASS"
        planning_only_launcher = "PASS"
        upgrade_planning_to_full = "PASS"
        full_editing_runtime = "PASS"
        full_launcher = "PASS"
        same_version_repair = "PASS"
        deferred_speech_absent = "PASS"
        workspace_external = "PASS"
        workspace_preserved_after_upgrade = "PASS"
        workspace_preserved_after_repair = "PASS"
        uninstall = "PASS"
        app_removed_after_uninstall = "PASS"
        workspace_preserved_after_uninstall = "PASS"
    }
    $Payload | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 $Evidence
    Write-Host "Installer lifecycle smoke PASSED." -ForegroundColor Green
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

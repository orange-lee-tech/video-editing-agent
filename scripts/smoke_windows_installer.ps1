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
$EvidenceRoot = Split-Path -Parent $Evidence
$SmokeLogRoot = Join-Path $EvidenceRoot "smoke-logs"
$FailureEvidence = Join-Path $EvidenceRoot "installer-smoke-failure.json"
$ProgressLog = Join-Path $EvidenceRoot "installer-smoke-progress.log"
$CurrentPhase = "initializing"

New-Item -ItemType Directory -Force -Path $EvidenceRoot, $SmokeLogRoot | Out-Null
Remove-Item -LiteralPath $FailureEvidence, $ProgressLog -Force -ErrorAction SilentlyContinue

function Set-SmokePhase {
    param([string]$Name)
    $script:CurrentPhase = $Name
    $Line = "$(Get-Date -Format o) phase=$Name"
    Write-Host $Line -ForegroundColor Cyan
    Add-Content -Encoding utf8 -LiteralPath $ProgressLog -Value $Line
}

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
        [string]$Components,
        [string]$PhaseName
    )
    $SetupLog = Join-Path $SmokeLogRoot "$PhaseName-setup.log"
    Invoke-CheckedProcess $Installer @(
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/SP-",
        "/DIR=$InstallRoot",
        "/TYPE=$Type",
        "/COMPONENTS=$Components",
        "/TASKS=!desktopicon",
        "/LOG=$SetupLog"
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
    Set-SmokePhase "planning-install"

    # First install the smallest ordinary-user choice. Planning-only must not silently
    # acquire the heavy Editing runtime merely because the product also supports Editing.
    Invoke-Setup -Type "planning" -Components "core" -PhaseName "planning"

    Set-SmokePhase "planning-assertions"
    $App = Join-Path $InstallRoot "VideoEditingAgent.exe"
    if (-not (Test-Path -LiteralPath $App -PathType Leaf)) {
        throw "Planning-only installation has no application executable"
    }
    Assert-EditingAbsent
    Assert-DeferredSpeechAbsent
    Set-SmokePhase "planning-launcher"
    Invoke-LauncherSmoke $App

    Set-SmokePhase "planning-workspace"
    $ProjectDb = Join-Path $Workspace "project.sqlite3"
    if (-not (Test-Path -LiteralPath $ProjectDb -PathType Leaf)) {
        throw "Installed launcher smoke did not create external Workspace project.sqlite3"
    }

    # Re-run Setup into the same app-owned directory and expand the installation to Full.
    # This exercises the real upgrade/reconfiguration path without touching user Workspace data.
    Set-SmokePhase "upgrade-full-install"
    Invoke-Setup -Type "full" -Components "core,editing" -PhaseName "upgrade-full"
    Set-SmokePhase "upgrade-full-assertions"
    Assert-EditingPresent
    Assert-DeferredSpeechAbsent
    if (-not (Test-Path -LiteralPath $ProjectDb -PathType Leaf)) {
        throw "Planning-to-Full upgrade removed the external Project Workspace"
    }
    Set-SmokePhase "full-launcher"
    Invoke-LauncherSmoke $App

    # Same-version Full setup is the repair path. It must be idempotent for app-owned files
    # and preserve the external Workspace.
    Set-SmokePhase "repair-full-install"
    Invoke-Setup -Type "full" -Components "core,editing" -PhaseName "repair-full"
    Set-SmokePhase "repair-full-assertions"
    Assert-EditingPresent
    Assert-DeferredSpeechAbsent
    if (-not (Test-Path -LiteralPath $ProjectDb -PathType Leaf)) {
        throw "Repair removed the external Project Workspace"
    }

    Set-SmokePhase "uninstall"
    $Uninstaller = Get-ChildItem -LiteralPath $InstallRoot -Filter "unins*.exe" -File |
        Select-Object -First 1
    if ($null -eq $Uninstaller) {
        throw "Installed uninstaller was not found"
    }

    $UninstallLog = Join-Path $SmokeLogRoot "uninstall.log"
    Invoke-CheckedProcess $Uninstaller.FullName @(
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/LOG=$UninstallLog"
    )

    Set-SmokePhase "uninstall-assertions"
    if (Test-Path -LiteralPath $App -PathType Leaf) {
        throw "Uninstall left the application executable installed"
    }
    if (-not (Test-Path -LiteralPath $ProjectDb -PathType Leaf)) {
        throw "Uninstall incorrectly removed the external Project Workspace"
    }

    Set-SmokePhase "write-success-evidence"
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
catch {
    $RootName = [System.IO.Path]::GetPathRoot($InstallRoot).TrimEnd("\").TrimEnd(":")
    $Drive = Get-PSDrive -Name $RootName -ErrorAction SilentlyContinue
    [ordered]@{
        schema = "video-editing-agent-installer-smoke-failure/v1"
        phase = $CurrentPhase
        exception_type = $_.Exception.GetType().FullName
        message = $_.Exception.Message
        installer = $Installer
        install_root = $InstallRoot
        workspace = $Workspace
        free_bytes = if ($null -ne $Drive) { $Drive.Free } else { $null }
        progress_log = $ProgressLog
        smoke_log_root = $SmokeLogRoot
    } | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 $FailureEvidence
    Write-Host "Installer lifecycle smoke FAILED at phase '$CurrentPhase'." -ForegroundColor Red
    Write-Host "Failure evidence: $FailureEvidence" -ForegroundColor Yellow
    throw
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

param(
    [string]$OutputRoot = "build/packaging",
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Output = Join-Path $RepoRoot $OutputRoot
$Dist = Join-Path $Output "dist"
$Work = Join-Path $Output "work"
$Evidence = Join-Path $Output "evidence"
$Manifest = Join-Path $RepoRoot "resources/packaging/runtime-manifest.json"

Push-Location $RepoRoot
try {
    $PythonVersion = (uv run python -c "import platform; print(platform.python_version())").Trim()
    if ($LASTEXITCODE -ne 0 -or $PythonVersion -ne "3.12.13") {
        throw "Windows packaging requires exact CPython 3.12.13; resolved '$PythonVersion'"
    }
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File `
        (Join-Path $RepoRoot "scripts/prepare_windows_runtime_payloads.ps1")
    if ($LASTEXITCODE -ne 0) { throw "Windows runtime payload preparation failed" }
    uv run python -m video_editing_agent.adapters.bootstrap.package_validation --manifest $Manifest
    if ($LASTEXITCODE -ne 0) { throw "Runtime manifest validation failed" }
    if (-not $SkipBuild) {
        uv run --group packaging pyinstaller --noconfirm --clean `
            --distpath $Dist --workpath $Work `
            packaging/video_editing_agent.spec
        if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }
    }
    $Stage = Join-Path $Dist "VideoEditingAgent"
    $GuiExecutable = Join-Path $Stage "VideoEditingAgent.exe"
    $CliExecutable = Join-Path $Stage "VideoEditingAgent-cli.exe"
    if (-not (Test-Path -LiteralPath $GuiExecutable -PathType Leaf)) {
        throw "Windowed application executable is missing from staged package"
    }
    if (-not (Test-Path -LiteralPath $CliExecutable -PathType Leaf)) {
        throw "Console diagnostics executable is missing from staged package"
    }
    New-Item -ItemType Directory -Force -Path $Evidence | Out-Null
    $SourceSha = (git rev-parse HEAD).Trim()
    uv run python -m video_editing_agent.adapters.bootstrap.package_validation `
        --manifest $Manifest --staged-root $Stage `
        --evidence (Join-Path $Evidence "package-evidence.json") --source-sha $SourceSha
    if ($LASTEXITCODE -ne 0) { throw "Static package validation failed" }

    foreach ($DeferredPath in @(
        (Join-Path $Stage "_internal\runtimes\speech"),
        (Join-Path $Stage "_internal\models\faster-whisper-base")
    )) {
        if (Test-Path -LiteralPath $DeferredPath) {
            throw "Deferred 2.0 speech payload leaked into the 1.0 staging tree: $DeferredPath"
        }
    }

    & $CliExecutable doctor |
        Set-Content -Encoding utf8 (Join-Path $Evidence "packaged-doctor.json")
    if ($LASTEXITCODE -ne 0) { throw "Packaged Doctor failed" }
    & $CliExecutable runtime-probe |
        Set-Content -Encoding utf8 (Join-Path $Evidence "packaged-runtime-probe.json")
    if ($LASTEXITCODE -ne 0) { throw "Packaged runtime probe failed" }
    $Workspace = Join-Path ([System.IO.Path]::GetTempPath()) "video-editing-agent-packaged-smoke"
    if (Test-Path -LiteralPath $Workspace) {
        Remove-Item -LiteralPath $Workspace -Recurse -Force
    }
    $env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE = "1"
    $env:VIDEO_EDITING_AGENT_SMOKE_WORKSPACE = $Workspace
    $GuiProcess = Start-Process -FilePath $GuiExecutable -Wait -PassThru
    if ($GuiProcess.ExitCode -ne 0) {
        throw "Packaged launcher smoke failed with exit code $($GuiProcess.ExitCode)"
    }
    if (-not (Test-Path (Join-Path $Workspace "project.sqlite3"))) {
        throw "External Workspace smoke did not create project.sqlite3"
    }
    if ((Resolve-Path $Workspace).Path.StartsWith((Resolve-Path $Stage).Path)) {
        throw "Packaged smoke Workspace must remain outside the install tree"
    }
    @{
        schema = "video-editing-agent-packaged-smoke/v1"
        source_git_sha = $SourceSha
        launcher = "PASS"
        gui_without_console = "PASS"
        diagnostics_cli = "PASS"
        doctor = "PASS"
        runtime_payloads = "PASS"
        shipped_components = @("core", "media-runtime", "transnet-runtime")
        deferred_speech_absent = "PASS"
        external_workspace = "PASS"
        workspace_outside_install = "PASS"
    } | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $Evidence "packaged-smoke.json")
    Write-Host "Windows 1.0 onedir candidate: $Stage" -ForegroundColor Green
    Write-Host "Evidence: $Evidence" -ForegroundColor Green
}
finally {
    Remove-Item Env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE -ErrorAction SilentlyContinue
    Remove-Item Env:VIDEO_EDITING_AGENT_SMOKE_WORKSPACE -ErrorAction SilentlyContinue
    Pop-Location
}

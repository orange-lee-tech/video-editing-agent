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
    uv run python -m video_editing_agent.adapters.bootstrap.package_validation --manifest $Manifest
    if ($LASTEXITCODE -ne 0) { throw "Runtime manifest validation failed" }
    if (-not $SkipBuild) {
        uv run --group packaging pyinstaller --noconfirm --clean `
            --distpath $Dist --workpath $Work `
            packaging/video_editing_agent.spec
        if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }
    }
    $Stage = Join-Path $Dist "VideoEditingAgent"
    New-Item -ItemType Directory -Force -Path $Evidence | Out-Null
    $SourceSha = (git rev-parse HEAD).Trim()
    uv run python -m video_editing_agent.adapters.bootstrap.package_validation `
        --manifest $Manifest --staged-root $Stage `
        --evidence (Join-Path $Evidence "package-evidence.json") --source-sha $SourceSha
    if ($LASTEXITCODE -ne 0) { throw "Static package validation failed" }
    & (Join-Path $Stage "VideoEditingAgent.exe") doctor |
        Set-Content -Encoding utf8 (Join-Path $Evidence "packaged-doctor.json")
    if ($LASTEXITCODE -ne 0) { throw "Packaged Doctor failed" }
    $Workspace = Join-Path ([System.IO.Path]::GetTempPath()) "video-editing-agent-packaged-smoke"
    $env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE = "1"
    $env:VIDEO_EDITING_AGENT_SMOKE_WORKSPACE = $Workspace
    & (Join-Path $Stage "VideoEditingAgent.exe")
    if ($LASTEXITCODE -ne 0) { throw "Packaged launcher smoke failed" }
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
        doctor = "PASS"
        external_workspace = "PASS"
        workspace_outside_install = "PASS"
    } | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $Evidence "packaged-smoke.json")
    Write-Host "Windows onedir candidate: $Stage" -ForegroundColor Green
    Write-Host "Evidence: $Evidence" -ForegroundColor Green
}
finally {
    Remove-Item Env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE -ErrorAction SilentlyContinue
    Remove-Item Env:VIDEO_EDITING_AGENT_SMOKE_WORKSPACE -ErrorAction SilentlyContinue
    Pop-Location
}

param(
    [string]$StageRoot = "build/packaging/dist/VideoEditingAgent",
    [string]$OutputRoot = "build/installer",
    [string]$AppVersion = "0.1.0",
    [string]$IsccPath = "",
    [string]$InstallerToolVersion = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Stage = Join-Path $RepoRoot $StageRoot
$Output = Join-Path $RepoRoot $OutputRoot
$InstallerScript = Join-Path $RepoRoot "packaging/windows/VideoEditingAgent.iss"

function Resolve-Iscc([string]$ExplicitPath) {
    if ($ExplicitPath) {
        if (-not (Test-Path -LiteralPath $ExplicitPath -PathType Leaf)) {
            throw "Specified Inno Setup compiler does not exist: $ExplicitPath"
        }
        return (Resolve-Path -LiteralPath $ExplicitPath).Path
    }

    $Command = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($Command) { return $Command.Source }

    $Candidates = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 7\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 7\ISCC.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 7\ISCC.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe")
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) }

    if ($Candidates.Count -gt 0) {
        return (Resolve-Path -LiteralPath $Candidates[0]).Path
    }

    throw "Inno Setup compiler ISCC.exe was not found. Install the approved Inno Setup tool or pass -IsccPath explicitly."
}

if (-not (Test-Path -LiteralPath $Stage -PathType Container)) {
    throw "Staged onedir does not exist: $Stage"
}
if (-not (Test-Path -LiteralPath (Join-Path $Stage "VideoEditingAgent.exe") -PathType Leaf)) {
    throw "Staged onedir has no VideoEditingAgent.exe: $Stage"
}
if (-not (Test-Path -LiteralPath (Join-Path $Stage "_internal\tools\ffmpeg.exe") -PathType Leaf)) {
    throw "Staged Editing runtime has no approved FFmpeg payload"
}
if (-not (Test-Path -LiteralPath (Join-Path $Stage "_internal\runtimes\transnet\transnetv2_pytorch\transnetv2-pytorch-weights.pth") -PathType Leaf)) {
    throw "Staged Editing runtime has no reviewed TransNetV2 weights"
}
if (-not (Test-Path -LiteralPath $InstallerScript -PathType Leaf)) {
    throw "Installer script is missing: $InstallerScript"
}
if ($InstallerToolVersion -and $InstallerToolVersion -notmatch '^\d+\.\d+\.\d+$') {
    throw "InstallerToolVersion must be an exact semantic release version"
}

$Iscc = Resolve-Iscc $IsccPath
New-Item -ItemType Directory -Force -Path $Output | Out-Null
$SourceSha = (git -C $RepoRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or -not $SourceSha) {
    throw "Could not resolve source Git SHA"
}

$ResolvedStage = (Resolve-Path -LiteralPath $Stage).Path
$ResolvedOutput = (Resolve-Path -LiteralPath $Output).Path
$CompilerFileVersion = (Get-Item -LiteralPath $Iscc).VersionInfo.FileVersion
$CompilerVersion = if ($InstallerToolVersion) {
    $InstallerToolVersion
}
elseif ($CompilerFileVersion -and $CompilerFileVersion -ne "0.0.0.0") {
    $CompilerFileVersion
}
else {
    "unreported"
}

Write-Host "Building guided Windows installer" -ForegroundColor Cyan
Write-Host "  source:   $SourceSha"
Write-Host "  stage:    $ResolvedStage"
Write-Host "  output:   $ResolvedOutput"
Write-Host "  compiler: $Iscc (release $CompilerVersion; file resource $CompilerFileVersion)"

& $Iscc `
    "/DStageRoot=$ResolvedStage" `
    "/DOutputDir=$ResolvedOutput" `
    "/DAppVersion=$AppVersion" `
    "/DSourceSha=$SourceSha" `
    $InstallerScript
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup compilation failed with exit code $LASTEXITCODE"
}

$Installer = Join-Path $ResolvedOutput "VideoEditingAgent-Setup-$AppVersion.exe"
if (-not (Test-Path -LiteralPath $Installer -PathType Leaf)) {
    throw "Expected Setup.exe was not produced: $Installer"
}

$Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Installer).Hash.ToLowerInvariant()
$Evidence = [ordered]@{
    schema = "video-editing-agent-installer-evidence/v1"
    source_git_sha = $SourceSha
    application_version = $AppVersion
    installer_tool = "Inno Setup"
    installer_tool_version = $CompilerVersion
    installer_tool_file_version = $CompilerFileVersion
    staged_root = $ResolvedStage
    installer_path = $Installer
    installer_sha256 = $Hash
    default_components = @("core", "editing")
    deferred_not_shipped_by_installer = @("speech-runtime", "speech-model", "translated-subtitles", "cross-language-tts")
}
$EvidencePath = Join-Path $ResolvedOutput "installer-evidence.json"
$Evidence | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 $EvidencePath

Write-Host "Setup.exe: $Installer" -ForegroundColor Green
Write-Host "SHA-256:  $Hash" -ForegroundColor Green
Write-Host "Evidence: $EvidencePath" -ForegroundColor Green

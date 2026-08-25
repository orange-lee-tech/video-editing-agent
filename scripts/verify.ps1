param(
    [switch]$SkipSync,
    [switch]$SkipLauncherSmoke,
    [switch]$RequireClean
)

$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    Write-Host ""
    Write-Host "> $FilePath $($Arguments -join ' ')" -ForegroundColor Cyan
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $RepoRoot

try {
    if (-not $SkipSync) {
        Invoke-Checked "uv" @("sync", "--frozen")
    }

    # Keep the local gate aligned with repository governance before spending time on the full suite.
    Invoke-Checked "uv" @("run", "python", "tools/maintenance/repo_doctor.py")
    Invoke-Checked "uv" @("run", "ruff", "format", "--check", ".")
    Invoke-Checked "uv" @("run", "ruff", "check", ".")
    Invoke-Checked "uv" @("run", "mypy", "src")
    Invoke-Checked "uv" @("run", "pytest")
    Invoke-Checked "uv" @("run", "lint-imports")
    Invoke-Checked "uv" @("build")
    Invoke-Checked "git" @("diff", "--check")

    if (-not $SkipLauncherSmoke) {
        Write-Host ""
        Write-Host "> launcher smoke" -ForegroundColor Cyan
        $previousSmoke = $env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE
        try {
            $env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE = "1"
            Invoke-Checked "uv" @(
                "run",
                "python",
                "-c",
                "from video_editing_agent.adapters.product.tkinter_app import launch; raise SystemExit(launch())"
            )
        }
        finally {
            if ($null -eq $previousSmoke) {
                Remove-Item Env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE -ErrorAction SilentlyContinue
            }
            else {
                $env:VIDEO_EDITING_AGENT_LAUNCHER_SMOKE = $previousSmoke
            }
        }
    }
    else {
        Write-Host ""
        Write-Host "Launcher smoke SKIPPED explicitly; this is not sufficient for GUI acceptance." -ForegroundColor Yellow
    }

    $workingTree = git status --porcelain
    if ($LASTEXITCODE -ne 0) {
        throw "git status failed with exit code $LASTEXITCODE"
    }
    if ($workingTree) {
        Write-Host ""
        Write-Host "Working tree contains changes (expected during pre-commit verification):" -ForegroundColor Yellow
        $workingTree | ForEach-Object { Write-Host $_ }
        if ($RequireClean) {
            throw "Verification was invoked with -RequireClean but the working tree is not clean"
        }
    }

    Write-Host ""
    Write-Host "Repository verification PASSED." -ForegroundColor Green
}
finally {
    Pop-Location
}

param(
    [switch]$SkipSync
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

    Invoke-Checked "uv" @("run", "ruff", "format", "--check", ".")
    Invoke-Checked "uv" @("run", "ruff", "check", ".")
    Invoke-Checked "uv" @("run", "mypy", "src")
    Invoke-Checked "uv" @("run", "pytest")
    Invoke-Checked "uv" @("run", "lint-imports")
    Invoke-Checked "uv" @("build")
    Invoke-Checked "git" @("diff", "--check")

    $workingTree = git status --porcelain
    if ($LASTEXITCODE -ne 0) {
        throw "git status failed with exit code $LASTEXITCODE"
    }
    if ($workingTree) {
        Write-Host "" 
        Write-Host "Working tree is not clean:" -ForegroundColor Yellow
        $workingTree | ForEach-Object { Write-Host $_ }
        throw "Verification requires a clean working tree"
    }

    Write-Host "" 
    Write-Host "Repository verification PASSED." -ForegroundColor Green
}
finally {
    Pop-Location
}

param(
    [ValidateSet("preflight", "doctor", "foreman", "handoff", "verify")]
    [string]$Task = "doctor",
    [string]$Output,
    [ValidateSet("architecture", "location", "quality", "git", "external", "high-risk")]
    [string]$Trigger,
    [switch]$SkipSync,
    [switch]$SkipLauncherSmoke,
    [switch]$RequireClean
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

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

function Invoke-Foreman {
    $args = @("run", "python", "tools/maintenance/foreman.py")
    if ($Trigger) {
        $args += @("--trigger", $Trigger)
    }
    Invoke-Checked "uv" $args
}

Push-Location $RepoRoot
try {
    switch ($Task) {
        "preflight" {
            Invoke-Checked "uv" @("run", "python", "tools/maintenance/repo_doctor.py")
            Invoke-Foreman
            Write-Host ""
            Write-Host "Preflight PASSED. Use .private/codex_brief.md as the compact Codex entry." -ForegroundColor Green
        }
        "doctor" {
            Invoke-Checked "uv" @("run", "python", "tools/maintenance/repo_doctor.py")
        }
        "handoff" {
            $args = @("run", "python", "tools/maintenance/handoff_snapshot.py")
            if ($Output) {
                $args += @("--output", $Output)
            }
            Invoke-Checked "uv" $args
        }
        "foreman" {
            Invoke-Foreman
        }
        "verify" {
            $verifyArgs = @{}
            if ($SkipSync) {
                $verifyArgs["SkipSync"] = $true
            }
            if ($SkipLauncherSmoke) {
                $verifyArgs["SkipLauncherSmoke"] = $true
            }
            if ($RequireClean) {
                $verifyArgs["RequireClean"] = $true
            }
            & "$PSScriptRoot\verify.ps1" @verifyArgs
        }
    }
}
finally {
    Pop-Location
}

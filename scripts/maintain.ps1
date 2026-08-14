param(
    [ValidateSet("doctor", "foreman", "handoff", "verify")]
    [string]$Task = "doctor",
    [string]$Output,
    [switch]$SkipSync
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

Push-Location $RepoRoot
try {
    switch ($Task) {
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
            Invoke-Checked "uv" @("run", "python", "tools/maintenance/foreman.py")
        }
        "verify" {
            if ($SkipSync) {
                & "$PSScriptRoot\verify.ps1" -SkipSync
            }
            else {
                & "$PSScriptRoot\verify.ps1"
            }
        }
    }
}
finally {
    Pop-Location
}

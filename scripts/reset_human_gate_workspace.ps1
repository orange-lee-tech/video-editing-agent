param(
    [string]$Workspace = (Join-Path $env:TEMP "VideoEditingAgent-HumanGate"),
    [switch]$AllowCustomPath
)

$ErrorActionPreference = "Stop"

$Resolved = [System.IO.Path]::GetFullPath($Workspace)
$TempRoot = [System.IO.Path]::GetFullPath($env:TEMP).TrimEnd("\") + "\"

if (-not $AllowCustomPath -and -not $Resolved.StartsWith(
    $TempRoot,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    throw "Refusing to clean a non-TEMP path without -AllowCustomPath: $Resolved"
}

$Leaf = Split-Path -Leaf $Resolved
if ([string]::IsNullOrWhiteSpace($Leaf) -or $Leaf -in @(".", "..")) {
    throw "Refusing to clean an unsafe workspace path: $Resolved"
}

if (Test-Path -LiteralPath $Resolved) {
    Remove-Item -LiteralPath $Resolved -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $Resolved | Out-Null

Write-Host "Clean Human Gate workspace ready: $Resolved" -ForegroundColor Green
Write-Output $Resolved

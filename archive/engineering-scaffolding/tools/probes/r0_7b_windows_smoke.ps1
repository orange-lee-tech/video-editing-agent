param(
  [Parameter(Mandatory = $true)][string]$ProjectRoot,
  [string]$MediaPath
)

$ErrorActionPreference = "Stop"
uv run video-editing-agent --project $ProjectRoot project init
uv run video-editing-agent --project $ProjectRoot brief create `
  --title "Windows smoke" `
  --objective "Verify local application startup" `
  --audience "developer" `
  --platform "local" `
  --core-message "Offline workspace is operational"

if (-not (Get-Command ffprobe -ErrorAction SilentlyContinue)) {
  Write-Output '{"asset_ingest":"skipped","reason":"ffprobe unavailable"}'
  uv run video-editing-agent --project $ProjectRoot project status
  exit 0
}
if (-not $MediaPath) {
  Write-Output '{"asset_ingest":"skipped","reason":"pass -MediaPath for local ingest smoke"}'
  uv run video-editing-agent --project $ProjectRoot project status
  exit 0
}
if (-not (Test-Path -LiteralPath $MediaPath -PathType Leaf)) {
  throw "MediaPath must identify an existing local file: $MediaPath"
}

$ingestPath = Join-Path $ProjectRoot "smoke-asset.json"
$ingest = @{
  path = (Resolve-Path -LiteralPath $MediaPath).Path
  origin = "imported_local"
  provenance = @{ origin_type = "imported_local" }
  usage_role = "editable_visual_footage"
} | ConvertTo-Json -Depth 4
[System.IO.File]::WriteAllText($ingestPath, $ingest, [System.Text.UTF8Encoding]::new($false))
$assetJson = uv run video-editing-agent --project $ProjectRoot asset ingest --json $ingestPath
$assetJson
$asset = $assetJson | ConvertFrom-Json
uv run video-editing-agent --project $ProjectRoot asset show $asset.envelope.id $asset.envelope.revision
uv run video-editing-agent --project $ProjectRoot project status
uv run video-editing-agent --project $ProjectRoot index rebuild
uv run video-editing-agent --project $ProjectRoot index query smoke

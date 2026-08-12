param([Parameter(Mandatory = $true)][string]$ProjectRoot)

$ErrorActionPreference = "Stop"
uv run video-editing-agent --project $ProjectRoot project init
uv run video-editing-agent --project $ProjectRoot brief create `
  --title "Windows smoke" `
  --objective "Verify local application startup" `
  --audience "developer" `
  --platform "local" `
  --core-message "Offline workspace is operational"
uv run video-editing-agent --project $ProjectRoot project status

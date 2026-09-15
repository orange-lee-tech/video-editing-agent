param(
    [Parameter(Mandatory = $true)]
    [string]$PfxPath,
    [Parameter(Mandatory = $true)]
    [string]$PfxPassword,
    [Parameter(Mandatory = $true)]
    [string[]]$File,
    [string]$TimestampUrl = "http://timestamp.digicert.com",
    [string]$EvidencePath = ""
)

$ErrorActionPreference = "Stop"

function Resolve-SignTool {
    $command = Get-Command signtool.exe -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }

    $roots = @(
        (Join-Path ${env:ProgramFiles(x86)} "Windows Kits\10\bin"),
        (Join-Path $env:ProgramFiles "Windows Kits\10\bin")
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Container) }

    foreach ($root in $roots) {
        $candidate = Get-ChildItem -LiteralPath $root -Filter signtool.exe -Recurse -File `
            -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -match '\\x64\\signtool\.exe$' } |
            Sort-Object FullName -Descending |
            Select-Object -First 1
        if ($candidate) { return $candidate.FullName }
    }
    throw "signtool.exe was not found in the Windows SDK"
}

function Get-CertificateSha256([System.Security.Cryptography.X509Certificates.X509Certificate2]$Certificate) {
    $bytes = $Certificate.Export(
        [System.Security.Cryptography.X509Certificates.X509ContentType]::Cert
    )
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $digest = $sha.ComputeHash($bytes)
    }
    finally {
        $sha.Dispose()
    }
    return (($digest | ForEach-Object { $_.ToString("x2") }) -join "")
}

if (-not (Test-Path -LiteralPath $PfxPath -PathType Leaf)) {
    throw "Code-signing PFX is missing: $PfxPath"
}
if ([string]::IsNullOrWhiteSpace($PfxPassword)) {
    throw "Code-signing PFX password is missing"
}
if (-not $File -or $File.Count -lt 1) {
    throw "At least one artifact must be supplied for signing"
}

$signtool = Resolve-SignTool
$evidence = @()
foreach ($item in $File) {
    $resolved = (Resolve-Path -LiteralPath $item -ErrorAction Stop).Path
    & $signtool sign /fd SHA256 /td SHA256 /tr $TimestampUrl /f $PfxPath /p $PfxPassword $resolved
    if ($LASTEXITCODE -ne 0) {
        throw "signtool failed for $resolved with exit code $LASTEXITCODE"
    }

    $signature = Get-AuthenticodeSignature -LiteralPath $resolved
    if ($signature.Status -ne [System.Management.Automation.SignatureStatus]::Valid) {
        throw "Authenticode verification failed for $resolved: $($signature.Status)"
    }
    if ($null -eq $signature.SignerCertificate) {
        throw "Authenticode signer certificate is missing for $resolved"
    }
    $certificateSha256 = Get-CertificateSha256 $signature.SignerCertificate
    $evidence += [ordered]@{
        path = $resolved
        file_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolved).Hash.ToLowerInvariant()
        authenticode_status = [string]$signature.Status
        signer_subject = $signature.SignerCertificate.Subject
        signer_certificate_sha256 = $certificateSha256
        timestamp_status = if ($signature.TimeStamperCertificate) { "present" } else { "missing" }
    }
}

if ($EvidencePath) {
    $directory = Split-Path -Parent $EvidencePath
    if ($directory) {
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
    }
    [ordered]@{
        schema = "video-editing-agent-authenticode-evidence/v1"
        signtool = $signtool
        timestamp_url = $TimestampUrl
        artifacts = $evidence
    } | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 $EvidencePath
}

$evidence | ConvertTo-Json -Depth 4

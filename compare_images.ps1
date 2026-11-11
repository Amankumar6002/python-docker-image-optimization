param(
    [string]$BaselineImage = "python-image-optimization:baseline",
    [string]$OptimizedImage = "python-image-optimization:optimized",
    [string]$OutputPath = "reports/image-comparison.json"
)

$ErrorActionPreference = "Stop"

$images = @(
    $BaselineImage,
    $OptimizedImage
)

$sizes = @{}

foreach ($image in $images) {
    $sizeText = & docker image inspect $image --format "{{.Size}}" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker image '$image' was not found. Build it before running this comparison."
    }
    if ($sizeText -notmatch '^\d+$') {
        throw "Could not read a valid byte size for Docker image '$image'."
    }

    $sizes[$image] = [long]$sizeText
}

$baselineBytes = $sizes[$images[0]]
$optimizedBytes = $sizes[$images[1]]
$savedBytes = $baselineBytes - $optimizedBytes
$reduction = if ($baselineBytes -gt 0) {
    ($savedBytes / [double]$baselineBytes) * 100
} else {
    0
}
$timestamp = [DateTime]::UtcNow.ToString("o", [cultureinfo]::InvariantCulture)
$report = [ordered]@{
    generated_at = $timestamp
    measurement_method = "docker image inspect .Size"
    baseline_image = $images[0]
    optimized_image = $images[1]
    baseline_size_bytes = $baselineBytes
    optimized_size_bytes = $optimizedBytes
    baseline_size_mb = [math]::Round($baselineBytes / 1000000, 2)
    baseline_size_mib = [math]::Round($baselineBytes / 1048576, 2)
    optimized_size_mb = [math]::Round($optimizedBytes / 1000000, 2)
    optimized_size_mib = [math]::Round($optimizedBytes / 1048576, 2)
    saved_bytes = $savedBytes
    saved_mb = [math]::Round($savedBytes / 1000000, 2)
    saved_mib = [math]::Round($savedBytes / 1048576, 2)
    reduction_percent = [math]::Round($reduction, 2)
}

$reportDirectory = Split-Path -Parent $OutputPath
if ($reportDirectory) {
    New-Item -ItemType Directory -Force -Path $reportDirectory | Out-Null
}
$report | ConvertTo-Json | Set-Content -Path $OutputPath -Encoding utf8

$results = @(
    [pscustomobject]@{
        Image = "Baseline"
        Tag = $images[0]
        Bytes = $baselineBytes.ToString("N0", [cultureinfo]::InvariantCulture)
        MB = ($baselineBytes / 1000000).ToString("N2", [cultureinfo]::InvariantCulture)
        MiB = ($baselineBytes / 1048576).ToString("N2", [cultureinfo]::InvariantCulture)
    }
    [pscustomobject]@{
        Image = "Optimized"
        Tag = $images[1]
        Bytes = $optimizedBytes.ToString("N0", [cultureinfo]::InvariantCulture)
        MB = ($optimizedBytes / 1000000).ToString("N2", [cultureinfo]::InvariantCulture)
        MiB = ($optimizedBytes / 1048576).ToString("N2", [cultureinfo]::InvariantCulture)
    }
)

Write-Output "PYTHON DOCKER IMAGE OPTIMIZATION RESULTS"
Write-Output ""
$results | Format-Table -AutoSize
Write-Output ("Space saved: {0} bytes ({1} MB / {2} MiB)" -f `
    $savedBytes.ToString("N0", [cultureinfo]::InvariantCulture), `
    ($savedBytes / 1000000).ToString("N2", [cultureinfo]::InvariantCulture), `
    ($savedBytes / 1048576).ToString("N2", [cultureinfo]::InvariantCulture))
Write-Output ("Percentage reduction: {0}%" -f $reduction.ToString("N2", [cultureinfo]::InvariantCulture))
Write-Output "Sizes are Docker image inspect byte totals, not compressed registry sizes or docker images disk usage."
Write-Output ("JSON report written to: {0}" -f (Resolve-Path $OutputPath))

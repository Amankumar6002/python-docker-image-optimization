param(
    [string]$BaselineImage = "python-image-optimization:baseline",
    [string]$OptimizedImage = "python-image-optimization:optimized"
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

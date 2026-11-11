$ErrorActionPreference = "Stop"

$namespace = "docker-optimization"
$requiredVariables = @("K8S_DB_USERNAME", "K8S_DB_PASSWORD")
foreach ($variable in $requiredVariables) {
    if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($variable))) {
        throw "Set $variable in the current PowerShell process before deployment. No credentials were read from or written to files."
    }
}

$context = & kubectl config current-context 2>$null
if ($LASTEXITCODE -ne 0 -or $context -ne "docker-desktop") {
    throw "Refusing deployment: select the Docker Desktop context 'docker-desktop' after creating its Kubernetes cluster."
}

& kubectl cluster-info
if ($LASTEXITCODE -ne 0) {
    throw "The Docker Desktop Kubernetes API is not reachable."
}

$nodesJson = & kubectl get nodes -o json
if ($LASTEXITCODE -ne 0) {
    throw "Could not read Kubernetes nodes."
}
$nodes = $nodesJson | ConvertFrom-Json
$nodeList = @($nodes.items)
$readyNodes = @($nodeList | Where-Object {
        @($_.status.conditions | Where-Object { $_.type -eq "Ready" -and $_.status -eq "True" }).Count -gt 0
    })
if ($nodeList.Count -lt 1 -or $readyNodes.Count -ne $nodeList.Count) {
    throw "At least one Kubernetes node must be Ready before deployment."
}

$storageClassesJson = & kubectl get storageclasses.storage.k8s.io -o json
if ($LASTEXITCODE -ne 0) {
    throw "Could not inspect Kubernetes storage classes."
}
$storageClasses = $storageClassesJson | ConvertFrom-Json
if ($storageClasses.items.Count -lt 1) {
    throw "No storage class is available for the PostgreSQL PersistentVolumeClaim."
}
$defaultStorageClasses = @($storageClasses.items | Where-Object {
        $_.metadata.annotations.'storageclass.kubernetes.io/is-default-class' -eq "true"
    })
if ($defaultStorageClasses.Count -lt 1) {
    throw "No default StorageClass is available for the PostgreSQL PersistentVolumeClaim."
}

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$reportPath = Join-Path $projectRoot "reports\image-comparison.json"
if (-not (Test-Path -LiteralPath $reportPath -PathType Leaf)) {
    throw "The Docker image measurement report is missing. Build both images and run compare_images.ps1 first."
}

$image = "python-image-optimization:optimized"
& docker image inspect $image --format "{{.Id}}" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Local optimized image '$image' is missing. Build it with Dockerfile before deploying."
}

$runtimeVersions = @($nodes.items | ForEach-Object { $_.status.nodeInfo.containerRuntimeVersion } | Select-Object -Unique)
Write-Output ("Docker Desktop Kubernetes node runtime(s): {0}" -f ($runtimeVersions -join ", "))
Write-Output ("Using local optimized image: {0}" -f $image)
Write-Output "Image pull policy is Never; the cluster must have the local image available, and no registry fallback will occur."

& kubectl apply -f (Join-Path $PSScriptRoot "namespace.yaml")
if ($LASTEXITCODE -ne 0) {
    throw "Could not create the Kubernetes namespace."
}

$secretData = @{
    apiVersion = "v1"
    kind = "Secret"
    metadata = @{
        name = "db-credentials"
        namespace = $namespace
    }
    type = "Opaque"
    data = @{
        username = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($env:K8S_DB_USERNAME))
        password = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($env:K8S_DB_PASSWORD))
    }
} | ConvertTo-Json -Depth 6 -Compress

$secretData | & kubectl apply -f -
if ($LASTEXITCODE -ne 0) {
    throw "Could not create the local Kubernetes database Secret."
}

$reportConfig = & kubectl create configmap image-comparison `
    --namespace $namespace `
    "--from-file=image-comparison.json=$reportPath" `
    --dry-run=client `
    -o yaml
if ($LASTEXITCODE -ne 0) {
    throw "Could not create the dashboard measurement ConfigMap."
}
$reportConfig | & kubectl apply -f -
if ($LASTEXITCODE -ne 0) {
    throw "Could not apply the dashboard measurement ConfigMap."
}

& kubectl apply -f $PSScriptRoot
if ($LASTEXITCODE -ne 0) {
    throw "Could not apply the Kubernetes application resources."
}

& kubectl rollout status deployment/postgres --namespace $namespace --timeout=180s
if ($LASTEXITCODE -ne 0) {
    throw "PostgreSQL did not become ready. Inspect its pod events and logs."
}
& kubectl rollout status deployment/python-optimization --namespace $namespace --timeout=180s
if ($LASTEXITCODE -ne 0) {
    throw "The Flask deployment did not become ready. Inspect pod events; an image availability issue may require loading the local Docker image into the selected cluster runtime."
}

& kubectl get deployments,pods,services,pvc --namespace $namespace
if ($LASTEXITCODE -ne 0) {
    throw "Could not verify the deployed resources."
}

Write-Output ""
Write-Output "Dashboard URL: http://localhost:8080 (start port-forward with: kubectl port-forward -n docker-optimization service/python-optimization 8080:80)"

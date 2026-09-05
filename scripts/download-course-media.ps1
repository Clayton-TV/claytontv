param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$OutputDirectory,
    [string]$Manifest = (Join-Path $PSScriptRoot "course-downloads.tsv")
)

$ErrorActionPreference = "Stop"
$curl = Get-Command curl.exe -ErrorAction SilentlyContinue
if ($null -eq $curl) { throw "curl.exe is required." }
if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) { throw "Manifest not found: $Manifest" }

$stateDirectory = Join-Path $OutputDirectory ".course-downloads-state"
New-Item -ItemType Directory -Force -Path $stateDirectory | Out-Null
$report = Join-Path $OutputDirectory "download-report.tsv"
"status`tpath`turl`tmessage" | Set-Content -LiteralPath $report
$failures = $false
$retries = if ($env:CURL_RETRIES) { $env:CURL_RETRIES } else { "3" }

Import-Csv -LiteralPath $Manifest -Delimiter "`t" | ForEach-Object {
    $target = Join-Path $OutputDirectory $_.path
    $partial = "$target.part"
    $marker = Join-Path $stateDirectory "$($_.path).url"
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target), (Split-Path -Parent $marker) | Out-Null

    if (Test-Path -LiteralPath $target -PathType Leaf) {
        if ((Test-Path -LiteralPath $marker -PathType Leaf) -and ((Get-Content -LiteralPath $marker -Raw).TrimEnd("`r", "`n") -eq $_.url)) {
            "skipped`t$($_.path)`t$($_.url)`tpreviously completed" | Add-Content -LiteralPath $report
            return
        }
        "failed`t$($_.path)`t$($_.url)`ttarget exists without a matching completion record" | Add-Content -LiteralPath $report
        Write-Error "Refusing to overwrite $target"
        $failures = $true
        return
    }

    & $curl.Source --fail --location --continue-at - --retry $retries --retry-delay 2 --retry-all-errors --connect-timeout 30 --output $partial $_.url
    if ($LASTEXITCODE -eq 0) {
        Move-Item -LiteralPath $partial -Destination $target
        $_.url | Set-Content -LiteralPath $marker -NoNewline
        "completed`t$($_.path)`t$($_.url)`t" | Add-Content -LiteralPath $report
    } else {
        "failed`t$($_.path)`t$($_.url)`tcurl failed; retained .part file for resume" | Add-Content -LiteralPath $report
        Write-Error "Failed: $($_.url)"
        $failures = $true
    }
}

if ($failures) {
    Write-Error "One or more downloads failed. See $report"
    exit 1
}

Write-Output "Completed. Report: $report"

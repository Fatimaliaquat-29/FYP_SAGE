<#
.SYNOPSIS
  Upload ONLY the 298 round6_heldout frames (+ current labels) to a private Roboflow project.

.DESCRIPTION
  Refuses to run unless ALL of these hold:
    -ConfirmConsent   you agree to upload these 298 frames (identifiable people) to Roboflow
    -ConfirmOptOut    you have turned on the workspace's data-use opt-out and set the project Private
    $env:ROBOFLOW_API_KEY is set in this session (it is never printed)
    you retype "<workspace>/<project>" exactly at the interactive prompt
  Uploads only .\upload_heldout (next to this script). Nothing else.

  CLI syntax verified against `roboflow --help` / `roboflow image upload --help`
  (roboflow 1.7.1, saved in cli_help.txt): -w is a GLOBAL option, placed before
  the subcommand; the key is read from $ROBOFLOW_API_KEY by the CLI itself.

.EXAMPLE
  .\upload_to_roboflow.ps1 -Workspace my-workspace -Project sage-heldout-retag -ConfirmConsent -ConfirmOptOut
#>
param(
    [Parameter(Mandatory = $true)][string]$Workspace,
    [Parameter(Mandatory = $true)][string]$Project,
    [switch]$ConfirmConsent,
    [switch]$ConfirmOptOut
)

$ErrorActionPreference = 'Stop'
$RoboflowExe = 'D:\FYP\PROJECT FILES\_tools\venv_roboflow\Scripts\roboflow.exe'
$Folder = Join-Path $PSScriptRoot 'upload_heldout'
$BatchName = 'round6-heldout-retag-original-labels'
$ExpectedCount = 298

function Refuse($msg) { Write-Host "REFUSED: $msg" -ForegroundColor Red; exit 1 }

if (-not $ConfirmConsent) { Refuse "pass -ConfirmConsent to confirm you consent to uploading these frames." }
if (-not $ConfirmOptOut)  { Refuse "pass -ConfirmOptOut to confirm the project is Private and the data-use opt-out is ON." }
if ([string]::IsNullOrWhiteSpace($env:ROBOFLOW_API_KEY)) {
    Refuse "`$env:ROBOFLOW_API_KEY is not set in this session. See ROBOFLOW_SETUP.md step 2."
}
if ($Workspace -notmatch '^[A-Za-z0-9._-]+$' -or $Project -notmatch '^[A-Za-z0-9._-]+$') {
    Refuse "workspace/project must be plain IDs (letters, digits, . _ -)."
}
if (-not (Test-Path -LiteralPath $RoboflowExe)) { Refuse "roboflow CLI not found at $RoboflowExe" }
if (-not [Environment]::UserInteractive -or [Console]::IsInputRedirected) {
    Refuse "must be run from an interactive console (the destination must be retyped by hand)."
}

# ---- what will be uploaded ----
if (-not (Test-Path -LiteralPath $Folder)) { Refuse "staging folder not found: $Folder" }
$images = @(Get-ChildItem -LiteralPath (Join-Path $Folder 'train\images') -File -Filter *.jpg)
$labels = @(Get-ChildItem -LiteralPath (Join-Path $Folder 'train\labels') -File -Filter *.txt)
$yaml   = Join-Path $Folder 'data.yaml'
$other  = @(Get-ChildItem -LiteralPath $Folder -File -Recurse | Where-Object {
              $_.FullName -ne $yaml -and $_.DirectoryName -notlike '*\train\images' -and $_.DirectoryName -notlike '*\train\labels' })
if ($images.Count -ne $ExpectedCount) { Refuse "expected $ExpectedCount images, found $($images.Count)." }
if ($labels.Count -ne $ExpectedCount) { Refuse "expected $ExpectedCount label files, found $($labels.Count)." }
if (-not (Test-Path -LiteralPath $yaml)) { Refuse "data.yaml missing in $Folder" }
if ($other.Count -gt 0) { Refuse "unexpected extra files in staging folder: $($other.Name -join ', ')" }

$dest = "$Workspace/$Project"
Write-Host ""
Write-Host "About to upload:" -ForegroundColor Yellow
Write-Host "  folder      : $Folder"
Write-Host "  images      : $($images.Count)   labels: $($labels.Count)   + data.yaml (13 classes)"
Write-Host "  destination : workspace '$Workspace', project '$Project'"
Write-Host "  batch name  : $BatchName"
Write-Host "  API key     : set (not shown)"
Write-Host ""
$typed = Read-Host "Retype the destination exactly as  $dest  to continue (anything else aborts)"
if ($typed -cne $dest) { Refuse "destination not confirmed (typed '$typed'). Nothing uploaded." }

Write-Host "Uploading..." -ForegroundColor Yellow
& $RoboflowExe -w $Workspace image upload $Folder -p $Project -b $BatchName -r 3
$rc = $LASTEXITCODE
if ($rc -ne 0) { Write-Host "roboflow exited with code $rc" -ForegroundColor Red; exit $rc }
Write-Host "Done. Check the project in the browser: it should show $ExpectedCount images with boxes." -ForegroundColor Green

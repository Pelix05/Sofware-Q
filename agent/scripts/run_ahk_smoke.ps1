param(
    [string]$Workspace = ".",
    [string]$ExePath = ""
)

$ErrorActionPreference = "Stop"

# Resolve workspace absolute path
$ws = Resolve-Path $Workspace

# Default exe path if not provided
if (-not $ExePath -or $ExePath -eq "") {
    $ExePath = Join-Path $ws "cpp_project\diagramscene_ultima\release\diagramscene.exe"
}

$ahk = "C:\Program Files\AutoHotkey\AutoHotkeyU64.exe"
$script = "D:\flowchart_test\diagramscene_autohotkey_smoke.ahk"
$log = Join-Path $ws "ahk_result.txt"

Write-Host "Workspace: $ws"
Write-Host "ExePath:   $ExePath"
Write-Host "LogPath:   $log"
Write-Host "Script:    $script"

if (-not (Test-Path $ahk)) {
    Write-Error "AutoHotkey not found at $ahk"
    exit 1
}
if (-not (Test-Path $script)) {
    Write-Error "Script not found at $script"
    exit 1
}

$env:AHK_EXE_PATH = $ExePath
$env:AHK_LOG_PATH = $log

& $ahk $script
$code = $LASTEXITCODE
Write-Host "AHK exit code: $code"
if (Test-Path $log) {
    Write-Host "AHK log:"
    Get-Content $log
}
exit $code

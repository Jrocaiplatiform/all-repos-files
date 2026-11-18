param(
    [Parameter(Mandatory=$true)]
    [string]$NewVersion
)

Set-Location "C:\J-roc-AI"

# 1. Update package.json
npm version $NewVersion --no-git-tag-version

# 2. Update src-tauri/tauri.conf.json
$tauriConfPath = "C:\J-roc-AI\src-tauri\tauri.conf.json"
$tauriConf = Get-Content $tauriConfPath -Raw | ConvertFrom-Json
$tauriConf.version = $NewVersion
$tauriConf | ConvertTo-Json -Depth 10 | Set-Content $tauriConfPath

# 3. Update src-tauri/Cargo.toml
$cargoPath = "C:\J-roc-AI\src-tauri\Cargo.toml"
(Get-Content $cargoPath) -replace '^version = ".*"', "version = `"$NewVersion`"" | Set-Content $cargoPath

Write-Host "Updated project version to $NewVersion across package.json, tauri.conf.json, and Cargo.toml" -ForegroundColor Green

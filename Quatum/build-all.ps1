$ErrorActionPreference = "Stop"
Set-Location "C:\J-roc-AI"

Write-Host "=== [1/4] Verifying Environment & Paths ===" -ForegroundColor Cyan
$env:Path += ";$env:USERPROFILE\.cargo\bin"

if (-not $env:ANDROID_HOME) {
    $env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
}
if (-not $env:JAVA_HOME -and (Test-Path "C:\Program Files\Android\Android Studio\jbr")) {
    $env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
}
if (-not $env:NDK_HOME -and (Test-Path "$env:ANDROID_HOME\ndk")) {
    $latestNdk = Get-ChildItem -Path "$env:ANDROID_HOME\ndk" -Directory | Sort-Object Name -Descending | Select-Object -First 1
    if ($latestNdk) { $env:NDK_HOME = $latestNdk.FullName }
}

Write-Host "ANDROID_HOME : $env:ANDROID_HOME"
Write-Host "JAVA_HOME    : $env:JAVA_HOME"
Write-Host "NDK_HOME     : $env:NDK_HOME"

# Create clean output folder
$releaseDir = "C:\J-roc-AI\releases"
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

Write-Host "`n=== [2/4] Version 2.0: Android Init & Build ===" -ForegroundColor Cyan
if (-not (Test-Path "C:\J-roc-AI\src-tauri\gen\android")) {
    Write-Host "Initializing Tauri Android project..."
    npx tauri android init
}
Write-Host "Building Android APK & AAB..."
npx tauri android build --apk --aab

Write-Host "`n=== [3/4] Version 3.0: Windows Desktop Production Build ===" -ForegroundColor Cyan
npx tauri build

Write-Host "`n=== [4/4] Version 4.0: Collecting All Release Artifacts ===" -ForegroundColor Cyan
# Copy Android APKs/AABs
$androidOut = "C:\J-roc-AI\src-tauri\gen\android\app\build\outputs"
if (Test-Path $androidOut) {
    Get-ChildItem -Path $androidOut -Include *.apk,*.aab -Recurse | Copy-Item -Destination $releaseDir -Force
}

# Copy Windows Installers (.msi, .exe)
$winOut = "C:\J-roc-AI\src-tauri\target\release\bundle"
if (Test-Path $winOut) {
    Get-ChildItem -Path $winOut -Include *.msi,*.exe -Recurse | Copy-Item -Destination $releaseDir -Force
}

Write-Host "`n=== BUILD COMPLETE ===" -ForegroundColor Green
Write-Host "All compiled installers and APKs are saved in: $releaseDir"
Get-ChildItem -Path $releaseDir | Select-Object Name, Length, LastWriteTime

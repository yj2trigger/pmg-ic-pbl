# ── Windows 빌드 스크립트 ──────────────────────────────────────────
# 실행 방법: project/ 디렉토리에서  .\build_windows.ps1
# 결과물:    dist\kiosk\kiosk.exe  +  dist\kiosk\data\

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$DistDir     = Join-Path $ProjectRoot "dist\kiosk"
$DataSrc     = Join-Path $ProjectRoot "src\app\data"
$DataDest    = Join-Path $DistDir     "data"

# ── 1. 의존성 설치 ──────────────────────────────────────────────────
Write-Host "=== 의존성 설치 ===" -ForegroundColor Cyan
pip install pyinstaller pyqt6 pygame-ce edge-tts

# ── 2. 빌드 ────────────────────────────────────────────────────────
Write-Host "`n=== PyInstaller 빌드 ===" -ForegroundColor Cyan
Set-Location $ProjectRoot
pyinstaller kiosk.spec --clean --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host "빌드 실패" -ForegroundColor Red
    exit 1
}

# ── 3. 초기 데이터 파일 복사 ────────────────────────────────────────
# data/ 폴더는 exe 옆에 분리 배치 (런타임에 JSON 파일을 읽고 써야 하므로)
Write-Host "`n=== 데이터 파일 복사 ===" -ForegroundColor Cyan
if (-not (Test-Path $DataDest)) {
    New-Item -ItemType Directory -Path $DataDest | Out-Null
}

# products.json, ingredients.json, options.json 은 필수 초기 데이터
$required = @("products.json", "ingredients.json", "options.json")
foreach ($f in $required) {
    $src = Join-Path $DataSrc $f
    if (Test-Path $src) {
        Copy-Item $src $DataDest -Force
        Write-Host "  복사: $f"
    } else {
        Write-Host "  경고: $f 없음 (첫 실행 전 수동 생성 필요)" -ForegroundColor Yellow
    }
}
# change_reserve.json, admin_config.json 은 없으면 앱이 기본값으로 자동 생성

Write-Host "`n=== 빌드 완료 ===" -ForegroundColor Green
Write-Host "실행 파일 : $DistDir\kiosk.exe"
Write-Host "데이터 폴더: $DataDest"
Write-Host ""
Write-Host "배포 시 dist\kiosk\ 폴더 전체를 전달하세요." -ForegroundColor Yellow

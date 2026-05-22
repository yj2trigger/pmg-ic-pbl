# ── Windows 빌드 스크립트 ──────────────────────────────────────────
# 실행 방법: 프로젝트 루트(project/)에서 .\build_windows.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot

Write-Host "=== 의존성 설치 ===" -ForegroundColor Cyan
pip install pyinstaller pyqt6

Write-Host "`n=== PyInstaller 빌드 시작 ===" -ForegroundColor Cyan
Set-Location $ProjectRoot
pyinstaller kiosk.spec --clean --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host "빌드 실패" -ForegroundColor Red
    exit 1
}

# 실행 파일 옆에 빈 data 폴더 생성 (첫 실행 시 자동 초기화됨)
$DataDest = Join-Path $ProjectRoot "dist\data"
if (-not (Test-Path $DataDest)) {
    New-Item -ItemType Directory -Path $DataDest | Out-Null
}

Write-Host "`n=== 빌드 완료 ===" -ForegroundColor Green
Write-Host "실행 파일: dist\kiosk.exe"
Write-Host "데이터 폴더: dist\data\"

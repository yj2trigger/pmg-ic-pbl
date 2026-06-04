# ── Windows 빌드 스크립트 ──────────────────────────────────────────
# 실행 방법: project/ 디렉토리에서  .\build_windows.ps1
# 결과물:    dist\kiosk.exe  (단일 파일)
#
# 초기 데이터(products/ingredients/options)는 exe 내부에 번들됨.
# 첫 실행 시 %AppData%\EDK\data\ 에 자동 복사 → 이후 그곳에서 읽고 씀.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot

# ── 1. 의존성 설치 ──────────────────────────────────────────────────
Write-Host "=== 의존성 설치 ===" -ForegroundColor Cyan
pip install pyinstaller pyqt6 pygame-ce edge-tts

# ── 2. 빌드 ────────────────────────────────────────────────────────
Write-Host "`n=== PyInstaller 빌드 (--onefile) ===" -ForegroundColor Cyan
Set-Location $ProjectRoot
pyinstaller kiosk.spec --clean --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host "빌드 실패" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== 빌드 완료 ===" -ForegroundColor Green
Write-Host "실행 파일: dist\kiosk.exe"
Write-Host ""
Write-Host "kiosk.exe 파일 하나만 전달하면 됩니다." -ForegroundColor Yellow
Write-Host "첫 실행 시 %AppData%\EDK\data\ 에 데이터가 자동 생성됩니다." -ForegroundColor Cyan

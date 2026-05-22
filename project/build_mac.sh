#!/bin/bash
# ── Mac 빌드 스크립트 ────────────────────────────────────────────
# 실행 방법: 프로젝트 루트(project/)에서 bash build_mac.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== 의존성 설치 ==="
pip3 install pyinstaller pyqt6

echo ""
echo "=== PyInstaller 빌드 시작 ==="
cd "$PROJECT_ROOT"
pyinstaller kiosk.spec --clean --noconfirm

# 실행 파일 옆에 빈 data 폴더 생성 (첫 실행 시 자동 초기화됨)
DATA_DEST="$PROJECT_ROOT/dist/kiosk.app/Contents/MacOS/data"
mkdir -p "$DATA_DEST"

echo ""
echo "=== 빌드 완료 ==="
echo "실행 파일: dist/kiosk.app"
echo "데이터 폴더: dist/kiosk.app/Contents/MacOS/data/"
echo ""
echo "※ Mac에서 '개발자를 확인할 수 없음' 경고가 뜨면:"
echo "  시스템 환경설정 > 보안 및 개인정보 보호 > 확인 없이 열기"
echo "  또는: xattr -cr dist/kiosk.app"

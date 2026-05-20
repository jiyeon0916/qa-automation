@echo off
chcp 65001 > nul
echo ================================
echo  Weverse Automation Test Runner
echo ================================

REM 가상환경 없으면 생성
if not exist ".venv" (
    echo [1/4] 가상환경 생성 중...
    python -m venv .venv
)

REM 가상환경 활성화
call .venv\Scripts\activate.bat

REM 의존성 설치
echo [2/4] 패키지 설치 중...
pip install -r requirements.txt --quiet

REM Playwright 브라우저 설치
echo [3/4] Playwright Chromium 설치 중...
playwright install chromium

REM reports 폴더 생성
if not exist "reports" mkdir reports

REM 실행 옵션 파싱
echo [4/4] 테스트 실행...
echo.

if "%1"=="1" (
    echo [케이스 1] 회원가입 + 로그인 + WID 추출
    pytest tests/test_01_signup_login.py -v -s
) else if "%1"=="2" (
    echo [케이스 2] 커뮤니티 + 포스트 CRUD
    pytest tests/test_02_community_post_crud.py -v -s
) else (
    echo [전체] 케이스 1 + 2 순서대로 실행
    pytest tests/ -v -s
)

echo.
echo 테스트 완료. 결과: reports\report.html
pause

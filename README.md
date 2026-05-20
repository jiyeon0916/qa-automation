# Weverse QA Automation — Playwright POM

위버스(weverse.io) 회원가입 / 로그인 / 커뮤니티 / 포스트 CRUD 자동화 테스트 프로젝트입니다.

---

## 프로젝트 구조

```
qa-automation/
├── pages/                              # Page Object Model
│   ├── base_page.py                    # 공통 베이스 클래스
│   ├── auth/
│   │   ├── login_page.py               # 로그인 + WID 추출
│   │   └── signup_page.py              # 회원가입
│   ├── community/
│   │   ├── community_list_page.py      # 커뮤니티 목록 / 가입
│   │   └── community_profile_page.py   # 내 커뮤니티 프로필
│   └── post/
│       ├── post_create_page.py         # 포스트 작성 / 수정
│       └── post_detail_page.py         # 포스트 삭제 / 확인
├── tests/
│   ├── conftest.py                     # 브라우저 픽스처 / WID 네트워크 인터셉터
│   ├── test_01_signup_login.py         # 케이스 1: 회원가입 → 로그인 → WID
│   └── test_02_community_post_crud.py  # 케이스 2: 커뮤니티 + 포스트 CRUD
├── utils/
│   ├── config.py                       # 환경변수 로드
│   └── test_data.py                    # 공유 데이터 객체
├── assets/
│   ├── test_image.jpg                  # ⚠️ 직접 추가 필요
│   └── test_video.mp4                  # ⚠️ 직접 추가 필요
├── .env
├── .env.example
├── pytest.ini
└── requirements.txt
```

---

## 사전 준비

### 1. Python 설치 확인

Python **3.10 이상**이 필요합니다.

```powershell
python --version
```

설치되어 있지 않다면 [python.org](https://www.python.org/downloads/) 에서 다운로드하세요.
설치 시 **"Add Python to PATH"** 옵션을 반드시 체크합니다.

---

### 2. 가상환경 생성 및 활성화

```powershell
# 프로젝트 루트에서 실행
python -m venv .venv

# 활성화 (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 활성화 (Windows CMD)
.venv\Scripts\activate.bat

# 활성화 (macOS / Linux)
source .venv/bin/activate
```

활성화되면 터미널 프롬프트 앞에 `(.venv)` 가 표시됩니다.

> **PowerShell 실행 정책 오류가 발생하는 경우**
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

---

### 3. 패키지 설치

```powershell
pip install -r requirements.txt
playwright install chromium
```

---

### 4. 환경변수 설정

`.env.example`을 복사해 `.env` 파일을 만들고 값을 채웁니다.

```powershell
copy .env.example .env
```

`.env` 파일:

```env
TEST_EMAIL=your@email.com      # 실제 수신 가능한 이메일 (필수)
TEST_PASSWORD=YourPassword1!   # 테스트 비밀번호 (필수)

WEVERSE_URL=https://weverse.io
HEADLESS=false
SLOW_MO=100
TARGET_COMMUNITY=AKMU
```

| 변수 | 설명 | 필수 |
|---|---|---|
| `TEST_EMAIL` | 위버스 가입/로그인에 사용할 이메일 | 필수 |
| `TEST_PASSWORD` | 테스트 계정 비밀번호 | 필수 |
| `TARGET_COMMUNITY` | 가입할 커뮤니티 이름 (기본: AKMU) | 선택 |
| `HEADLESS` | 헤드리스 모드 여부 (기본: false) | 선택 |
| `SLOW_MO` | 동작 간 딜레이 ms (기본: 100) | 선택 |

---

### 5. 테스트 에셋 추가

포스트 CRUD 테스트에 사용할 파일을 `assets/` 폴더에 추가합니다.

```
assets/test_image.jpg    # 첨부 이미지 (유해 이미지 불가)
assets/test_video.mp4      # 수정 시 첨부 영상 (유해 영상 불가)
```

---

## 실행 방법

### 전체 실행

```powershell
pytest
```

### 케이스별 실행

```powershell
# 케이스 1: 회원가입 → 로그인 → WID 추출
pytest tests/test_01_signup_login.py -v

# 케이스 2: 커뮤니티 가입 → 포스트 CRUD
pytest tests/test_02_community_post_crud.py -v
```

### 마커별 실행

```powershell
pytest -m signup      # 회원가입
pytest -m login       # 로그인 + WID
pytest -m community   # 커뮤니티
pytest -m post        # 포스트 CRUD
```

---

## 테스트 케이스 목록

| TC | 설명 | 파일 |
|---|---|---|
| TC-01 | 위버스 회원가입 (OTP 수동 입력) | test_01 |
| TC-02 | 로그인 | test_01 |
| TC-03 | WID 추출 및 출력 (ID / PW / WID) | test_01 |
| TC-04 | 케이스 1 계정으로 로그인 | test_02 |
| TC-05 | 커뮤니티 검색 및 가입 | test_02 |
| TC-06 | 커뮤니티 프로필 진입 | test_02 |
| TC-07 | 포스트 생성 (텍스트 + 이미지) | test_02 |
| TC-08 | 포스트 등록 확인 | test_02 |
| TC-09 | 포스트 수정 (텍스트 변경 + 이미지 → 영상 교체) | test_02 |
| TC-10 | 포스트 삭제 | test_02 |
| TC-11 | 빈 피드 메시지 확인 | test_02 |

---

## 회원가입 유의사항

- **임시 메일 서비스(`@teml.net` 등)는 위버스 정책에 의해 차단됩니다.** 반드시 실제 수신 가능한 이메일을 사용하세요.
- 가입 시 인증코드 발송 후 터미널에서 입력 대기 상태가 됩니다. 브라우저에서 직접 인증코드를 입력한 뒤 터미널에서 Enter를 누르면 이어서 진행됩니다.
- 이미 가입된 이메일로 실행하면 `test_signup`은 자동으로 SKIP 처리되고 로그인 단계부터 이어집니다.

---

## 보고서

테스트 실행 후 `reports/` 폴더에서 결과를 확인할 수 있습니다.

```powershell
# 실행 후 HTML 보고서 열기
start reports/report.html
```

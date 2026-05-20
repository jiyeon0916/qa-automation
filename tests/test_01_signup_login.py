"""
케이스 1 – 위버스 회원가입 + 로그인 + WID 추출
==============================================
테스트 순서
  1. .env의 TEST_EMAIL / TEST_PASSWORD 로 회원가입 (OTP 수동 입력)
  2. 로그인
  3. WID 추출 (localStorage → Cookie → 네트워크 인터셉트 순)
  4. 결과 출력: ID / PW / WID
"""

import pytest
from pages.auth.signup_page import SignupPage, AlreadyRegisteredError
from pages.auth.login_page import LoginPage
from utils.config import Config
from utils import test_data


# ------------------------------------------------------------------ #
#  픽스처                                                               #
# ------------------------------------------------------------------ #
@pytest.fixture(scope="module")
def credentials():
    assert Config.TEST_EMAIL,    ".env에 TEST_EMAIL을 설정하세요."
    assert Config.TEST_PASSWORD, ".env에 TEST_PASSWORD를 설정하세요."
    test_data.account.email    = Config.TEST_EMAIL
    test_data.account.password = Config.TEST_PASSWORD
    return Config.TEST_EMAIL, Config.TEST_PASSWORD


# ------------------------------------------------------------------ #
#  TC-01 회원가입                                                        #
# ------------------------------------------------------------------ #
@pytest.mark.signup
def test_signup(page, credentials):
    """위버스 신규 계정을 생성합니다. OTP는 수동으로 입력합니다."""
    email, password = credentials
    signup_page = SignupPage(page)
    try:
        signup_page.signup(email, password)
    except AlreadyRegisteredError:
        pytest.skip(f"이미 가입된 계정입니다. 로그인 테스트로 이어갑니다. ({email})")
    assert signup_page.is_signup_complete(), "회원가입이 완료되지 않았습니다."
    print(f"\n[회원가입 완료] ID: {email} / PW: {password}")


# ------------------------------------------------------------------ #
#  TC-02 로그인                                                          #
# ------------------------------------------------------------------ #
@pytest.mark.login
def test_login(page, credentials):
    """생성한 계정으로 위버스에 로그인합니다."""
    email, password = credentials
    login_page = LoginPage(page)
    login_page.login(email, password)
    login_page.screenshot("tc01_after_login")
    assert login_page.is_logged_in(), "로그인 상태가 확인되지 않습니다."
    print(f"\n[로그인 완료] ID: {email}")


# ------------------------------------------------------------------ #
#  TC-03 WID 추출                                                        #
# ------------------------------------------------------------------ #
@pytest.mark.login
def test_extract_wid(page, account_data):
    """로그인 후 WID 값을 추출합니다."""
    login_page = LoginPage(page)

    # 1차: localStorage / sessionStorage / Cookie
    wid = login_page.extract_wid()

    # 2차: 네트워크 인터셉트 결과 (conftest의 on_response 핸들러)
    if not wid:
        wid = test_data.account.wid

    # 3차: API 직접 호출
    if not wid:
        wid = _fetch_wid_via_api(page)

    if wid:
        account_data.wid       = str(wid)
        test_data.account.wid  = str(wid)

    print("\n" + "=" * 50)
    print(f"  ID  : {account_data.email}")
    print(f"  PW  : {account_data.password}")
    print(f"  WID : {account_data.wid or '미추출 (수동 확인 필요)'}")
    print("=" * 50)

    if not account_data.wid:
        pytest.xfail(
            "WID를 자동으로 추출하지 못했습니다. "
            "위버스 API 응답 구조를 확인하여 _fetch_wid_via_api()를 업데이트하세요."
        )


def _fetch_wid_via_api(page) -> str:
    import json

    api_endpoints = [
        "https://global.apis.naver.com/weverse/wevweb/v1/users/me",
        "https://global.apis.naver.com/weverse/wevweb/v2/users/me",
        "https://weversewebapi.weverse.io/wapi/v1/users/me",
    ]

    for endpoint in api_endpoints:
        try:
            resp = page.request.get(endpoint)
            if resp.ok:
                data = resp.json()
                wid = (
                    data.get("wid")
                    or data.get("data", {}).get("wid")
                    or data.get("memberId")
                    or data.get("data", {}).get("memberId")
                )
                if wid:
                    return str(wid)
        except Exception:
            continue
    return ""

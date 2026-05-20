"""
pytest 전역 픽스처.
pytest-playwright 내장 픽스처를 활용하고 WID 네트워크 인터셉트를 추가합니다.

실행 전 .env에 TEST_EMAIL / TEST_PASSWORD를 반드시 설정하세요.
"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, Browser, BrowserContext

from utils.config import Config
from utils import test_data

Path("reports").mkdir(exist_ok=True)


# ------------------------------------------------------------------ #
#  pytest-playwright 옵션 오버라이드                                     #
# ------------------------------------------------------------------ #
def pytest_configure(config):
    """pytest-playwright 기본 옵션을 .env 값으로 덮어씁니다."""
    config.option.__dict__.setdefault("headed", not Config.HEADLESS)
    config.option.__dict__.setdefault("slowmo", Config.SLOW_MO)


# ------------------------------------------------------------------ #
#  브라우저 컨텍스트 (session 스코프)                                    #
# ------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def browser_context_args():
    return {
        "viewport": None,
        "locale": "ko-KR",
        "timezone_id": "Asia/Seoul",
    }


@pytest.fixture(scope="session")
def browser_type_launch_args():
    return {
        "headless": Config.HEADLESS,
        "slow_mo": Config.SLOW_MO,
        "args": ["--start-maximized", "--window-size=1920,1080"],
    }


# ------------------------------------------------------------------ #
#  context / page – module 스코프 (파일 단위로 탭 유지)                  #
# ------------------------------------------------------------------ #
@pytest.fixture(scope="module")
def context(browser: Browser, browser_context_args: dict):
    ctx = browser.new_context(**browser_context_args)
    yield ctx
    ctx.close()


@pytest.fixture(scope="module")
def page(context: BrowserContext):
    p = context.new_page()
    _attach_wid_interceptor(p)
    yield p
    p.close()


# ------------------------------------------------------------------ #
#  WID 네트워크 인터셉트                                                 #
# ------------------------------------------------------------------ #
def _attach_wid_interceptor(page: Page) -> None:
    def on_response(response):
        if test_data.account.wid:
            return
        try:
            if not re.search(r"/api/|/member|/users/me", response.url):
                return
            if response.status != 200:
                return
            body = response.json()
            wid = _find_wid(body)
            if wid:
                test_data.account.wid = str(wid)
        except Exception:
            pass

    page.on("response", on_response)


def _find_wid(body, depth: int = 0):
    if depth > 5:
        return None
    if isinstance(body, dict):
        for k, v in body.items():
            if k.lower() in ("wid", "memberid", "weversememberid", "userid"):
                return v
            found = _find_wid(v, depth + 1)
            if found is not None:
                return found
    elif isinstance(body, list):
        for item in body:
            found = _find_wid(item, depth + 1)
            if found is not None:
                return found
    return None


# ------------------------------------------------------------------ #
#  공유 데이터 픽스처                                                    #
# ------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def account_data():
    return test_data.account


@pytest.fixture(scope="session")
def post_data():
    return test_data.post

"""위버스 로그인 페이지 POM.

실제 로그인 플로우:
  weverse.io
    → button.button-_--secondary1 클릭
    → account.weverse.io/ko/login (소셜/이메일 선택)
    → button.button_button__lgTgI (이메일로 로그인) 클릭
    → account.weverse.io/ko/login/credential (이메일+비밀번호 입력)
    → 로그인 제출
"""

import base64
import json
from playwright.sync_api import Page
from pages.base_page import BasePage


class LoginPage(BasePage):
    # ------------------------------------------------------------------ #
    #  Selectors                                                            #
    # ------------------------------------------------------------------ #
    # 1단계: weverse.io 헤더 로그인 버튼 (secondary1 = 텍스트형)
    BTN_LOGIN_HEADER = "button.button-_--secondary1"

    # 2단계: account.weverse.io/ko/login — 이메일 선택 버튼 (첫 번째)
    BTN_EMAIL_LOGIN = "button.button_button__lgTgI"

    # 3단계: /ko/login/credential — 이메일+비밀번호 폼
    INPUT_EMAIL    = "input[placeholder='your@email.com'], input[type='email']"
    INPUT_PASSWORD = "input[type='password']"
    BTN_SUBMIT     = "button[class*='AuthLoginCredentialWidgetUi_button_logi'], button.button_button__lgTgI"

    # 로그인 완료 판단 (weverse.io 로 복귀 후 프로필 영역)
    TEXT_LOGGED_IN = (
        "img[alt*='profile'], [data-testid='user-avatar'], "
        ".UserProfileImage, a[href*='/profile'], "
        "button[class*='profile'], [class*='UserMenu']"
    )

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ------------------------------------------------------------------ #
    #  Actions                                                              #
    # ------------------------------------------------------------------ #
    def go_to_login(self) -> None:
        self.navigate()
        # 1단계: 헤더 로그인 버튼
        self.wait_and_click(self.BTN_LOGIN_HEADER)
        self.wait_for_url_contains("account.weverse.io")
        self.page.wait_for_timeout(1500)
        # 2단계: 이메일로 로그인 선택
        self.wait_and_click(self.BTN_EMAIL_LOGIN)
        self.wait_for_url_contains("credential")
        self.page.wait_for_timeout(1000)

    def fill_credentials(self, email: str, password: str) -> None:
        self.wait_and_fill(self.INPUT_EMAIL, email)
        self.wait_and_fill(self.INPUT_PASSWORD, password)

    def submit_login(self) -> None:
        self.wait_and_click(self.BTN_SUBMIT)
        self.page.wait_for_timeout(3000)
        # OTP 화면이 나타나면 수동 입력 대기 (GitHub 방식 유지)
        self._handle_otp()

    def _handle_otp(self) -> None:
        """인증코드 입력 화면이 감지되면 사용자가 직접 입력할 때까지 대기합니다."""
        otp_indicators = (
            "input[maxlength='6'], "
            "input[class*='verification'], "
            ":has-text('인증코드'), "
            ":has-text('verification code')"
        )
        if self.page.locator(otp_indicators).count() > 0:
            print("\n[로그인] 인증코드 입력 화면 감지됨")
            input("이메일에서 인증코드 확인 후 브라우저에 입력하고 Enter를 누르세요: ")
            self.page.wait_for_timeout(2000)

        # 확인 버튼 팝업 처리
        confirm_btn = self.page.get_by_role("button", name="확인", exact=True)
        if confirm_btn.count() > 0:
            try:
                confirm_btn.first.click(timeout=3000)
            except Exception:
                pass

        # weverse.io 로 리다이렉트 될 때까지 대기
        self.page.wait_for_function(
            "() => !window.location.href.includes('account.')",
            timeout=30_000
        )
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(2000)

    def login(self, email: str, password: str) -> None:
        self.go_to_login()
        self.fill_credentials(email, password)
        self.screenshot("login_form_filled")
        self.submit_login()
        self.screenshot("login_complete")

    def is_logged_in(self) -> bool:
        return (
            "weverse.io" in self.page.url
            and "account." not in self.page.url
        )

    # ------------------------------------------------------------------ #
    #  WID 추출                                                             #
    # ------------------------------------------------------------------ #
    def extract_wid(self) -> str:
        """we2_access_token 쿠키의 JWT sub 필드에서 WID를 추출합니다."""
        token = self.get_cookie("we2_access_token")
        if token:
            return self._decode_jwt_sub(token)
        return ""

    def _decode_jwt_sub(self, token: str) -> str:
        try:
            payload = token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            decoded = json.loads(base64.b64decode(payload))
            return decoded.get("sub", "")
        except Exception:
            return ""

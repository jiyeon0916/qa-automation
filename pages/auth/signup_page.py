"""위버스 회원가입 페이지 POM.

실제 가입 플로우:
  weverse.io
    → button.button-_--secondary1 (로그인 버튼)
    → account.weverse.io/ko/login
    → button[class*=AuthEntranceWidgeUI_login_button] (회원가입)
    → account.weverse.io/ko/signup
    → button.button_button__lgTgI (이메일로 가입하기)
    → 이메일 입력 → 인증코드 받기
    → [수동] 이메일에서 인증코드 입력 후 Enter
    → 비밀번호 입력 → 다음
    → 약관 동의 → 가입하기
"""

from playwright.sync_api import Page
from pages.base_page import BasePage


class AlreadyRegisteredError(Exception):
    pass


class SignupPage(BasePage):
    # ------------------------------------------------------------------ #
    #  Selectors                                                            #
    # ------------------------------------------------------------------ #
    BTN_LOGIN_HEADER  = "button.button-_--secondary1"
    BTN_JOIN          = "button[class*='AuthEntranceWidgeUI_login_button']"
    BTN_EMAIL_SIGNUP  = "button.button_button__lgTgI"

    INPUT_EMAIL       = "input[placeholder='your@email.com']"
    BTN_SEND_CODE     = "button:has-text('인증코드 받기')"

    INPUT_PASSWORD    = "input[type='password']"
    BTN_NEXT          = "button[role='button']:has-text('다음'), button:has-text('다음')"

    CHECKBOX_AREA     = ".checkbox_icon_area__eXl5v"
    BTN_SUBMIT        = "button:has-text('가입하기')"
    BTN_CONFIRM       = "button:has-text('확인')"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ------------------------------------------------------------------ #
    #  Actions                                                              #
    # ------------------------------------------------------------------ #
    def go_to_signup(self) -> None:
        self.navigate()
        self.wait_and_click(self.BTN_LOGIN_HEADER)
        self.wait_for_url_contains("account.weverse.io")
        self.page.wait_for_timeout(1500)
        self.wait_and_click(self.BTN_JOIN)
        self.wait_for_url_contains("signup")
        self.page.wait_for_timeout(1500)
        self.wait_and_click(self.BTN_EMAIL_SIGNUP)
        self.wait_for_url_contains("credential")
        self.page.wait_for_timeout(1000)

    def request_verification_code(self, email: str) -> None:
        """이메일 입력 후 인증코드를 발송하고 수동 입력을 대기합니다."""
        self.page.get_by_placeholder("your@email.com").fill(email)
        self.page.get_by_text("인증코드 받기").click()
        self.page.wait_for_timeout(1500)

        # 이미 가입된 이메일 팝업 감지
        if self.page.get_by_text("이미 가입한", exact=False).count() > 0:
            self.page.get_by_role("button", name="네").click()
            raise AlreadyRegisteredError(email)

        print("\n[회원가입] 인증코드가 발송되었습니다.")
        input("이메일에서 인증코드를 확인하고 브라우저에 입력한 뒤 Enter를 누르세요: ")
        self.page.wait_for_timeout(1000)

    def fill_password(self, password: str) -> None:
        self.page.get_by_placeholder("비밀번호 입력").first.fill(password)
        self.page.get_by_placeholder("비밀번호 입력").nth(1).fill(password)

    def click_next(self) -> None:
        self.page.get_by_role("button", name="다음").click()
        self.page.wait_for_timeout(1500)

    def agree_and_submit(self) -> None:
        """약관 체크박스를 순서대로 클릭하고 가입하기를 제출합니다."""
        submit_btn = self.page.get_by_role("button", name="가입하기")
        checkboxes = self.page.locator(self.CHECKBOX_AREA)

        for i in range(checkboxes.count()):
            if submit_btn.is_enabled():
                break
            cb = checkboxes.nth(i)
            cb.scroll_into_view_if_needed()
            cb.click(force=True)

        submit_btn.wait_for(state="visible")
        submit_btn.click()

        confirm_btn = self.page.get_by_role("button", name="확인")
        confirm_btn.wait_for(state="visible")
        confirm_btn.click()

    # ------------------------------------------------------------------ #
    #  복합 플로우                                                           #
    # ------------------------------------------------------------------ #
    def signup(self, email: str, password: str) -> None:
        """회원가입 전체 플로우를 실행합니다. OTP는 수동으로 입력합니다."""
        self.go_to_signup()
        self.request_verification_code(email)
        self.screenshot("tc01_signup_form")
        self.fill_password(password)
        self.click_next()
        self.agree_and_submit()
        self.screenshot("tc01_signup_complete")

    def is_signup_complete(self) -> bool:
        return (
            self.page.locator("[class*='complete'], [class*='success']").count() > 0
            or ("weverse.io" in self.page.url and "account." not in self.page.url)
        )

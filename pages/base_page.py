"""모든 Page Object의 공통 베이스 클래스."""

from playwright.sync_api import Page
from utils.config import Config


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.page.set_default_timeout(Config.DEFAULT_TIMEOUT)

    # ------------------------------------------------------------------ #
    #  Navigation                                                           #
    # ------------------------------------------------------------------ #
    def navigate(self, path: str = "") -> None:
        url = f"{Config.WEVERSE_URL}{path}"
        self.page.goto(url, timeout=Config.NAVIGATION_TIMEOUT, wait_until="domcontentloaded")
        self.page.wait_for_timeout(2000)

    # ------------------------------------------------------------------ #
    #  Element helpers — 항상 .first 사용하여 strict mode 오류 방지            #
    # ------------------------------------------------------------------ #
    def wait_and_click(self, selector: str, timeout: int = None) -> None:
        locator = self.page.locator(selector).first
        locator.wait_for(state="visible", timeout=timeout or Config.DEFAULT_TIMEOUT)
        locator.click()

    def wait_and_fill(self, selector: str, value: str) -> None:
        locator = self.page.locator(selector).first
        locator.wait_for(state="visible")
        locator.fill(value)

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).first.inner_text()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).first.is_visible()

    def wait_for_url_contains(self, keyword: str, timeout: int = None) -> None:
        self.page.wait_for_url(
            f"**{keyword}**", timeout=timeout or Config.NAVIGATION_TIMEOUT
        )

    # ------------------------------------------------------------------ #
    #  JavaScript 유틸                                                      #
    # ------------------------------------------------------------------ #
    def get_local_storage(self, key: str) -> str | None:
        return self.page.evaluate(f"window.localStorage.getItem('{key}')")

    def get_all_local_storage(self) -> dict:
        return self.page.evaluate(
            "Object.fromEntries(Object.entries(window.localStorage))"
        )

    def get_cookie(self, name: str) -> str | None:
        cookies = self.page.context.cookies()
        for c in cookies:
            if c["name"] == name:
                return c["value"]
        return None

    # ------------------------------------------------------------------ #
    #  스크린샷                                                              #
    # ------------------------------------------------------------------ #
    def screenshot(self, name: str) -> None:
        self.page.screenshot(path=f"reports/{name}.png", full_page=True)

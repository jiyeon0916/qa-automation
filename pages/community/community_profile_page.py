"""위버스 커뮤니티 프로필(내 프로필) 페이지 POM."""

from playwright.sync_api import Page
from pages.base_page import BasePage


class CommunityProfilePage(BasePage):
    # 프로필 진입 링크
    # GitHub 검증값: trailing slash 포함
    BTN_MY_PROFILE = (
        "a[href*='/profile/'], "
        "[data-testid='my-profile'], "
        ".MyProfileButton, "
        "a:has-text('내 프로필'), "
        "a:has-text('My Profile')"
    )
    # 커뮤니티 내 프로필 탭
    TAB_MY_FEED = "a:has-text('내 게시물'), a:has-text('My Posts'), [role='tab']:has-text('게시물')"

    # 포스트 없을 때 메시지
    TEXT_NO_POST = (
        ":has-text('아직 작성한 포스트가 없습니다'), "
        ":has-text('게시물이 없'), "
        ":has-text('No posts'), "
        ":has-text('작성한 게시물이 없'), "
        ".EmptyFeed, "
        "[data-testid='empty-feed']"
    )

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def go_to_my_profile(self) -> None:
        """홈에서 내 프로필 페이지로 이동합니다."""
        self.wait_and_click(self.BTN_MY_PROFILE)
        self.page.wait_for_load_state("networkidle")
        self.screenshot("my_profile_page")

    def go_to_my_feed_tab(self) -> None:
        """내 게시물 탭으로 이동합니다."""
        tab = self.page.locator(self.TAB_MY_FEED).first
        if tab.is_visible():
            tab.click()
            self.page.wait_for_load_state("networkidle")

    def get_no_post_message(self) -> str:
        """게시물이 없을 때 노출되는 메시지 텍스트를 반환합니다."""
        locator = self.page.get_by_text("아직 작성한 포스트가 없습니다", exact=False)
        locator.wait_for(state="visible", timeout=15_000)
        return locator.inner_text()

    def has_no_post_message(self) -> bool:
        return self.page.get_by_text("아직 작성한 포스트가 없습니다", exact=False).count() > 0

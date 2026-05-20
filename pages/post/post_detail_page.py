"""포스트 상세 / 삭제 페이지 POM."""

from playwright.sync_api import Page
from pages.base_page import BasePage


class PostDetailPage(BasePage):
    # 포스트 카드 (피드 목록에서 첫 번째)
    FIRST_POST_CARD = ".PostCard:first-child, [data-testid='post-card']:first-child, .FeedItem:first-child"

    # 더보기 메뉴 — GitHub 검증값
    BTN_MORE = "button.toolbar-_-button"

    # 삭제 버튼 — GitHub 검증값
    BTN_DELETE = "button:has-text('삭제하기')"

    # 삭제 확인 팝업 — GitHub 검증값 (last: 취소/확인 중 마지막)
    BTN_DELETE_CONFIRM = "button:has-text('확인')"

    # 수정된 텍스트 또는 영상이 노출되었는지 확인
    TEXT_VIDEO_ATTACHED = ".VideoPlayer, video, [data-testid='video-player']"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def click_first_post(self) -> None:
        locator = self.page.locator(self.FIRST_POST_CARD).first
        locator.wait_for(state="visible")
        locator.click()
        self.page.wait_for_load_state("networkidle")

    def open_more_menu(self) -> None:
        btn = self.page.locator(self.BTN_MORE).first
        btn.wait_for(state="visible")
        btn.click()
        self.page.wait_for_timeout(500)

    def delete_post(self) -> None:
        """첫 번째 포스트를 삭제하고 확인 팝업을 처리합니다."""
        self.open_more_menu()
        self.wait_and_click(self.BTN_DELETE)
        self.page.wait_for_timeout(800)

        # 삭제 확인 팝업 — GitHub 검증값: last 사용
        confirm = self.page.locator(self.BTN_DELETE_CONFIRM).last
        if confirm.is_visible():
            confirm.click()

        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1500)
        self.screenshot("post_deleted")

    def has_video(self) -> bool:
        return self.page.locator(self.TEXT_VIDEO_ATTACHED).count() > 0

    def get_first_post_text(self) -> str:
        locator = self.page.locator(
            ".PostCard__content:first-of-type, "
            "[data-testid='post-content']:first-of-type, "
            ".PostText:first-of-type"
        ).first
        if locator.is_visible():
            return locator.inner_text()
        return ""

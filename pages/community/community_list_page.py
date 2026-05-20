"""위버스 커뮤니티 목록 페이지 POM."""

from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.config import Config


class CommunityListPage(BasePage):
    PLACEHOLDER_SEARCH = "아티스트의 이름을 입력하세요."

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def join_community(self, community_name: str = None) -> None:
        name = community_name or Config.TARGET_COMMUNITY
        self.navigate("/")
        self.page.wait_for_load_state("networkidle")

        # 커뮤니티 찾기 버튼 클릭
        find_btn = self.page.locator("button.global-menu-list-item-_-item_link:has-text('커뮤니티 찾기')")
        find_btn.wait_for(state="visible")
        find_btn.click()
        self.page.wait_for_load_state("networkidle")

        # 검색창 입력
        search_input = self.page.get_by_placeholder(self.PLACEHOLDER_SEARCH)
        search_input.wait_for(state="visible")
        search_input.fill(name)
        self.page.wait_for_timeout(1500)

        # 커뮤니티 카드 클릭 → 항상 커뮤니티 안으로 진입
        card = self.page.locator(f"a:has-text('{name}')").first
        card.wait_for(state="visible")
        card.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)

        # 커뮤니티 내 가입 버튼이 있으면 가입, 없으면 이미 가입된 상태
        join_btn = self.page.get_by_role("button", name="가입", exact=True)
        if join_btn.is_visible():
            join_btn.click()
            self.page.wait_for_load_state("networkidle")

    def is_joined(self) -> bool:
        return (
            self.page.locator(
                "button:has-text('탈퇴'), button:has-text('Unfollow'), button:has-text('가입됨')"
            ).count() > 0
        )

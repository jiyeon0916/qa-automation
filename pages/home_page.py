"""위버스 홈 페이지 POM."""

from playwright.sync_api import Page
from pages.base_page import BasePage


class HomePage(BasePage):
    NAV_COMMUNITY = "a[href*='/community'], nav a:has-text('커뮤니티'), nav a:has-text('Community')"
    SEARCH_INPUT = "input[type='search'], input[placeholder*='검색'], input[placeholder*='Search']"
    COMMUNITY_CARD = ".CommunityCard, [data-testid='community-item'], .artist-item"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def go_home(self) -> None:
        self.navigate("/")

    def go_to_community_list(self) -> None:
        self.navigate("/")
        self.wait_and_click(self.NAV_COMMUNITY)
        self.page.wait_for_load_state("networkidle")

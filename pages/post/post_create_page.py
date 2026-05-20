"""포스트 작성/수정 페이지 POM."""

from pathlib import Path
from playwright.sync_api import Page
from pages.base_page import BasePage


class PostCreatePage(BasePage):
    # ------------------------------------------------------------------ #
    #  Selectors                                                            #
    # ------------------------------------------------------------------ #
    # 포스트 작성 버튼 (피드 상단)
    BTN_WRITE_POST = (
        "button:has-text('게시물 작성'), "
        "button:has-text('Write a post'), "
        "button:has-text('포스트 작성'), "
        "[data-testid='post-write-btn'], "
        ".WritePostButton"
    )

    # 텍스트 입력 영역 (#wev-editor 검증값 우선, 폴백 포함)
    INPUT_TEXT = "#wev-editor, [contenteditable='true'], .wev-editor-input-v3-_-text_wrap"

    # 이미지/영상 첨부
    BTN_ATTACH_MEDIA = (
        "button[aria-label*='이미지'], "
        "button[aria-label*='사진'], "
        "button[aria-label*='photo'], "
        "button[aria-label*='image'], "
        "input[type='file'], "
        "[data-testid='media-attach-btn']"
    )
    # #weuii 검증값 우선
    INPUT_FILE = "#weuii, input[type='file'][accept*='image'], input[type='file']"

    # 등록 / 수정 제출
    BTN_SUBMIT = (
        "button:has-text('등록'), "
        "button:has-text('Post'), "
        "button:has-text('게시'), "
        "button[type='submit'], "
        "[data-testid='post-submit-btn']"
    )

    # 수정 진입
    BTN_EDIT = (
        "button:has-text('수정'), "
        "[data-testid='post-edit-btn'], "
        ".PostMenu__edit"
    )

    INPUT_VIDEO_FILE = "#weuvi"

    # 첨부된 이미지/영상 삭제 버튼 (button._deleteWidget 검증값 우선)
    BTN_REMOVE_MEDIA = (
        "button._deleteWidget, "
        "button[aria-label*='삭제'], "
        "button[aria-label*='remove'], "
        "button[aria-label*='delete'], "
        "[data-testid='media-remove-btn']"
    )

    # 등록 완료 확인 (토스트 or 피드에 카드 노출)
    TEXT_POST_DONE = (
        ":has-text('게시되었습니다'), "
        ":has-text('posted'), "
        ":has-text('등록되었습니다'), "
        ".PostCard:first-child"
    )

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ------------------------------------------------------------------ #
    #  Actions                                                              #
    # ------------------------------------------------------------------ #
    def open_write_dialog(self) -> None:
        # GitHub 검증값: 에디터 래퍼 클릭으로 작성 모드 진입
        wrapper = self.page.locator(".wev-editor-input-v3-_-text_wrap")
        wrapper.wait_for(state="visible")
        wrapper.click()
        self.page.wait_for_timeout(1000)

    def fill_text(self, text: str) -> None:
        editor = self.page.locator("#wev-editor")
        editor.wait_for(state="visible")
        editor.click()
        editor.fill(text)

    def attach_image(self, image_path: Path) -> None:
        file_input = self.page.locator("#weuii")
        file_input.set_input_files(str(image_path.resolve()))
        self._confirm_upload()

    def attach_video(self, video_path: Path) -> None:
        file_input = self.page.locator("#weuvi")
        file_input.set_input_files(str(video_path.resolve()))
        self._confirm_upload()

    def _confirm_upload(self) -> None:
        self.page.wait_for_timeout(5000)
        confirm = self.page.locator("button.confirm_button")
        try:
            confirm.wait_for(state="visible", timeout=10000)
            confirm.click()
            self.page.wait_for_timeout(2000)
        except Exception:
            pass

    def remove_attached_media(self) -> None:
        """첨부된 미디어(이미지/영상)를 모두 삭제합니다."""
        while True:
            btn = self.page.locator(self.BTN_REMOVE_MEDIA).first
            if not btn.is_visible():
                break
            btn.click()
            self.page.wait_for_timeout(500)

    def submit(self) -> None:
        # GitHub 검증값
        self.page.get_by_text("등록", exact=True).click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    # ------------------------------------------------------------------ #
    #  복합 플로우                                                           #
    # ------------------------------------------------------------------ #
    def create_post(self, text: str, image_path: Path) -> None:
        """텍스트 + 이미지를 포함한 포스트를 작성하고 등록합니다."""
        self.open_write_dialog()
        self.fill_text(text)
        self.attach_image(image_path)
        self.screenshot("post_before_submit")
        self.submit()
        self.screenshot("post_created")

    def edit_post_text(self, new_text: str) -> None:
        """열려 있는 수정 폼에서 텍스트를 교체합니다."""
        editor = self.page.locator("#wev-editor")
        editor.wait_for(state="visible")
        editor.click()
        editor.fill(new_text)

    def open_edit_dialog(self) -> None:
        """피드의 첫 번째 포스트 더보기 메뉴를 열어 수정 버튼을 클릭합니다."""
        self._open_post_menu()
        self.page.locator("button.menu-_-button:has-text('수정하기')").click()
        self.page.wait_for_load_state("networkidle")

    def _open_post_menu(self) -> None:
        more_btn = self.page.locator("button.toolbar-_-button").first
        more_btn.wait_for(state="visible")
        more_btn.click()
        self.page.wait_for_timeout(500)

    def is_post_visible(self, text: str) -> bool:
        return self.page.get_by_text(text, exact=False).count() > 0

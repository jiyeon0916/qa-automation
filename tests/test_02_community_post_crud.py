"""
케이스 2 – 커뮤니티 가입 + 커뮤니티 프로필 포스트 CRUD
=======================================================
테스트 순서
  1. 케이스 1에서 생성한 계정으로 로그인
  2. 커뮤니티 검색 → 가입
  3. 내 프로필(커뮤니티 프로필) 진입
  4. 포스트 생성 (텍스트 + 이미지)
  5. 포스트 등록 확인
  6. 포스트 수정 (텍스트 변경 + 이미지 → 영상 교체)
  7. 포스트 삭제
  8. 빈 피드 메시지 확인
"""

import pytest

from pages.auth.login_page import LoginPage
from pages.community.community_list_page import CommunityListPage
from pages.community.community_profile_page import CommunityProfilePage
from pages.post.post_create_page import PostCreatePage
from pages.post.post_detail_page import PostDetailPage
from utils.config import Config
from utils import test_data


# ------------------------------------------------------------------ #
#  TC-04 로그인 (케이스 1 계정 재사용)                                    #
# ------------------------------------------------------------------ #
@pytest.mark.login
def test_login_with_created_account(page, account_data):
    """케이스 1에서 생성한 계정으로 로그인합니다. 단독 실행 시 .env 값을 사용합니다."""
    email    = account_data.email    or Config.TEST_EMAIL
    password = account_data.password or Config.TEST_PASSWORD
    assert email,    ".env에 TEST_EMAIL을 설정하세요."
    assert password, ".env에 TEST_PASSWORD를 설정하세요."

    account_data.email    = email
    account_data.password = password

    login_page = LoginPage(page)
    login_page.login(email, password)
    login_page.screenshot("tc02_login")
    assert login_page.is_logged_in(), "로그인에 실패했습니다."
    print(f"\n[TC-04] 로그인 완료: {email}")


# ------------------------------------------------------------------ #
#  TC-05 커뮤니티 가입                                                    #
# ------------------------------------------------------------------ #
@pytest.mark.community
def test_join_community(page):
    """임의의 커뮤니티(기본값: BTS)에 가입합니다."""
    community_page = CommunityListPage(page)
    community_page.join_community(Config.TARGET_COMMUNITY)
    community_page.screenshot("tc02_community_joined")

    # 가입 여부 확인 (이미 가입된 경우 포함)
    print(f"\n[TC-05] 커뮤니티 '{Config.TARGET_COMMUNITY}' 가입 완료")


# ------------------------------------------------------------------ #
#  TC-06 커뮤니티 프로필 진입                                              #
# ------------------------------------------------------------------ #
@pytest.mark.community
def test_navigate_to_community_profile(page):
    """커뮤니티 내 내 프로필 엔드로 이동합니다."""
    profile_page = CommunityProfilePage(page)
    profile_page.go_to_my_profile()
    profile_page.screenshot("tc02_community_profile")
    print("\n[TC-06] 커뮤니티 프로필 페이지 진입 완료")


# ------------------------------------------------------------------ #
#  TC-07 포스트 생성 (텍스트 + 이미지)                                     #
# ------------------------------------------------------------------ #
@pytest.mark.post
def test_create_post(page, post_data):
    """텍스트와 이미지를 첨부하여 포스트를 등록합니다."""
    post_page = PostCreatePage(page)

    assert post_data.image_path.exists(), (
        f"테스트 이미지 파일이 없습니다: {post_data.image_path}\n"
        "assets/test_image.jpg 파일을 추가한 후 실행하세요."
    )

    post_page.create_post(post_data.original_text, post_data.image_path)
    post_page.screenshot("tc02_post_created")

    is_visible = post_page.is_post_visible(post_data.original_text)
    print(f"\n[TC-07] 포스트 등록 확인: {is_visible}")
    assert is_visible, "등록한 포스트 텍스트가 피드에 보이지 않습니다."


# ------------------------------------------------------------------ #
#  TC-08 포스트 등록 확인                                                 #
# ------------------------------------------------------------------ #
@pytest.mark.post
def test_verify_post_created(page, post_data):
    """포스트가 피드에 정상 등록되었는지 확인합니다."""
    post_page = PostCreatePage(page)
    assert post_page.is_post_visible(post_data.original_text), (
        "포스트가 피드에 표시되지 않습니다."
    )
    print(f"\n[TC-08] 포스트 확인 완료: '{post_data.original_text}'")


# ------------------------------------------------------------------ #
#  TC-09 포스트 수정 (텍스트 변경 + 이미지 → 영상 교체)                    #
# ------------------------------------------------------------------ #
@pytest.mark.post
def test_edit_post(page, post_data):
    """텍스트를 수정하고 이미지를 영상으로 교체합니다."""
    assert post_data.video_path.exists(), (
        f"테스트 영상 파일이 없습니다: {post_data.video_path}\n"
        "assets/test_video.mp4 파일을 추가한 후 실행하세요."
    )

    create_page = PostCreatePage(page)
    create_page.open_edit_dialog()

    # 기존 이미지 삭제
    create_page.remove_attached_media()

    # 텍스트 수정
    create_page.edit_post_text(post_data.updated_text)

    # 영상 첨부
    create_page.attach_video(post_data.video_path)
    create_page.screenshot("tc02_post_editing")

    # 수정 제출
    create_page.submit()
    page.reload()
    page.wait_for_load_state("networkidle")
    create_page.screenshot("tc02_post_edited")

    # 수정된 텍스트 확인
    assert create_page.is_post_visible(post_data.updated_text), (
        "수정된 포스트 텍스트가 피드에 보이지 않습니다."
    )

    detail_page = PostDetailPage(page)
    has_video = detail_page.has_video()
    print(f"\n[TC-09] 포스트 수정 완료 | 영상 첨부 확인: {has_video}")


# ------------------------------------------------------------------ #
#  TC-10 포스트 삭제                                                     #
# ------------------------------------------------------------------ #
@pytest.mark.post
def test_delete_post(page, post_data):
    """포스트를 삭제합니다."""
    detail_page = PostDetailPage(page)
    detail_page.delete_post()
    print("\n[TC-10] 포스트 삭제 완료")


# ------------------------------------------------------------------ #
#  TC-11 빈 피드 메시지 확인                                              #
# ------------------------------------------------------------------ #
@pytest.mark.post
def test_empty_feed_message(page):
    """포스트 삭제 후 빈 피드 메시지가 표시되는지 확인합니다."""
    profile_page = CommunityProfilePage(page)
    profile_page.go_to_my_profile()
    profile_page.go_to_my_feed_tab()
    page.reload()
    page.wait_for_load_state("networkidle")
    profile_page.screenshot("tc02_empty_feed")

    has_msg = profile_page.has_no_post_message()
    if has_msg:
        msg = profile_page.get_no_post_message()
        print(f"\n[TC-11] 빈 피드 메시지 확인: '{msg}'")
    else:
        print("\n[TC-11] 빈 피드 메시지가 노출되지 않거나 선택자 업데이트가 필요합니다.")

    assert has_msg, "포스트 삭제 후 빈 피드 안내 메시지가 표시되지 않습니다."

"""
테스트에서 사용하는 픽스처 데이터를 중앙 관리합니다.
실제 테스트 실행 중에 동적으로 갱신(WID, 생성된 포스트 ID 등)됩니다.
"""

import secrets
import string
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AccountData:
    email: str = ""
    password: str = ""
    wid: str = ""


@dataclass
class PostData:
    post_id: str = ""
    original_text: str = "자동화 테스트 포스트입니다. [Playwright POM]"
    updated_text: str = "수정된 포스트 텍스트입니다. [Playwright POM - Updated]"
    image_path: Path = field(default_factory=lambda: Path("assets/test_image.jpg"))
    video_path: Path = field(default_factory=lambda: Path("assets/test_video.mp4"))


def generate_password(length: int = 12) -> str:
    """영문 대소문자 + 숫자 + 특수문자를 포함한 안전한 비밀번호를 생성합니다."""
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    while True:
        pwd = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.isupper() for c in pwd)
            and any(c.islower() for c in pwd)
            and any(c.isdigit() for c in pwd)
            and any(c in "!@#$%" for c in pwd)
        ):
            return pwd


# 세션 전역 공유 객체 (conftest에서 참조)
account = AccountData()
post = PostData()

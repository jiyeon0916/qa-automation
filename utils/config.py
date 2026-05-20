import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    WEVERSE_URL: str = os.getenv("WEVERSE_URL", "https://weverse.io")

    TEST_EMAIL: str = os.getenv("TEST_EMAIL", "")
    TEST_PASSWORD: str = os.getenv("TEST_PASSWORD", "")

    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "100"))

    TARGET_COMMUNITY: str = os.getenv("TARGET_COMMUNITY", "BTS")

    DEFAULT_TIMEOUT: int = 30_000
    NAVIGATION_TIMEOUT: int = 60_000

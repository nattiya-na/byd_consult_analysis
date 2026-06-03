from dotenv import load_dotenv
import os

load_dotenv()

# --- API Credentials ---
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

FACEBOOK_EMAIL = os.getenv("FACEBOOK_EMAIL", "")
FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD", "")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# --- Database ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///byd_perception.db")

# --- Claude Settings ---
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5")
# Minimum text length (chars) to trigger sentiment analysis
CLAUDE_MIN_TEXT_LENGTH = int(os.getenv("CLAUDE_MIN_TEXT_LENGTH", "20"))

# --- Crawler Settings ---
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "2.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

YOUTUBE_MAX_RESULTS = int(os.getenv("YOUTUBE_MAX_RESULTS", "50"))
YOUTUBE_MAX_COMMENT_PAGES = int(os.getenv("YOUTUBE_MAX_COMMENT_PAGES", "5"))

FACEBOOK_MAX_POSTS = int(os.getenv("FACEBOOK_MAX_POSTS", "50"))
FACEBOOK_MIN_COMMENTS = int(os.getenv("FACEBOOK_MIN_COMMENTS", "3"))
FACEBOOK_HEADLESS = os.getenv("FACEBOOK_HEADLESS", "true").lower() != "false"

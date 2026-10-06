"""YouTube API client + URL helpers."""
import os
import re

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY not found in environment variables.")

youtube = build("youtube", "v3", developerKey=API_KEY)

# Matches watch?v=, youtu.be/, /shorts/, /embed/ forms
_ID_PATTERN = re.compile(
    r"(?:youtube\.com/(?:watch\?(?:.*&)?v=|shorts/|embed/)|youtu\.be/)([a-zA-Z0-9_-]{11})"
)


def get_youtube_video_id(url):
    """Return the 11-char video ID from a YouTube URL, or None if invalid."""
    match = _ID_PATTERN.search(url)
    return match.group(1) if match else None


class YouTubeVideo:
    """A YouTube video identified by URL."""

    def __init__(self, url):
        self.url = url
        self.video_id = get_youtube_video_id(url)

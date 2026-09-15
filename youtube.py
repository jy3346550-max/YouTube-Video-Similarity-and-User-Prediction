
import re
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY not found in environment variables.")

youtube = build('youtube', 'v3', developerKey=API_KEY)

class YouTubeVideo:
    """
    A class to represent a YouTube video.

    Attributes:
        url (str): The URL of the YouTube video.
        video_id (str): The unique identifier for the YouTube video.
    """

    def __init__(self, url):
        """
        Initializes a YouTubeVideo instance.

        Args:
            url (str): The URL of the YouTube video.
        """
        self.url = url
        self.video_id = get_youtube_video_id(url)

    
def get_youtube_video_id(url):
    """
    Extracts the YouTube video ID from a given URL.

    Args:
        url (str): The YouTube URL.

    Returns:
        str: The extracted video ID, or None if the URL is invalid.
    """

    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.match(pattern, url)
    if match:
        return match.group(1)
    else:
        return None


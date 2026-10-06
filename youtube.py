
import re
import os
from datetime import datetime, timedelta

import isodate
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
from youtube_transcript_api._errors import VideoUnavailable, TranscriptsDisabled, NoTranscriptFound

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
        if self.video_id is None:
            raise ValueError("Invalid YouTube URL provided.")

        # Text Attributes

        self.title = None
        self.description = None
        self.tags = []
        self.transcript = None

        # Categorical Attributes

        self.category_id = None
        self.channel_id = None
        self.channel_title = None
        self.default_language = None
        self.default_audio_language = None

    def fetch(self, include_transcript=True):
        """
        Fetches video details and optionally the transcript.

       
        """
        try:
            video_response = youtube.videos().list(
                part="snippet,contentDetails",
                id=self.video_id
            ).execute()

            if not video_response['items']:
                raise ValueError("Video not found.")

            video_data = video_response['items'][0]['snippet']
            self.title = video_data.get('title')
            self.description = video_data.get('description')
            self.tags = video_data.get('tags', [])
            self.category_id = video_data.get('categoryId')
            self.channel_id = video_data.get('channelId')
            self.channel_title = video_data.get('channelTitle')
            self.default_language = video_data.get('defaultLanguage')
            self.default_audio_language = video_data.get('defaultAudioLanguage')

            if include_transcript:
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(self.video_id)
                    transcript = transcript_list.find_transcript(['en'])
                    formatter = TextFormatter()
                    self.transcript = formatter.format_transcript(transcript.fetch())
                except (TranscriptsDisabled, NoTranscriptFound):
                    self.transcript = None
        except HttpError as e:
            raise ValueError(f"An error occurred while fetching video details: {e}")

    
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


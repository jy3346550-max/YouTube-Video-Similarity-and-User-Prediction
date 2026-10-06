"""Data collection: search -> video metadata -> channel metadata -> transcripts.

Quota costs (YouTube Data API v3, 10,000 units/day default):
  search.list   = 100 units per call (50 results max)  <- the expensive one
  videos.list   = 1 unit per call (up to 50 IDs)
  channels.list = 1 unit per call (up to 50 IDs)
"""
import json
import re
import time

from .db import (
    existing_video_ids,
    upsert_channel,
    upsert_transcript,
    upsert_video,
    video_ids_without_transcript,
)
from .youtube import youtube

_DURATION = re.compile(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def parse_duration(iso):
    """ISO-8601 duration ('PT1H2M3S') -> seconds."""
    m = _DURATION.fullmatch(iso or "")
    if not m:
        return None
    d, h, mi, s = (int(x) if x else 0 for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def _int(value):
    return int(value) if value is not None else None


def _chunks(items, n=50):
    items = list(items)
    for i in range(0, len(items), n):
        yield items[i : i + n]


# ---------- search ----------

def search_video_ids(query, pages=1, category_id=None, language="en"):
    """Return video IDs for a query. Costs 100 quota units per page."""
    ids, token = [], None
    for _ in range(pages):
        params = dict(
            q=query, part="id", type="video", maxResults=50,
            relevanceLanguage=language, safeSearch="moderate",
        )
        if category_id:
            params["videoCategoryId"] = category_id
        if token:
            params["pageToken"] = token
        resp = youtube.search().list(**params).execute()
        ids += [i["id"]["videoId"] for i in resp.get("items", [])]
        token = resp.get("nextPageToken")
        if not token:
            break
    return ids


# ---------- metadata ----------

def fetch_video_details(video_ids, seed_query=None):
    rows = []
    for batch in _chunks(video_ids):
        resp = youtube.videos().list(
            part="snippet,contentDetails,statistics", id=",".join(batch)
        ).execute()
        for item in resp.get("items", []):
            sn, cd, st = item["snippet"], item["contentDetails"], item.get("statistics", {})
            rows.append({
                "video_id": item["id"],
                "channel_id": sn["channelId"],
                "title": sn.get("title"),
                "description": sn.get("description"),
                "tags": json.dumps(sn.get("tags", [])),
                "category_id": sn.get("categoryId"),
                "default_language": sn.get("defaultLanguage"),
                "default_audio_language": sn.get("defaultAudioLanguage"),
                "duration_seconds": parse_duration(cd.get("duration")),
                "published_at": sn.get("publishedAt"),
                "view_count": _int(st.get("viewCount")),
                "like_count": _int(st.get("likeCount")),
                "comment_count": _int(st.get("commentCount")),
                "seed_query": seed_query,
            })
    return rows


def fetch_channel_details(channel_ids):
    rows = []
    for batch in _chunks(set(channel_ids)):
        resp = youtube.channels().list(
            part="snippet,statistics", id=",".join(batch)
        ).execute()
        for item in resp.get("items", []):
            sn, st = item["snippet"], item.get("statistics", {})
            hidden = st.get("hiddenSubscriberCount", False)
            rows.append({
                "channel_id": item["id"],
                "title": sn.get("title"),
                "country": sn.get("country"),
                "subscriber_count": None if hidden else _int(st.get("subscriberCount")),
                "video_count": _int(st.get("videoCount")),
                "view_count": _int(st.get("viewCount")),
            })
    return rows


# ---------- transcripts ----------

def fetch_transcript(video_id, languages=("en",)):
    """Never raises: returns a row with status 'ok' / 'unavailable' / 'error'."""
    row = {"video_id": video_id, "status": "unavailable",
           "language": None, "is_generated": None, "text": None}
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        api = YouTubeTranscriptApi()
        if hasattr(api, "fetch"):  # v1.x API
            fetched = api.fetch(video_id, languages=list(languages))
            text = " ".join(s.text for s in fetched)
            row.update(status="ok", text=text, language=fetched.language_code,
                       is_generated=int(fetched.is_generated))
        else:  # legacy API
            chunks = YouTubeTranscriptApi.get_transcript(video_id, languages=list(languages))
            row.update(status="ok", text=" ".join(c["text"] for c in chunks),
                       language=languages[0])
    except Exception as e:
        name = type(e).__name__
        # Missing captions are expected (10-30% of videos); anything else is a real error
        if name not in {"TranscriptsDisabled", "NoTranscriptFound", "VideoUnavailable"}:
            row["status"] = "error"
    return row


# ---------- orchestration ----------

def collect_videos(conn, queries, pages=1, category_id=None):
    """Search each query, skip IDs we already have, store videos + channels."""
    known = existing_video_ids(conn)
    added = 0
    for q in queries:
        found = [v for v in dict.fromkeys(search_video_ids(q, pages, category_id)) if v not in known]
        if not found:
            print(f"[{q}] nothing new")
            continue
        videos = fetch_video_details(found, seed_query=q)
        for ch in fetch_channel_details(v["channel_id"] for v in videos):
            upsert_channel(conn, ch)
        known_channels = {r[0] for r in conn.execute("SELECT channel_id FROM channels")}
        for v in videos:
            if v["channel_id"] in known_channels:  # skip if channel lookup failed (FK)
                upsert_video(conn, v)
                known.add(v["video_id"])
                added += 1
        conn.commit()
        print(f"[{q}] +{len(videos)} videos")
    return added


def collect_transcripts(conn, delay=0.5, limit=None):
    todo = video_ids_without_transcript(conn)[:limit]
    for i, vid in enumerate(todo, 1):
        upsert_transcript(conn, fetch_transcript(vid))
        if i % 25 == 0:
            conn.commit()
            print(f"transcripts: {i}/{len(todo)}")
        time.sleep(delay)  # be polite; rapid-fire requests can get your IP blocked
    conn.commit()
    return len(todo)

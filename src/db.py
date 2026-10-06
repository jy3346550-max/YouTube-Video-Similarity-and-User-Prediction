"""SQLite schema + upsert helpers. Three normalized tables:
channels <- videos <- transcripts
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("data/youtube.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS channels (
    channel_id        TEXT PRIMARY KEY,
    title             TEXT,
    country           TEXT,
    subscriber_count  INTEGER,          -- NULL if hidden
    video_count       INTEGER,
    view_count        INTEGER,
    fetched_at        TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS videos (
    video_id              TEXT PRIMARY KEY,
    channel_id            TEXT NOT NULL REFERENCES channels(channel_id),
    title                 TEXT,
    description           TEXT,
    tags                  TEXT,          -- JSON-encoded list
    category_id           TEXT,
    default_language      TEXT,
    default_audio_language TEXT,
    duration_seconds      INTEGER,
    published_at          TEXT,
    view_count            INTEGER,
    like_count            INTEGER,       -- NULL if hidden/disabled
    comment_count         INTEGER,       -- NULL if comments disabled
    seed_query            TEXT,          -- which search found it
    fetched_at            TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transcripts (
    video_id      TEXT PRIMARY KEY REFERENCES videos(video_id),
    status        TEXT NOT NULL,         -- 'ok' | 'unavailable' | 'error'
    language      TEXT,
    is_generated  INTEGER,
    text          TEXT,
    fetched_at    TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_videos_channel ON videos(channel_id);
CREATE INDEX IF NOT EXISTS idx_videos_category ON videos(category_id);
"""


def get_conn(path=DB_PATH):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def _upsert(conn, table, key, row):
    cols = list(row)
    placeholders = ", ".join(f":{c}" for c in cols)
    updates = ", ".join(f"{c}=excluded.{c}" for c in cols if c != key)
    conn.execute(
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders}) "
        f"ON CONFLICT({key}) DO UPDATE SET {updates}",
        row,
    )


def upsert_channel(conn, row):
    _upsert(conn, "channels", "channel_id", row)


def upsert_video(conn, row):
    _upsert(conn, "videos", "video_id", row)


def upsert_transcript(conn, row):
    _upsert(conn, "transcripts", "video_id", row)


def existing_video_ids(conn):
    return {r[0] for r in conn.execute("SELECT video_id FROM videos")}


def video_ids_without_transcript(conn):
    return [
        r[0]
        for r in conn.execute(
            "SELECT v.video_id FROM videos v "
            "LEFT JOIN transcripts t ON v.video_id = t.video_id "
            "WHERE t.video_id IS NULL"
        )
    ]

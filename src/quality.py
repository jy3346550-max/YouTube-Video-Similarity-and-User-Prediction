"""Data-quality report -> paste into README (Week 2, Day 6)."""
import pandas as pd


def quality_report(conn):
    v = pd.read_sql("SELECT * FROM videos", conn)
    t = pd.read_sql("SELECT status FROM transcripts", conn)
    n = len(v)
    if n == 0:
        return "No videos collected yet."

    lines = [f"# Data quality report", f"- Videos: {n}",
             f"- Channels: {v['channel_id'].nunique()}",
             f"- Duplicate titles: {v['title'].duplicated().sum()}"]

    if len(t):
        counts = t["status"].value_counts()
        for status, c in counts.items():
            lines.append(f"- Transcripts {status}: {c} ({c / n:.0%} of videos)")
        lines.append(f"- Transcripts not yet attempted: {n - len(t)}")

    lines.append("- Missing values (% of videos):")
    for col in ["description", "tags", "default_language", "like_count", "comment_count", "view_count"]:
        if col == "tags":
            miss = (v[col] == "[]").mean()
        elif col == "description":
            miss = (v[col].fillna("").str.strip() == "").mean()
        else:
            miss = v[col].isna().mean()
        lines.append(f"    - {col}: {miss:.0%}")

    non_ascii = v["title"].fillna("").map(lambda s: not s.isascii()).mean()
    lines.append(f"- Titles with non-ASCII characters: {non_ascii:.0%}")
    lines.append(f"- Duration (min): median {v['duration_seconds'].median() / 60:.1f}, "
                 f"max {v['duration_seconds'].max() / 60:.1f}")
    lines.append("- Videos per category_id:")
    for cat, c in v["category_id"].value_counts().items():
        lines.append(f"    - {cat}: {c}")
    return "\n".join(lines)

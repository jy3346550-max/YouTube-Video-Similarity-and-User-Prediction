"""CLI entry point.

  python main.py collect --pages 2          # search + metadata (uses quota!)
  python main.py transcripts                # fetch captions
  python main.py quality                    # data-quality report
  python main.py similar-to <video_url>     # (Week 3) coming soon
"""
import argparse

from src.db import get_conn

# TODO: replace with 4-6 topics you personally know well (so you can sanity-check results later)
SEED_QUERIES = [
    "python programming tutorial",
    "machine learning explained",
    "cooking pasta recipe",
    "college study tips",
    "indie game review",
    "lofi study music",
]


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("collect")
    c.add_argument("--pages", type=int, default=1, help="pages of 50 results per query (100 quota units each)")
    c.add_argument("--queries", nargs="*", default=SEED_QUERIES)

    t = sub.add_parser("transcripts")
    t.add_argument("--limit", type=int, default=None)

    sub.add_parser("quality")
    args = p.parse_args()

    conn = get_conn()
    if args.cmd == "collect":
        from src.collect import collect_videos
        cost = len(args.queries) * args.pages * 100
        print(f"Estimated search quota: ~{cost} units (daily limit 10,000)")
        print(f"Added {collect_videos(conn, args.queries, args.pages)} videos")
    elif args.cmd == "transcripts":
        from src.collect import collect_transcripts
        print(f"Processed {collect_transcripts(conn, limit=args.limit)} videos")
    elif args.cmd == "quality":
        from src.quality import quality_report
        print(quality_report(conn))


if __name__ == "__main__":
    main()

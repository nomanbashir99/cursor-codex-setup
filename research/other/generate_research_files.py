#!/usr/bin/env python3
"""Generate organized research files from the collected source CSVs."""

from __future__ import annotations

import csv
import re
import shutil
import unicodedata
from pathlib import Path

import requests


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = Path("/Users/nomanbashir/b2b-outreach-expert-content")
YOUTUBE_CSV = SOURCE_ROOT / "data" / "youtube_sources.csv"
LINKEDIN_CSV = SOURCE_ROOT / "data" / "linkedin_public_posts.csv"
OLD_SYNTHESIS = SOURCE_ROOT / "content_synthesis.md"

RESEARCH = REPO_ROOT / "research"
LINKEDIN_DIR = RESEARCH / "linkedin-posts"
YOUTUBE_DIR = RESEARCH / "youtube-transcripts"
OTHER_DIR = RESEARCH / "other"

SNAPSHOT_DATE = "2026-05-19"

EXPERTS = {
    "Jason Bay": {
        "profile": "https://www.outboundsquad.com/",
        "proof": "Founder of Outbound Squad; teaches outbound prospecting and cold calling from operating work with B2B sales teams.",
        "why": "Strong source for practical outbound pipeline design, call strategy, and sequencing.",
    },
    "Florin Tatulea": {
        "profile": "https://www.linkedin.com/in/florintatulea/",
        "proof": "Sales development leader and cold email educator focused on practical prospecting workflows.",
        "why": "Useful for research-first personalization, AI prospecting, and outbound messaging quality.",
    },
    "Eric Nowoslawski": {
        "profile": "https://www.linkedin.com/in/outboundphd/",
        "proof": "Founder/operator building cold email systems and Clay-based outbound workflows.",
        "why": "Useful for modern cold email operations, signal testing, and conversion-focused KPIs.",
    },
    "Michel Lieben": {
        "profile": "https://www.coldiq.com/",
        "proof": "Founder of ColdIQ; builds AI-assisted GTM and outbound systems for B2B companies.",
        "why": "Useful for connecting cold outreach with enrichment, routing, ads, LinkedIn, and re-engagement.",
    },
    "Bill Stathopoulos": {
        "profile": "https://www.salescaptain.io/",
        "proof": "CEO of SalesCaptain; runs outbound and cold email campaigns for B2B companies.",
        "why": "Useful for experimentation, infrastructure, timing, offer tests, and deliverability-aware outbound.",
    },
    "Jack Reamer": {
        "profile": "https://salesbread.com/",
        "proof": "Founder of SalesBread; works on personalized B2B email and LinkedIn outreach.",
        "why": "Useful for warm-path checks, personalization, and LinkedIn/email lead generation.",
    },
    "Becc Holland": {
        "profile": "https://www.flipthescript.com/",
        "proof": "Founder of Flip the Script; trains outbound teams on buyer research, messaging, cold email, and calls.",
        "why": "Useful for the buyer-problem research layer before writing outreach copy.",
    },
    "Tito Bohrt": {
        "profile": "https://www.altisales.com/",
        "proof": "CEO of AltiSales; builds and advises SDR/outbound teams.",
        "why": "Useful for the limits of AI SDR volume and the need for business acumen in outreach.",
    },
    "Guillaume Moubeche": {
        "profile": "https://www.lemlist.com/",
        "proof": "Co-founder of lemlist; built a SaaS product around personalized cold email and outreach.",
        "why": "Useful as an operator case study for reply-focused, personalized outbound.",
    },
    "Michael Maximoff": {
        "profile": "https://belkins.io/",
        "proof": "Co-founder of Belkins; operates a B2B lead generation agency using email, LinkedIn, and calling.",
        "why": "Useful for benchmark-backed omnichannel outreach and declining-reply-rate context.",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def slug(value: str, max_len: int = 70) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text)
    ascii_text = ascii_text.strip("-")
    return ascii_text[:max_len].strip("-") or "source"


def fetch_upload_date(url: str) -> str:
    try:
        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
    except Exception:
        return "unknown"

    html = response.text
    for field in ("datePublished", "uploadDate"):
        match = re.search(
            rf'itemprop="{field}" content="([^"]+)"',
            html,
        )
        if match:
            return match.group(1)
    return "unknown"


def youtube_upload_dates(rows: list[dict[str, str]]) -> dict[str, str]:
    cache_path = OTHER_DIR / "youtube-upload-dates.csv"
    cached: dict[str, str] = {}
    if cache_path.exists():
        cached = {
            row["video_id"]: row["upload_date"]
            for row in read_csv(cache_path)
            if row.get("video_id")
        }

    for row in rows:
        video_id = row["video_id"]
        if video_id and video_id not in cached:
            cached[video_id] = fetch_upload_date(row["url"])

    OTHER_DIR.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["video_id", "upload_date", "url"])
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "video_id": row["video_id"],
                    "upload_date": cached.get(row["video_id"], "unknown"),
                    "url": row["url"],
                }
            )
    return cached


def best_video(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    best: dict[str, dict[str, str]] = {}
    for row in rows:
        expert = row["expert"]
        if expert not in best:
            best[expert] = row
        if row["caption_status"] == "caption_found_youtube_transcript_api":
            if best[expert].get("caption_status") != "caption_found_youtube_transcript_api":
                best[expert] = row
    return best


def sources_md(
    youtube_rows: list[dict[str, str]],
    linkedin_rows: list[dict[str, str]],
    upload_dates: dict[str, str],
) -> str:
    linkedin_by_expert = {row["expert"]: row for row in linkedin_rows}
    best_by_expert = best_video(youtube_rows)

    lines = [
        "# Research Sources: Cold Outreach Pipeline for B2B SaaS",
        "",
        f"Snapshot date: {SNAPSHOT_DATE}",
        "",
        "This source list favors practitioners: founders, operators, trainers, and agency builders who actively run or teach B2B outbound systems.",
        "",
        "Copyright note: long verbatim YouTube transcripts are not stored in this repo. The transcript files contain source metadata, transcript availability, word counts, and short excerpts only.",
        "",
        "## Expert Source Index",
        "",
        "| Expert | Practitioner proof | Main link | YouTube source date | LinkedIn source date | Brief annotation |",
        "|---|---|---|---|---|---|",
    ]

    for expert, meta in EXPERTS.items():
        video = best_by_expert[expert]
        linkedin = linkedin_by_expert[expert]
        video_date = upload_dates.get(video["video_id"], "unknown")
        linkedin_date = linkedin["observed_post_age_or_date"]
        lines.append(
            "| {expert} | {proof} | {profile} | {video_date} | {linkedin_date} | {why} |".format(
                expert=expert,
                proof=meta["proof"],
                profile=meta["profile"],
                video_date=video_date,
                linkedin_date=linkedin_date,
                why=meta["why"],
            )
        )

    lines.extend(
        [
            "",
            "## Primary YouTube Sources",
            "",
            "| Expert | Video | Upload date | Transcript status | Source |",
            "|---|---|---|---|---|",
        ]
    )
    for expert in EXPERTS:
        video = best_by_expert[expert]
        status = video["caption_status"]
        word_count = video["transcript_word_count"] or "not available"
        lines.append(
            f"| {expert} | {video['title']} | {upload_dates.get(video['video_id'], 'unknown')} | {status}; {word_count} words | {video['url']} |"
        )

    lines.extend(
        [
            "",
            "## Public LinkedIn Sources",
            "",
            "| Expert | Public post | Observed date/age | Annotation |",
            "|---|---|---|---|",
        ]
    )
    for expert in EXPERTS:
        row = linkedin_by_expert[expert]
        lines.append(
            f"| {expert} | {row['source_url']} | {row['observed_post_age_or_date']} | {row['research_note']} |"
        )

    return "\n".join(lines)


def write_linkedin_posts(rows: list[dict[str, str]]) -> None:
    for row in rows:
        author_dir = LINKEDIN_DIR / slug(row["expert"])
        text = f"""# {row['expert']}: Public LinkedIn Post Source

Source: {row['source_url']}

Observed date/age: {row['observed_post_age_or_date']}

Capture status: {row['public_capture_status']}

Content theme:

{row['content_theme']}

Research use:

{row['research_note']}
"""
        write(author_dir / "post.md", text)


def write_youtube_files(
    rows: list[dict[str, str]],
    upload_dates: dict[str, str],
) -> None:
    index_lines = [
        "# YouTube Transcript Source Index",
        "",
        f"Snapshot date: {SNAPSHOT_DATE}",
        "",
        "These files are organized by video ID. Full transcripts are not stored; each file records the source, upload date, transcript status, word count, and a short excerpt.",
        "",
        "| Expert | Video | Upload date | Transcript status | File |",
        "|---|---|---|---|---|",
    ]

    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["video_id"], []).append(row)

    for video_id, source_rows in grouped.items():
        row = next(
            (
                item
                for item in source_rows
                if item["caption_status"] == "caption_found_youtube_transcript_api"
            ),
            source_rows[0],
        )
        title_slug = slug(row["title"], max_len=55)
        filename = f"{video_id}--{title_slug}.md"
        path = YOUTUBE_DIR / filename
        upload_date = upload_dates.get(video_id, "unknown")
        word_count = row["transcript_word_count"] or "not available"
        excerpt = row["transcript_excerpt_24_words"] or "No transcript excerpt available."
        experts = ", ".join(dict.fromkeys(item["expert"] for item in source_rows))
        collection_rows = "\n".join(
            f"- {item['expert']}: rank {item['video_rank']}, status {item['caption_status']}, {item['transcript_word_count'] or 'not available'} words"
            for item in source_rows
        )
        text = f"""# {row['title']}

Associated expert(s): {experts}

Video URL: {row['url']}

Video ID: {video_id}

Upload date: {upload_date}

Collected at: {row['collected_at_utc']}

Transcript status: {row['caption_status']}

Transcript language: {row['caption_language'] or 'unknown'}

Transcript word count: {word_count}

Short transcript excerpt:

> {excerpt}

Collection rows:

{collection_rows}

Notes:

- This is a transcript source file, not a full transcript dump.
- Full transcript text is intentionally not stored here because the videos are copyrighted source material.
- Use the video URL and transcript status above to retrieve the transcript through an approved API during private analysis.
"""
        write(path, text)
        index_lines.append(
            f"| {experts} | {row['title']} | {upload_date} | {row['caption_status']} | {filename} |"
        )

    write(YOUTUBE_DIR / "index.md", "\n".join(index_lines))


def write_other_files() -> None:
    shutil.copyfile(YOUTUBE_CSV, OTHER_DIR / "raw-youtube-sources.csv")
    shutil.copyfile(LINKEDIN_CSV, OTHER_DIR / "raw-linkedin-public-posts.csv")
    if OLD_SYNTHESIS.exists():
        shutil.copyfile(OLD_SYNTHESIS, OTHER_DIR / "content-synthesis.md")

    methodology = f"""# Collection Methodology

Snapshot date: {SNAPSHOT_DATE}

## YouTube

- Public YouTube search pages were used to identify candidate videos for each expert.
- `youtube-transcript-api` was used to check transcript availability and transcript word counts where captions were accessible.
- Full transcripts were not stored in this repository. The organized source files include metadata and short excerpts only.

## LinkedIn

- LinkedIn posts were collected from public/indexed post pages.
- Logged-in or private LinkedIn scraping was not used.
- If a source was only partially visible publicly, that limitation is marked in `raw-linkedin-public-posts.csv`.

## Why These Experts

The project topic is cold outreach pipeline for B2B SaaS. The experts were selected because they are operators, founders, agency builders, or sales trainers with direct outbound practice, not just commentary.
"""
    write(OTHER_DIR / "collection-methodology.md", methodology)


def main() -> None:
    youtube_rows = read_csv(YOUTUBE_CSV)
    linkedin_rows = read_csv(LINKEDIN_CSV)
    upload_dates = youtube_upload_dates(youtube_rows)

    write(RESEARCH / "sources.md", sources_md(youtube_rows, linkedin_rows, upload_dates))
    write_linkedin_posts(linkedin_rows)
    write_youtube_files(youtube_rows, upload_dates)
    write_other_files()

    print("Generated research files in", RESEARCH)


if __name__ == "__main__":
    main()

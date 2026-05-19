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

VIDEO_RESEARCH_NOTES = {
    "dDM80maP1N0": [
        "Use this as the main outbound pipeline source: it connects account selection, reasons for outreach, sequencing, and meeting conversion.",
        "The useful project takeaway is that outbound should be designed as a system with targeting, messaging, follow-up, and performance review, not as one-off cold emails.",
        "Add its ideas to the project sections on ICP, sequence design, reply handling, and meeting-booking KPIs.",
    ],
    "ibsqb3M9rT0": [
        "Use this for the phone/call layer of the pipeline.",
        "The key takeaway is that cold calls need a fast relevance hook, a clear problem hypothesis, and a direct next-step ask.",
        "Add this to the sequence as a call step after email or LinkedIn engagement signals.",
    ],
    "m2z1tgfv8Kc": [
        "Use this as a practical SaaS SDR script source.",
        "The useful takeaway is to structure calls around persona pain, a short opener, qualification, objection handling, and meeting conversion.",
        "Add this to the project as a sample call script and talk track.",
    ],
    "CLH1lfk_DQU": [
        "Use this for the 2026 outbound context section.",
        "The key takeaway is that AI increases outbound volume, so quality control, data hygiene, offer clarity, and channel mix become more important.",
        "Add this to the risk section: avoid generic AI blasting and protect the total addressable market.",
    ],
    "aaFjjDBBEzk": [
        "Use this for cold email copy and message relevance.",
        "The useful takeaway is that outreach should be built from the buyer's likely business problem, not from a product-feature pitch.",
        "Add this to the project as a before/after rewrite framework for cold emails.",
    ],
    "YYZUVbMbln8": [
        "Use this for intent-based prospecting.",
        "The key takeaway is to prioritize accounts using buying signals, product/community activity, hiring signals, and public trigger events.",
        "Add this to the lead scoring and account prioritization section.",
    ],
    "noRavDnWhr8": [
        "Use this as a broad prospecting fundamentals source.",
        "The useful takeaway is that consistent meeting generation depends on list quality, daily execution, strong personalization, and follow-up discipline.",
        "Add this to the operating cadence and SDR workflow section.",
    ],
    "Ag-6pB51s5o": [
        "Use this to show the difference between weak and strong cold email execution.",
        "The key takeaway is that experienced outbound operators make the buyer's context specific, reduce fluff, and ask for a simple next step.",
        "Add this to the email QA checklist.",
    ],
    "f9NSfp8M1P8": [
        "Use this as a tactical cold email checklist.",
        "The useful takeaway is that performance comes from many small details: list quality, relevant triggers, deliverability, concise copy, and clear testing.",
        "Add this to the campaign launch checklist.",
    ],
    "cfpLJqkmB6I": [
        "Use this for evidence that cold email is still useful when treated as a tested conversion channel.",
        "The key takeaway is to test offers, segments, copy angles, and infrastructure instead of assuming one template will work for every market.",
        "Add this to the experiment plan and KPI dashboard.",
    ],
    "3THIdISjTkk": [
        "Use this for signal testing in Clay or similar tooling.",
        "The useful takeaway is to test which intent signals actually predict replies before scaling a campaign.",
        "Add this to the data enrichment and scoring workflow.",
    ],
    "8i3OwYsp3vM": [
        "Use this as an automation workflow example.",
        "The key takeaway is that automation should enrich and route prospects, while humans still validate relevance and messaging quality.",
        "Add this to the AI-assisted workflow section.",
    ],
    "8YmzlSHX6vo": [
        "Use this for the outbound tech-stack section.",
        "The useful takeaway is that AI tools are most valuable when they reduce manual research, enrichment, routing, and campaign setup time.",
        "Add this to the recommended tool workflow for finding and preparing prospects.",
    ],
    "0q23Y0EyM5Y": [
        "Use this for lead generation strategy.",
        "The key takeaway is that B2B lead generation should start with a narrow ICP and a repeatable source of relevant prospects.",
        "Add this to the list-building and qualification process.",
    ],
    "C9aFa9kNENw": [
        "Use this for Clay-specific enrichment and workflow ideas.",
        "The useful takeaway is to rank tools and features by whether they improve signal quality, personalization, or speed to launch.",
        "Add this to the technical process map for enrichment.",
    ],
    "nWRvk-uiYq0": [
        "Use this for building an outbound service or internal outbound engine from zero.",
        "The key takeaway is to start with a tight niche, a simple offer, repeatable proof, and a clear acquisition workflow before scaling.",
        "Add this to the zero-to-one campaign launch plan.",
    ],
    "u0Fe2l1qBAI": [
        "Use this as a deep cold email campaign source.",
        "The useful takeaway is that high-performing campaigns depend on infrastructure, targeting, offer-market fit, copy testing, and consistent reporting.",
        "Add this to the project as the backbone for the deliverability and experimentation sections.",
    ],
    "15fX0czKypg": [
        "Use this for the operator view of running cold email as a business process.",
        "The key takeaway is to connect outbound activity to OKRs, learning loops, and revenue outcomes.",
        "Add this to the measurement and management section.",
    ],
    "dTZ87UJ1y1c": [
        "Use this for AI, warmup, and testing considerations.",
        "The useful takeaway is that AI and warmup tools do not replace fundamentals: relevant targeting, good domains, sound copy, and controlled experiments.",
        "Add this to the deliverability and AI guardrails section.",
    ],
    "XLsAAnNaFOc": [
        "Use this as a compact expert-advice source on cold email.",
        "The key takeaway is to combine concise copy, strong targeting, social proof, and disciplined follow-up.",
        "Add this to the final best-practices checklist.",
    ],
    "rXTd1DFoYGI": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use it only as a source pointer for Jack Reamer's cold email outreach content.",
        "If needed, manually review the video before citing specific claims.",
    ],
    "9_Isu6MNlio": [
        "Use this for copywriting and personalization principles.",
        "The useful takeaway is that cold outreach copy should be specific, easy to answer, and tied to a believable business reason.",
        "Add this to the cold email writing checklist.",
    ],
    "vhl5fWFUgf0": [
        "Use this for combined email and LinkedIn strategy.",
        "The key takeaway is that meetings are more likely when outreach uses multiple touchpoints and keeps the message consistent across channels.",
        "Add this to the multi-channel sequence section.",
    ],
    "k3fCuTaBCcw": [
        "Use this for LinkedIn cold outreach in agency-style prospecting.",
        "The useful takeaway is to warm up the profile, choose a narrow prospect segment, and use connection/message steps that do not feel automated.",
        "Add this to the LinkedIn touchpoints in the 14-day cadence.",
    ],
    "PltwHHbWMVo": [
        "Use this for Becc Holland's problem-led messaging approach.",
        "The key takeaway is that strong outbound starts with the buyer's unknown or under-prioritized problem, not the seller's product category.",
        "Add this to the buyer research template before copywriting.",
    ],
    "2yrkpp_uH2M": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use the source as a pointer for common cold email mistakes and pattern-breaking ideas.",
        "Manually review before adding exact examples to the project.",
    ],
    "xvgEXRZ7NRs": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use the source as a pointer for making cold email more differentiated.",
        "Manually review before citing specific tactics.",
    ],
    "VeiQFhr-1Oc": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use it as a pointer to Becc Holland's cold email training content.",
        "Manually review before using exact recommendations.",
    ],
    "yVyd07vdZ8c": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use the title/source as a pointer to Tito Bohrt's outbound success framework.",
        "Pair this with the collected LinkedIn post for citation-ready evidence on AI SDR noise and business acumen.",
    ],
    "Zxlk5s13ZX0": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use the source as a pointer for where AI fails in sales development.",
        "Pair this with Tito Bohrt's public LinkedIn source before making claims in the project.",
    ],
    "0jSdFJDFbxQ": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use it as a discovery-call source pointer, not as a cold email source.",
        "Only cite after manual review if the project includes post-reply discovery handling.",
    ],
    "8DQ6oLXp9RA": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use it as background on AltiSales and sales leadership, not as a primary outbound source.",
        "Keep it in supporting materials rather than the main project argument.",
    ],
    "XNcCkLdqjoc": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use it as a pointer to Guillaume Moubeche's cold email origin story.",
        "Pair this with lemlist/operator sources when discussing reply-focused outbound.",
    ],
    "1ceYB2XXbDk": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use it as a SaaS growth case-study pointer for lemlist.",
        "Keep the project takeaway high level unless manually reviewed.",
    ],
    "Sf6nOjQS0fk": [
        "No caption track was found, so this file is metadata-only.",
        "Use it as a pointer to Guillaume Moubeche's French-language cold mailing content.",
        "Do not use it as a primary source unless reviewed manually.",
    ],
    "IdJFUDNddv4": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use it as background on customer loss and SaaS learning loops, not as a primary outbound tactic source.",
        "Keep it in supporting materials.",
    ],
    "4MIBWWzGEKw": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use it as a pointer to Michael Maximoff's view that cold outreach needs repair through relevance and channel mix.",
        "Pair this with the Belkins benchmark LinkedIn source before citing.",
    ],
    "bzTjF7Dhu-I": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use it as a pointer for creative outbound ideas.",
        "Manually review before turning any idea into a playbook step.",
    ],
    "EdfXK1Phge8": [
        "Transcript was not retrievable, so do not treat this file as transcript-derived evidence.",
        "Use it as a pointer to cold email playbook design with Michael Maximoff.",
        "Pair with Belkins benchmark material for source-backed claims.",
    ],
}

VIDEO_SUMMARIES = {
    "dDM80maP1N0": "Jason Bay lays out a full outbound prospecting system for booking meetings in 2026. The video frames outbound as a pipeline process: pick the right accounts, find a real reason to reach out, use multiple touches, handle replies, and measure meetings rather than raw activity.",
    "ibsqb3M9rT0": "This video focuses on cold calling strategy for the current outbound environment. The main idea is that calls work better when the opener is relevant, the problem hypothesis is specific, and the rep quickly earns permission to continue instead of launching into a pitch.",
    "m2z1tgfv8Kc": "This is a practical cold calling course for SaaS sales reps. It walks through how to structure a call from opener to qualification to meeting ask, with emphasis on concise language, buyer pain, and objection handling.",
    "CLH1lfk_DQU": "This playbook discusses how AI is changing outbound and what teams should expect in 2026. The big takeaway is that AI raises the volume of outreach, which makes targeting, data quality, offer relevance, and multi-channel execution more important.",
    "aaFjjDBBEzk": "Florin Tatulea discusses what makes cold email work from an outbound operator's perspective. The video emphasizes buyer relevance, strong problem framing, simple copy, and avoiding product-heavy messages that do not connect to the prospect's situation.",
    "YYZUVbMbln8": "This video explains intent-based selling and how prospecting improves when outreach is triggered by signals. It is useful for building a lead scoring model around account activity, community engagement, hiring, funding, technology use, or other evidence of need.",
    "noRavDnWhr8": "This older but useful interview covers SDR prospecting fundamentals. The discussion centers on consistent execution, strong list quality, personalization, follow-up discipline, and the habits that turn outbound activity into meetings.",
    "Ag-6pB51s5o": "This video compares weaker cold email execution with a more experienced outbound approach. It is useful because it shows how better operators tighten the message, remove fluff, make the buyer context more specific, and ask for a clearer next step.",
    "f9NSfp8M1P8": "Eric Nowoslawski shares a dense set of cold email tactics based on high-volume campaign work. The video is best used as a campaign checklist covering list quality, deliverability, offer testing, personalization, copy length, and how to judge results.",
    "cfpLJqkmB6I": "This video summarizes lessons from sending millions of cold emails. The main argument is that cold email can still work, but only when teams test segments, offers, copy angles, sending infrastructure, and conversion outcomes instead of relying on a single template.",
    "3THIdISjTkk": "This video is about testing outbound signals with Clay. It shows why a team should validate which intent or enrichment signals predict replies before scaling a campaign, rather than assuming all personalization data is equally useful.",
    "8i3OwYsp3vM": "This short workflow video shows how cold email teams can use Clay to automate enrichment and campaign preparation. The useful point is that automation should support better research and routing, while humans still review whether the message is relevant.",
    "8YmzlSHX6vo": "Michel Lieben reviews AI sales tools and how they fit into a modern outbound workflow. The video is useful for mapping where AI can reduce manual work, especially in prospect research, enrichment, list building, personalization, and campaign operations.",
    "0q23Y0EyM5Y": "This video explains a B2B lead generation strategy from a systems point of view. The core lesson is to start with a narrow ICP, use repeatable sources for finding prospects, and build a workflow that turns qualified accounts into outreach opportunities.",
    "C9aFa9kNENw": "Michel Lieben ranks Clay features based on practical usefulness. For the project, the summary is that enrichment tools matter only when they improve signal quality, routing, personalization, or speed to launch.",
    "nWRvk-uiYq0": "This video explains how Michel Lieben would rebuild a cold email agency from zero. It is useful for the project because it highlights niche selection, a simple offer, repeatable proof, a clear acquisition workflow, and controlled scaling.",
    "u0Fe2l1qBAI": "Bill Stathopoulos discusses the mechanics behind large cold email campaigns. The video is useful as a deep source on campaign infrastructure, targeting, deliverability, offer-market fit, copy testing, and reporting.",
    "15fX0czKypg": "This conversation covers cold email from an operator and founder perspective. It connects outbound to company goals, OKRs, learning loops, experimentation, and the need to measure revenue outcomes rather than email activity alone.",
    "dTZ87UJ1y1c": "This video covers AI, email warmup, and experimentation in cold email. The main lesson is that tools can help, but fundamentals still decide performance: clean targeting, healthy domains, relevant copy, and controlled testing.",
    "XLsAAnNaFOc": "This video compresses years of cold email advice into a practical overview. It is useful as a final checklist source because it reinforces concise copy, strong targeting, credible proof, follow-up, and disciplined testing.",
    "rXTd1DFoYGI": "Transcript-derived summary is not available because captions were not found. Based on the metadata, this is a Jack Reamer source focused on cold email outreach and should be treated as a pointer until manually reviewed.",
    "9_Isu6MNlio": "This conversation with Jack Reamer focuses on copywriting for outbound. The practical takeaway is that cold emails should be easy to understand, specific to the buyer, tied to a real business reason, and simple to respond to.",
    "vhl5fWFUgf0": "This video covers how email and LinkedIn can work together to book meetings. The summary for the project is that outreach performs better when prospects see consistent, relevant touches across channels instead of isolated email blasts.",
    "k3fCuTaBCcw": "This video focuses on LinkedIn cold outreach for agencies. It is useful for building the LinkedIn part of the sequence: profile preparation, narrow targeting, connection steps, and messages that feel human rather than automated.",
    "PltwHHbWMVo": "Becc Holland explains how to build outbound around unknown or under-prioritized buyer problems. The key idea is to research the buyer's metrics and situation first, then lead with a problem hypothesis instead of a generic product pitch.",
    "2yrkpp_uH2M": "Transcript-derived summary is not available because captions could not be retrieved. Based on the title, this source appears to cover common cold email patterns that reduce replies and should be manually reviewed before citing specific examples.",
    "xvgEXRZ7NRs": "Transcript-derived summary is not available because captions could not be retrieved. Based on the title, this source appears to focus on making cold emails stand out, so it can be used as a pointer for differentiation tactics after manual review.",
    "VeiQFhr-1Oc": "Transcript-derived summary is not available because captions could not be retrieved. Based on the metadata, this is Becc Holland training content on cold emails and should be treated as a supporting source until reviewed.",
    "yVyd07vdZ8c": "Transcript-derived summary is not available because captions could not be retrieved. Based on the title, the video appears to frame outbound success around a small number of core pillars and should be paired with Tito Bohrt's LinkedIn source before citation.",
    "Zxlk5s13ZX0": "Transcript-derived summary is not available because captions could not be retrieved. Based on the title, this source appears to discuss where AI fails in modern sales development, especially when automation replaces judgment and business context.",
    "0jSdFJDFbxQ": "Transcript-derived summary is not available because captions could not be retrieved. Based on the title, this source is more about running discovery calls than cold outreach, so it is best used only if the project covers what happens after a positive reply.",
    "8DQ6oLXp9RA": "Transcript-derived summary is not available because captions could not be retrieved. Based on the metadata, this is background on AltiSales, sales leadership, and startup sales operations rather than a primary cold email tactic source.",
    "XNcCkLdqjoc": "Transcript-derived summary is not available because captions could not be retrieved. Based on the title, this source is useful as a pointer to Guillaume Moubeche's cold email origin story and lemlist's reply-focused positioning.",
    "1ceYB2XXbDk": "Transcript-derived summary is not available because captions could not be retrieved. Based on the metadata, this is a lemlist growth case study and can support the idea that cold outreach helped create early SaaS traction.",
    "Sf6nOjQS0fk": "Transcript-derived summary is not available because no caption track was found. Based on the title, this is French-language content about cold mailing from Guillaume Moubeche and should be manually reviewed before use.",
    "IdJFUDNddv4": "Transcript-derived summary is not available because captions could not be retrieved. Based on the title, this is more about customer loss and SaaS learning loops than outbound tactics, so it belongs in supporting materials.",
    "4MIBWWzGEKw": "Transcript-derived summary is not available because captions could not be retrieved. Based on the title and source metadata, this video is a pointer to Michael Maximoff's argument that cold outreach needs stronger relevance, personalization, and channel strategy.",
    "bzTjF7Dhu-I": "Transcript-derived summary is not available because captions could not be retrieved. Based on the title, this source likely covers creative outbound ideas and should be manually reviewed before adding tactics to the playbook.",
    "EdfXK1Phge8": "Transcript-derived summary is not available because captions could not be retrieved. Based on the title, this source is about building cold email playbooks with Michael Maximoff and should be paired with Belkins benchmark material for citation.",
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
        research_notes = "\n".join(
            f"- {note}" for note in VIDEO_RESEARCH_NOTES.get(video_id, [])
        )
        video_summary = VIDEO_SUMMARIES.get(
            video_id,
            "Summary is not available yet. Review the source manually before citing.",
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

Research notes:

Video summary: {video_summary}

{research_notes}

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

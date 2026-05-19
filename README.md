# Cursor, Claude Code, and Codex Setup

This repository documents the setup work I completed for Cursor, Claude Code, Codex, and GitHub.

## B2B SaaS Cold Outreach Research Project

I also used this repository to organize my hiring research project on:

**Cold outreach pipeline for B2B SaaS**

I chose this topic because it is closest to revenue: a strong project can show how to find qualified accounts, build lead lists, write relevant outbound messages, sequence email/LinkedIn/calls, and measure booked meetings or pipeline instead of vanity metrics.

### What I Collected

- [research/sources.md](research/sources.md) - source index for 10 cold outreach experts, with links, dates, practitioner proof, and short annotations.
- [research/linkedin-posts/](research/linkedin-posts/) - public LinkedIn post notes organized by author.
- [research/youtube-transcripts/](research/youtube-transcripts/) - YouTube transcript source files organized by video ID. These include video links, upload dates, transcript availability, word counts, and short excerpts.
- [research/other/](research/other/) - raw source CSVs, collection methodology, upload-date cache, and synthesis notes.

Full YouTube transcripts are not stored in this repo because the videos are copyrighted source material. The repo keeps source links and transcript metadata so the research can be verified and expanded through approved tools.

### Why These Experts

The experts were selected because they are practitioners, not just commentators. They include outbound agency founders, SaaS founders, sales trainers, and GTM operators who actively build or teach cold outreach systems:

- Jason Bay
- Florin Tatulea
- Eric Nowoslawski
- Michel Lieben
- Bill Stathopoulos
- Jack Reamer
- Becc Holland
- Tito Bohrt
- Guillaume Moubeche
- Michael Maximoff

The common pattern across their content is that modern outbound works best as a signal-based, multi-channel pipeline: strong ICP selection, buyer-specific research, clean data, deliverability controls, LinkedIn/email/call sequencing, and measurement around qualified replies and booked meetings.

## Tools I Installed

- Cursor IDE `3.2.21`
- Codex Cursor extension `openai.chatgpt@26.429.30905`
- GitHub CLI `gh 2.92.0`

I also attempted to add Claude Code in Cursor, but I could not complete the Claude Code setup because it required buying a paid Claude subscription.

Codex CLI was already installed on my machine, and I verified that it was logged in using ChatGPT.

## Steps I Completed

1. I installed Cursor IDE using Homebrew.
2. I opened Cursor and worked through the extension setup.
3. I attempted to add Claude Code in Cursor.
4. I installed the Codex extension in Cursor.
5. I verified Codex login status with the CLI: `Logged in using ChatGPT`.
6. I installed GitHub CLI.
7. I authenticated GitHub CLI with my GitHub account.
8. I created a public GitHub repository:
   `https://github.com/nomanbashir99/cursor-codex-setup`
9. I cloned the repository locally.
10. I opened the repository in Cursor.
11. I created this `README.md` file.

## Issues I Ran Into and How I Solved Them

- Cursor was not installed at the start.
  - I solved this by installing Cursor with `brew install --cask cursor`.

- The Cursor extension marketplace did not work on the first attempt because the network request was blocked.
  - I solved this by rerunning the extension installation with network permission.

- Claude Code could not be completed in Cursor.
  - I found out that Claude Code required a paid Claude subscription, so I documented the issue instead of completing that login/setup step.

- GitHub CLI was not installed.
  - I solved this by installing `gh` with Homebrew.

- GitHub CLI was not logged in.
  - I solved this by completing the GitHub device login flow and authenticating as `nomanbashir99`.

- The GitHub repository was empty after I created it.
  - I solved this by cloning it locally and adding this README as the first file.

# Agent Instructions

## Project

This repository contains the A.J. Vale X/Twitter draft and posting bot for `@TakeInvester1`.

The product goal is to generate literary, curiosity-first posts for A.J. Vale, an American author. The bot should make readers interested in the author's mind, worldview, atmosphere, recurring questions, and book universe without sounding like an advertisement.

## Core Voice Rules

Keep posts:

- literary, sharp, atmospheric, psychologically observant
- dystopian, speculative, philosophical, cinematic, elegant
- curiosity-first, not promotion-first
- subtle, memorable, and non-salesy

Avoid:

- `Buy now`
- `Available on Amazon now`
- `link in bio`
- hard CTA language
- spammy hashtags
- generic motivation posts
- robotic `as an author` phrasing
- direct product-pushing

Treat the catalog as creative source material, not ad inventory.

## Important Files

- `main.py` - CLI and optional FastAPI webhook entrypoint.
- `trigger_router.py` - validates triggers and returns structured draft output.
- `post_generator.py` - local draft generator and style logic.
- `scorer.py` - heuristic scoring for draft quality.
- `history_store.py` - local JSON history and duplicate detection.
- `prompts.py` - trigger definitions, style rules, avoided phrases, hashtags.
- `catalog.py` - editable catalog, aliases, motifs, and brand config.
- `x_client.py` - dry-run-first X API client.
- `.github/workflows/x-control.yml` - manual GitHub Actions workflow.
- `.github/workflows/x-autopost.yml` - scheduled GitHub Actions workflow.
- `github_control/README.md` - GitHub control instructions.
- `sample_payloads/` - sample input payloads.

## Local Commands

Generate a persona draft:

```bash
python3 main.py --trigger persona_post
```

Generate a book-adjacent draft:

```bash
python3 main.py --trigger book_echo --title "Cities of Judgment"
```

Turn a rough thought into drafts:

```bash
python3 main.py --trigger manual_note --note "machines can finish creation before humans finish meaning"
```

Dry-run a post action:

```bash
python3 main.py --trigger persona_post --post
```

Persist the recommended draft to local history:

```bash
python3 main.py --trigger persona_post --persist
```

Compile check:

```bash
python3 -m py_compile main.py trigger_router.py post_generator.py scorer.py history_store.py prompts.py catalog.py x_client.py
```

Optional webhook mode requires `fastapi` and `uvicorn` installed through `pip`, not `apt`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn
python main.py --webhook
```

## Supported Triggers

- `persona_post`
- `mood_post`
- `book_echo`
- `reader_question`
- `writing_update`
- `launch_whisper`
- `review_reflection`
- `cultural_observation`
- `manual_note`

Every trigger should return:

- 5 tweet options
- 1 recommended tweet
- 1 shorter version
- 1 more literary version
- 1 more accessible version
- optional light hashtag line
- rationale and score data

## X Posting Safety

The bot must remain safe by default.

Default local and GitHub behavior:

```text
DRY_RUN=true
AUTO_POST=false
```

Do not change defaults to live posting.

Live posting requires:

```text
DRY_RUN=false
AUTO_POST=true
valid X user-context credentials
```

Recommended X secrets:

```text
X_API_KEY
X_API_SECRET
X_ACCESS_TOKEN
X_ACCESS_TOKEN_SECRET
```

`X_BEARER_TOKEN` is only a fallback when it is a user-context token with the required write scope.

The X create-post endpoint is:

```text
POST https://api.x.com/2/tweets
```

## GitHub Actions Control

Manual control:

```text
.github/workflows/x-control.yml
```

Scheduled autopost:

```text
.github/workflows/x-autopost.yml
```

The scheduled workflow runs daily at:

```text
13:00 UTC
22:00 Asia/Tokyo
```

Autoposting is disabled unless this repository variable is exactly:

```text
ENABLE_X_AUTO_POST=true
```

To pause autoposting, set it to `false` or delete the variable.

## Editing Rules

- Keep edits small and practical.
- Preserve the non-promotional brand posture.
- Update `README.md` and `github_control/README.md` when workflow behavior changes.
- Run the compile check after Python edits.
- Do not commit credentials, `.env`, `post_history.json`, or generated cache files.
- Do not remove safety gates around posting.

## Catalog Notes

Catalog entries live in `catalog.py`. Keep aliases there, including:

```text
Dept Without Closure
Debt Without Closure
```

When adding titles, include motifs and atmosphere so the generator can create book-adjacent posts without summarizing or selling the book.

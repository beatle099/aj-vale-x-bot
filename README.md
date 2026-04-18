# A.J. Vale X Draft Bot

Production-ready Python tool for generating X/Twitter post drafts for `@TakeInvester1`, branded as A.J. Vale, an American author.

The tool is intentionally curiosity-first. It treats the catalog as creative source material, not ad inventory. Drafts should make readers more interested in the authorial mind, worldview, emotional atmosphere, recurring questions, and mythology around the books.

## What It Does

- Generates 5 tweet options for each supported trigger.
- Returns a recommended tweet, shorter version, more literary version, and more accessible version.
- Scores each draft on originality, brand fit, elegance, resonance, curiosity, subtle commercial value, and non-promotional quality.
- Rejects near-duplicates using local JSON history and configurable similarity threshold.
- Keeps `DRY_RUN=true` and `AUTO_POST=false` by default.
- Supports CLI usage and an optional FastAPI webhook.
- Supports manual GitHub Actions control from the repository UI.
- Keeps the book catalog editable in `catalog.py`, including aliases such as `Dept Without Closure` and `Debt Without Closure`.

## Files

- `main.py` - CLI and optional FastAPI webhook entrypoint.
- `trigger_router.py` - validates triggers, generates options, applies history duplicate checks.
- `post_generator.py` - local A.J. Vale-style draft generator.
- `scorer.py` - heuristic scoring model.
- `history_store.py` - JSON history and near-duplicate detection.
- `prompts.py` - style rules, avoid list, trigger definitions, hashtags.
- `catalog.py` - brand config, titles, aliases, motifs.
- `x_client.py` - dry-run-first X API client.
- `sample_payloads/` - ready-to-run JSON payloads.
- `.env.example` - configuration template.
- `.github/workflows/x-control.yml` - manual GitHub Actions control workflow.
- `github_control/` - instructions for running the bot from GitHub.

## Setup

This project works with the Python standard library for CLI draft generation.

Optional webhook dependencies:

```bash
pip install fastapi uvicorn
```

Copy the env template if you want local configuration:

```bash
cp .env.example .env
```

The default safety posture is:

```bash
DRY_RUN=true
AUTO_POST=false
```

## CLI Examples

Generate persona drafts:

```bash
python main.py --trigger persona_post
```

Generate a book-adjacent echo:

```bash
python main.py --trigger book_echo --title "The Last Prophet Machine"
```

Use a sample payload:

```bash
python main.py --payload sample_payloads/sample_manual_note.json
```

Persist the recommended draft to history:

```bash
python main.py --trigger mood_post --persist
```

Dry-run a post action:

```bash
python main.py --trigger reader_question --post
```

Actual posting requires all of these:

```bash
DRY_RUN=false
AUTO_POST=true
X_API_KEY=...
X_API_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_TOKEN_SECRET=...
```

## GitHub Actions Control

You can control the bot from GitHub without using your local terminal:

1. Open the repository on GitHub.
2. Go to `Actions`.
3. Select `A.J. Vale X Control`.
4. Click `Run workflow`.
5. Choose the trigger and optional title/note fields.
6. Leave `post_to_x=false` for draft-only mode.

The completed run uploads an `aj-vale-x-draft` artifact containing `draft_result.json`.

To enable direct posting from GitHub, add these repository secrets:

```text
X_API_KEY
X_API_SECRET
X_ACCESS_TOKEN
X_ACCESS_TOKEN_SECRET
```

Direct posting is still disabled unless the manual workflow input `post_to_x=true` is selected.

## Optional Webhook

Install optional dependencies first:

```bash
pip install fastapi uvicorn
```

Run:

```bash
python main.py --webhook
```

Then post JSON to:

```text
POST http://127.0.0.1:8000/generate
```

Example body:

```json
{
  "trigger": "book_echo",
  "title": "Cities of Judgment"
}
```

## Supported Triggers

- `persona_post` - deepen the A.J. Vale persona.
- `mood_post` - atmospheric standalone lines.
- `book_echo` - title-inspired post without plot summary.
- `reader_question` - questions that reveal the worldview.
- `writing_update` - writing/editing/worldbuilding progress.
- `launch_whisper` - restrained release or milestone announcement.
- `review_reflection` - reflective post from reader reaction.
- `cultural_observation` - real-world detail transformed through the brand lens.
- `manual_note` - rough thought polished into A.J. Vale-aligned drafts.

## Output Shape

Each run returns JSON:

```json
{
  "trigger": "book_echo",
  "options": [],
  "recommended_tweet": {},
  "shorter_version": {},
  "more_literary_version": {},
  "more_accessible_version": {},
  "optional_hashtag_line": "",
  "history_similarity": 0.0,
  "dry_run_note": "Draft generated only. Posting requires AUTO_POST=true and DRY_RUN=false."
}
```

## 20 Example Generated Tweets

1. The Last Prophet Machine is not about prediction as much as permission: the terrible moment when a future asks to be obeyed before it has earned belief.

2. A machine can speak like a prophet. The question is whether anyone remembers how to doubt beautifully.

3. The Last Prophet Machine began as a fear: that one day the future would stop arriving and start issuing instructions.

4. Prophecy becomes dangerous when it sounds less like thunder and more like policy.

5. Cities of Judgment: where every clean avenue seems to know what happened before the records were corrected.

6. Some cities do not bury their crimes. They zone them, rename them, and build excellent lighting nearby.

7. Judgment is easier to accept when the city has already taught you where to stand.

8. The First Room is the place before explanation, before defense, before the mind learns to decorate fear.

9. A person builds many rooms. The first one is usually made from what they were too young to name.

10. The Last Room waits after argument, after belief, after the final witness forgets why the door was locked.

11. Every ending imagines itself as a door. The Last Room knows some doors are only walls with better manners.

12. The Sparks of Eternity asks whether the soul is a flame, a memory, or the old habit of rising after darkness.

13. Eternity may not be endless time. It may be the one spark in us that refuses to become evidence.

14. The First Uninvented Idea begins where creation becomes automatic and meaning is left standing outside the factory.

15. When the machines finished creating, the silence afterward belonged to the first idea no one could manufacture.

16. The most frightening invention may be the one that teaches us originality was never the same thing as wonder.

17. Whispers Between Worlds is the sound of something almost remembered asking not to be translated too quickly.

18. Some worlds do not collide. They whisper until one life begins to answer for another.

19. Between worlds, language becomes less certain and more honest.

20. A.J. Vale's catalog keeps circling the same pressure: rooms, machines, cities, sparks, whispers, and the human need to explain what explanation cannot hold.

## Editorial Rules

Avoid hard CTA language, spammy hashtags, generic motivation, robotic phrasing, and obvious sales posture. Occasional mentions of Amazon or Kindle can be added manually when subtle, but the generator defaults away from them.

The most valuable draft is not the one that sells hardest. It is the one that makes a reader remember the author name, click the profile, recognize a title later, and feel that the books belong to one coherent worldview.

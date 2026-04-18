# GitHub X Account Control

This directory documents how to control the A.J. Vale X draft bot from GitHub Actions.

The workflow lives at:

```text
.github/workflows/x-control.yml
```

## Safe Default

The workflow defaults to draft-only mode:

```text
DRY_RUN=true
AUTO_POST=false
```

Running it without `post_to_x=true` will generate a JSON artifact with drafts. It will not post to X.

## How To Run From GitHub

1. Open the repository on GitHub.
2. Go to `Actions`.
3. Select `A.J. Vale X Control`.
4. Click `Run workflow`.
5. Choose a trigger such as `persona_post`, `book_echo`, or `manual_note`.
6. Optionally enter a title, note, or review excerpt.
7. Keep `post_to_x=false` to generate drafts only.
8. Download the `aj-vale-x-draft` artifact from the completed workflow run.

## Required Secrets For Posting

To post directly to X from GitHub, add repository secrets:

```text
X_API_KEY
X_API_SECRET
X_ACCESS_TOKEN
X_ACCESS_TOKEN_SECRET
```

These should be X API user-context credentials with write access. The workflow also supports `X_BEARER_TOKEN` as a fallback only when it is a user-context token with the correct write scope.

## Posting Guardrails

Direct posting only happens when all of these are true:

```text
post_to_x=true
DRY_RUN=false
AUTO_POST=true
valid X credentials are present
```

The workflow is manual-only through `workflow_dispatch`. It does not schedule posts by itself.

## Recommended Use

Use draft-only mode most of the time. Review the generated `recommended_tweet`, `shorter_version`, `more_literary_version`, and `more_accessible_version` before posting.

Use direct posting only for low-risk, already-reviewed content.

"""Prompt and style guidance used by the local generator and optional LLM flows."""

AVOID_PHRASES = [
    "buy now",
    "available on amazon now",
    "link in bio",
    "as an author",
    "must-read",
    "don't miss",
    "limited time",
    "grab your copy",
    "new release alert",
]

SOFT_HASHTAGS = [
    "#SpeculativeFiction",
    "#DystopianFiction",
    "#AuthorLife",
    "#AmWriting",
]

STYLE_RULES = """
Write as A.J. Vale: literary, sharp, atmospheric, psychologically observant.
Use intrigue over explanation, aura over pitch, identity over advertisement.
Treat the catalog as creative source material, not ad inventory.
Never use hard sales language. Prefer 0-1 hashtag, never more than 2.
Default to 260 characters or fewer.
"""

TRIGGER_INTENTS = {
    "persona_post": "deepen the A.J. Vale persona through conviction, tension, or observation",
    "mood_post": "produce atmospheric standalone lines that feel quotable",
    "book_echo": "amplify the emotional or philosophical gravity around one title",
    "reader_question": "ask a question that invites readers into the worldview",
    "writing_update": "share writing progress without routine productivity language",
    "launch_whisper": "announce a release or milestone as an opening, not a campaign",
    "review_reflection": "turn reader reaction into reflection on emotional effect",
    "cultural_observation": "transform a real-world detail into an A.J. Vale reflection",
    "manual_note": "polish a rough thought into aligned tweet drafts",
}

OPTION_LABELS = [
    "primary",
    "shorter",
    "more_literary",
    "more_accessible",
    "catalog_bridge",
]

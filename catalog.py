"""Editable catalog and brand configuration for the A.J. Vale draft bot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Book:
    title: str
    aliases: List[str] = field(default_factory=list)
    motifs: List[str] = field(default_factory=list)
    atmosphere: str = ""


BRAND = {
    "handle": "@TakeInvester1",
    "name": "A.J. Vale",
    "role": "American author",
    "voice": [
        "literary",
        "sharp",
        "atmospheric",
        "psychologically observant",
        "intelligent",
        "memorable",
    ],
    "mood": [
        "dystopian",
        "speculative",
        "philosophical",
        "cinematic",
        "elegant",
        "quietly intense",
    ],
    "primary_language": "English",
}


CATALOG: List[Book] = [
    Book(
        "The Last Prophet Machine",
        motifs=["prophecy", "machines", "conscience", "future", "permission"],
        atmosphere="mechanical prophecy under a human sky",
    ),
    Book(
        "Cities of Judgment",
        motifs=["cities", "order", "crime", "judgment", "public silence"],
        atmosphere="civilization wearing a calm face over violence",
    ),
    Book(
        "The First Room",
        motifs=["rooms", "origin", "fear", "memory", "threshold"],
        atmosphere="the first private architecture of dread",
    ),
    Book(
        "Debt Without Closure",
        aliases=["Dept Without Closure"],
        motifs=["debt", "closure", "accounting", "unfinished guilt", "records"],
        atmosphere="a ledger that refuses to become history",
    ),
    Book(
        "The Last Room",
        motifs=["final rooms", "ending", "witness", "silence", "locked memory"],
        atmosphere="the room left after every answer has failed",
    ),
    Book(
        "The Sparks of Eternity: A Mythic Journey Through the Ages of the Soul",
        aliases=["The Sparks of Eternity"],
        motifs=["soul", "eternity", "myth", "sparks", "ages"],
        atmosphere="ancient fire moving through human time",
    ),
    Book(
        "The First Uninvented Idea: When the Machines Finished Creating",
        aliases=["The First Uninvented Idea"],
        motifs=["invention", "machines", "creation", "meaning", "last originality"],
        atmosphere="the silence after creation becomes automated",
    ),
    Book(
        "Whispers Between Worlds",
        motifs=["whispers", "worlds", "thresholds", "dreams", "hidden speech"],
        atmosphere="a voice crossing from somewhere almost remembered",
    ),
]


def canonical_title(value: Optional[str]) -> Optional[str]:
    """Return the canonical catalog title for a title or alias."""
    if not value:
        return None
    normalized = value.strip().casefold()
    for book in CATALOG:
        names = [book.title, *book.aliases]
        if normalized in {name.casefold() for name in names}:
            return book.title
    return value.strip()


def get_book(value: Optional[str]) -> Optional[Book]:
    """Find a book by title or alias."""
    title = canonical_title(value)
    if not title:
        return None
    for book in CATALOG:
        if book.title == title:
            return book
    return None


def catalog_index() -> Dict[str, Book]:
    """Return a lookup that includes aliases."""
    index: Dict[str, Book] = {}
    for book in CATALOG:
        for name in [book.title, *book.aliases]:
            index[name.casefold()] = book
    return index

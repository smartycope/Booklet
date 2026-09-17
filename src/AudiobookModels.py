from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import time
from typing import Any, Iterable


def value(obj: Any, *names: str, default=None):
    """Read the first matching key/attribute from API objects or dictionaries."""
    for name in names:
        if isinstance(obj, dict) and name in obj:
            return obj[name]
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


@dataclass(slots=True)
class Series:
    id: str
    name: str
    sequence: str | None = None


@dataclass(slots=True)
class Chapter:
    title: str
    start: float
    end: float


@dataclass(slots=True)
class Track:
    title: str
    source: str
    duration: float
    start_offset: float = 0.0
    mime_type: str | None = None


@dataclass(slots=True)
class Book:
    id: str
    title: str
    authors: list[str] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    series: list[Series] = field(default_factory=list)
    added_at: int = 0
    duration: float = 0.0
    tracks: list[Track] = field(default_factory=list)
    chapters: list[Chapter] = field(default_factory=list)

    @classmethod
    def from_api(cls, item: Any) -> "Book":
        media = value(item, "media", default={}) or {}
        metadata = value(media, "metadata", default={}) or {}
        title = value(metadata, "title", default="Untitled") or "Untitled"

        authors = value(metadata, "authors", default=[]) or []
        author_names = [
            str(value(author, "name", default=author))
            for author in authors
        ]
        if not author_names:
            author_name = value(metadata, "author_name", "authorName")
            if author_name:
                author_names = [str(author_name)]

        series_items = []
        for series in value(metadata, "series", default=[]) or []:
            series_items.append(
                Series(
                    id=str(value(series, "id_", "id", default="")),
                    name=str(value(series, "name", default="Untitled Series")),
                    sequence=value(series, "sequence"),
                )
            )

        tracks = []
        for track in value(media, "tracks", default=[]) or []:
            tracks.append(
                Track(
                    title=str(value(track, "title", default="Audio")),
                    source=str(value(track, "content_url", "contentUrl", default="")),
                    duration=float(value(track, "duration", default=0) or 0),
                    start_offset=float(value(track, "start_offset", "startOffset", default=0) or 0),
                    mime_type=value(track, "mime_type", "mimeType"),
                )
            )

        chapters = []
        for chapter in value(media, "chapters", default=[]) or value(item, "chapters", default=[]) or []:
            chapters.append(
                Chapter(
                    title=str(value(chapter, "title", default="Chapter")),
                    start=float(value(chapter, "start", default=0) or 0),
                    end=float(value(chapter, "end", default=0) or 0),
                )
            )

        return cls(
            id=str(value(item, "id_", "id", "library_item_id", "libraryItemId", default="")),
            title=str(title),
            authors=author_names,
            genres=[str(genre) for genre in (value(metadata, "genres", default=[]) or [])],
            series=series_items,
            added_at=int(value(item, "added_at", "addedAt", default=0) or 0),
            duration=float(value(media, "duration", default=value(item, "duration", default=0)) or 0),
            tracks=tracks,
            chapters=chapters,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Book":
        return cls(
            id=data["id"],
            title=data["title"],
            authors=list(data.get("authors", [])),
            genres=list(data.get("genres", [])),
            series=[Series(**item) for item in data.get("series", [])],
            added_at=int(data.get("added_at", 0)),
            duration=float(data.get("duration", 0)),
            tracks=[Track(**item) for item in data.get("tracks", [])],
            chapters=[Chapter(**item) for item in data.get("chapters", [])],
        )

    def with_sources(self, sources: Iterable[str | Path]) -> "Book":
        local_sources = [str(source) for source in sources]
        tracks = []
        for index, source in enumerate(local_sources):
            original = self.tracks[index] if index < len(self.tracks) else None
            tracks.append(
                Track(
                    title=original.title if original else Path(source).name,
                    source=source,
                    duration=original.duration if original else 0.0,
                    start_offset=original.start_offset if original else sum(t.duration for t in tracks),
                    mime_type=original.mime_type if original else None,
                )
            )
        copy = Book.from_dict(self.to_dict())
        copy.tracks = tracks
        return copy


@dataclass(slots=True)
class PlaybackSession:
    id: str
    book: Book
    current_time: float
    duration: float


@dataclass(slots=True)
class PlaybackContext:
    book: Book
    local: bool
    session_id: str | None = None
    back_route: str | tuple[str, dict[str, Any]] = "AudiobookshelfLanding"
    last_sync_position: float = 0.0
    last_sync_at: float = field(default_factory=time.monotonic)
    was_playing: bool = False
    pending_listened: float = 0.0

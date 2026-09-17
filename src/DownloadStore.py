from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

from src import CONFIG
from src.AudiobookModels import Book


AUDIO_EXTENSIONS = {".flac", ".m4a", ".m4b", ".mp3", ".ogg", ".opus", ".wav"} # ".aac"


class DownloadStore:
    manifest_name = "booklet.json"

    def __init__(self, root: str | Path | None = None):
        configured = root or CONFIG.get("download_directory") or (Path.home() / "Audiobooks")
        self.root = Path(configured).expanduser().absolute()

    def book_dir(self, book_id: str) -> Path:
        if not book_id or Path(book_id).name != book_id or book_id in {".", ".."}:
            raise ValueError("Invalid audiobook ID")
        return self.root / book_id

    def contains(self, book_id: str) -> bool:
        return (self.book_dir(book_id) / self.manifest_name).is_file()

    def load(self, book_id: str) -> Book:
        directory = self.book_dir(book_id)
        data = json.loads((directory / self.manifest_name).read_text())
        book = Book.from_dict(data["book"])
        sources = [directory / relative for relative in data["audio_files"]]
        if not sources or not all(source.is_file() for source in sources):
            raise RuntimeError(f"Downloaded files for {book.title} are incomplete")
        return book.with_sources(sources)

    def list_books(self) -> list[Book]:
        if not self.root.exists():
            return []
        books = []
        for manifest in self.root.glob(f"*/{self.manifest_name}"):
            try:
                books.append(self.load(manifest.parent.name))
            except (OSError, RuntimeError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                continue
        return sorted(books, key=lambda book: book.title.casefold())

    async def download(self, api, book: Book, progress=None) -> Book:
        if self.contains(book.id):
            return self.load(book.id)

        self.root.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=f".{book.id}-", dir=self.root))
        archive = temporary / "download.part"
        content_type = ""
        filename = ""
        try:
            filename, content_type = await api.download_book(book.id, archive, progress)
            staging = temporary / "book"
            staging.mkdir()
            is_zip = content_type.startswith("application/zip") or filename.casefold().endswith(".zip")
            if is_zip:
                self._safe_extract(archive, staging)
                archive.unlink()
            else:
                suffix = Path(filename).suffix or ".m4b"
                archive.replace(staging / f"audio{suffix}")

            audio_files = sorted(
                path for path in staging.rglob("*")
                if path.is_file() and path.suffix.casefold() in AUDIO_EXTENSIONS
            )
            if not audio_files:
                raise RuntimeError("The download did not contain a supported audio file")

            audio_files = self._order_audio_files(book, audio_files)
            relative_files = [str(path.relative_to(staging)) for path in audio_files]
            manifest = {"version": 1, "book": book.to_dict(), "audio_files": relative_files}
            (staging / self.manifest_name).write_text(json.dumps(manifest, indent=2))
            os.replace(staging, self.book_dir(book.id))
            return self.load(book.id)
        except BaseException:
            shutil.rmtree(temporary, ignore_errors=True)
            raise
        finally:
            if temporary.exists():
                shutil.rmtree(temporary, ignore_errors=True)

    @staticmethod
    def _safe_extract(archive: Path, destination: Path) -> None:
        destination = destination.resolve()
        with zipfile.ZipFile(archive) as zipped:
            for member in zipped.infolist():
                target = (destination / member.filename).resolve()
                if not target.is_relative_to(destination):
                    raise RuntimeError("Unsafe path in audiobook archive")
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with zipped.open(member) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)

    @staticmethod
    def _order_audio_files(book: Book, files: list[Path]) -> list[Path]:
        by_name: dict[str, list[Path]] = {}
        for path in files:
            by_name.setdefault(path.name.casefold(), []).append(path)
        ordered = []
        for track in book.tracks:
            matches = by_name.get(Path(track.title).name.casefold(), [])
            if matches:
                ordered.append(matches.pop(0))
        ordered.extend(path for path in files if path not in ordered)
        return ordered

    def delete(self, book_id: str) -> None:
        directory = self.book_dir(book_id)
        if directory.exists():
            shutil.rmtree(directory)

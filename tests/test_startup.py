import asyncio
from unittest.mock import AsyncMock

import src.__main__ as app


def test_api_connection_failure_enters_offline_mode(monkeypatch):
    error = OSError("server unavailable")
    create = AsyncMock(side_effect=error)
    monkeypatch.setattr(app.AudiobookshelfApiManager, "create", create)

    api = asyncio.run(app.connect_audiobookshelf(object()))

    assert api is None
    assert app.AUDIOBOOKSHELF_CONNECTION_ERROR is error
    create.assert_awaited_once()


def test_successful_api_connection_clears_previous_error(monkeypatch):
    expected = object()
    app.AUDIOBOOKSHELF_CONNECTION_ERROR = OSError("old failure")
    monkeypatch.setattr(
        app.AudiobookshelfApiManager,
        "create",
        AsyncMock(return_value=expected),
    )

    assert asyncio.run(app.connect_audiobookshelf(object())) is expected
    assert app.AUDIOBOOKSHELF_CONNECTION_ERROR is None

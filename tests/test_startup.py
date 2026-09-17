import asyncio
from unittest.mock import AsyncMock

import src.__main__ as app


def test_api_connection_failure_enters_offline_mode(monkeypatch):
    create = AsyncMock(side_effect=OSError("server unavailable"))
    monkeypatch.setattr(app.AudiobookshelfApiManager, "create", create)

    api = asyncio.run(app.connect_audiobookshelf(object()))

    assert api is None
    create.assert_awaited_once()

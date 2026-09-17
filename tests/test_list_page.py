import asyncio

from src.pages.ListPage import ListPage


def test_list_page_preserves_duplicate_labels_and_values():
    page = asyncio.run(ListPage(items=[("Same", 1), ("Same", 2)], scrollable=True))
    assert page.items == ["Same", "Same"]
    assert page.selected_value == 1
    asyncio.run(page.down_pressed())
    assert page.selected_value == 2


def test_empty_list_does_not_navigate_or_raise():
    page = asyncio.run(ListPage(items=[], scrollable=True, empty_text="Nothing here"))
    assert page.selected_item is None
    assert asyncio.run(page.down_pressed()) is None
    assert asyncio.run(page.center_pressed()) is None

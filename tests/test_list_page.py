import asyncio

import src.pages.ListPage as list_page_module
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


def test_viewport_only_moves_when_selection_reaches_an_edge():
    page = asyncio.run(ListPage(items=[f"Item {index}" for index in range(20)], scrollable=True))
    visible = page._visible_count()
    for _ in range(visible - 1):
        asyncio.run(page.down_pressed())
    assert page._first_visible_index == 0

    asyncio.run(page.down_pressed())
    assert page._first_visible_index == 1
    asyncio.run(page.up_pressed())
    assert page._first_visible_index == 1
    for _ in range(visible - 1):
        asyncio.run(page.up_pressed())
    assert page._first_visible_index == 0


def test_jump_selection_clamps_instead_of_wrapping():
    page = asyncio.run(ListPage(items=[str(index) for index in range(12)], scrollable=True))
    page.move_selection(10)
    assert page.selected_index == 10
    page.move_selection(10)
    assert page.selected_index == 11
    page.move_selection(-20)
    assert page.selected_index == 0


def test_marquee_reverses_after_reaching_the_end(monkeypatch):
    page = asyncio.run(ListPage(items=["A title much wider than the display " * 3], scrollable=True))
    page._selection_changed_at = 0
    available = 100
    overflow = round(page.draw.textlength(page.selected_item, font=page.font) - available)
    travel = overflow / page.marquee_speed
    reverse_start = page.marquee_delay + travel + page.marquee_delay

    monkeypatch.setattr(list_page_module.time, "monotonic", lambda: reverse_start + 0.01)
    near_end = page._marquee_offset(page.selected_item, available)
    monkeypatch.setattr(list_page_module.time, "monotonic", lambda: reverse_start + travel / 2)
    moving_back = page._marquee_offset(page.selected_item, available)
    assert near_end > moving_back > 0

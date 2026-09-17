# Booklet Development Guide

## Project Scope

Booklet is a Python 3.12+ handheld audiobook player targeting a Raspberry Pi Zero 2 W and a 240x240 Waveshare LCD HAT. It connects to Audiobookshelf for browsing, streaming, downloads, resume positions, and progress synchronization. Podcasts are out of scope.

Preserve the existing async page-routing architecture and the hardware/simulated-screen split. Keep changes focused and do not discard unrelated staged or unstaged work. In particular, the repository's `booklet` file is a live shelve database and must not be rewritten, deleted, or treated as source code.

## Runtime and Configuration

- Run the application with `python -m src`.
- Python dependencies are in `requirements.txt`; development dependencies are in `dev-requirements.txt`.
- `python-vlc` is only the Python binding. The target system must also have VLC/libVLC installed.
- Read-only deployment configuration comes from `~/booklet_config.json` on the Pi and the repository copy in debug mode. Existing keys include:
  - `audiobookshelf_url`
  - `audiobookshelf_api_key`
  - `audiobookshelf_library_name`
  - optional `download_directory`, defaulting to `~/Audiobooks`
- Stable runtime state is stored in the `CONFIG` shelve opened by `src/constants.py`. Current keys include:
  - `library_id`
  - `current_book`
  - `local_positions`
  - `playback_speeds`, a dictionary of library-item ID to rate
  - `default_playback_speed`, default `1.0`
  - `volume`
  - `brightness`
  - `screensaver_timeout`, default `30` seconds
- Persist only stable, serializable values. Never shelve Audiobookshelf response objects, aiohttp sessions, page instances, VLC objects, or running tasks.

## Async Page and Navigation Contract

- All page input handlers are `async def`, including pressed, released, and held handlers.
- Pages with async constructors inherit `aobject`; construct them with `await`.
- A handler returns:
  - a route string, such as `"Landing"`;
  - `(route_name, kwargs)` for a parameterized route;
  - `True` when the current image changed and must be rendered;
  - `None` or `False` when nothing changed.
- `GuiManager.page()` resolves a route with `globals()[name + "Page"]`. Every routable page must therefore be imported into `src/GuiManager.py`.
- Use `on_enter()` and `on_exit()` for refresh loops, cancellation, playback synchronization, and other page lifecycle work. Do not leave orphan tasks.
- `GuiManager` displays `LoadingPage` while a route is being constructed and suppresses duplicate input while an event or navigation is active. Retain this guard around slow requests.
- `ScreensaverPage` is an overlay, not ordinary navigation. It keeps the exact underlying page alive, powers off the display, and consumes the first input only to wake and restore that page.
- All pages may time out to the screensaver except `DownloadBookPage`, `BluetoothPage`, `LoadingPage`, and the screensaver itself.

## Rendering and List Pages

- UI rendering uses Pillow and the dimensions/constants in `src/constants.py`.
- `ListPage` accepts strings, dictionaries, or ordered `(label, value)` entries. Ordered entries are required when duplicate visible labels are possible.
- Use `selected_value` for routing or actions; labels are presentation only.
- Empty lists must remain drawable and all input handlers must be safe.
- `ListPage` owns:
  - edge-aware viewport movement;
  - the non-interactive scrollbar;
  - held up/down repeat;
  - selected-row marquee timing;
  - jump controls and viewport tracking.
- Long selected labels marquee after a delay, pause at the far edge, and slide backward rather than jumping to the beginning.
- Audiobook cloud lists currently use left to return and right/center to select. Preserve the checked-in direction unless the user explicitly changes it again.
- Settings is intentionally different from ordinary lists: the selected row is outlined instead of filled.

## Audiobookshelf Pages and Routes

The current cloud hierarchy is:

- `AudiobookshelfLandingPage`
- `SelectCloudBookPage(download=...)`
  - `SelectInProgressBookPage`
  - `SelectRecentlyAddedPage`
  - `SelectAllBooksPage`
  - `ChooseByAuthorPage`
    - `ChooseAuthorsBooksPage`
  - `ChooseFromGenrePage`
    - `ChooseGenreBooksPage`
  - `ChooseFromSeriesPage`
- `DownloadBookPage` or `PlayerPage`
- `SelectDownloadedBookPage` and `DeleteDownloadedBookPage`

Always preserve the exact `back_route` payload rather than reconstructing an assumed parent route.

Caching rules:

- `AudiobookshelfApiManager.get_books()` caches the normalized all-books list until explicitly refreshed.
- `AudiobookshelfApiManager.get_authors()` caches the normalized author index until explicitly refreshed.
- `ChooseByAuthorPage` contains its refresh entry.
- `ChooseAuthorsBooksPage` does not cache author-specific book results and must not contain the author-index refresh control.
- Do not reintroduce the old `ChooseFromAuthorPage` or `ChooseAuthorBooksPage` route names.

## API Layer

- Prefer `aioaudiobookshelf` where its endpoint and schema support are sufficient.
- Use the manager's shared authenticated `aiohttp.ClientSession` for missing endpoints.
- Normalize API data into the dataclasses in `src/AudiobookModels.py`; do not leak inconsistent raw dictionaries through pages.
- The manager owns the host, API token, library ID, caches, and HTTP session references.
- VLC stream URLs use Audiobookshelf's authenticated GET token query mechanism because VLC cannot reliably attach the Bearer header.
- Expanded `Book.media.size` is the authoritative expected download byte count. Do not assume the item-download response supplies a useful `Content-Length`.

## Downloads

- Downloads live under `download_directory/<item-id>/` with `booklet.json` and ordered audio files.
- `DownloadStore` must retain atomic publication, temporary staging, cleanup on failure/cancellation, ZIP traversal rejection, playable-audio validation, and manifest compatibility.
- Never call Audiobookshelf's server-side delete endpoint. Deletion removes only the selected local item-ID directory and requires a center hold.
- `DownloadBookPage` uses `Book.size` for the total, displays binary-scaled `KB`/`MB`/`GB`, and only shows a percentage when the total is known.
- Center-hold cancels an active download, waits for temporary cleanup, and returns through the exact previous route.

## Playback

- `AudioPlayer` is the VLC/libVLC adapter and presents one global timeline across multiple tracks.
- Keep track transitions, cross-file seeking, chapter navigation, rate, volume, and completion logic inside the adapter rather than duplicating them in pages.
- `PlayerPage` refreshes once per second and synchronizes active playback every 15 seconds only while playing.
- Pausing, seeking, changing chapters, or exiting may still trigger an immediate final sync.
- Streaming sessions remain open when leaving the player, but are closed when switching books or shutting down.
- Downloaded playback uses local fallback positions when the server is unavailable.
- Playback speed is restored from `CONFIG["playback_speeds"][book_id]`, falling back to `default_playback_speed`. Persist a book's rate whenever the player changes it.
- Current player controls are defined by `PlayerPage`; inspect that file before changing mappings because they have evolved during development.

## Settings and Screensaver

- `SettingsPage` inherits `ListPage` but renders its own rows.
- Up/down changes selection.
- Left/right decreases/increases brightness, volume, default playback speed, and screensaver timeout directly on the page.
- Adjustable rows use a full-width split bar: white text on black for the completed portion and black text on white for the remainder.
- Center activates Check for updates, Bluetooth, or Back. The update action asynchronously runs `git pull` with the current working directory as the repository root. Key 2 also returns to `Landing`.
- Brightness changes update the screen, volume changes update VLC, and every value is persisted in `CONFIG`.
- The screensaver timeout is configurable in Settings and defaults to 30 seconds.
- Waking must not forward the wake event to the restored page.
- Screensaving during playback must not pause playback or discard the player page's state.

## Bluetooth

- `BluetoothPage` is exempt from screensaving while pairing, scanning, connecting, or disconnecting.
- Pairing may connect as part of `Device1.Pair()`. Refresh state before issuing a separate connect.
- Hardware pairing behavior cannot be considered verified solely from mocked tests; use `bluetoothctl` to isolate remote-device or BlueZ authentication failures.

## Testing and Validation

- Run tests from an isolated working directory because importing from the checkout root opens the existing `booklet` shelve, whose `dbm.gnu` backend may be unavailable in another interpreter.
- Recommended commands:

  ```bash
  cd /tmp
  PYTHONPATH=/home/zeke/hello/Booklet python -m pytest -q /home/zeke/hello/Booklet/tests
  python -m compileall -q /home/zeke/hello/Booklet/src /home/zeke/hello/Booklet/tests
  git -C /home/zeke/hello/Booklet diff --check
  git -C /home/zeke/hello/Booklet diff --cached --check
  ```

- Use the project interpreter that has `aioaudiobookshelf`, `python-vlc`, `dbus-next`, and the development requirements installed.
- Keep API tests network-free unless explicitly performing a read-only integration check.
- Use fake VLC adapters for player tests and fake managers/APIs/screens for page and lifecycle tests.
- Validate visual changes at the native 240x240 resolution in addition to behavioral assertions.
- Physical speaker output, LCD backlight, GPIO, and Bluetooth still require final Raspberry Pi hardware validation.

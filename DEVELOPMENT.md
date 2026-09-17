# Booklet Project Structure

Booklet is a small, hardware-oriented Python application that turns a Raspberry Pi into an Audiobookshelf client. The UI is rendered as 240x240 Pillow images, input comes from the buttons on the display HAT, and audio is played through VLC/libVLC.

The application has four main layers:

1. `GuiManager` connects hardware events to pages and handles navigation.
2. Pages render the user interface and translate button presses into actions or routes.
3. Audiobook services handle the server API, downloads, normalized data, and VLC playback.
4. Screen and Bluetooth adapters isolate Raspberry Pi hardware from the simulated development environment.

## Starting the Application

`python -m src` runs `src/__main__.py`.

Startup performs the following work:

1. Selects `SimulatedScreen` on the development machine or `Screen` on the Raspberry Pi.
2. Creates the VLC-backed `AudioPlayer`.
3. Opens one shared `aiohttp.ClientSession`.
4. Creates `AudiobookshelfApiManager` and resolves the configured library.
5. Creates `GuiManager` with `LandingPage` as the first page.
6. Starts listening for screen/button events.

Shutdown exits the visible page, synchronizes and closes active playback, stops VLC, and then lets the shared HTTP session close.

## Source Tree at a Glance

```text
src/
├── __main__.py                    Application startup and shutdown
├── constants.py                   Display theme, dimensions, config, and shelve state
├── GuiManager.py                  Event dispatch, routes, loading, screensaver, playback lifecycle
├── AudiobookModels.py             Normalized Book, Track, Chapter, Series, and session models
├── AudiobookshelfApiManager.py    Audiobookshelf client and direct HTTP endpoints
├── AudioPlayer.py                 VLC adapter and continuous multi-track timeline
├── DownloadStore.py               Safe local download/manifests/delete operations
├── BluetoothManager.py            BlueZ/D-Bus device operations
├── aobject.py                     Async-constructor helper
├── pages/                         Pillow-rendered application pages
└── screens/                       Physical and simulated display implementations

tests/                              Automated API, player, page, download, and lifecycle tests
assets/                             Font, icon, and landing-page image
old_code/                           Retired Spotify implementation; not part of the current app
test_scripts/                       Older manual experiments and hardware/debug scripts
```

## Pages and Navigation

Every page inherits from `Page`, which owns its Pillow image and defines async handlers for pressed, released, and held button events.

Routes are represented by either:

```python
"Settings"
```

or a parameterized route:

```python
("Player", {"book_id": book.id, "local": False, "back_route": previous_route})
```

`GuiManager` resolves the string by finding the imported class named `SettingsPage`, `PlayerPage`, and so on. This avoids circular imports between pages. A routable page must therefore be imported into `GuiManager.py`.

Many pages need API data during construction. Those classes inherit `aobject`, which makes construction awaitable:

```python
page = await SelectAllBooksPage()
```

`Page` itself is deliberately not an `aobject`. Synchronous pages such as `ErrorPage` must still be constructible while error handling is already in progress.

The most important shared page classes are:

- `Page`: image creation, drawing helpers, lifecycle hooks, and the input interface.
- `ListPage`: ordered label/value entries, selection, viewport scrolling, scrollbar, held-button repeat, jump navigation, and marquee text.
- `StaticPage`: displays an image asset.
- `StaticTextPage`: wraps and scrolls arbitrary text, including errors and confirmations.
- `LoadingPage`: blocks duplicate input while a slow route is being constructed.
- `ScreensaverPage`: black overlay that preserves the exact underlying page while the display is powered down.

## Main Page Areas

### Landing and Settings

`LandingPage` is the root menu and links to the Audiobookshelf and settings areas.

`SettingsPage` is a specialized `ListPage`. Brightness, volume, default playback speed, and screensaver timeout are adjusted directly with left/right. Their values are drawn as split backgrounds. Check for updates asynchronously runs `git pull` in the current working directory, while Bluetooth and Back remain selectable rows. Key 2 also returns to the landing page.

The older `BrightnessPage`, `VolumePage`, and `BarLevelPage` files remain in the tree for compatibility/history, but the active Settings flow adjusts those values inline.

### Audiobookshelf Browsing

`AudiobookshelfLandingPage` is the entry point for cloud and downloaded books. Cloud browsing lives mostly in `CloudBooksPages.py`:

```text
SelectCloudBookPage
├── SelectInProgressBookPage
├── SelectRecentlyAddedPage
├── SelectAllBooksPage
├── ChooseByAuthorPage
│   └── ChooseAuthorsBooksPage
├── ChooseFromGenrePage
│   └── ChooseGenreBooksPage
└── ChooseFromSeriesPage
```

Each result eventually opens `PlayerPage` or `DownloadBookPage`. Route payloads carry the exact previous route so Back returns to the correct filtered list.

The all-books list and author index are cached in `AudiobookshelfApiManager` and have explicit refresh entries. An individual author's book results are queried when that page is opened.

### Local Books

`LocalBooksPage.py` contains:

- `SelectDownloadedBookPage` for playback or deletion selection;
- the compatibility `LocalBooksPage` route;
- `DeleteDownloadedBookPage`, which requires a center hold and only removes local files.

### Playback and Downloads

`PlayerPage` presents the current title, chapter, state, elapsed time, progress, volume, and speed. Its one-second refresh loop polls VLC for track completion. Server progress is periodically synchronized only while audio is playing, with immediate synchronization for important state changes.

`DownloadBookPage` starts a foreground download, renders byte, percentage, and estimated-time-remaining progress from the expanded book's media size and observed transfer speed, and supports center-hold cancellation. Navigation is disabled while the transfer is active except for that explicit cancellation gesture.

## Event and Navigation Flow

Button callbacks originate in `BaseScreen` and are attached to `GuiManager.dispatch_event()`. GPIO callbacks may run outside the asyncio thread, so `dispatch_event()` safely schedules `handle_event()` on the main loop.

The active page handler can return:

- a route string;
- a `(route, kwargs)` tuple;
- `True` to redraw the current page;
- `None` or `False` when no render or navigation is needed.

Only one input handler or navigation request is processed at a time. When constructing a new page requires a noticeable API request, `GuiManager` immediately shows `LoadingPage` and ignores repeated button presses until the request finishes.

Page lifecycle hooks are significant:

- `on_enter()` starts page-specific refresh or download tasks.
- `on_exit()` cancels tasks and performs required playback synchronization.

The screensaver is intentionally different. It does not call `on_exit()` on the covered page, so playback and page state survive. The first subsequent event wakes the display and restores that same page without forwarding the event to it. Downloads and Bluetooth operations are exempt from automatic screensaving.

## Audiobookshelf Integration

`AudiobookshelfApiManager` owns the shared API client, HTTP session, host, token, and library ID.

It uses `aioaudiobookshelf` for supported calls and authenticated `aiohttp` requests for missing endpoints. Responses are converted into the dataclasses in `AudiobookModels.py`, which keeps pages independent of differences between library objects, dictionaries, and direct REST responses.

Important normalized objects include:

- `Book`: metadata, authors, genres, series, duration, byte size, tracks, and chapters;
- `Track`: source, duration, MIME type, and its offset in the complete book;
- `PlaybackSession`: the open Audiobookshelf session and resume position;
- `PlaybackContext`: the active local or streaming book and unsynchronized listening state.

Streaming URLs use Audiobookshelf's token query parameter because VLC cannot reliably attach the normal Bearer header itself.

## Audio Playback

`AudioPlayer` wraps python-vlc and hides individual media files behind one continuous book timeline. It is responsible for:

- loading ordered local paths or remote URLs;
- translating a global seek into a track and track-relative timestamp;
- moving automatically to the next track;
- chapter navigation across file boundaries;
- play, pause, stop, volume, rate, position, duration, and state.

`GuiManager` owns the higher-level playback lifecycle. It restores Audiobookshelf or local progress, starts and closes streaming sessions, stores offline fallback positions, and persists playback speed per book.

## Download Storage

`DownloadStore` places books under:

```text
<download_directory>/<library-item-id>/
├── booklet.json
└── one or more audio files
```

The manifest stores normalized, serializable book metadata and the ordered relative audio paths. A download is first written into a temporary directory. ZIP files are safely extracted with path-traversal checks, playable files are validated, and the completed directory is atomically published. Failures and cancellation remove temporary data.

## Screens and Hardware

`BaseScreen` defines the eight input buttons and shared brightness/display-power behavior.

- `Screen` drives the physical SPI LCD and GPIO backlight.
- `SimulatedScreen` uses pygame and mock GPIO pins for desktop development.

The same page images and event handlers are used in both environments. Bluetooth is similarly separated into `BluetoothManager`, which talks to BlueZ through D-Bus, and `BluetoothPage`, which presents device actions.

## Configuration and Persistent State

Static user configuration is read from `booklet_config.json`. See `README.md` for the expected Audiobookshelf keys and optional download directory.

Runtime state is stored in the `booklet` shelve through `CONFIG`. This includes the selected library, current book, local fallback positions, volume, brightness, screensaver timeout, default playback speed, and per-book playback speeds.

The repository's `booklet` file is live application data rather than source code. Avoid modifying it during development. Run imports and tests from `/tmp` when possible because the checkout's database may use a `dbm.gnu` backend unavailable to another Python interpreter.

## Tests

The automated suite is organized by subsystem:

- `test_api_manager.py`: API normalization, authentication, caching, playback sessions, and streamed downloads;
- `test_audio_player.py`: global seeking, chapters, transitions, volume, and rate;
- `test_cloud_pages.py`: routes, grouping, refresh behavior, and list navigation;
- `test_download_store.py`: atomic storage, manifests, ZIP safety, deletion, and size formatting;
- `test_list_page.py`: duplicates, empty states, viewport behavior, jumps, and marquee movement;
- `test_playback_lifecycle.py`: pause/sync/session behavior and saved playback speeds;
- `test_settings_and_screensaver.py`: inline settings, loading suppression, and wake/restore behavior.

A typical isolated validation run is:

```bash
cd /tmp
PYTHONPATH=/home/zeke/hello/Booklet python -m pytest -q /home/zeke/hello/Booklet/tests
python -m compileall -q /home/zeke/hello/Booklet/src /home/zeke/hello/Booklet/tests
git -C /home/zeke/hello/Booklet diff --check
git -C /home/zeke/hello/Booklet diff --cached --check
```

The tests use fake APIs, VLC adapters, screens, and managers. Final speaker output, LCD/backlight behavior, GPIO input, and Bluetooth pairing still require validation on the Raspberry Pi.

For implementation rules and invariants intended for coding agents, see `AGENTS.md`.

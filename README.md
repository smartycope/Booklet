![icon](assets/icon.png)

# Booklet
A custom handheld audiobook player, built from the ground up and connecting to a personal audiobookshelf instance.

This is a personal project. It shouldn't be too hard for someone else to make one as well, but it's probably going to be lacking in explanations and documentation.

Originally, the idea was to be able to stream/download from Spotify as well, but authentication became a hassle after they made refresh tokens expire after 6 months, as well as not being able to download music, and registering as an offical "spotify player", and so on. It's now just targetting audiobookshelf.

## Hardware
* Raspberry pi 2W (the one with wifi and bluetooth)
* [240x240, 1.3inch IPS LCD display HAT](https://www.waveshare.com/1.3inch-lcd-hat.htm)
* Micro SD card (enough to download books onto, but at least 4GB)
TODO: Add a battery

## Useful links
* [How to power your Raspberry Pi with a lithium battery](https://www.circuitbasics.com/how-to-power-your-raspberry-pi-with-a-lithium-battery/)
* [Using the LCD HAT](https://www.waveshare.com/wiki/1.3inch_LCD_HAT)
<!-- * [Spotify Access Tokens](https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens) -->

## Commands
* Install requirements:
    * `pip install -r requirements.txt`
    * Install VLC/libVLC through the operating system as well (for Raspberry Pi OS: `sudo apt install vlc`).
* Install dev requirements:
    * `pip install -r dev-requirements.txt`
* Run program:
    * `python -m src`

## Configuration
API keys and other user configurations are stored in `~/booklet_config.json`. It shoud look like this:
    <!-- "spotify_refresh_token": "...",
    "spotify_client_id": "...",
    "spotify_client_secret": "...", -->
```JSON
{
    "audiobookshelf_url": "...",
    "audiobookshelf_api_key": "...",
    "audiobookshelf_library_name": "Audiobooks",
    "download_directory": "~/Audiobooks"
}
```

`download_directory` is optional and defaults to `~/Audiobooks`. The Audiobookshelf user associated with the API key must have download permission to save books locally.
<!--
I had the keys left over from a different project. I honestly forgot exactly how I got them. Some of them came from the [spotify web api docs](https://developer.spotify.com/documentation/web-api/tutorials/getting-started) somewhere, and the rest came from a streamlit application I made for the purpose.
TODO: include that streamlit application -->

The `audiobookshelf_url` is the URL of your audiobookshelf instance. It's self hosted. You can create an API key by going to `Settings > API Keys` in your audiobookshelf instance (you need to be logged in as the root user).

## TODO
Not yet in scope, but eventually we'll want to implement:
* better playback acceleration algorithm
* cover-art UI
* bookmarks
* search keyboard
* Battery percentage in the player page (or possibly in Page)
* background downloads?
* concurrent downloads?
* podcast support?

Credit to ChatGPT for the icon

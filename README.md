![icon](icon.png)

# Booklet
A custom handheld audiobook player

This is a personal project. It shouldn't be too hard for someone else to make one as well, but it's probably going to be lacking in explanations and documentation.

## Hardware
* Raspberry pi 2W (the one with wifi and bluetooth)
* [240x240, 1.3inch IPS LCD display HAT](https://www.waveshare.com/1.3inch-lcd-hat.htm)
* Micro SD card (I'm currently using 4GB, but I want to upgrade that later)
TODO: Add a battery

Credit to ChatGPT for the icon

## Useful links
* [How to power your Raspberry Pi with a lithium battery](https://www.circuitbasics.com/how-to-power-your-raspberry-pi-with-a-lithium-battery/)
* [Using the LCD HAT](https://www.waveshare.com/wiki/1.3inch_LCD_HAT)
* [Spotify Access Tokens](https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens)

## Commands
* `pip install -r requirements.txt`
* `python -m src`

## Configuration
API keys and other user configurations are stored in `~/booklet_config.json`. It shoud look like this:
{
    "spotify_refresh_token": "...",
    "spotify_client_id": "...",
    "spotify_client_secret": "...",

    "audiobookshelf_url": "...",
    "audiobookshelf_api_key": "..."
}

I had the keys left over from a different project. I honestly forgot exactly how I got them. Some of them came from the [spotify web api docs](https://developer.spotify.com/documentation/web-api/tutorials/getting-started) somewhere, and the rest came from a streamlit application I made for the purpose.
TODO: include that streamlit application

The `audiobookshelf_url` is the URL of your audiobookshelf instance. It's self hosted. You can create an API key by going to `Settings > API Keys` in your audiobookshelf instance (you need to be logged in as the root user).

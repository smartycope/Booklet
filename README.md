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

## Instructions from the ground up
### Set up the OS
Write the OS to a micro SD card. I use Raspberry Pi Imager, and install a generic 64-bit headless image. You can optionally pre-set a network connection from the Imager config menu.

Enable SPI before starting Booklet. The Waveshare LCD uses SPI bus 0 and chip
select 0 (`/dev/spidev0.0`), and Raspberry Pi OS disables SPI by default:

```bash
sudo raspi-config nonint do_spi 0
sudo reboot
```

After reconnecting, verify that the display interface is available:

```bash
test -e /dev/spidev0.0 && echo "SPI is ready"
```

### Get the project & Dependancies
Log in or SSH into the pi, and from the home folder, run:
```bash
# Update the pi
sudo apt update
# Install OS dependancies
sudo apt install git vlc python3-dev python3-gdbm swig liblgpio-dev pulseaudio-module-bluetooth # python3-gpiozero
# Grab the code
git clone https://github.com/smartycope/Booklet
cd Booklet
# Create & activate a virtual environment
python -m venv .
source bin/activate
# Install python dependancies
pip install -r requirements.txt
# Setup the SPI pins
sudo raspi-config nonint do_spi 0
# Reboot
sudo reboot
```

### Set up the config file
Next go to your audiobookshelf server, go to settings, click on "API Keys" and add a new API key.

Then create a file at `~/booklet_config.json` and enter the following:
```json
{
    "audiobookshelf_url": "https://your.audiobook.server.com/",
    "audiobookshelf_api_key": "<the api key you just created>",
    "audiobookshelf_library_name": "<the name of the library you want to use",
    "download_directory": "~/Audiobooks"
}
```

## Install as a systemd service

Make sure to update the paths in Booklet.service with the username you picked.

`Booklet.service` is a per-user systemd unit. It assumes the repository contents are directly in the Pi user's home directory, so `~/src` exists. Install it in the user unit directory:

```bash
# mkdir -p ~/.config/systemd/user
# cp ~/Booklet.service ~/.config/systemd/user/Booklet.service
sudo cp Booklet.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now Booklet.service
```

Enable lingering so the user's service manager—and therefore Booklet—starts during boot without waiting for an interactive login:

```bash
sudo loginctl enable-linger "$USER"
```

Useful service commands:

```bash
systemctl --user status Booklet.service
systemctl --user restart Booklet.service
systemctl --user stop Booklet.service
```

The service runs `/usr/bin/python3 -m src` from `~`, restarts automatically after it exits, sends standard output to the systemd journal, and appends standard error to `~/booklet-errors.log`:

```bash
tail -f ~/booklet-errors.log
journalctl --user -u Booklet.service -f
```

If the repository is stored somewhere other than directly in `~`, update `WorkingDirectory=` in the installed unit. If dependencies are installed in a virtual environment, also update `ExecStart=` to that environment's Python executable, while retaining `-m src`.

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
include that streamlit application -->

The `audiobookshelf_url` is the URL of your audiobookshelf instance. It's self hosted. You can create an API key by going to `Settings > API Keys` in your audiobookshelf instance (you need to be logged in as the root user).

## TODO
* Decrease the timeout when attempting to connect to bluetooth
* Have the PlayerPage show "Loading..." where the time progress text is, which gets overwritten once it's loaded up
* Add the ability to interrupt an attemtping connection to a bluetooth device (if that's something the library supports)
* profile stuff
* Need a wifi connection page -- will need a keyboard for this!
* better playback acceleration algorithm
* cover-art UI
* bookmarks
* search keyboard
* Battery percentage in the player page (or possibly in Page)
* background downloads?
* concurrent downloads?
* podcast support?


Credit to ChatGPT for the icon

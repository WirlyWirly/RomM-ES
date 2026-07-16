<div align="center">

  # ** ☁️ RomM-ES 🕹️ **
</div>

<div align="center">
  <img src=".github/assets/preview.webp" alt="romm-es" width="100%" />
</div>

<br>


# Description
This utility will allow you to import games from your (RomM)[https://romm.app/] library into (ES-DE)[https://es-de.org/]. It queries the RomM API for the metadata to create ES-DE library entries.

Starting a game in ES-DE will download the game file from RomM and store it on your system, allowing you to launch it in your emulator of choice.

# Dependencies
* (RomM)[https://romm.app/]
* (ES-DE)[https://es-de.org/]
* (Python 3.10+)[https://www.python.org/]
* `pip install -r requirements.txt`


# Notice
Make sure to **exit** ES-DE before running the `GameImporter` script.

Adding RomM games while ES-DE is running may result in undetected changes, overwritten changes, or even corrupted `gamelist.xml` files within the ES-DE directory.

# Limitations
As of this writing, there is work to be done and therefore limitations to be aware of...

* No archive extractions: Files downloaded from RomM are not extracted, which means that your emulator must be able to play the files as they appear in RomM.

# Setup

1) From the ES-DE settings menu, enable the option `Other Settings > Enable Custom Event Actions` then exit ES-DE
    * The `game-start` custom event action is what will trigger roms to be downloaded on demand. Be aware that while the download is happening, ES-DE will appear to stall. This is normal as it is waiting for the triggered script to finish.
2) Clone\Download this repo and place the main `RomM-ES` folder in your `ES-DE` data directory, alongside the `gamelists` and `downloaded_media` directories.
    * Relative paths are used wherever possible for the sake of portability
3) Generate a basic 'settings.ini' file in the `RomM-ES` directory by running the script for the first time. Edit this file with your appropriate RomM credentials and `esde_roms` path.
    `python "C:\path\to\GameImporter.py"`
4) Edit the `GameStart.bat` (windows) or `GameStart.sh` (linux) file with the appropriate paths for calling the `GameStart.py` script. Place this file in the `ES-DE/scripts/game-start/` directory.
    * This directory may not exist, if so create it. Scripts in here will be called whenever a game is started in ES-DE if you have enabled the *Custom Event Actions*, as we did in step 1.

# Usage

Invoking the `GameImporter.py` script will query RomM for each platform that has been enabled for importing in the `settings.ini` file. For each platform that is queried, the artwork and metadata of every game not already in ES-DE will be downloaded and populated into the appropriate ES-DE directories. When you next start ES-DE, the new game items will appear in your library as if they were scanned in.

`python ./GameImporter.py`

# TO-DO
* Archive extractions
* Artwork\Metadata refreshing
* More relative paths and less setup
* Go to bed

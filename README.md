<div align="center">

  # ☁️ RomM-ES 🕹️
</div>
<br>


# Description
This utility will allow you to import games from your [RomM](https://romm.app/) library into [ES-DE](https://es-de.org/). The artwork\metadata necessary to create ES-DE library entries will be pulled from the RomM api and appear in ES-DE as if they were scanned in.

Byte sized placeholder files will be created in the ROMs directory of ES-DE and only when a game is started for the first time will the file be fetched from RomM and saved on the system.

# Dependencies
* [RomM](https://romm.app/)
* [ES-DE](https://es-de.org/)
* [Python 3.10+](https://www.python.org/)
* `pip install -r requirements.txt`

# Setup

1) From the ES-DE settings menu, enable the option `Other Settings > Enable Custom Event Actions` then exit ES-DE
    * The `game-start` custom event action is what will trigger roms to be downloaded on demand. Be aware that while the download is happening, ES-DE will appear to stall. This is normal as it is waiting for the triggered script to finish its work.
2) Clone\Download this repo and place the main `RomM-ES` folder in your `ES-DE` data directory, alongside the `gamelists` and `downloaded_media` directories.
    * Relative paths are used wherever possible for the sake of portability
3) Generate a basic 'settings.ini' file in the `RomM-ES` directory by running the script for the first time. Edit this file with your appropriate RomM credentials and `esde_roms` path.
    `python "C:\path\to\GameImporter.py"`
4) Edit the `GameStart.bat` (windows) file with the appropriate paths for calling the `GameStart.py` script. Place this file in the `ES-DE/scripts/game-start/` directory.
    * This directory may not exist, if so create it. Scripts in here will be called whenever a game is started in ES-DE if you have enabled the *Custom Event Actions*, as we did in step 1.

# Notice
Make sure to **exit** ES-DE before running the `GameImporter` script.

Adding RomM games while ES-DE is running may result in undetected changes, overwritten changes, or even corrupted `gamelist.xml` files within the ES-DE directory.

# Usage

Invoking the `GameImporter.py` script will query RomM for each platform that has been enabled for importing in the `settings.ini` file. For each platform that is queried, the artwork and metadata of every game not already in ES-DE will be downloaded and populated into the appropriate ES-DE directories. When you next start ES-DE, the new game items will appear in your library as if they were scanned in.

`python ./GameImporter.py`

# TO-DO
* text metadata in `gamelist.xml` files
* linux `GameStart.sh` wrapper script
* Archive extractions
* Artwork\Metadata refreshing
* More relative paths and less setup
* Go to bed

<div align="center">

  # ☁️ RomM-ES 🕹️
</div>
<br>


# Description
This "plugin" will allow you to import games from your [RomM](https://romm.app/) library to be browsed and then downloaded directly from [ES-DE](https://es-de.org/) . The artwork\metadata necessary to create ES-DE library entries will be pulled from the RomM api and appear in ES-DE as if they were scanned in.

Byte sized **placeholder** files will be created in the ROMs directories of ES-DE, which will be used to download the actual rom files on-demand when the game is first started. This allows you to list your entire RomM library in ES-DE, but with no game files taking up storage space until you actually decide to play the game.

Inspiration for this "plugin" comes from the [RomM Playnite Plugin](https://playnite.link/addons.html#RomM_9700aa21-447d-41b4-a989-acd38f407d9f), which works great and does basically the same thing.

# Dependencies
* [RomM](https://romm.app/)
* [ES-DE](https://es-de.org/)
* [Python 3.10+](https://www.python.org/)
* `pip install -r requirements.txt`

# Setup

1) Enable the ES-DE setting  `Other Settings > Enable Custom Event Actions`
    * The [`game-start`](https://gitlab.com/es-de/emulationstation-de/-/blob/master/INSTALL.md#custom-event-scripts) custom event is what will trigger roms to be downloaded on demand when a game is first started. Be aware that for larger roms or slower connections, ES-DE may appear to stall until the download is complete.
2) Clone\Download this repo and place the main `RomM-ES` folder in your `ES-DE` data directory (alongside the `gamelists` and `downloaded_media` directories)
3) Run the `GameImporter.py` script to generate a template 'settings.ini' file that will appear in the `RomM-ES` directory. Edit the settings with your RomM credentials and `esde_roms` path.
    `python "C:\path\to\GameImporter.py"`
4) Move the `GameStart.bat` (windows) file to the `ES-DE/scripts/game-start/` directory. Edit this file with the correct paths to call the `GameStart.py` script.
    * If the `game-start` directory does not exist, create it. Scripts in this directory will be triggered between when a game is started in ES-DE and when the emulator is actually launched.

# Notice
Make sure to **exit** ES-DE before running the `GameImporter` script.

Adding RomM games while ES-DE is running may result in undetected changes, overwritten changes, or even corrupted `gamelist.xml` files within the ES-DE directory.

# Usage

After going through the setup, simply call the `GameImporter.py` script and it will query RomM to begin importing games. For each platform that is queried, the artwork and metadata of every game not already listed in ES-DE will be downloaded and placed into the appropriate ES-DE directories. When you next start ES-DE, these new game items will appear as if they were scanned in.

`python ./GameImporter.py`

To download games on demand, simply start a game and RomM and it will be downloaded from RomM. Keep in mind that ES-DE may appear to stall until the download is complete.

# TO-DO
* Archive extractions
* Artwork\Metadata refreshing
* More relative paths and less setup
* Go to bed

<div align="center">

  # ☁️ RomM-ES 🕹️
</div>

<div align="center">
  <img src=".github/assets/preview.webp" alt="preview" width="100%" />
</div>

<br>

This "plugin" will allow you to import games from a ☁️ [RomM](https://romm.app/) server into 🕹️ [ES-DE](https://es-de.org/)

Games can be browsed in ES-DE will be automatically downloaded from RomM the first time they are launched

Inspiration for this "plugin" comes from the [RomM Playnite Plugin](https://playnite.link/addons.html#RomM_9700aa21-447d-41b4-a989-acd38f407d9f), which works great and does basically the same thing within Playnite


## 🤖 Dependencies
* [RomM](https://romm.app/)
* [ES-DE](https://es-de.org/)
* [Python 3.10+](https://www.python.org/)
* `pip install -r requirements.txt`


## 🖥️ Setup
1) Enable the ES-DE setting  `Other Settings > Enable Custom Event Actions`
    * The [`game-start`](https://gitlab.com/es-de/emulationstation-de/-/blob/master/INSTALL.md#custom-event-scripts) custom event is what will trigger roms to be downloaded on demand when a game is first started
      
2) Download\Clone this repo and place the main `RomM-ES` folder into your `ES-DE` data directory, alongside the `gamelists` and `downloaded_media` directories
    * RomM-ES assumes you are using the ES-DE default `ES-DE/downloaded_media/` directory for artwork
   
4) Run the `GameImporter.py` script to generate a `settings.ini` file, which will appear in the `RomM-ES` directory. Edit **at-least** the options in the `[Required]` section of the settings file.

      ```cmd
   python "C:\path\to\GameImporter.py"
      ````
   
5) Move the `GameStart.bat` (windows) or `GameStart.sh` (linux) file to the `ES-DE/scripts/game-start/` directory. Edit the file with the correct paths to call the `GameStart.py` script.
    * Create the `game-start` directory if it does not already exist. Scripts in this directory will be triggered when when a game is started in ES-DE but before the emulator is actually launched. This in-between time is when rom files will be downloaded from RomM.


## 🧭 Instructions
> [!WARNING]
>  Make sure to **exit** ES-DE **before** running the `GameImporter` script.
>
> Importing games with external-tools while ES-DE is running can result in undetected changes, overwritten changes, or even corrupted `gamelist.xml` files.


After doing the setup above, simply call the `GameImporter.py` script and it will begin importing games from RomM into ES-DE
 
```cmd
python "./GameImporter.py"
```

After importing, you need only start a game in ES-DE and it will be downloaded from RomM using the `GameStart.py` script.


> [!NOTE]
> When downloading larger rom files or on slower connections, ES-DE may appear to hang until the download is complete

## ℹ️ Info
* If you enable the ES-DE option `Other Settings > Run in Background (While game is launched)`, you can avoid the black-screen that may appear while a rom is downloading larger files. You will instead be left inside ES-DE until the download completes and the emulator is started.

* When importing, byte-sized **placeholder** files will be created in the ROMs directory of ES-DE. These tiny plain-text placeholder files store the RomM id of that game, which will later be used by `GameStart.py` to download from RomM when a game is first launched. If the RomM id changes (such as the game being removed and then re-scanneed into RomM), then the download will fail because the RomM id in the placeholder file will no longer be valid. You will have to re-import your games to update the placeholder files with the current RomM id.
  
* All metadata is sourced directly from the RomM api and used to create the ES-DE library items, so any edits should be done server side in RomM.

## 📝 TO-DO
* Improve error-handling
* Archive extracting
* Artwork\Metadata refreshing
* MixImage uploading from ES-DE to RomM
* More relative paths and streamlined setup process
* Go to bed 😩

# A utility to import RomM hosted game files into ES-DE 🕹️
# GitHub: https://github.com/WirlyWirly/RomM-ES

# ==================================== PACKAGE IMPORTS ====================================

# Standard Library
import base64
import json
import logging as log
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET

from configparser import ConfigParser
from pathlib import Path

# Third-party
import requests

# A basic logger
log.basicConfig(level=log.INFO, style='{', format='Line: {lineno} | level: {levelname} | Time: {asctime} | Info: {message}')


# ==================================== FUNCTIONS ====================================

def importPlatformGames(platform_id, platform_slug):
    # Get every game for the provided platform_id and add any missing games to ES-DE

    gamelist_file = esde / f"gamelists/{mappings[platform_slug]['esde']}/gamelist.xml"
    log.info(f'gamelist.xml: {gamelist_file}')

    # If the gamelist.xml does not exits, create it and the necessary path folders
    if gamelist_file.exists() == False:
        gamelist_file.parents[0].mkdir(parents=True, exist_ok=True)
        with gamelist_file.open('w', encoding='UTF-8') as file:
            file.write('''<?xml version="1.0"?>
<gameList></gameList>''')

    # Parse the gamelist.xml and check for duplicates
    xml_tree = ET.parse(gamelist_file)
    xml_root = xml_tree.getroot()

    imported_paths = []

    for list_item in xml_root:
        for value_item in list_item:
            if value_item.tag == 'path':
                imported_paths.append(value_item.text)

    # Query RomM for all games for this platform
    response = requests.get(f'{romm_url}/api/roms?platform_ids={platform_id}&order_by=name&order_dir=asc&limit=10000', headers=romm_auth)
    games = response.json()

    # Loop through every returned game and add it to ES-DE
    for game in games['items']:
        log.info(f"Name: {game['name']}")

        # ---------- Prepare Metadata ----------

        # Compare the RomM path to the .xml path to check if the game has already been imported 
        gamefile_path = f"./{game['fs_name']}",
        #gamefile_path = re.sub('&', r'&amp;', gamefile_path[0])

        if gamefile_path in imported_paths:
            # This game is already in the gamelist.xml, so continue to the next item
            print('dupe')
            log.debug(f'Dupe: {gamefile_path}')
            continue

        # Milliseconds to seconds to date-string
        epoch_timestamp = game['metadatum']['first_release_date'] / 1000
        release_date = time.strftime('%Y%m%dT000000', time.gmtime(epoch_timestamp))

        # Rating rounded to decimal
        rating = round(game['metadatum']['average_rating'] / 100, 1)

        # The game metadata that will be added to 'gamelist.xml'
        metadata = {
            'desc': game['summary'],
            'favorite': 'false',
            'name': game['name'],
            'path': gamefile_path,
            'players': game['metadatum']['player_count'],
            'publisher': game['metadatum']['companies'][0],
            'publisher': game['metadatum']['genres'][0],
            'rating': rating,
            'releasedate': release_date,
        }

        log.debug(metadata)

        # ---------- Add to gameList.xml ----------
        # Add this game to the appropriate 'gamelist.xml' if no other <game> entry has the same path value

        # ---------- GameFile Placeholders ----------

        # Create placeholder files in ES-DE ROMs directories
        gamefile = roms_folder / f"{mappings[platform_slug]['esde']}/{game['fs_name']}"

        if gamefile.exists() == False:
            gamefile.parents[0].mkdir(parents=True, exist_ok=True)
            with gamefile.open('w', encoding='UTF-8') as file:
                file.write(f"RomM-ES={game['id']}")

        # ---------- Download Artwork ----------

        media_urls = {
            '3dboxes': game['ss_metadata']['box3d_path'],
            'backcovers': game['ss_metadata']['box2d_back_path'],
            'covers': game['path_cover_large'],
            'fanart': game['ss_metadata']['fanart_path'],
            'manuals': game['path_manual'],
            'marquees': game['ss_metadata']['marquee_path'],
            'miximages': game['ss_metadata']['miximage_path'],
            'physicalmedia': game['ss_metadata']['physical_path'],
            'screenshots': game['merged_screenshots'][0] if len(game['merged_screenshots']) > 1 else None,
            'titlescreens': game['ss_metadata']['title_screen_path'],
            'videos': game['path_video']
        }

        for key, value in media_urls.items():
            # Prepare, parse, and then download each available media_url

            if value is None:
                # RomM has no media for this artwork type, so do nothing
                continue

            media_url = value
            if re.match(r'^/assets/', media_url) is None:
                # The media URL needs to be prepended with /assets/
                media_url = f'/assets/romm/resources/{value}'

            # Complete the url with the RomM domain
            media_url = f'{romm_url}{media_url}'
            log.debug(f'mediaURL: {media_url}')

            # The extension to use when saving the media
            extension = re.search(r'\.(png|jpg|webp|jxl|mp4)', media_url)[1]

            # The path for where the media will be saved
            media_file = downloaded_media / f"{mappings[platform_slug]['esde']}/{key}/{game['fs_name_no_ext']}.{extension}"
            media_file.parents[0].mkdir(parents=True, exist_ok=True)

            # GET and then save the media_url as media_file
            response = requests.get(media_url, headers=romm_auth)

            with media_file.open('wb') as file:
                file.write(response.content)


# ==================================== MAIN ====================================

# The absolute path to the RomM-ES directory
romm_es = Path(sys.argv[0]).resolve().parents[0]

log.info(f'RomM-ES Path: {romm_es}')

# Read the options in 'settings.ini' file
config_file = romm_es / 'settings.ini'
if config_file.exists() == False:
    # The 'settings.ini' file does not exists, so create it and then exit

    settings_template = '''[General]
# A RomM URL and valid ApiToken
romm_url = http://localhost:8080
romm_apitoken = abc123

# The path to the ES-DE roms folder
esde_roms = C:/path/to/roms

# The path to 7zip, if it is not already in the RomM-ES folder
7zip = C:/path/to/7z.exe

# If the RomM-ES folder is not placed inside the ES-DE folder, then specify the absolute path to the ES-DE directory
esde_folder = C:/path/to/ES-DE/

[ImportPlatforms]
# The RomM platforms for whose games will be imported into ES-DE

# Setting this to 'true' will ignore individual platform settings and import all of them
all = true

gba = false
n64 = false 
nds = false 
ngc = false
ps2 = false
psp = false
xbox = false
'''
    with config_file.open('w', encoding='UTF-8') as file:
        file.write(settings_template)
    input("A 'settings.ini' file has been created in the RomM-ES directory.\n\nEdit this file to fit your settings and then re-run this script.")
    sys.exit()


config = ConfigParser()
config.read(config_file)

# The ES-DE directory and relevant child directories
esde = Path(sys.argv[0]).resolve().parents[1]

if esde.name != 'ES-DE':
    esde = Path(config['General']['esde_folder']).resolve()

roms_folder = Path(config['General']['esde_roms'])
gamelists = esde / 'gamelists'
downloaded_media = esde / 'downloaded_media'

# Read the mapped RomM slugs in 'rommSlugMapper.json'
mapping_file = romm_es / 'platformMaps.json'
with mapping_file.open('r', encoding='utf-8') as file:
    mappings = json.load(file)

# ==================================== ROMM IMPORTING ====================================

romm_url = config['General']['romm_url']
romm_api = config['General']['romm_apitoken']

romm_auth = { 'Authorization': f'Bearer {romm_api}' }

# Get all RomM platforms
response = requests.get(f'{romm_url}/api/platforms', headers=romm_auth)
platforms = response.json()

# Import games for each enabled platform
import_all = True if config['ImportPlatforms']['all'] == 'true' else False
for platform in platforms:
    platform_slug = platform['fs_slug']

    if platform_slug not in config['ImportPlatforms']:
        # Unsupported platform
        log.info(f'Unsupported Platform: {platform_slug}')
        continue

    elif import_all or config['importPlatforms'][platform_slug] == 'true':
        # Yes, the games in this platform should be imported
        log.info(f'========== Importing Platform: {platform_slug} ==========')

        importPlatformGames(platform['id'], mappings[platform_slug]['esde'])
    else:
        # No, the games in this platform should not be imported
        log.info(f'Skipping Platform: {platform_slug}')
        continue





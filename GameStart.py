# A script that utilizes the ES-DE 'game-start' event action to replace a placeholder file with the actual rom file provided by RomM
# GitHub: https://github.com/WirlyWirly/RomM-ES

# ==================================== Package Imports ====================================

# Standard Library
import json
import logging as log
import os
import re
import shlex
import shutil
import subprocess
import sys

from configparser import ConfigParser
from pathlib import Path

# Third-party
import requests

# Set the CWD to the RomM-ES directory
os.chdir(Path(sys.argv[0]).resolve().parent)

# A basic logger
log_file = Path(sys.argv[0]).resolve().parent / 'GameStart.log'
log.basicConfig(filename=log_file, filemode='w+', level=log.DEBUG, style='{', format='Line: {lineno} | level: {levelname} | Time: {asctime} | Info: {message}')

# ES-DE will pass 4 positional arguments when calling this script...
# "C:\path\to\rom.zip" "Game Name" "platform slug" "full platform name"
# Ex: "C:\path\to\Kirby - Nightmare in Dream Land (USA).zip" "Kirby - Nightmare in Dream Land (USA)" "gba" "Nintendo Game Boy Advance" 

log.debug(f'ES-DE Arg1: "{sys.argv[1]}"')
log.debug(f'ES-DE Arg2: "{sys.argv[2]}"')
log.debug(f'ES-DE Arg3: "{sys.argv[3]}"')
log.debug(f'ES-DE Arg4: "{sys.argv[4]}"')
log.debug('Python command template (for terminal testing\debugging)...')
log.debug(f'$ python ./GameStart.py "{sys.argv[1]}" "{sys.argv[2]}" "{sys.argv[3]}" "{sys.argv[4]}"')

esde_rom = Path(sys.argv[1]).resolve() # 'C:\path\to\rom.zip'
esde_slug = sys.argv[3] # 'gba'

extract_file = False

# ==================================== Placeholder Verification ====================================

# Determine if the started game is a RomM placeholder and if so parse the RomM id
if os.path.getsize(esde_rom) > 20:
    # This game file is too large to be a placeholder file, so exit
    log.debug('Not a RomM placeholder, filesize is too large')
    sys.exit()

else:
    # This game file is small enough to be a placeholder file, continue verification...
    with esde_rom.open('r', encoding='UTF-8') as file:

        # Search the contents of the file for a RomM id number
        placeholder_text = re.search(r'^RomM-ES:(\d+)(:\w+)?$', file.read())

        if placeholder_text is None:
            # No RomM id, so exit
            log.debug('Not a RomM placeholder file')
            sys.exit()

        else:
            # Yes, this is a RomM placeholder file with a RomM id
            romm_id = int(placeholder_text[1])
            log.info(f'RomM id: {romm_id}')

            romm_server_filename = esde_rom.name

            if placeholder_text[2] != None:
                # This RomM placeholder file has a saved extension, indicating the downloaded RomM archive should be extracted to that extension

                extract_file = True
                romm_extension = re.search(r'^:(\w+)$', placeholder_text[2])[1] # The extension saved in the RomM placeholder file
                romm_server_filename = f'{esde_rom.stem}.{romm_extension}' # The actual name of the archive in RomM
                log.info(f'RomM Extension: {romm_extension}')
                log.info(f'RomM Server Filename: "{romm_server_filename}"')


# ==================================== Load Settings ====================================

# The absolute path to the RomM-ES directory
romm_es = Path(sys.argv[0]).resolve().parent

# Load the options in the 'settings.ini' file
config_file = romm_es / 'settings.ini'
config = ConfigParser()
config.read(config_file)

# Read the mapped RomM slugs in 'platformMaps.json'
platform_maps = romm_es / 'platformMaps.json'
with platform_maps.open('r', encoding='utf-8') as file:
    platform_maps = json.load(file)

# Reverse match the ES-DE provided platform slug with the RomM equivalent
romm_map_slug = False
for key, value in platform_maps.items():
    if platform_maps[key]['esde'] == esde_slug:
        romm_map_slug = key
        log.debug(f'RomM Platform: {romm_map_slug}')
        break

if romm_map_slug == False:
    # The ES-DE provided platform slug did not match a supported RomM slug, so exit
    log.info(f"Unsupported platform: {esde_slug}")
    sys.exit()

# ==================================== RomM Download  ====================================

romm_url = config['Required']['romm_url']
romm_api = config['Required']['romm_apitoken']

romm_auth = { 'Authorization': f'Bearer {romm_api}' }

# Use the parsed RomM id to get the details about this rom
request_url = f'{romm_url}/api/roms/{romm_id}'
log.debug(f'Request URL: {request_url}')
response = requests.get(request_url, headers=romm_auth)
log.debug(f'Request Status: {response.status_code}')

game = response.json()
#log.debug(game)

# If a rom_file_id is not determined, the placeholder file will not be replaced
rom_file_id = False

# Determine the rom file id from the list of attached files
for rom_file in game['files']:

    if (romm_server_filename == rom_file['file_name']) and romm_map_slug == game['platform_fs_slug']:
        # Match: The ES-DE filename and platform slug match the returned game, this must be the correct file

        log.info(f"RomM File id: {rom_file['id']}")
        log.info(f"RomM Filepath: \"{rom_file['full_path']}\"")
        rom_file_id = rom_file['id']
        break

if rom_file_id != False:
    # A file id was found, meaning there was a rom file match. The placeholder file will be replaced with the actual RomM provided rom file

    # The curl RomM download command
    curl_download = f"curl -X GET '{romm_url}/api/roms/{rom_file_id}/files/content/romfile' -H 'Authorization: Bearer {romm_api}' --output \"{esde_rom.parent / romm_server_filename}\""
    log.debug('Curl Command...')
    log.debug(curl_download)

    curl_download = shlex.split(curl_download)
    log.debug('Curl subprocess list...')
    log.debug(curl_download)

    # ES-DE will wait until this script (including subprocess') has completed before starting the emulator. For larger files or slower connections, this may cause a stall.
    subprocess.run(curl_download)

    if extract_file == True:
        # The downloaded archive needs to be extracted and the placeholder file replaced with the contents

        # The archive file that was downloaded by curl into the ES-DE ROMs folder
        archive_file = esde_rom.parent / romm_server_filename

        # A temp location for the extracted archive
        temp_location = esde_rom.parent / f"temp_RomM-ES"
        temp_location.parent.mkdir(parents=True, exist_ok=True)
        log.debug(f'Temp Archive: {temp_location}')

        # The path to '7z.exe',
        sevenzip = romm_es / '7z.exe'
        if sevenzip.exists() == False:
            sevenzip = Path(config['General']['7zip'])

        # The 7zip extraction command
        sevenzip_extract = f"\"{sevenzip}\" x \"{archive_file}\" -o\"{temp_location}\" *.{config['ExtractedExtension'][romm_map_slug]}"
        log.debug('7zip Command...')
        log.debug(sevenzip_extract)

        sevenzip_extract = shlex.split(sevenzip_extract)
        log.debug('7zip subprocess list...')
        log.debug(sevenzip_extract)

        subprocess.run(sevenzip_extract)

        # Search the extracted files in the temp folder for a placeholder replacement
        exact_match = False
        placeholder_replaced = False
        for file in temp_location.rglob(f"*.{config['ExtractedExtension'][romm_map_slug]}"):

            if str(file.name).lower() == str(esde_rom.name).lower():
                # This extracted file is an exact filename match to the RomM placeholder file, so use it for the replacement
                exact_match = True
                log.info(f'Exact placeholder replacement: "{file}"')
                file.replace(esde_rom)
                placeholder_replaced = True
                break

        if exact_match == False:
            # No exact match was found, so use the first available file with the same extension as the placeholder
            for file in temp_location.rglob(f"*.{config['ExtractedExtension'][romm_map_slug]}"):
                log.info(f'First available placeholder replacement: "{file}"')
                file.replace(esde_rom)
                placeholder_replaced = True

        # Clean-up after archive extraction and placeholder replacement

        if placeholder_replaced == True and config['General']['delete_archive_after_extraction'] == 'true':
            # Delete the downloaded archive
            archive_file.unlink()

        # Delete the temp folder and any remaining files
        shutil.rmtree(temp_location)
        
    sys.exit()

else:
    log.info('No Rom File: The search result returned by RomM did not have any files that matched the ES-DE file')
    log.info(f'RomM id: {romm_id} | ES-DE Filename: {romm_server_filename}')
    sys.exit()

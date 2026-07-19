# A script that utilizes the ES-DE 'game-start' event action to replace a placeholder file with the actual rom file provided by RomM
# GitHub: https://github.com/WirlyWirly/RomM-ES

# ==================================== Package Imports ====================================

# Standard Library
import json
import logging as log
import os
import re
import shlex
import subprocess
import sys

from configparser import ConfigParser
from pathlib import Path

# Third-party
import requests

# A basic logger
log_file = Path(sys.argv[0]).resolve().parents[0] / 'GameStart.log'
log.basicConfig(filename=log_file, filemode='w+', level=log.DEBUG, style='{', format='Line: {lineno} | level: {levelname} | Time: {asctime} | Info: {message}')

# ES-DE will pass 4 positional arguments when calling this script...
# "C:\path\to\rom.zip" "Game Name" "platform slug" "full platform name"
# Ex: "C:\path\to\Kirby - Nightmare in Dream Land (USA).zip" "Kirby - Nightmare in Dream Land (USA)" "gba" "Nintendo Game Boy Advance" 

log.debug(f'ES-DE Arg1: "{sys.argv[1]}"')
log.debug(f'ES-DE Arg2: "{sys.argv[2]}"')
log.debug(f'ES-DE Arg3: "{sys.argv[3]}"')
log.debug(f'ES-DE Arg4: "{sys.argv[4]}"')
log.debug(f'$ python ./GameStart.py "{sys.argv[1]}" "{sys.argv[2]}" "{sys.argv[3]}" "{sys.argv[4]}"')

esde_rom = Path(sys.argv[1]).resolve() # 'C:\path\to\rom.zip'
esde_rom_filename = esde_rom.name # 'rom.zip'
esde_slug = sys.argv[3] # 'gba'

# ==================================== Placeholder Verification ====================================

# Determine if the started game is a RomM placeholder and if so parse the RomM id
if os.path.getsize(esde_rom) > 20:
    # This game file is too large to be a placeholder file, so exit
    log.debug('Not a RomM placeholder, filesize is too small')
    sys.exit()

else:
    # This game file is small enough to be a placeholder file, continue verification...
    with esde_rom.open('r', encoding='UTF-8') as file:

        # Search the contents of the file for a RomM id number
        romm_id = re.search('^RomM-ES:(\d+)$', file.read())

        if romm_id is None:
            # No RomM id, so exit
            log.debug('Not a RomM placeholder, no RomM id')
            sys.exit()

        else:
            # Yes, this is a RomM placeholder file with a RomM id
            romm_id = int(romm_id[1])
            log.info(f'RomM id: {romm_id}')


# ==================================== Load Settings ====================================

# The absolute path to the RomM-ES directory
romm_es = Path(sys.argv[0]).resolve().parents[0]

# Load the options in the 'settings.ini' file
config_file = romm_es / 'settings.ini'
config = ConfigParser()
config.read(config_file)

# Read the mapped RomM slugs in 'platformMaps.json'
platform_maps = romm_es / 'platformMaps.json'
with platform_maps.open('r', encoding='utf-8') as file:
    platform_maps = json.load(file)

# Reverse match the ES-DE provided platform slug with the RomM equivalent
romm_slug = False
for key, value in platform_maps.items():
    if platform_maps[key]['esde'] == esde_slug:
        romm_slug = key
        log.debug(f'RomM Platform: {romm_slug}')
        break

if romm_slug == False:
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

# Check if this platform has a specified extension indicating extraction
extract_file = False
if config['ExtractExtension'][romm_slug] != '':
    extract_file = True


# Determine the rom file id from the list of attached files
for rom_file in game['files']:
    if esde_rom_filename == rom_file['file_name'] and romm_slug == game['platform_fs_slug']:
        # Match: The ES-DE filename and platform slug match the returned game, this must be the correct file

        log.info(f"RomM File id: {rom_file['id']}")
        log.info(f"RomM Filepath: \"{rom_file['full_path']}\"")
        rom_file_id = rom_file['id']
        break

if rom_file_id != False:
    # A file id was found, meaning there was a rom file match. The placeholder file will be replaced with the actual RomM provided rom file

    curl_download = f"curl -X GET '{romm_url}/api/roms/{rom_file_id}/files/content/romfile' -H 'Authorization: Bearer {romm_api}' --output \"{esde_rom}\""
    log.debug('Curl Command...')
    log.debug(curl_download)

    command = shlex.split(curl_download)
    log.debug('subprocess list...')
    log.debug(command)

    # ES-DE will wait until this subprocess has completed before starting the emulator. For larger files or slower connections, this may cause a stall.
    subprocess.run(command)

    sys.exit()

else:
    log.info('No Rom File: The search result returned by RomM did not have any files that matched the ES-DE file')
    log.info(f'RomM id: {romm_id} | ES-DE Filename: {esde_rom_filename}')
    sys.exit()

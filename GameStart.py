# This script utilizes the ES-DE 'game-start' event action to download a game file from RomM the first time that game is launched

# ES-DE will pass 4 positional arguments when calling this script...
# "C:\path\to\rom.zip" "Game Name" "platform slug" "full platform name"
# Ex: "C:\path\to\Kirby - Nightmare in Dream Land (USA).zip" "Kirby - Nightmare in Dream Land (USA)" "gba" "Nintendo Game Boy Advance" 

import sys
import re
import os
import shlex
import subprocess

from configparser import ConfigParser
from pathlib import Path

import requests

game_file = Path(sys.argv[1]).resolve()
game_filename = game_file.name
platform_slug = sys.argv[3]

if os.path.getsize(game_file) > 20:
    # This game file is too large to be a placeholder file, so do nothing
    sys.exit()
else:
    # Open the file to verify it is a placeholder file
    with game_file.open('r', encoding='UTF-8') as file:
        contents = file.read()

        rom_id = re.search('^RomM-ES=(\d+)$', contents)

        if rom_id is None:
            sys.exit()
        else:
            rom_id = int(rom_id[1])



# The absolute path to the RomM-ES directory
romm_es = Path(sys.argv[0]).resolve().parents[0]

# Read the options in 'settings.ini' file
config_file = romm_es / 'settings.ini'
config = ConfigParser()
config.read(config_file)

# The ES-DE directory and relevant child directories
roms_folder = Path(config['General']['esde_roms'])

# ==================================== ROMM DOWNLOADING ====================================

romm_url = config['General']['romm_url']
romm_api = config['General']['romm_apitoken']

romm_auth = { 'Authorization': f'Bearer {romm_api}' }

# Search RomM by id
response = requests.get(f'{romm_url}/api/roms/{rom_id}', headers=romm_auth)
game = response.json()
rom_file_id = False

# Determine the rom id from the list of attached files
for rom_file in game['files']:
    if game_filename == rom_file['file_name'] and platform_slug == game['platform_fs_slug']:
        # The ES-DE filename and platform slug match that of RomM, this is the correct rom file

        rom_file_id = rom_file['id']
        break

if rom_file_id != False:

    rom_download_url = f'{romm_url}/api/roms/{rom_file_id}/files/content/romfile'
    curl_command = f"curl -X GET {rom_download_url} -H 'Authorization: Bearer {romm_api}' --output '{game_file}'"
    command = shlex.split(curl_command)
    subprocess.run(command)

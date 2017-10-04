# TTScraper
A tool for creating a local copy of all resources from a Tabletop Simulator save file, and patching the save file for re-deployment to a new server.

[![asciicast](https://asciinema.org/a/140743.png)](https://asciinema.org/a/140743)

## Usage
The script accepts two parameters:

1. The path to the save game file
2. The directory to output the resource files and new save game file to

For example, if the saved game was in `/home/user/tabletopkin.json`, and you wanted to output to `/home/user/new_save_game`, you would run: `python ttscraper.py /home/user/tabletopkin.json /home/user/new_save_game`

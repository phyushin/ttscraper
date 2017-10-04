import requests
import json
import sys
import os
import uuid

RED   = "\033[1;31m"
BLUE  = "\033[1;34m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD  = "\033[;1m"

print ""
print "  _____ _____ ___                            "
print " |_   _|_   _/ __| __ _ _ __ _ _ __  ___ _ _ "
print "   | |   | | \__ \/ _| '_/ _` | '_ \/ -_) '_|"
print "   |_|   |_| |___/\__|_| \__,_| .__/\___|_|  "
print "                              |_|            "
print ""

if len(sys.argv) < 3:
    print ' Usage: ttscraper.py [path to save file] [path to output folder]'
    print ''
    exit()

output_path = sys.argv[2]
cache_path = os.path.join(output_path, 'resources')

def recursive_iter(obj):
    if isinstance(obj, dict):
        for item in obj.values():
            for reitem in recursive_iter(item):
                yield reitem
    elif any(isinstance(obj, t) for t in (list, tuple)):
        for item in obj:
            for reitem in recursive_iter(item):
                yield reitem
    else:
        yield obj

def looks_like_url(x):
    try:
        return str(x).startswith("http://") or str(x).startswith("https://")
    except:
        return False

def parse_urls_from_json(path):
    urls = []
    with open(path, 'r') as f:
        data = json.load(f)
        for el in recursive_iter(data):
            if looks_like_url(el):
                if str(el) not in urls:
                    urls.append(str(el))
    return urls

def print_success(msg):
    print BOLD + ' [' + GREEN + '+' + RESET + BOLD + '] ' + RESET + msg

def print_info(msg):
    print BOLD + ' [' + BLUE + '*' + RESET + BOLD + '] ' + RESET + msg

def print_warning(msg):
    print BOLD + ' [' + RED + '!' + RESET + BOLD + '] ' + RESET +  msg

print_info('Parsing the save file...')
urls = parse_urls_from_json(sys.argv[1])

if len(urls) == 0:
    print_warning('No resources could be found in this file - are you sure this is a TTS save?')
    print ''
    exit()

print_success('Found {url_count} resources within the save.'.format(url_count=len(urls)))
print_info('Creating local resource cache in {cache}...'.format(cache=cache_path))

if not os.path.exists(cache_path):
    os.makedirs(cache_path)

user_agent_string = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
headers = { 'User-Agent': user_agent_string }
url_uuid_map = []

has_failure = False
url_index = 0
for url in urls:
    url_index += 1
    url_uuid = str(uuid.uuid4())
    res = requests.get(url, headers=headers, stream=True)
    if res.status_code == 200:
        with open(os.path.join(cache_path, url_uuid), 'wb') as f:
            for chunk in res:
                f.write(chunk)
        print_success('Processed file {i} of {c}'.format(i=url_index,c=len(urls)))
        url_uuid_map.append({ 'url': url, 'uuid': url_uuid})
    else:
        print_warning('Failed to download {url}'.format(url=url))
        has_failure = True

print_info('Patching save file...')
with open(sys.argv[1], 'r') as original_save:
    data = original_save.read()
    patch_count = 0
    for kvp in url_uuid_map:
        patch_count += 1
        data = data.replace(kvp['url'], '_TTSCRAPER_BASE_URL_{uuid}'.format(uuid=kvp['uuid']))
        print_success('Patched resource {i} of {c}'.format(i=patch_count, c=len(url_uuid_map)))

    with open(os.path.join(output_path, 'Save.json'), 'w') as patch:
        patch.write(data)
        patch.close()

print ''
print ' ---'
print ''
print_success('Created patched file in {patch_path}'.format(patch_path=os.path.join(output_path, 'Save.json')))

if has_failure:
    print_warning('One or more resources failed to download. These resources will be loaded from their original URL.')

print ''
print ' ---'
print ''
print ' When ready to deploy the new save, follow these steps:'
print ''
print '   1. Upload all files in the "resources" directory to your server.'
print '   2. Replace all instances of _TTSCRAPER_BASE_URL_ in Save.json with the URL of '
print '      the directory that you uploaded the resources to in step 1.'
print '   3. Copy Save.json into your "Saves" directory within Tabletop Simulator'
print '   4. Launch the game, load your new saved game, have fun!'
print ''
print ' Happy table topping!'
print ''

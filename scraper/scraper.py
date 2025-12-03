import requests
from bs4 import BeautifulSoup
import sys
import subprocess
from backups import backup_sync 
headers = {
    'User-Agent': 'Mozilla/5.0'
}

db = backup_sync.DB('my_devices', 'M722319355m', 'musa', 'localhost')
rows = db.query('SELECT * FROM devices')
print(rows)
sys.exit(0)

URL = "https://thepibay.site/search/stranger.things.elite"

def soup(url):
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")

def run(cmd, **kwargs):
    try:
        res = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)
        out = res.stdout.strip()
        return out
    except Exception as e:
        return f'Failed Command: {cmd} ({e})'

season = soup(URL)

if not season:
    print('Series not found')
    sys.exit()

episode = season.find('a', href = lambda x: x and 'E01' in x)
print(season)

if episode:
    torr = soup(episode['href'])
    magnet = torr.find('a', href = lambda x: x and x.startswith('magnet:'))
    print(magnet['href'])
else:
    print('Episode not found')

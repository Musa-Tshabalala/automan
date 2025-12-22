from .config import logfile, headers
from bs4 import BeautifulSoup
import re, requests, subprocess, json
from datetime import datetime
from datetime import datetime
from zoneinfo import ZoneInfo

################################################################################################
# General Utils --------------------------------------------------------------------------------

def run(cmd, **kwargs):
    try:
        res = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)
        out = res.stdout.strip()
        return out
    except Exception as e:
        return f'Failed Command: {cmd} ({e})'
    
# Appends output state to_dev file:
def log(msg):
    
    now = (
        datetime
        .now(ZoneInfo("Africa/Johannesburg"))
        .strftime(f"Date: %Y/%m/%d\nTime: %H:%M")
        )

    with open(logfile, 'a') as f:
        f.write(f'{now}\n{msg}\n--- --- ---\n')
    

def is_valid_ip(ip, db):
    octet = '(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])'
    regex = fr'^100\.{octet}\.{octet}\.{octet}$'

    match = re.search(f'{regex}', ip)

    if match:
        device = db.query('SELECT * FROM devices WHERE ip = %s;', (ip,))
        return { 'ok': True, 'payload': device } if device else { 'ok': False, 'error': 'Unregisterd IP address' }
    else:
        return { 'ok': False,  'error': 'Invalid IP address' }

###############################################################################################
# Utils for torrent ---------------------------------------------------------------------------

def soup(url):
    res = requests.get(url, headers=headers)
    return BeautifulSoup(res.text, 'html.parser')

def imdb(meta):
    id = meta['id'].strip()
    if not id:
        return None
    
    URL = (
        f'https://www.imdb.com/title/{id}/' 
        if meta['type'] == 'movie' 
        else f"https://www.imdb.com/title/{id}/episodes?season={meta['s']}"
    )
 
    bsoup = soup(URL)
    try:
        script_tag = bsoup.find('script', id='__NEXT_DATA__', type='application/json')
        data = json.loads(script_tag.string)
        if meta['type'] != 'movie':
            episodes = (
                data['props']['pageProps']['contentData']['section']['episodes']['items']
            )
            return next((x for x in episodes if x['episode'] == meta['e']), None)
        else:
            movie = data['props']['pageProps']['aboveTheFoldData']
            return movie
        
    except Exception as e:
        log(f'ERROR: {e}')
        return None
    
def get_mime(path: str) -> str:
    return run(f'file --mime-type -b "{path}"')
    
############################################################################################
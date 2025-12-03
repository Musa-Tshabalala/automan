import subprocess
from .config import logfile, date_time
import re

def run(cmd, **kwargs):
    try:
        res = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)
        out = res.stdout.strip()
        return out
    except Exception as e:
        return f'Failed Command: {cmd} ({e})'
    
# Appends output state to_dev file:
def log(msg):
    with open(logfile, 'a') as f:
        f.write(f'{date_time}\n{msg}\n--- --- ---\n')

def is_valid_ip(ip, db):
    octet = '(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])'
    regex = fr'^100\.{octet}\.{octet}\.{octet}$'

    match = re.search(f'{regex}', ip)

    if match:
        device = db.query('SELECT * FROM devices WHERE ip = %s;', (ip,))
        return { 'ok': True, 'payload': device } if device else { 'ok': False, 'error': 'Unregisterd IP address' }
    else:
        return { 'ok': False,  'error': 'Invalid IP address' }

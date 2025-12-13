from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=str)
parser.add_argument('--ip', type=str)
parser.add_argument('--reverse', action='store_true', help='Enable reverse mode')
parser.add_argument('--partial', action='store_true', help='Disable Full Push')
args = parser.parse_args()

termux_port = 8022
src = f'~/storage/shared/{args.source}' if args.source else '~/storage/shared/Download'
relay = str(Path.home() / "stage")
logfile = f'{relay}/logs/sync-{datetime.now(ZoneInfo('Africa/Johannesburg')):%Y%m%d}.log'
dest = "C:/Users/TRUser/My_Phone"
torr_dest = "C:/Users/TRUser/Videos"
headers = {"User-Agent": "Mozilla/5.0"}
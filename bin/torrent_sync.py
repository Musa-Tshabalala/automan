import os, sys, time
from core.utils import log
from torrent.torrent import Torrent
from core.ssh import SSH
from core.adb import ADB
from core.db import DB
from dotenv import load_dotenv

load_dotenv()

devices_db = os.getenv('DEVICES_DB')
torrent_db = os.getenv('TORRENT_DB')
db_user = os.getenv('DBUSER')
db_pass = os.getenv('DBPASS')
ssh_key_file = os.getenv('SSHKEYFILE')

def main():
    with DB(torrent_db, db_pass, db_user, 'localhost') as torr_db:
        torr = torr_db.query('SELECT * FROM torrents')

        if not torr:
            return
        
        LOCK_FILE = "/tmp/torrent_sync.lock"

        if os.path.exists(LOCK_FILE):
            log('Script is already running!')
            sys.exit()

        open(LOCK_FILE, 'w').close()

        dev_db = DB(devices_db, db_pass, db_user, 'localhost')
        me = dev_db.query('SELECT * FROM devices WHERE id = 1;')[0]
        win_me = dev_db.query('SELECT * FROM devices WHERE id = 2;')[0]

        dev_db.close()

        adb_inst = ADB(me['ip'])
        adb = adb_inst.connect()

        if adb is None:
            log(f'Could not be reached to initialize torrent services')
            sys.exit(1)
        
        with SSH(me, ssh_key_file) as ssh_inst:
            tries = 3
            attempt = 0

            ssh = ssh_inst.connect()

            while attempt < tries and ssh.client is None:
                attempt += 1
                ssh = ssh_inst.connect()
                if ssh.client is None:
                    adb_inst.notify(f'Enable_SSH:_Attempt_{attempt}_of_{tries}')
                    time.sleep(300)
                else:
                    break
            
            if ssh.client is None:
                log('SSH main client was offline.')
                sys.exit(1)

            torrent = Torrent(adb_inst, ssh, win_me)
            torrent.start(torr, torr_db)
            os.remove(LOCK_FILE)

if __name__ == '__main__':
    main()



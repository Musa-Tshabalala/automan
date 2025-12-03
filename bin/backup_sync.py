#!/usr/bin/python3

import os, sys
from core.db import DB
from core.adb import ADB
from core.ssh import SSH
from core.utils import log
from core.config import args
from backup.sync import SyncService
from dotenv import load_dotenv

load_dotenv()

my_db = os.getenv('DBNAME')
db_user = os.getenv('DBUSER')
db_pass = os.getenv('DBPASS')
ssh_key_file = os.getenv('SSHKEYFILE')

def main():
    with DB(my_db, db_pass, db_user, 'localhost') as db:
        me = db.query('SELECT * FROM devices WHERE id = 1;')[0]
        adb_inst = ADB(me['ip'])
        adb_me = adb_inst.connect()
        with SSH(me, ssh_key_file) as ssh_inst:
            ssh_me = ssh_inst.connect()

            if adb_me is None:
                log('Could not connect to adb')
                if ssh_me.client is not None:
                    ssh_me.notify('ADB', 'ADB Could no be reached.')
                sys.exit(1)
            
            if ssh_me.client is None:
                log('')
                adb_inst.notify('Enable_SSH')
                sys.exit(1)

            service = SyncService(db, ssh_me, adb_inst)
            service.sync(args)    
            
if __name__ == '__main__':
    main()




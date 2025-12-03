from .rsync import RSync
from .sftp import sftp
from core.ssh import SSH
from core.utils import is_valid_ip, log, run
from core.config import relay
import sys

class SyncService:
    def __init__(self, db, ssh, adb):
        self.db = db
        self.ssh_me = ssh
        self.adb_me = adb

    def sync(self, args):

        if args.ip:
            is_valid = is_valid_ip(args.ip, self.db)

            if not is_valid.get('ok'):
                error = is_valid.get('error')
                log(f'Failure for IP: {args.ip}\nERROR: {error}')
                self.adb_me.push_log()
                self.ssh_me.notify('Devices', f'{error}')
                sys.exit(1)

            payload = is_valid.get('payload')[0]
            ssh_inst = SSH(payload, self.ssh_me.key_file)
            ssh_ready = ssh_inst.connect()

            if ssh_ready.client is None:
                log(f"Could not establish SSH connection:\nIP: {args.ip} [{payload['brand']}]")
                self.adb_me.push_log()
                self.ssh_me.notify('Devices', 'Could not establish SSH connection to given IP')
                sys.exit(1)

            ssh_ready.client.close()

        run(f'mkdir -p {relay} && mkdir -p {relay}/logs')
        me = self.adb_me.me
        ip = args.ip if args.ip else me

        client = self.db.query('SELECT * FROM devices WHERE ip = %s;', (ip,))[0]
        if args.reverse:
            if client['os'] != 'Windows':
                log(f'Attempting download to {ip}...')
                self.adb_me.push_log()
                self.ssh_me.notify('Download Attempt', f'VPS -> {ip}')
                sync = RSync(client, self.adb_me, self.ssh_me)
                sync.download()
        else:
            if args.partial:
                log(f'{client['brand']} [{ip}] attempting to push to VPS...')
                self.adb_me.push_log()
                self.ssh_me.notify('Upload Attempt', f'{ip} -> VPS')
                sync = RSync(client, self.adb_me, self.ssh_me)
                sync.upload()
            else:
                windows_client = self.db.query('SELECT * FROM devices WHERE id = 2;')
                if not windows_client:
                    log('Destination device is not registered.')
                    self.adb_me.push_log()
                    self.ssh_me.notify('Database', 'Could not find windows on the database.')
                    sys.exit(1)
                
                windows_inst = SSH(windows_client[0], self.ssh_me.key_file)
                windows_ssh = windows_inst.connect()

                if windows_ssh.client is not None:
                    sync = RSync(client, self.adb_me, self.ssh_me)
                    log(f'{windows_client[0]['brand']} [{ip}] attempting to push to Windows...')
                    self.adb_me.push_log()
                    self.ssh_me.notify('Upload Attempt', f'{ip} -> Windows')
                    download = sync.upload()

                    if download.completed:
                        push = sftp(windows_ssh.client, windows_client[0], self.adb_me, self.ssh_me)
                        
                        if push.get('ok'):
                            log('Full upload complete.')
                            self.adb_me.push_log()
                            self.ssh_me.notify('Backups', 'Full backup complete.')
                else:
                    log('Cannot push to Windows, Target could not be found.')
                    self.adb_me.push_log()
                    self.ssh_me.notify('VPS -> Wndows', 'Could not find windows on SSH')







            
        

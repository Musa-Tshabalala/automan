from core.utils import log, run
from core.config import relay, src
import asyncio

class RSync:
    def __init__(self, client, adb, ssh):
        self.client = client
        self.adb = adb
        self.ssh = ssh
        self.opts = '-avz --partial --delay-updates --ignore-existing --bwlimit=5000 --compress-level=1'
        self.completed = False
        self.error = ''

    def download(self):
        msg = f"Beginning sync to '{self.client['owner']}\'s  {self.client['brand']}"
        log(f'VPS -> {self.client['brand']}\n{msg}')
        self.adb.push_log()
        self.ssh.notify('Server Push', f'{msg}')
        rsync_to = f"rsync {self.opts} -e 'ssh -p {self.client['port']}' {relay} {self.client['uname']}@{self.client['ip']}:{src}"
        download = run(rsync_to)

        if 'sent' in download:
            log(f'Download for {self.client['owner']} is complete!')
            self.adb.push_log()
            self.ssh.notify('Server Push', 'Your data has been loaded.')
            self.completed = True
            return self
        else:
            log(f'Transfer Failure\n"{download}"')
            self.adb.push_log
            self.ssh.notify('Server Pull', 'Pull failed! Updated logs.')
            self.completed = False
            self.error = download
            return self
                
    def upload(self):
        sync = f'rsync {self.opts} -e "ssh -p {self.client['port']}" {self.client['uname']}@{self.client['ip']}:{src} {relay}'
        push = run(sync)
        if 'sent' in push:
            log(f'Upload from {self.client['owner']} is complete!')
            self.adb.push_log()
            self.ssh.notify('Server Pull', 'Backup process has completed')
            self.completed = True
            return self
        else:
            log(f'Transfer Failure\n"{push}"')
            self.adb.push_log()
            self.ssh.notify('Server Pull', 'Push failed! Updated logs.')
            self.completed = False
            self.error = push
            return self
        
async def push(self, ssh):
    ssh.notify('Server Push', f'Uploading new downloads')
    ip = ssh.host
    port = ssh.port
    user = ssh.user
    rsync_opts = '-avz --partial --delay-updates --ignore-existing --bwlimit=5000 --compress-level=1'
    path = '/home/musa/downloads'
    sync = f"rsync {rsync_opts} -e 'ssh -p {port}' '{path}' {user}@{ip}:~/storage/shared/automan"
    loop = asyncio.get_event_loop()

    res = await loop.run_in_executor(None, lambda: run(sync))
    
    if 'sent' in res:
        log(res)
        loop.run_in_executor(None, lambda: ssh.notify('Server Push', f'New downloads successfully uploaded.'))
    else:
        log(res)
        loop.run_in_executor(None, lambda: ssh.notify('Server Push', f'Could not upload new downloads'))
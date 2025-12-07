from abc import abstractmethod, ABC
from core.utils import run, log
import os, asyncio

class Show(ABC):
    site = 'https://thepibay.site/search/'

    def __init__(self, meta):
        self._name = None
        self._meta = meta
        self.downloaded = False
        self.magnet = None
        self._path = None
        self._title = meta['title']

    @property
    def meta(self):
        return self._meta
    
    @property
    def name(self):
        return self._name
    
    @abstractmethod
    def search(self, title):
        pass

    def download(self):
        if self.magnet is None:
            raise ValueError(f'{self.magnet} is invalid for downloads')

        base_dir = os.path.expanduser("~/downloads")
        path = os.path.join(base_dir, self._title.title())
        self._path = path

        cmd = f"aria2c --seed-ratio=0 --seed-time=0 --dir='{path}' '{self.magnet}'"
        download = run(cmd)

        ep = self._name if self._name is not None else f"Episode {self._meta['e']}"

        if '(OK):download completed.' in download:
            log(f'Downloads: {self._title.title()}: {ep} completed successfully!')
            self.downloaded = True
            return
        if 'aborted' in download or 'ERROR' in download:
            log(f'Download failed for {self._title}')
            self.downloaded = False
            return
        return self.downloaded

    async def push(self, ssh):
        ssh.notify('Server Push', f'Uploading: {self._name}')
        ip = ssh.host
        port = ssh.port
        user = ssh.user
        rsync_opts = '-avz --partial --delay-updates --ignore-existing --bwlimit=5000 --compress-level=1'
        path = self._path
        sync = f"rsync {rsync_opts} -e 'ssh -p {port}' '{path}' {user}@{ip}:~/storage/shared/automan"
        loop = asyncio.get_event_loop()

        res = await loop.run_in_executor(None, lambda: run(sync))
        
        if 'sent' in res:
            log(res)
            loop.run_in_executor(None, lambda: ssh.notify('Server Push', f'{self._name} successfully uploaded.'))
        else:
            log(res)
            loop.run_in_executor(None, lambda: ssh.notify('Server Push', f'Could not upload {self._name}'))





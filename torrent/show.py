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

        category = 'SERIES' if self.meta['type'] == 'series' else 'MOVIES'
        base_dir = os.path.expanduser(f"~/downloads/{category}")
        path = os.path.join(base_dir, self._title.title()) if self.meta['type'] == 'series' else base_dir 
        self._path = path

        cmd = f"aria2c --seed-ratio=0 --seed-time=0 --dir='{path}' '{self.magnet}'"
        download = run(cmd)

        torr = self._name if self._name is not None else self._title.title()

        if '(OK):download completed.' in download:
            log(f'Downloads: {self._title.title()}: {torr} completed successfully!')
            self.downloaded = True
            return
        if 'aborted' in download or 'ERROR' in download:
            log(f'Download failed for {self._title}')
            self.downloaded = False
            return
        return self.downloaded




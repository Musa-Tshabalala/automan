from abc import abstractmethod, ABC
from pathlib import Path
from core.utils import run, log, get_mime
import os, shutil

class Show(ABC):
    site = 'https://thepibay.site/search/'
    dest = Path.home() / 'downloads'
    quarantine = Path.home() / 'downloads' / '.quarantine' 
    MIME_SET = { 'video/x-matroska', 'video/mp4' }
    MALWARE_SET = { 
        'application/x-iso9660-image',
        'application/x-dosexec',
        'application/x-executable'            
    }

    def __init__(self, meta):
        self._name = None
        self._meta = meta
        self.downloaded = False
        self.magnet = None
        self._path = None
        self._quarantine = None
        self._title = meta['title']
        self._malware = False

    @property
    def meta(self):
        return self._meta
    
    @property
    def malware(self):
        return self._malware
    
    @property
    def name(self):
        return self._name
    
    @abstractmethod
    def search(self):
        pass

    def is_malware(self, child):
        mime = get_mime(child)
        if mime in Show.MALWARE_SET:
            log(f'Malware of mime {mime} detected:\n{child}')
            print('Malware detected:', child)
            return True, f'Malware: {mime}'
        
        return False, mime
    
    def malware_safe(self):
        malware = False
        msg = None
        for child in self._quarantine.iterdir():
            if child.is_dir():
                for sub_child in child.iterdir():
                    malware, msg = self.is_malware(sub_child)
                    if malware:
                        print('Removing directory containing malware:', child)
            else:
                malware, msg = self.is_malware(child)

        if malware:
            for child in Show.quarantine.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    os.remove(child)
        
        return True, 'Safe' if not malware else False, msg
                        
    def download(self):
        if self.magnet is None:
            log(f'{self.magnet} is invalid for downloads')
            return
        
        Show.quarantine.mkdir(parents=True, exist_ok=True)

        category = 'SERIES' if self.meta['type'] == 'series' else 'MOVIES'
        quarantine_dir = Show.quarantine / category
        path = os.path.join(quarantine_dir, self._title.title()) if self.meta['type'] == 'series' else quarantine_dir 
        
        download = run(f"aria2c --seed-ratio=0 --seed-time=0 --dir='{path}' '{self.magnet}'")

        print(download)

        torr = self._name if self._name is not None else self._title.title()

        if '(OK):download completed.' in download:
            log(f'Downloads: {self._title.title()}: {torr} completed successfully!')
            self._quarantine = Path(path)
            self._path = Show.dest / category if self.meta['type'] == 'movie' else Show.dest / category / self._title.title()
            self.downloaded = True
            return
        else:
            log(f'Download failed for {self._title}\nERROR:\n{download}')
            return




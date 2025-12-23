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

    def is_malware(self, dir):
        found_malware = False

        for child in dir.iterdir():
            if child.is_dir():
                if self.is_malware(child):
                    found_malware = True
            else:
                is_bad = get_mime(child) in Show.MALWARE_SET
                if is_bad:
                    log(f'Malware: {child}')
                    found_malware = True

        return found_malware
    
    def move(self, src: Path, to: str) -> bool:
        video = False
        for child in src.iterdir():
            if child.is_dir():
                if self.move(child, to):
                    video = True
            else:
                if get_mime(child) in Show.MIME_SET:
                    shutil.move(str(child), to + child.suffix.lower())
                    video = True

        return video
    
    def cleanup(self, dir):
        for child in dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                os.remove(child)
                        
    def download(self):
        if self.magnet is None:
            log(f'{self.magnet} is invalid for downloads')
            return
        
        Show.quarantine.mkdir(parents=True, exist_ok=True)

        category = 'SERIES' if self.meta['type'] == 'series' else 'MOVIES'
        quarantine_dir = Show.quarantine / category
        path = os.path.join(quarantine_dir, self._title.title()) if self.meta['type'] == 'series' else quarantine_dir 
        
        download = run(f"aria2c --seed-ratio=0 --seed-time=0 --dir='{path}' '{self.magnet}'")

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




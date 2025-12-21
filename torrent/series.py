from .show import Show
from pathlib import Path
from core.utils import soup, imdb, log, get_mime
import re, shutil, os

class Series(Show):
    def search(self):
        title = self._meta['title']
        search_string = re.sub(r'\s+', '.', title.strip()).lower()
        url = Show.site + search_string + '.elite'
        ep = f"S{int(self._meta['s']):02}E{int(self._meta['e']):02}"

        bsoup = soup(url)
        magnet = bsoup.find('a', href = lambda x: x and x.startswith('magnet:') and not x in self.meta['malware'] and ep in x)
        if magnet is None:
            return
        
        imdb_data = imdb(self._meta)
        self._name = imdb_data['titleText'] if imdb_data is not None else None
        self.magnet = magnet['href']
        return self.magnet
    
    def format(self):
        if self._path is None or self._quarantine is None:
            log(f'ERROR:\n{self._path} is not a working directory.')
            return False, f'Path for {self._title} found'
        
        ok, msg = self.malware_safe()

        if not ok:
            self._malware = True
            return msg

        base_path = Path(self._path)

        s = self._meta['s']
        e = f"{int(self._meta['e']):02}"
        rename_title = f"{e}. {re.sub(r'\:+', ' -', self._name)}.mkv" if self._name is not None else f'Episode {e}.mkv'

        season_folder = base_path / f'Season {s}'

        season_folder.mkdir(parents=True, exist_ok=True)
        new_mkv = season_folder / rename_title

        for child in self._quarantine.iterdir():
            mime = get_mime(child)
            if child.is_dir():
                for sub_child in child.iterdir():
                    mime = get_mime(sub_child)

                    if mime in Show.MIME_SET:
                        shutil.move(str(sub_child), str(new_mkv))

                shutil.rmtree(child)
            elif mime in Show.MIME_SET:
                shutil.move(str(child), str(new_mkv))
            else:
                os.remove(child)

        for child in Show.quarantine.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                os.remove(child)
                       
        
        


        

        
        

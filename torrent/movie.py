from .show import Show
from core.utils import soup, imdb, log, get_mime
import re, shutil, os
from pathlib import Path

class Movie(Show):
    def search(self):
        title = self._meta['title']
        search_string = re.sub(r'\s+', '.', title.strip()).lower()
        url = Show.site + search_string + '.bluray'
        y = self._meta['y']
        px = '1080p'
        bsoup = soup(url)
        magnet = bsoup.find('a', href = lambda x: x and x.startswith('magnet:') and y in x and px in x)
        if magnet is None:
            return
        
        imdb_data = imdb(self._meta)
        self._name = imdb_data['titleText']['text'] if imdb_data is not None else title
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
        mov_name = f"{re.sub(r'\:+', ' -', self._name)} " + f"({self.meta['y']})"
        movie_path = str(base_path / mov_name)

        base_path.mkdir(parents=True, exist_ok=True)

        for child in self._quarantine.iterdir():
            mime = get_mime(child)
            if child.is_dir():
                for sub_child in child.iterdir():
                    mime = get_mime(sub_child)
                    if mime in Show.MIME_SET:
                        movie_path += sub_child.suffix.lower()
                        shutil.move(str(sub_child), movie_path)
            elif mime in Show.MIME_SET:
                movie_path += child.suffix.lower()
                shutil.move(str(child), movie_path)
            else:
                os.remove(child)
                
        for child in Show.quarantine.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                os.remove(child)


        




from .show import Show
from core.utils import soup, imdb, log
import re
from pathlib import Path

class Movie(Show):
    def search(self):
        title = self._meta['title']
        search_string = re.sub(r'\s+', '.', title.strip()).lower()
        url = Show.site + search_string + '.bluray'
        y = self._meta['y']
        px = '1080p'
        bsoup = soup(url)
        magnet = bsoup.find('a', href = lambda x: x and x.startswith('magnet:') and not x in self.meta['malware'] and y in x and px in x)
        if magnet is None:
            return
        
        imdb_data = imdb(self._meta)
        self._name = imdb_data['titleText']['text'] if imdb_data is not None else title
        self.magnet = magnet['href']
        return self.magnet
    
    def format(self):
        if self._path is None or self._quarantine is None:
            log(f'ERROR:\n{self._path} is not a working directory.')
            return
        
        malware = self.is_malware()

        if malware:
            self.cleanup(Show.quarantine)
            self._malware = True
            return

        base_path = Path(self._path)
        mov_name = f"{re.sub(r'\:+', ' -', self._name)} " + f"({self.meta['y']})"
        movie_path = str(base_path / mov_name)

        base_path.mkdir(parents=True, exist_ok=True)

        self.cleanup(Show.quarantine) if self.move(self._quarantine, movie_path) else log(f"{mov_name}: Not Found")
                
        


        




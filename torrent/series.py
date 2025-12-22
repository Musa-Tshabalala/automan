from .show import Show
from pathlib import Path
from core.utils import soup, imdb, log
import re

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
        if self._path is None:
            log(f'ERROR:\n{self._path} is not a working directory.')
            return
        
        malware = self.is_malware()

        if malware:
            self.cleanup(Show.quarantine)
            self._malware = True
            return

        base_path = Path(self._path)

        s = self._meta['s']
        e = f"{int(self._meta['e']):02}"
        rename_title = f"{e}. {re.sub(r'\:+', ' -', self._name)}" if self._name is not None else f'Episode {e}'

        season_folder = base_path / f'Season {s}'

        season_folder.mkdir(parents=True, exist_ok=True)
        new_mkv = str(season_folder / rename_title)

        self.cleanup(Show.quarantine) if self.move(self._quarantine, new_mkv) else log(f'{new_mkv}: Not found')
                       
        
        


        

        
        

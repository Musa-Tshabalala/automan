from .show import Show
from pathlib import Path
from core.utils import soup, imdb, run, log
import re, shutil, os

class Series(Show):
    def search(self):
        title = self._meta['title']
        search_string = re.sub(r'\s+', '.', title.strip()).lower()
        url = Show.site + search_string + '.elite'
        s = self._meta['s']
        e = self._meta['e']
        ep = ''

        try:
            ep += f'S0{s}' if int(s) < 10 else f'S{s}'
            ep += f'E0{e}' if int(e) < 10 else f'E{e}'
        except ValueError:
            self.magnet = None
            return self.magnet

        bsoup = soup(url)
        magnet = bsoup.find('a', href = lambda x: x and x.startswith('magnet:') and ep in x)
        imdb_data = imdb(self._meta)
        self._name = imdb_data['titleText'] if imdb_data is not None else None
        self.magnet = magnet['href'] if magnet is not None else None
        return self.magnet
    
    def format(self):
        if self._path is None:
            log(f'ERROR:\n{self._path} is not a working directory.')
            raise Exception('Cannot rename an unexisting file.')
        
        s = self._meta['s']
        e = f"{int(self._meta['e']):02}"     # Formats 1 → 01, 9 → 09, 10 → 10
        rename_title = f"{e}. {re.sub(r'\:+', ' -', self._name)}.mkv" if self._name is not None else f'Episode {e}.mkv'

        base_path = Path(self._path)
        season_folder = base_path / f'Season {s}'

        season_folder.mkdir(parents=True, exist_ok=True)

        mkv = None
        episode_folder = None
        new_mkv = season_folder / rename_title

        for child in base_path.iterdir():
            if child.suffix.lower() == '.aria2':
                os.remove(child)

            if child.suffix.lower() == '.mkv':
                mkv = child
                shutil.move(str(child), str(new_mkv))
            else:
                if f'E{e}' in child.name and child.is_dir():
                    episode_folder = child

        if mkv is not None:
            return
        
        for file in episode_folder.iterdir():
            if file.suffix.lower() == '.mkv':
                shutil.move(str(file), str(new_mkv))
                shutil.rmtree(episode_folder)
        


        

        
        

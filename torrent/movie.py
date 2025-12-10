from .show import Show
from core.utils import soup, imdb, log
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
        imdb_data = imdb(self._meta)
        self._name = imdb_data['titleText']['text'] if imdb_data is not None else title
        self.magnet = magnet['href'] if magnet is not None else None
        return self.magnet
    
    def format(self):
        base_path = Path(self._path)
        mov_folder = None
        mov_name = f"{re.sub(r'\:+', ' -', self._name)}"
        movie_in_base = None
        movie_path = base_path / mov_name

        for child in base_path.iterdir():
            if child.suffix.lower() == '.aria2':
                os.remove(child)
                
            if child.suffix.lower() == '.mp4' or child.suffix.lower() == '.mkv':
                movie = str(movie_path) + child.suffix.lower()
                movie_in_base = child
                shutil.move(str(child), movie)
            else:
                if 'bluray' in child.name.lower() and child.is_dir():
                    mov_folder = child
        
        if movie_in_base is not None:
            return
        
        if mov_folder is None:
            log(f'{mov_name} was not found.')
            return

        for file in mov_folder.iterdir():
            if file.suffix.lower() == '.mp4' or file.suffix.lower() == '.mkv':
                movie = str(movie_path) + file.suffix.lower()
                shutil.move(str(file), movie)
                shutil.rmtree(str(mov_folder))


        




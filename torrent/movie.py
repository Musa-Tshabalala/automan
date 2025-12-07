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
        magnet = bsoup.find('a', href = lambda x: x and x.startswith('magnet:') and y and px in x)
        imdb_data = imdb(self._meta)
        self._name = imdb_data['titleText']['text'] if imdb_data is not None else title
        self.magnet = magnet['href'] if magnet is not None else None
        return self.magnet
    
    def format(self):
        base_path = Path(self._path)
        mov_folder = None
        mov_name = f"{re.sub(r'\:+', ' -', self._name)}.mp4"

        for child in base_path.iterdir():
            if child.suffix.lower() == '.aria2':
                os.remove(child)
            if 'bluray' in child.name.lower() and child.is_dir():
                mov_folder = child
        
        if not mov_folder:
            log(f'Folder for {mov_name} was not found.')
            return

        movie = None
        for file in mov_folder.iterdir():
            if file.suffix.lower() == '.mp4':
                movie = file
                break
        
        if not movie:
            log(f"Movie not found: {mov_name}")
            return
        
        new_movie = base_path / mov_name
        shutil.move(str(movie), str(new_movie))
        shutil.rmtree(mov_folder)


        




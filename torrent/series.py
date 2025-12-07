from .show import Show
from core.utils import soup, imdb, run, log
import re

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
            raise Exception('Cannot rename an unexisting file.')
        
        s = self._meta['s']
        e = f"{int(self._meta['e']):02}"     # Formats 1 → 01, 9 → 09, 10 → 10
        rename_title = f"{e}. {self._name}.mkv" if self._name is not None else f'Episode {e}.mkv'

        # Create season directory
        mkdir = f"mkdir -p '{self._path}/Season {s}'"
        if run(mkdir):
            return

        # Find episode folder
        find_episode_folder = f"ls {self._path} | grep 'E{e}' | grep -v .aria"
        aria_file = run(f"ls {self._path} | grep .aria")
        if aria_file:
            log(f"Removing aria file: {aria_file}")
            run(f" rm '{self._path}/{aria_file}'")

        episode_folder = run(find_episode_folder).strip()

        if not episode_folder:
            log(f"episode folder for {rename_title} not found")
            return

        episode_path = f"{self._path}/{episode_folder}"

        # Find the mkv
        find_mkv = f"ls '{episode_path}' | grep '.mkv'"
        mkv_file = run(find_mkv).strip()

        if f'E{e}' not in mkv_file:
            log(f"No mkv file found for {rename_title}")
            return

        # Rename and move file
        move_cmd = (
            f"mv '{episode_path}/{mkv_file}' "
            f"'{self._path}/Season {s}/{rename_title}'"
        )

        if not run(move_cmd):
            # remove episode folder
            log(f"{mkv_file} has been renamed to {rename_title}")
            run(f"rm -rf '{episode_path}'")


        

        
        

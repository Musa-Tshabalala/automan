
from .movie import Movie
from .series import Series
from core.utils import log
from backup.rsync import push
import asyncio

class Torrent:
    def __init__(self, adb_client, ssh_client):
        self.__adb = adb_client
        self.__ssh = ssh_client
        
    def start(self, torr, torr_db):
        if not isinstance(torr, (list, tuple)):
            raise TypeError(f'ERROR: {torr} is not a type of list or tuple.')
        
        ssh = self.__ssh
        adb = self .__adb 
        new_torrent = False

        for meta in torr:
            torrent = None

            if meta['type'] == 'series':
                torrent = Series(meta)
            elif meta['type'] == 'movie':
                torrent = Movie(meta)
            else:
                log(f'ERROR Invalid torrent type:\n{meta}')
                adb.push_log()
                ssh.notify('ERROR', 'Invalid torrent type.')
                continue
            
            magnet = torrent.search()

            if magnet is not None:
                title = 'Downloading'
                content = f"{meta['title'].title()}: {torrent.name}" if meta['type'] == 'series' else torrent.name
                log(f'Beginning download:\n{content}')
                ssh.notify(title, content)
                downloaded = torrent.download()

                if downloaded or torrent.downloaded:
                    new_torrent = True
                    log(f'Download Complete:\n{torrent.name}')
                    adb.push_log()
                    ssh.notify('Downloads', f'{torrent.name}: Complete!')
                    torrent.format()
                    id = meta['id']
                    if meta['type'] == 'series':
                        e = meta['e']
                        max_e = meta['max_e']
                        if int(e) >= int(max_e):
                            torr_db.execute(
                                """
                                DELETE FROM torrents WHERE id = %s; 
                                """,
                                (id,)
                            )
                        else:
                            next_e = str(int(e) + 1)
                            torr_db.execute("UPDATE torrents SET e = %s WHERE id = %s;", (next_e, id))
                    else:
                        torr_db.execute("DELETE FROM torrents WHERE id = %s", (id,))
            else:
                message = f"{meta['type'].title()} has not been found yet: {meta['title'].title}"
                log(message)
                continue

        if new_torrent:
            asyncio.run(push(ssh))

                





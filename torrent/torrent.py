from .movie import Movie
from .series import Series
from core.utils import log
from core.ssh import SSH
from backup.sftp import torr_sftp
from backup.rsync import push
from core.config import torr_dest
import asyncio, time, os, sys

class Torrent:
    def __init__(self, adb_client, ssh_client, win_me):
        self.__adb = adb_client
        self.__ssh = ssh_client
        self.win_me = win_me
        
    def start(self, torr, torr_db):
        if not isinstance(torr, (list, tuple)):
            raise TypeError(f'ERROR: {torr} is not a type of list or tuple.')
        
        ssh = self.__ssh
        adb = self.__adb 
        downloads = []
        non_downloads = []

        malware = torr_db.query('SELECT magnet FROM malware')
        malware = malware[0] if malware else { 'magnet': [] }

        for meta in torr:
            torrent = None
            meta['malware'] = malware['magnet']

            if meta['type'] == 'series':
                torrent = Series(meta)
            elif meta['type'] == 'movie':
                torrent = Movie(meta)
            else:
                log(f'ERROR Invalid torrent type:\n{meta}')
                ssh.notify('ERROR', 'Invalid torrent type.')
                continue
            
            torrent.search()
            
            if torrent.magnet is not None:
                title = 'Downloading'
                content = f"{meta['title'].title()}: {torrent.name}" if meta['type'] == 'series' else torrent.name
                log(f'Beginning download:\n{content}')
                ssh.notify(title, content)
                torrent.download()

                if torrent.downloaded:
                    torrent.format()
                    if not torrent.malware:
                        download = f"{meta['title']}: {torrent.name} (Episode {meta['e']})" if meta['type'] == 'series' else {torrent.name}
                        downloads.append(download)
                        ssh.notify('Downloads', f'{torrent.name}: Complete!')
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
                                meta['e'] = next_e
                                torr.append(meta)
                        else:
                            torr_db.execute("DELETE FROM torrents WHERE id = %s", (id,))
                    else:
                        log(f'{torrent.name} was virus infected and effectively removed')
                        adb.push_log()
                        malware['magnet'].append(torrent.magnet)
                        torr.append(meta)
                        torr_db.execute(
                            '''
                            UPDATE malware
                            SET magnet = array_append(COALESCE(magnet, '{}'), %s)
                            WHERE id = 1;
                            ''',
                            (torrent.magnet,)
                        )

                        ssh.notify('Downloads', f'{torrent.name}: Malware detected!')
            else:
                non_downloads.append(meta['title'])
                continue

        if non_downloads:
            log(f'Shows Skipped:\n{"\n".join(non_downloads)}'.strip())

        if downloads:
            with SSH(self.win_me, ssh.key_file) as windows:
                log(f"Downloads:\n{"\n".join(downloads)}".strip())
                attempt = 0
                tries = 3
                powershell = windows.connect()
                while powershell.client is None and attempt < tries:
                    attempt += 1
                    ssh.notify('Windows', f'Enable SSH on windows. Attempt {attempt} of {tries}')
                    time.sleep(300)
                    powershell = windows.connect()
                    
                if powershell.client is None:
                    log('Windows push failed, switched to termux push')
                    asyncio.run(push(ssh))
                else:
                    src = os.path.expanduser('~/downloads')
                    ssh.notify('Server Push', 'Downloads -> Windows')
                    ok, msg = torr_sftp(powershell.client, src, torr_dest)

                    if ok:
                        log(msg)
                        ssh.notify('Server Push', msg)
                    else:
                        log(f'Failed to push to Windows:\n{msg}')
                        ssh.notify('Server Push', 'Redirecting Downloads to Phone.')
                        asyncio.run(push(ssh))
        
                    



                





import os
from core.config import relay, dest
from core.utils import log

def sftp(client, payload, adb, ssh):
    if payload['os'] == 'Windows':
        try:
            sftp = client.open_sftp()

            def sftp_upload(local_dir, remote_dir):
                try:
                    sftp.stat(remote_dir)
                except FileNotFoundError:
                    sftp.mkdir(remote_dir)

                for file in os.listdir(local_dir):
                    local_path = os.path.join(local_dir, file)
                    remote_path = f"{remote_dir}/{file}"

                    if os.path.isdir(local_path):
                        sftp_upload(local_path, remote_path)
                    else:
                        sftp.put(local_path, remote_path)

            sftp_upload(relay, dest)
            return { 'ok': True }
        except Exception as e:
            log(f'VPS -> Windows transfer failure:\n{e}')
            adb.push_log()
            ssh.notify('VPS -> Windows', 'Transfer failure! Updated logs.')
            return { 'ok': False, 'error': str(e) }
        finally:
            client.close()
        
def torr_sftp(client, src, dest):
    try:
        sftp = client.open_sftp()

        def sftp_upload(local_dir, remote_dir):
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                sftp.mkdir(remote_dir)

            for entry in os.listdir(local_dir):
                local_path = os.path.join(local_dir, entry)
                remote_path = f"{remote_dir}/{entry}"

                if os.path.isdir(local_path):
                    sftp_upload(local_path, remote_path)
                else:
                    try:
                        sftp.stat(remote_path)
                    except FileNotFoundError:
                        sftp.put(local_path, remote_path)

        sftp_upload(src, dest)
        return True, 'Windows Upload Done!'
    except Exception as e:
        log(f'Downloads could not transfer: {e}')
        return False, e

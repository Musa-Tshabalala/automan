import paramiko
from core.utils import log

class SSH:
    def __init__(self, client, key_file):
        self.host = client['ip']
        self.user = client['uname']
        self.port = client['port']
        self.key_file = key_file
        self.password = client['password']
        self.client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def connect(self):
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            c.connect(
                hostname=self.host,
                username=self.user,
                key_filename=self.key_file,
                port=self.port,
                allow_agent=False,
                look_for_keys=False,
                timeout=5
            )
            
            self.client = c
            return self
        except paramiko.AuthenticationException:
            if self.password:
                try:
                    c.connect(
                        hostname=self.host,
                        username=self.user,
                        password=self.password,
                        port=self.port,
                        timeout=5,
                    )
                    self.client = c
                    return self
                except Exception as e:
                    log(f'SSH Connection Failure: {e}')
                    return self
            return self
        except Exception as e:
            log(f'SSH Connection Failure: {e}')
            return self

    def notify(self, title, content):
        termux_cmd = f'termux-notification --title "{title}" --content "{content}"'
        stdin, stdout, stderr = self.client.exec_command(termux_cmd)
        
        err = stderr.read().decode().strip()
        if err:
            log('Termux SSH notification failed.')
            return False, err
        
        return True, stdout.read().decode().strip()

    def close(self):
        if self.client:
            self.client.close()

    
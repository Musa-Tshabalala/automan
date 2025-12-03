from core.utils import run, log
from  core.config import logfile

class ADB:
    def __init__(self, ip):
        self.ip = ip
        self.me = None
        
    def connected(self):
        dev = run(f'adb devices | grep {self.ip}')

        if not dev:
            return None
        
        is_dev = True if 'device' in dev else False
        self.me = self.ip if is_dev else None
        return self.me

    def connect(self):
        me = self.connected()
        
        if me is None:
            me = self.ip
            conn = run(f'adb connect {me}:5555')
            self.me = me if 'connected' in conn else None

        return self.me

    def notify(self, content):
        return run(f"adb -s {self.me}:5555 shell cmd notification post 'Tag' '{content}' 'NULL'")

    def push_log(self):
        return (
            log(run(f'adb -s {self.me} push {logfile} /sdcard/backup_logs'))
            if self.me
            else log('Could not push log: No connection established')
        )
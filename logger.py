class Logger:
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        print(msg)

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

global progress
progress = 0
# ℹ️ See "progress_hooks" in help(yt_dlp.YoutubeDL)
def progress_hook(d):
    if d['status'] == 'downloading':
        downloaded = d['downloaded_bytes']
        total = d['total_bytes']

        progress = (downloaded / total) * 100
    if d['status'] == 'finished':
        progress = 0
        print('Done downloading, now post-processing ...')
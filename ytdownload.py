from yt_dlp import YoutubeDL
import json


class Logger:
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        print(f'{msg} --> #')

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

# ℹ️ See "progress_hooks" in help(yt_dlp.YoutubeDL)
def progress_hook(d):
    # print(d['downloaded_bytes'])
    # print(d['total_bytes'])
    if d['status'] == 'finished':
        print('Done downloading, now post-processing ...')

ydl_opts = {
    'ignoreerrors': True,
    'format': 'mp3/bestaudio/best',
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }],
    'outtmpl': '%(title)s.%(ext)s',
    'logger': Logger(),
    'progress_hooks': [progress_hook],
    'forcethumbnail': True
}

urls = [
    'https://www.youtube.com/playlist?list=PLO1GWcsPJ5701bE2yplS7iq9kJA8wdKFB',
    # 'https://www.youtube.com/watch?v=rXRvs_FrwEk',
    # 'https://www.youtube.com/watch?v=1vhVKk5tx3s'
]

with YoutubeDL(ydl_opts) as ydl:
    # error_code = ydl.download(urls)
    info = ydl.extract_info(*urls, download=False)
    # print(info['entries'][0]['thumbnail'])
    

with open("./video.info.json", "w") as info_file:
    info_file.write(json.dumps(ydl.sanitize_info(info), indent=4))

with open("./video.info.json", 'r') as json_file:
    info:dict = json.load(json_file)
    print(info.get('_type'))


# print(error_code)
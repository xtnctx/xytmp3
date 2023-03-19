'''
   Copyright 2023 Ryan Christopher D. Bahillo
   
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
   
       http://www.apache.org/licenses/LICENSE-2.0
       
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

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

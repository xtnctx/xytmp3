# xytmp3
A simple UI for YouTube to Mp3 converter

Uses a [yt-dlp](https://github.com/yt-dlp/yt-dlp) which is a YouTube download manager for video and audio.
Settings for embedding the download manager is in the class `YtMp3.ydl_opts` of main.py, it uses a `QtCore.pyqtSignal` with `YtMp3.progress_hook` to get the logs or callbacks of the yt-dlp itself when the downloading begins. 

More importantly, to avoid freezing, this also inherits a function (`run`) from the `QtCore.QThread` to implement background processing.

---
### Learn more on how to [embed yt-dlp](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp) on your python code.

### Download the latest release build of ffmpeg [here](https://www.gyan.dev/ffmpeg/builds/)

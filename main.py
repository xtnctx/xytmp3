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

from PyQt5 import QtCore, QtGui, QtWidgets
from yt_dlp import YoutubeDL
from logger import Logger
from typing import Union
import datetime
import requests
import timeit
import json
import sys
import os


class Item:
    def __init__(
        self,
        id = 0, title = '', channel = '', 
        thumbnail_url = '', duration = '',
        url = ''
    ) -> None:
        self.id = id
        self.title = title
        self.channel = channel
        self.thumbnail_url = thumbnail_url
        self.duration = duration
        self.url = url

    def __repr__(self) -> str:
        return f'Item {self.id}'

class YtMp3(QtCore.QThread):
    ''' 
    if mode = "preview" (default), <url> must be a type of str which is a single video url from youtube.
    if mode = "download", <url> must be a type of list containing list of video url from youtube.
    '''
    infoChanged = QtCore.pyqtSignal(dict)
    info = dict

    progressChanged = QtCore.pyqtSignal(dict)
    progress = 0
    current_queue = 1
    total_queue = 0


    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'logger': Logger(),

    }
    def __init__(self, url:Union[str, list], path:str, mode:str='preview', parent=None) -> None:
        # mode: preview | download
        super().__init__(parent)
        self.ydl_opts['outtmpl'] = f'{path}/%(title)s.%(ext)s'
        self.ydl_opts['progress_hooks'] = [self.progress_hook]

        if type(path) != str:
            raise Exception('Not a valid path!')

        if mode == 'preview':
            assert type(url) == str, f'url must be a type of {str}, caught {type(url)}.'
        elif mode == 'download':
            assert type(url) == list, f'url must be a type of {list}, caught {type(url)}.'
            self.total_queue = len(url)
        else:
            raise Exception('<mode> must be either "preview" or "download" only.')

        self.url = url
        self.mode = mode
    
    def progress_hook(self, d):
        if d['status'] == 'downloading' and self.mode == 'download':
            downloaded = d['downloaded_bytes']
            total = d['total_bytes']
            self.progress = (downloaded / total) * 100
            # if self.progress == float(100):
            #     self.current_queue += 1
        
            self.progressChanged.emit(
                {
                    'progress': self.progress,
                    'current_queue': self.current_queue,
                    'total_queue': self.total_queue
                }
            )

        if d['status'] == 'finished':
            self.progress = 0
            self.current_queue += 1
            print('Done downloading, now post-processing ...')

    def run(self):
        if self.mode == 'preview':
            try:
                with YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(self.url, download=False)
                
                with open("./video.info.json", "w") as info_file:
                    info_file.write(json.dumps(ydl.sanitize_info(info), indent=4))

                with open("./video.info.json", 'r') as json_file:
                    self.info = json.load(json_file)
                self.infoChanged.emit(self.info)
            except:
                pass

        elif self.mode == 'download':
            with YoutubeDL(self.ydl_opts) as ydl:
                error_code = ydl.download(self.url)


class Ui_MainWindow(QtWidgets.QWidget):
    urls = list()
    info = dict()
    item_list = list()

    def __init__(self, MainWindow) -> None:
        super().__init__()
        self.setFocus()
        self.isProcessing = False
        with open("./pref.json", "r") as jsonFile:
            data = json.load(jsonFile)
        if os.path.exists(data["recently_used_path"]):
            self.selectedPath = data["recently_used_path"]
        else:
            self.selectedPath = "Please select a folder"
        self.start_time = 0

        MainWindow.resize(620, 580)
        self.MainWindow = MainWindow
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)

        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
 
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 584, 525))
        
        self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)

        # self.folderShow = QtWidgets.QLabel(self.selectedPath)
        # self.gridLayout_2.addWidget(self.folderShow, 1, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.scrollArea, 1, 0, 1, 1)

        self.search_frame = QtWidgets.QFrame(self.centralwidget)
        self.search_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.search_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.search_frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        
        font = QtGui.QFont()
        font.setFamily("Poppins")

        self.searchbar = QtWidgets.QLineEdit(self.search_frame)
        self.searchbar.setPlaceholderText('Paste youtube url here')
        self.searchbar.setFont(QtGui.QFont("Poppins", 8))
        self.searchbar.setMinimumSize(QtCore.QSize(0, 30))

        self.horizontalLayout.addWidget(self.searchbar)
        self.add_btn = QtWidgets.QPushButton(self.search_frame)
        self.add_btn.setFont(font)
        self.add_btn.setMinimumSize(QtCore.QSize(0, 30))
        
        self.horizontalLayout.addWidget(self.add_btn)
        self.select_folder_btn = QtWidgets.QPushButton(self.search_frame)
        self.select_folder_btn.setFont(font)
        self.select_folder_btn.setMinimumSize(QtCore.QSize(0, 30))

        self.horizontalLayout.addWidget(self.select_folder_btn)
        self.gridLayout_2.addWidget(self.search_frame, 0, 0, 1, 1)

        self.download_btn = QtWidgets.QPushButton('Download')
        self.download_btn.setFont(font)
        self.download_btn.setMinimumSize(QtCore.QSize(0, 30))

        self.gridLayout_2.addWidget(self.download_btn, 2, 0, 1, 1)

        self.statusBar = QtWidgets.QStatusBar()
        self.statusBar.setFont(font)
        self.statusBar.showMessage('Waiting for download ...')
        MainWindow.setStatusBar(self.statusBar)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    
    def include(self):
        """ Add to queue and fetch information """

        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(9)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(40)
        font.setKerning(True)

        input_url = self.searchbar.text().strip()
        if input_url == '':
            info = QtWidgets.QMessageBox()
            info.setWindowIcon(QtGui.QIcon('./logo.ico'))
            info.setIcon(QtWidgets.QMessageBox.Critical)
            info.setFont(font)
            info.setText("Must not be empty.")
            info.setWindowTitle("URL=null")
            info.exec_()
            return

        if os.path.isdir(self.selectedPath):
            self.isProcessing = True
            self.add_btn.setDisabled(True)
            self.statusBar.showMessage('Getting url info please wait')
            self.process = YtMp3(input_url, mode='preview', path=self.selectedPath)
            self.process.infoChanged.connect(self.onPreviewProgressChanged)
            self.process.finished.connect(self.onPreviewFinished)
            self.process.start()
        else:
            info = QtWidgets.QMessageBox()
            info.setWindowIcon(QtGui.QIcon('./logo.ico'))
            info.setIcon(QtWidgets.QMessageBox.Critical)
            info.setFont(font)
            info.setText("Please select a folder to store your downloads.")
            info.setWindowTitle("Error")
            info.exec_()

    def onPreviewProgressChanged(self, value):
        self.info = value
        
    def onPreviewFinished(self):
        # _type = video | playlist
        if self.info.get('_type') == 'video':
            title = self.info.get('title')
            url = self.info.get('original_url')
            channel = self.info.get('uploader')
            thumbnail_url = self.info.get('thumbnail')
            duration = self.info.get('duration_string')

            item = Item(
                id=len(self.item_list),
                title=title,
                channel=channel,
                thumbnail_url=thumbnail_url,
                duration=duration,
                url=url,

            )
            self.item_list.append(item)
            ext = self.info.get('ext')
            if not os.path.exists(f'{self.selectedPath}/{title}.{ext}'):
                self.add_item(item, exist=False)
                self.urls.append(url)
            else:
                self.add_item(item, exist=True)
            
            print(self.urls)
            print(self.item_list)

        elif self.info.get('_type') == 'playlist':
            for i in range(self.info.get('playlist_count')):
                entry:dict = self.info.get('entries')[i]
                url = entry.get('original_url')

                title = entry.get('title')
                channel = entry.get('uploader')
                thumbnail_url = entry.get('thumbnail')
                duration = entry.get('duration_string')
                
                item = Item(
                    id=len(self.item_list),
                    title=title,
                    channel=channel,
                    thumbnail_url=thumbnail_url,
                    duration=duration,
                    url=url,
                )
                self.item_list.append(item)

                ext = entry.get('ext')
                print(f'{self.selectedPath}/{title}.{ext}')
                if not os.path.exists(f'{self.selectedPath}/{title}.{ext}'):
                    self.add_item(item, exist=False)
                    self.urls.append(url)
                else:
                    self.add_item(item, exist=True)

        self.add_btn.setDisabled(False)
        self.isProcessing = False
        self.statusBar.showMessage('Done adding, ready to download.')
    
    def onDownloadProgressChanged(self, value):
        print(value, 'RYANRYAN')
        progress = value['progress']
        current_queue = value['current_queue']
        total_queue = value['total_queue']

        self.statusBar.showMessage(f'Downloading {current_queue}/{total_queue}  {progress}%')

    def onDownloadFinished(self):
        self.urls = []
        self.searchbar.clear()
        for i in reversed(range(self.gridLayout.count())): 
            self.gridLayout.itemAt(i).widget().setParent(None)
        self.download_btn.setDisabled(False)
        self.isProcessing = False
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(9)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(40)
        font.setKerning(True)

        info = QtWidgets.QMessageBox()
        info.setWindowIcon(QtGui.QIcon('./logo.ico'))
        info.setIcon(QtWidgets.QMessageBox.Information)
        info.setFont(font)
        info.setText('Download done!                 ')

        elapsed_time = round(timeit.default_timer() - self.start_time, 2)
        # str(datetime.timedelta(seconds = elapsed_time))
        info.setInformativeText(f"Elapsed time: {elapsed_time}s")
        info.setWindowTitle("YTMp3 Downloader")
        info.exec_()

        self.statusBar.showMessage('Waiting for download ...')

    def start_download(self):
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(9)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(40)
        font.setKerning(True)

        if len(self.urls) == 0:
            info = QtWidgets.QMessageBox()
            info.setWindowIcon(QtGui.QIcon('./logo.ico'))
            info.setIcon(QtWidgets.QMessageBox.Critical)
            info.setFont(font)
            info.setText("Text field might be empty or url already downloaded.")
            info.setWindowTitle("URL=null")
            info.exec_()
            return

        if os.path.isdir(self.selectedPath):
            self.download_btn.setDisabled(True)
            self.isProcessing = True
            self.process = YtMp3(self.urls, mode='download', path=self.selectedPath)
            self.process.progressChanged.connect(self.onDownloadProgressChanged)
            self.process.finished.connect(self.onDownloadFinished)
            self.process.start()
            self.start_time = timeit.default_timer()
        else:
            info = QtWidgets.QMessageBox()
            info.setWindowIcon(QtGui.QIcon('./logo.ico'))
            info.setIcon(QtWidgets.QMessageBox.Critical)
            info.setFont(font)
            info.setText("Please select a folder to store your downloads.")
            info.setWindowTitle("Error")
            info.exec_()

    def add_item(self, item:Item, exist=False):
        image = QtGui.QImage()
        image.loadFromData(requests.get(item.thumbnail_url).content)
        image_label = QtWidgets.QLabel()
        image_size = (168, 94)

        target = QtGui.QPixmap(*image_size)  
        target.fill(QtCore.Qt.transparent) 

        pixmap = QtGui.QPixmap(image).scaled(*image_size, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
        
        painter = QtGui.QPainter(target)

        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        path = QtGui.QPainterPath()
    
        path.addRoundedRect(0, 0, *image_size, 10, 10)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
    
        image_label.setPixmap(target)
        
        container = QtWidgets.QFrame()
        if exist:
            container.setStyleSheet(".QFrame {border: 1px solid black; background-color: rgba(0, 0, 0, 75);}")
        else:
            container.setStyleSheet(".QFrame {border: 1px solid black}")

        row_wrapper = QtWidgets.QGridLayout(container)
        row_wrapper.setContentsMargins(5, 5, 5, 5)
        
        # Thumbnail and duration
        self.col0_grid = QtWidgets.QGridLayout()
        self.col0_grid.addWidget(image_label, 0, 0, alignment=QtCore.Qt.AlignCenter)
        wDuration = QtWidgets.QLabel(item.duration)

        duration_font = QtGui.QFont()
        duration_font.setFamily('Poppins')
        duration_font.setBold(True)
        # duration_font.setPointSize(12)
        wDuration.setFont(duration_font)
        
        # duration.setFixedWidth(40)
        # duration.setFixedHeight(25)
        wDuration.setAlignment(QtCore.Qt.AlignCenter)
        wDuration.setStyleSheet('background-color: rgba(0, 0, 0, 180); color: white; \
                                padding: 3px; margin: 4px; border-radius: 5px;')
        self.col0_grid.addWidget(wDuration, 0, 0, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        row_wrapper.addLayout(self.col0_grid, item.id, 0, alignment=QtCore.Qt.AlignCenter)

        # Title and author
        self.col1_grid = QtWidgets.QGridLayout()

        # wTitle = QtWidgets.QLabel('Post Malone - Circles (Lyrics)')
        wTitle = QtWidgets.QLabel(item.title)
        title_font = QtGui.QFont()
        title_font.setFamily('Poppins')
        title_font.setPointSize(12)
        title_font.setWeight(60)
        wTitle.setFont(title_font)
        self.col1_grid.addWidget(wTitle, 1, 0, alignment=QtCore.Qt.AlignCenter)

        wchannel = QtWidgets.QLabel(item.channel)
        channel_font = QtGui.QFont()
        channel_font.setFamily('Poppins')
        channel_font.setPointSize(10)
        wchannel.setFont(channel_font)
        self.col1_grid.addWidget(wchannel, 2, 0, alignment=QtCore.Qt.AlignCenter)

        row_wrapper.addLayout(self.col1_grid, item.id, 1, alignment=QtCore.Qt.AlignCenter)
        
        self.gridLayout.addWidget(container, item.id, 0, alignment=QtCore.Qt.AlignTop)
    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", self.selectedPath))
        MainWindow.setWindowIcon(QtGui.QIcon('./logo.ico'))
        self.add_btn.setText(_translate("MainWindow", "Add"))
        self.select_folder_btn.setText(_translate("MainWindow", "Select folder"))

        self.add_btn.clicked.connect(self.include)
        self.download_btn.clicked.connect(self.start_download)
        self.select_folder_btn.clicked.connect(self.selectPath)
    
    def selectPath(self):
        self.selectedPath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.MainWindow.setWindowTitle(self.selectedPath)

        with open("./pref.json", "r") as jsonFile:
            data = json.load(jsonFile)

        data["recently_used_path"] = self.selectedPath

        with open("./pref.json", "w") as jsonFile:
            json.dump(data, jsonFile)

class qProgress(QtWidgets.QProgressBar):
    """docstring for qProgress"""
    def __init__(self):
        super(qProgress, self).__init__()
        self.valueChanged.connect(self.onValueChanged)
        self.setFont(QtGui.QFont('Poppins', 7))
        self.setFixedHeight(10)
        self.setStyleSheet('QProgressBar {padding: 0px; border: 0px; border-radius: 5px; text-align: center;} \
                                QProgressBar::chunk {background: #7D94B0; border-radius: 5px}')

    def onValueChanged(self, value):
        self.setFormat('%.02f%%' % (self.prefixFloat))

    def setValue(self, value):
        self.prefixFloat = value
        QtWidgets.QProgressBar.setValue(self, int(value))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

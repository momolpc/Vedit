import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog, QComboBox, QSpinBox, QSlider, QPlainTextEdit, QProgressBar, QFrame, QGraphicsView, QListWidget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("视频处理软件")
        self.setGeometry(100, 100, 1200, 800)

        self.initUI()

    def initUI(self):
        widget = QWidget(self)
        self.setCentralWidget(widget)

        # 主布局
        mainLayout = QVBoxLayout()

        # 上部分：批处理进度提示
        progressLayout = QHBoxLayout()  # 使用QHBoxLayout让进度条和状态列表水平排列

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)  # 初始化进度条为0
        progressLayout.addWidget(self.progress_bar)


        # 中部分：视频预览窗口和功能栏
        middleLayout = QHBoxLayout()

        # 视频预览窗口
        videoPreviewLayout = QVBoxLayout()
        videoPreviewLayout.addWidget(QLabel("视频预览窗口"))
        videoPreviewLayout.addWidget(QGraphicsView())  # 使用QGraphicsView来表示视频预览窗口

        # 功能栏
        functionLayout = QGridLayout()

        # 视频剪辑
        functionLayout.addWidget(QLabel("剪辑文件"), 0, 0)
        self.clip_file_edit = QLineEdit()
        functionLayout.addWidget(self.clip_file_edit, 0, 1)
        self.clip_file_button = QPushButton("选择文件夹")
        functionLayout.addWidget(self.clip_file_button, 0, 2)
        functionLayout.addWidget(QLabel("添加片头"), 1, 0)
        self.add_header_edit = QLineEdit()
        functionLayout.addWidget(self.add_header_edit, 1, 1)
        self.add_header_button = QPushButton("选择文件夹")
        functionLayout.addWidget(self.add_header_button, 1, 2)
        functionLayout.addWidget(QLabel("拼接时间"), 2, 0)
        self.concat_time_edit = QLineEdit()
        functionLayout.addWidget(self.concat_time_edit, 2, 1)
        self.process_video_button = QPushButton("开始批处理视频")
        functionLayout.addWidget(self.process_video_button, 3, 1)

        # 音频处理
        functionLayout.addWidget(QLabel("视频"), 4, 0)
        self.audio_video_edit = QLineEdit()
        functionLayout.addWidget(self.audio_video_edit, 4, 1)
        self.audio_video_button = QPushButton("选择文件夹")
        functionLayout.addWidget(self.audio_video_button, 4, 2)
        functionLayout.addWidget(QLabel("背景音乐"), 5, 0)
        self.bg_music_edit = QLineEdit()
        functionLayout.addWidget(self.bg_music_edit, 5, 1)
        self.bg_music_button = QPushButton("选择文件")
        functionLayout.addWidget(self.bg_music_button, 5, 2)
        functionLayout.addWidget(QLabel("字幕配音"), 6, 0)
        self.subtitle_audio_edit = QLineEdit()
        functionLayout.addWidget(self.subtitle_audio_edit, 6, 1)
        self.subtitle_audio_button = QPushButton("选择文件")
        functionLayout.addWidget(self.subtitle_audio_button, 6, 2)
        functionLayout.addWidget(QLabel("音乐大小"), 7, 0)
        self.music_volume_spinbox = QSpinBox()  # 音量输入数字
        functionLayout.addWidget(self.music_volume_spinbox, 7, 1)
        self.audition_button = QPushButton("试听")
        functionLayout.addWidget(self.audition_button, 7, 2)
        self.process_audio_button = QPushButton("开始批处理音乐")
        functionLayout.addWidget(self.process_audio_button, 8, 1)

        # 字幕添加
        functionLayout.addWidget(QLabel("视频"), 9, 0)
        self.subtitle_video_edit = QLineEdit()
        functionLayout.addWidget(self.subtitle_video_edit, 9, 1)
        self.subtitle_video_button = QPushButton("选择文件夹")
        functionLayout.addWidget(self.subtitle_video_button, 9, 2)
        functionLayout.addWidget(QLabel("字体"), 10, 0)
        self.font_combobox = QComboBox()
        functionLayout.addWidget(self.font_combobox, 10, 1)
        functionLayout.addWidget(QLabel("大小"), 11, 0)
        self.font_size_spinbox = QSpinBox()
        functionLayout.addWidget(self.font_size_spinbox, 11, 1)
        functionLayout.addWidget(QLabel("样式"), 12, 0)
        self.font_style_combobox = QComboBox()
        functionLayout.addWidget(self.font_style_combobox, 12, 1)
        self.process_subtitle_button = QPushButton("开始批处理字幕")
        functionLayout.addWidget(self.process_subtitle_button, 13, 1)

        # 水印添加
        functionLayout.addWidget(QLabel("视频"), 14, 0)
        self.watermark_video_edit = QLineEdit()
        functionLayout.addWidget(self.watermark_video_edit, 14, 1)
        self.watermark_video_button = QPushButton("选择文件夹")
        functionLayout.addWidget(self.watermark_video_button, 14, 2)
        functionLayout.addWidget(QLabel("图片"), 15, 0)
        self.watermark_image_edit = QLineEdit()
        functionLayout.addWidget(self.watermark_image_edit, 15, 1)
        self.watermark_image_button = QPushButton("选择文件")
        functionLayout.addWidget(self.watermark_image_button, 15, 2)
        functionLayout.addWidget(QLabel("位置"), 16, 0)
        self.watermark_position_edit = QLineEdit()
        functionLayout.addWidget(self.watermark_position_edit, 16, 1)
        functionLayout.addWidget(QLabel("大小"), 17, 0)
        self.watermark_size_edit = QLineEdit()
        functionLayout.addWidget(self.watermark_size_edit, 17, 1)
        self.process_watermark_button = QPushButton("开始批处理水印")
        functionLayout.addWidget(self.process_watermark_button, 18, 1)

        middleLayout.addLayout(videoPreviewLayout)
        middleLayout.addLayout(functionLayout)

        # 下部分：文件栏
        fileLayout = QHBoxLayout()
        self.open_folder_button = QPushButton("打开文件夹")
        fileLayout.addWidget(self.open_folder_button)
        self.open_file_button = QPushButton("打开文件")
        fileLayout.addWidget(self.open_file_button)
        # 将各个布局添加到主布局
        mainLayout.addLayout(progressLayout)  # 将修改后的progressLayout添加到主布局
        mainLayout.addLayout(middleLayout)
        mainLayout.addLayout(fileLayout)

        widget.setLayout(mainLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

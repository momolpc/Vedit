import sys
import os
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog, QComboBox, QSpinBox, QSlider, QPlainTextEdit, QProgressBar, QFrame, QGraphicsView, QListWidget)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import moviepy.editor as mpe

class VideoHeaderProcessor(QThread):
    """视频片头拼接处理线程。"""
    progress_updated = pyqtSignal(int)  # 定义进度更新信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.header_file = ''
        self.output_folder = ''
        self._is_paused = False  # 添加暂停标志

    def set_parameters(self, header_file, output_folder):
        """设置处理参数。"""
        self.header_file = header_file
        self.output_folder = output_folder

    def run(self):
        """线程执行函数。"""
        print("开始拼接片头...")  # 添加调试信息
        self.concat_header(self.header_file, self.output_folder)
        print("拼接片头完成！")  # 添加调试信息

    def concat_header(self, header_file, output_folder):
        """将片头与文件夹中的视频拼接。"""
        header_clip = mpe.VideoFileClip(header_file)

        for file_name in os.listdir(output_folder):
            if file_name.startswith('final_'):
                video_path = os.path.join(output_folder, file_name)
                video_clip = mpe.VideoFileClip(video_path)
                final_clip = mpe.concatenate_videoclips([header_clip, video_clip])
                final_clip_name = f"final_{file_name}"
                print(f"正在生成最终视频: {final_clip_name}")  # 添加调试信息
                final_clip.write_videofile(os.path.join(output_folder, final_clip_name))

    def pause(self):
        """暂停处理并清除缓存。"""
        self._is_paused = True
        self.progress_updated.emit(0)  # 清除进度条
        self.clear_cache()  # 清除视频缓存

    def clear_cache(self):
        """清除视频缓存。"""
        self.header_file = ''
        self.output_folder = ''

class VideoProcessor(QThread):
    """视频处理线程。"""
    progress_updated = pyqtSignal(int)  # 定义进度更新信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clip_folder = ''
        self.output_folder = ''
        self.concat_time = 0
        self.operation = ''  # 添加操作标志：'clip' 或 'concat'
        self._is_paused = False  # 添加暂停标志
        self.parent = parent  # 添加对父类的引用

    def set_parameters(self, clip_folder, output_folder, concat_time, operation):
        """设置处理参数。"""
        self.clip_folder = clip_folder
        self.output_folder = output_folder
        self.concat_time = concat_time
        self.operation = operation

    def run(self):
        """线程执行函数。"""
        if self.operation == 'clip':
            self.log_message("开始剪辑视频...")  # 添加调试信息
            self.clip_videos(self.clip_folder, self.output_folder)
            self.log_message("剪辑视频完成！")  # 添加调试信息
        elif self.operation == 'concat':
            self.log_message("开始拼接视频...")  # 添加调试信息
            self.concat_videos(self.output_folder, self.concat_time)
            self.log_message("拼接视频完成！")  # 添加调试信息

    def log_message(self, message):
        """将日志信息输出到父类的UI。"""
        if self.parent:
            self.parent.log_message(message)

    def run(self):
        """线程执行函数。"""
        if self.operation == 'clip':
            print("开始剪辑视频...")  # 添加调试信息
            self.clip_videos(self.clip_folder, self.output_folder)
            print("剪辑视频完成！")  # 添加调试信息
        elif self.operation == 'concat':
            print("开始拼接视频...")  # 添加调试信息
            self.concat_videos(self.output_folder, self.concat_time)
            print("拼接视频完成！")  # 添加调试信息

    def clip_videos(self, clip_folder, output_folder):
        """将文件夹中的视频剪辑成3~5秒的片段。"""
        total_clips = 0
        for file_name in os.listdir(clip_folder):
            if file_name.lower().endswith(('.mp4', '.avi', '.mov')):
                video_path = os.path.join(clip_folder, file_name)
                try:
                    video = mpe.VideoFileClip(video_path)
                    duration = int(video.duration)
                    total_clips += (duration // 4) + (1 if duration % 4 > 0 else 0)  # 每 4 秒一个片段，最后可能有一个不足 4 秒的片段
                except Exception as e:
                    self.log_message(f"无法处理视频文件: {file_name}, 错误: {e}")

        processed_clips = 0
        for file_name in os.listdir(clip_folder):
            if file_name.lower().endswith(('.mp4', '.avi', '.mov')):
                self.log_message(f"正在处理视频文件: {file_name}")  # 添加调试信息
                processed_clips += self.process_video(os.path.join(clip_folder, file_name), output_folder, total_clips,
                                                      processed_clips)
                progress = int((processed_clips / total_clips) * 100)
                self.progress_updated.emit(progress)  # 更新进度条

    def process_video(self, video_path, output_folder, total_clips, processed_clips):
        """处理单个视频，将其剪辑成3~5秒的片段，无缝剪辑，不浪费任何一秒钟。"""
        try:
            video = mpe.VideoFileClip(video_path)
            video = video.without_audio()  # 删除音轨
        except Exception as e:
            self.log_message(f"无法打开视频文件: {video_path}, 错误: {e}")
            return 0

        duration = int(video.duration)
        start_time = 0
        i = 0

        while start_time < duration:  # 循环剪辑，直到处理完整个视频
            if self._is_paused:  # 检查暂停标志
                break

            end_time = min(start_time + random.randint(3, 5), duration)
            clip = video.subclip(start_time, end_time)
            clip_name = f"{int(end_time - start_time)}s_{os.path.splitext(os.path.basename(video_path))[0]}_{int(start_time)}s~{int(end_time)}s.mp4"
            self.log_message(f"正在剪辑片段: {clip_name}")  # 添加调试信息
            try:
                clip.write_videofile(os.path.join(output_folder, clip_name))
            except Exception as e:
                self.log_message(f"无法保存剪辑片段: {clip_name}, 错误: {e}")
                continue

            start_time = end_time  # 下一个片段从当前片段的结束时间开始
            i += 1
            processed_clips += 1
            progress = int((processed_clips / total_clips) * 100)
            self.progress_updated.emit(progress)  # 发送进度更新信号

        return i  # 返回处理的片段数量

    def concat_videos(self, output_folder, concat_time):
        """将剪辑后的片段拼接成指定长度的视频，并添加随机转场效果。"""
        clips = []
        total_duration = 0

        # 收集片段，确保总时长达到或超过指定的拼接时间
        while total_duration < concat_time:
            for file_name in os.listdir(output_folder):
                if file_name.lower().startswith(('0s_', '1s_', '2s_', '3s_', '4s_', '5s_', '6s_', '7s_', '8s_', '9s_')):
                    clip_path = os.path.join(output_folder, file_name)
                    try:
                        clip = mpe.VideoFileClip(clip_path)
                        clips.append(clip)
                        total_duration += clip.duration
                        if total_duration >= concat_time:
                            break
                    except Exception as e:
                        self.log_message(f"无法处理视频文件: {file_name}, 错误: {e}")

        if total_duration < concat_time:
            self.log_message("片段总时长不足拼接时间，将利用重复片段。")
            while total_duration < concat_time:
                clips.extend(clips)  # 重复片段
                total_duration *= 2

        random.shuffle(clips)  # 随机打乱片段顺序
        final_clips = []
        current_duration = 0

        while current_duration < concat_time and clips:
            clip = clips.pop(0)  # 使用pop(0)以确保顺序
            final_clips.append(clip)
            current_duration += clip.duration

        # 如果当前时长仍不足，继续添加片段
        while current_duration < concat_time:
            for clip in clips:
                if current_duration >= concat_time:
                    break
                final_clips.append(clip)
                current_duration += clip.duration

        # 拼接片段
        total_clips = len(final_clips)
        final_video = final_clips[0]
        for i in range(1, total_clips):
            transition = random.choice(['crossfadein', 'crossfadeout'])
            try:
                final_video = mpe.concatenate_videoclips([final_video, final_clips[i]], method="compose")
            except Exception as e:
                self.log_message(f"无法拼接视频片段: {i}, 错误: {e}")
            progress = int((i / total_clips) * 100)
            self.progress_updated.emit(progress)  # 更新进度条

        final_video_name = "final_output.mp4"
        self.log_message(f"正在生成最终视频: {final_video_name}")
        try:
            final_video.write_videofile(os.path.join(output_folder, final_video_name))
            self.log_message("拼接视频完成！")
        except Exception as e:
            self.log_message(f"无法生成最终视频: {final_video_name}, 错误: {e}")


    def pause(self):
        """暂停处理并清除缓存。"""
        self._is_paused = True
        self.progress_updated.emit(0)  # 清除进度条
        self.clear_cache()  # 清除视频缓存

    def clear_cache(self):
        """清除视频缓存。"""
        self.clip_folder = ''
        self.output_folder = ''

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("视频处理软件")
        self.setGeometry(100, 100, 1200, 800)

        self.initUI()
        self.connect_signals()  # 连接信号与槽函数
        self.video_processor = VideoProcessor(self)  # 创建视频处理线程并传递对父类的引用
        self.video_processor.progress_updated.connect(self.update_progress)  # 连接进度更新信号
        self.video_header_processor = VideoHeaderProcessor()  # 创建视频片头拼接处理线程
        self.video_header_processor.progress_updated.connect(self.update_progress)  # 连接进度更新信号

    def log_message(self, message):
        """将日志信息输出到UI。"""
        self.statusBar().showMessage(message)

    def initUI(self):
        widget = QWidget(self)
        self.setCentralWidget(widget)
        self.statusBar()  # 创建状态栏

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
        self.concat_output_folder_button = QPushButton("选择文件夹")
        functionLayout.addWidget(self.concat_output_folder_button, 2, 2)
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
        self.watermark_video_button.clicked.connect(self.select_watermark_video_file)
        functionLayout.addWidget(self.watermark_video_button, 14, 2)
        functionLayout.addWidget(QLabel("图片"), 15, 0)
        self.watermark_image_edit = QLineEdit()
        functionLayout.addWidget(self.watermark_image_edit, 15, 1)
        self.watermark_image_button = QPushButton("选择文件")
        self.watermark_image_button.clicked.connect(self.select_watermark_image_file)
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

    def connect_signals(self):
        self.open_folder_button.clicked.connect(self.open_processed_folder)  # 修改信号连接
        self.open_file_button.clicked.connect(self.open_processed_file)  # 修改信号连接
        self.clip_file_button.clicked.connect(self.select_clip_folder)
        self.add_header_button.clicked.connect(self.select_header_file)
        self.concat_output_folder_button.clicked.connect(self.select_concat_output_folder)
        self.process_video_button.clicked.connect(self.toggle_video_processing)

    def open_processed_folder(self):
        """打开处理后的文件夹。"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择处理后的文件夹")
        if folder_path:
            # 这里需要根据你的实际处理逻辑来显示处理后的文件
            # 例如，如果处理后的文件与原始文件在同一文件夹下，只是文件名不同，
            # 你可以在这里遍历文件夹，找到处理后的文件并显示。
            # 以下代码只是一个示例，你需要根据实际情况修改。
            self.file_list.clear()  # 清空文件列表
            for file_name in os.listdir(folder_path):
                if file_name.startswith('processed_'):  # 假设处理后的文件名以 "processed_" 开头
                    self.file_list.addItem(file_name)

    def open_processed_file(self):
        """打开处理后的文件。"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择处理后的文件")
        if file_path:
            # 这里需要根据你的实际处理逻辑来显示处理后的文件
            # 以下代码只是一个示例，你需要根据实际情况修改。
            self.file_list.clear()  # 清空文件列表
            self.file_list.addItem(os.path.basename(file_path))  # 显示文件名

    def select_clip_folder(self):
        """选择要剪辑的视频文件夹。"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择要剪辑的视频文件夹")
        if folder_path:
            self.clip_file_edit.setText(folder_path)

    def select_header_file(self):
        """选择要添加的片头文件。"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择要添加的片头文件", filter="视频文件 (*.mp4 *.avi *.mov)")
        if file_path:
            self.add_header_edit.setText(file_path)

    def select_concat_output_folder(self):
        """选择拼接视频的输出文件夹。"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择拼接视频的输出文件夹")
        if folder_path:
            self.concat_output_folder = folder_path

    def toggle_video_processing(self):
        """开始或暂停视频处理。"""
        if self.video_processor.isRunning():
            self.video_processor.pause()
            self.process_video_button.setText("开始批处理视频")
        elif self.video_header_processor.isRunning():
            self.video_header_processor.pause()
            self.process_video_button.setText("开始批处理视频")
        else:
            clip_folder = self.clip_file_edit.text()
            header_file = self.add_header_edit.text()
            concat_time = self.concat_time_edit.text()
            output_folder = getattr(self, 'concat_output_folder', None)  # 使用选择的输出文件夹

            if clip_folder:
                # 启动视频剪辑处理线程
                self.video_processor.set_parameters(clip_folder, clip_folder, 0, 'clip')  # 输出文件夹为源文件夹，拼接时间为0表示不拼接
                self.video_processor._is_paused = False  # 重置暂停标志
                self.video_processor.start()
                self.process_video_button.setText("暂停")
            elif concat_time and output_folder:
                try:
                    # 将拼接时间转换为秒
                    minutes, seconds = map(int, concat_time.split('-'))
                    concat_time_in_seconds = minutes * 60 + seconds
                except ValueError:
                    self.log_message("拼接时间格式无效，应为 '分钟-秒'。")  # 添加调试信息
                    return

                # 启动视频拼接处理线程
                self.video_processor.set_parameters(output_folder, output_folder, concat_time_in_seconds, 'concat')
                self.video_processor._is_paused = False  # 重置暂停标志
                self.video_processor.start()
                self.process_video_button.setText("暂停")
            elif header_file and output_folder:
                # 启动片头拼接处理线程
                self.video_header_processor.set_parameters(header_file, output_folder)
                self.video_header_processor._is_paused = False  # 重置暂停标志
                self.video_header_processor.start()
                self.process_video_button.setText("暂停")
            else:
                self.log_message("请确保已选择文件夹或输入拼接时间和片头文件。")  # 添加调试信息

    def select_watermark_video_file(self):
        """选择要添加水印的视频文件夹。"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择要添加水印的视频文件夹")
        if folder_path:
            self.watermark_video_edit.setText(folder_path)

    def select_watermark_image_file(self):
        """选择要添加的水印图片文件。"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择要添加的水印图片文件",
                                                   filter="图片文件 (*.png *.jpg *.bmp)")
        if file_path:
            self.watermark_image_edit.setText(file_path)


    @pyqtSlot(int)
    def update_progress(self, value):
        """更新进度条。"""
        self.progress_bar.setValue(value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

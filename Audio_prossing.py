from PyQt5.QtWidgets import QApplication
import gui
import audio_io
import filter_design
import music_play

class MusicPlayerApp:
    def __init__(self):
        self.music_player = MusicPlayer()  # 创建播放器对象
        self.ui = MusicPlayerUI(self.music_player)  # 创建UI对象，并传入播放器
        self.ui.show()

    def run(self):
        """启动应用程序"""
        app = QApplication([])  # 创建应用程序
        app.exec_()  # 进入事件循环

if __name__ == '__main__':
    app = MusicPlayerApp()
    app.run()
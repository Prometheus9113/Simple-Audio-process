import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class MusicPlayerUI(OWidget):
    def __init__(self):
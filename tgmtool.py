import tgmlib
import update_map
import mirror_map
import kd_map_tools
from pathlib import Path
from PyQt5 import QtCore, QtWidgets, QtGui
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.central_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        self.homepage = HomePage(self)
        self.central_widget.addWidget(self.homepage)
        self.kd_widget = kd_map_tools.Widget(self)
        self.central_widget.addWidget(self.kd_widget)
        self.mirror_widget = mirror_map.Widget(self)
        self.central_widget.addWidget(self.mirror_widget)
        self.update_widget = update_map.Widget(self)
        self.central_widget.addWidget(self.update_widget)
        
        self.switchWidget('homepage')
    
    def switchWidget(self, target):
        self.central_widget.setCurrentWidget(getattr(self, target, self.homepage))


class HomePage(QtWidgets.QWidget):
    def __init__(self, parent):
        super(HomePage, self).__init__(parent)
        
        layout = QtWidgets.QHBoxLayout()
        self.kd_button = QtWidgets.QPushButton('Kohan Duels Map Generator')
        self.kd_button.clicked.connect(lambda: self.parent().parent().switchWidget('kd_widget'))
        layout.addWidget(self.kd_button)
        self.update_button = QtWidgets.QPushButton('Update Map')
        self.update_button.clicked.connect(lambda: self.parent().parent().switchWidget('update_widget'))
        layout.addWidget(self.update_button)
        self.mirror_button = QtWidgets.QPushButton('Mirror Map')
        self.mirror_button.clicked.connect(lambda: self.parent().parent().switchWidget('mirror_widget'))        
        layout.addWidget(self.mirror_button)
        self.setLayout(layout)
        

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

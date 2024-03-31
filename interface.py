import sys
from PyQt5 import QtCore, QtWidgets, QtGui

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Kohan Map Editor")
        
        self.Map = QtWidgets.QLabel()
        self.Map.setPixmap(QtGui.QPixmap('test_map.png'))
        
        self.obj_list = QtWidgets.QComboBox();
        self.obj_list.addItems(["Obj1","Obj2","Obj3"])
        
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.obj_list)
        layout.addWidget(self.Map)
        
        
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        
        self.setCentralWidget(container)

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
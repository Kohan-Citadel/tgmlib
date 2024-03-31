import sys
from PyQt5 import QtCore, QtWidgets, QtGui

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, Map):
        super().__init__()

        self.setWindowTitle("Kohan Map Editor")
        
        self.Map = Map
        self.map_display = QtWidgets.QLabel()
        self.map_display.setPixmap(QtGui.QPixmap('Data/render.png'))
        
        
        
        #self.obj_properties = 
        
        
        self.obj_pane = ObjectPane(self.Map)
        self.obj_pane.update.clicked.connect(self.render)
        
        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(self.obj_pane)
        layout.addWidget(self.map_display)
        
        
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        
        self.setCentralWidget(container)
        
    def render(self):
        self.Map.render()
        self.map_display.setPixmap(QtGui.QPixmap('Data/render.png'))
    
    

class ObjectPane(QtWidgets.QVBoxLayout):
    def __init__(self, Map):
        super().__init__()
        self.Map = Map
        self.obj_list = QtWidgets.QComboBox()
        self.obj_list.addItems([f'{v.display_name} (id: {k})' for k, v in self.Map.objects.items()])
        self.obj_list.currentTextChanged.connect(self.showItem)
        self.addWidget(self.obj_list)
        
        self.name = QtWidgets.QLineEdit()
        self.name.setPlaceholderText('Obj Name')
        self.addWidget(self.name)
        
        self.player = QtWidgets.QComboBox()
        self.player.addItems(['Player 1', 'Player 2', 'Player 3', 'Player 4', 'Player 5', 'Player 6', 'Player 7', 'Player 8', 'Independent'])
        self.addWidget(self.player)
        
        self.pos_se = QtWidgets.QDoubleSpinBox()
        self.pos_se.setRange(0, self.Map.size)
        self.pos_sw = QtWidgets.QDoubleSpinBox()
        self.pos_sw.setMinimum(0)
        self.pos_sw.setMaximum(self.Map.size)
        l1 = QtWidgets.QHBoxLayout()
        l1.addWidget(self.pos_se)
        l1.addWidget(self.pos_sw)
        self.addLayout(l1)
        
        self.update = QtWidgets.QPushButton('Update')
        self.update.clicked.connect(self.updateItem)
        self.addWidget(self.update)
        
    def showItem(self, list_item):
        editor_id = int(list_item.split(' ')[-1][:-1])
        print(editor_id)
        obj = self.Map.objects[editor_id]
        self.name.setText(obj.display_name)
        self.player.setCurrentIndex(obj.player-1)
        self.pos_se.setValue(obj.position.se)
        self.pos_sw.setValue(obj.position.sw)
    
    def updateItem(self):
        editor_id = int(self.obj_list.currentText().split(' ')[-1][:-1])
        obj = self.Map.objects[editor_id]
        obj.display_name = self.name.text()
        self.obj_list.setItemText(self.obj_list.currentIndex(), f'{obj.display_name} (id: {obj.id})')
        obj.player = self.player.currentIndex()
        obj.position.set( self.pos_se.value(), self.pos_sw.value())
        
        
        
        

app = QtWidgets.QApplication(sys.argv)


import argparse
import json
import tgmlib
import update_map
import mirror_map
import kd_map_tools
from pathlib import Path
from PyQt5 import QtCore, QtWidgets, QtGui
import sys

def update(args: argparse.Namespace):
    with open(args.name_mapping, 'r') as fp:
        name_mapping = json.load(fp)
    
    ref_map = tgmlib.tgmFile(args.type_ref)
    ref_map.load()
    dest_path = Path(args.dest)
    source_path = Path(args.source)
    read_from = source_path.suffix.upper()
    match read_from:
        case '.TGM':
            if dest_path.suffix.upper() == '.TGM':
                filename = dest_path.name
                dest_path = dest_path.parent
            else:
                filename = source_path.name    
            dest_path.mkdir(exist_ok=True, parents=True)
            
            old_map = tgmlib.tgmFile(source_path)
            old_map.load()
            update_map.update(old_map, ref_map, name_mapping, dest_path / filename)
        case '':
            filelist = list(source_path.glob('*'))
            
            if dest_path.suffix != '':
                print(f'tgmtool.py(34) {dest_path.name} is not a valid folder name. Make sure the destination path does not end with a file extension.')
                exit()
            
            dest_path.mkdir(exist_ok=True, parents=True)
            for f in filelist:
                if f.suffix.upper() == '.TGM':
                    old_map = tgmlib.tgmFile(f)
                    old_map.load()
                    update_map.update(old_map, ref_map, name_mapping, dest_path/f.name)



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
        self.update_button.clicked.connect(lambda: self.parent().parent().switchWidget('kd_widget'))
        layout.addWidget(self.update_button)
        self.mirror_button = QtWidgets.QPushButton('Mirror Map')
        self.mirror_button.clicked.connect(lambda: self.parent().parent().switchWidget('mirror_widget'))        
        layout.addWidget(self.mirror_button)
        self.setLayout(layout)
        
        
        
    



## Define parsers
main_parse = argparse.ArgumentParser(prog="tgmtool")
sub_parsers = main_parse.add_subparsers(required=True, help="available commands")

update_parse = sub_parsers.add_parser("update")
update_parse.set_defaults(func=update)
update_parse.add_argument('source', type=str, help='path to target TGM file or folder containing TGM files')
update_parse.add_argument('dest', type=str, help='path to save source file, or containing folder if multiple source files')
update_parse.add_argument('type_ref', type=str, help='path to reference TGM file created with desired mod version(s)')
update_parse.add_argument('name_mapping', type=str, help='path to JSON mapping between old and new type-names')



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

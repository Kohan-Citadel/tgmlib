# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 23:34:28 2024

@author: Sceadu
"""
from PyQt5 import QtCore, QtWidgets


def FileDialog(directory=r"C:\Program Files (x86)\Steam\steamapps\common\Kohan Ahrimans Gift\Maps", forOpen=True, isFolder=False, multiple=False, filters=("Kohan Maps (*.tgm)",), default_name=None, default_extension=None):
    print(directory)
    print(f"isFolder: {isFolder}")
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseCustomDirectoryIcons
    dialog = QtWidgets.QFileDialog()

    dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)

    # ARE WE TALKING ABOUT FILES OR FOLDERS
    if isFolder:
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        options |= QtWidgets.QFileDialog.ShowDirsOnly
    else:
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles if multiple else QtWidgets.QFileDialog.AnyFile)
    # OPENING OR SAVING
    dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen) if forOpen else dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)

    # SET FILTERS, IF SPECIFIED
    if filters and isFolder is False:
        if type(filters) is str:
            filters = (filters,)
        dialog.setNameFilters(filters)
    
    if default_name:
        dialog.selectFile(str(default_name))
    
    if default_extension:
        dialog.setDefaultSuffix(default_extension)

    # SET THE STARTING DIRECTORY
    if directory:
        dialog.setDirectory(str(directory))

    dialog.setOptions(options)    
    if isFolder:
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)

    if dialog.exec() == QtWidgets.QDialog.Accepted:
        paths = dialog.selectedFiles()  # returns a list
        return paths
    else:
        return None
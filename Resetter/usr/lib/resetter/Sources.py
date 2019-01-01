#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fileinput
import fnmatch
import os
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from Tools import UsefulTools

class SourceEdit(QDialog):
    def __init__(self, parent=None):
        super(SourceEdit, self).__init__(parent)
        self.resize(600, 500)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.font2 = QtGui.QFont()
        self.font2.setBold(False)
        self.searchEditText = QLineEdit()
        self.searchEditText.setPlaceholderText("Search for repositories")
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.label = QLabel()
        self.btnRemove = QPushButton()
        self.btDisable = QPushButton()
        self.btnEnable = QPushButton()
        self.btnClose = QPushButton()
        self.btnClose.setText("Close")
        self.btnRemove.setText("Remove entries")
        self.btDisable.setText("Disable entries")
        self.btnEnable.setText("Enable entries")
        self.label.setPalette(palette)
        self.btnRemove.clicked.connect(self.removeSelectedSources)
        self.btDisable.clicked.connect(self.disableSelectedSources)
        self.btnEnable.clicked.connect(self.enableSelectedSources)
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setWindowTitle("Success")
        self.msg.setText("Your changes have been successfully applied")
        self.btnClose.clicked.connect(self.close)
        self.sourceslists = []
        self.items = []

    def editSources(self, title, tip):
        self.setWindowTitle(title)
        list_view = QListView(self)
        self.model = QtGui.QStandardItemModel(list_view)
        self.model.itemChanged.connect(self.setItems)
        self.setToolTip(tip)
        verticalLayout = QVBoxLayout(self)
        verticalLayout.addWidget(self.searchEditText)
        verticalLayout.addWidget(list_view)
        horizontalLayout = QHBoxLayout()
        horizontalLayout.setAlignment(QtCore.Qt.AlignRight)
        horizontalLayout.addWidget(self.label)
        horizontalLayout.addWidget(self.btDisable)
        horizontalLayout.addWidget(self.btnEnable)
        horizontalLayout.addWidget(self.btnRemove)
        horizontalLayout.addWidget(self.btnClose)
        verticalLayout.addLayout(horizontalLayout)
        mode = 0
        args = (self.model, list_view,  self.label, self.font, self.font2, mode)
        self.searchEditText.textChanged.connect(lambda: UsefulTools().searchItem(*args, self.searchEditText.text()))

        for dirpath, dirs, files in os.walk('/etc/apt/'):
            word = 'deb'
            for filename in fnmatch.filter(files, "*.list"):
                source_list = os.path.join(dirpath, filename)
                self.sourceslists.append(source_list)
                with open(source_list, "r") as sources:
                    for line in sources:
                        if line.startswith(word) or line.startswith('#') \
                                and line[2:].split(' ')[0][:3] == word:
                                item = QtGui.QStandardItem(line.strip())
                                item.setCheckable(True)
                                item.setCheckState(QtCore.Qt.Unchecked)
                                self.model.appendRow(item)
                    list_view.setModel(self.model)

    def setItems(self, item):
        if item.checkState() == QtCore.Qt.Checked:
            self.items.append(item)
        if item.checkState() == QtCore.Qt.Unchecked and len(self.items) > 0:
            self.items.remove(item)

    def disableSelectedSources(self):
        char = "#"
        for item in self.items:
            for line in fileinput.FileInput(self.sourceslists, inplace=1):

                if char not in item.text() and item.text() == line.strip()\
                        and item.checkState() == QtCore.Qt.Checked:
                    disable = "{} {}".format(char, item.text())
                    line = line.replace(item.text(), disable)
                    item.setText(disable)
                sys.stdout.write(line)
                fileinput.close()

    def enableSelectedSources(self):
        for item in self.items:
            for line in fileinput.FileInput(self.sourceslists, inplace=1):
                if str(item.text()).startswith("#") and item.text() == line.strip() \
                        and item.checkState() == QtCore.Qt.Checked:
                    enable = "{}".format(str(item.text())[2:])
                    line = line.replace(item.text(), enable)
                    item.setText(enable)
                sys.stdout.write(line)
                fileinput.close()

    def removeSelectedSources(self):
        item_r = list();
        for item in self.items:
            for line in fileinput.FileInput(self.sourceslists, inplace=1):
                if item.text() == line.strip() \
                        and item.checkState() == QtCore.Qt.Checked:
                    item_r.append(item)
                    line = line.replace(item.text(), '')
                sys.stdout.write(line)
                fileinput.close()
        [self.model.removeRow(r.row()) for r in item_r]

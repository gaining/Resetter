#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fileinput
import fnmatch
import os
import sys
from PyQt4 import QtCore, QtGui
from aptsources import sourceslist


class SourceEdit(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SourceEdit, self).__init__(parent)
        self.resize(600, 500)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.font2 = QtGui.QFont()
        self.font2.setBold(False)
        self.searchEditText = QtGui.QLineEdit()
        self.searchEditText.setPlaceholderText("Search for repositories")
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.label = QtGui.QLabel()
        self.btnRemove = QtGui.QPushButton()
        self.btDisable = QtGui.QPushButton()
        self.btnEnable = QtGui.QPushButton()
        self.btnClose = QtGui.QPushButton()
        self.btnClose.setText("Close")
        self.btnRemove.setText("Remove entries")
        self.btDisable.setText("Disable entries")
        self.btnEnable.setText("Enable entries")
        self.btDisable.setVisible(False)
        self.btnRemove.setVisible(False)
        self.btnEnable.setVisible(False)
        self.label.setPalette(palette)
        self.btnRemove.clicked.connect(self.removeSelectedSources)
        self.btDisable.clicked.connect(self.disableSelectedSources)
        self.btnEnable.clicked.connect(self.enableSelectedSources)
        self.msg = QtGui.QMessageBox()
        self.msg.setIcon(QtGui.QMessageBox.Information)
        self.msg.setWindowTitle("Success")
        self.btnClose.clicked.connect(self.close)
        self.s = sourceslist.SourcesList()
        self.sourceslists = []
        self.items = []

    def editSources(self, title, tip):
        self.setWindowTitle(title)
        self.list_view = QtGui.QListView(self)
        self.model = QtGui.QStandardItemModel(self.list_view)
        self.model.itemChanged.connect(self.setItems)
        self.setToolTip(tip)
        verticalLayout = QtGui.QVBoxLayout(self)
        verticalLayout.addWidget(self.searchEditText)
        verticalLayout.addWidget(self.list_view)
        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.setAlignment(QtCore.Qt.AlignRight)
        horizontalLayout.addWidget(self.label)
        horizontalLayout.addWidget(self.btDisable)
        horizontalLayout.addWidget(self.btnEnable)
        horizontalLayout.addWidget(self.btnRemove)
        horizontalLayout.addWidget(self.btnClose)
        verticalLayout.addLayout(horizontalLayout)
        self.searchEditText.textChanged.connect(lambda: self.searchItem(self.model, self.list_view))
        self.btnRemove.setVisible(True)
        self.btDisable.setVisible(True)
        self.btnEnable.setVisible(True)

        for dirpath, dirs, files in os.walk('/etc/apt/'):
            word = 'deb'
            for filename in fnmatch.filter(files, "*.list"):
                source_list = os.path.join(dirpath, filename)
                self.sourceslists.append(source_list)
                with open(source_list, "r") as sources:
                    for line in sources:
                        if line.startswith(word) or line.startswith('#') \
                                and line[2:].split(' ')[0][:3] == word:
                                self.item = QtGui.QStandardItem(line)
                                self.item.setCheckable(True)
                                self.item.setCheckState(QtCore.Qt.Unchecked)
                                self.model.appendRow(self.item)
                    self.list_view.setModel(self.model)


    def setItems(self, item):
        if item.checkState() == QtCore.Qt.Checked:
            self.items.append(item.text())
        if item.checkState() == QtCore.Qt.Unchecked \
                and len(self.items) > 0 and item.text() in self.items:
            self.items.remove(item.text())

    def disableSelectedSources(self):
        for item in self.items:
            item = str(item)
            char = "#"
            for line in fileinput.FileInput(self.sourceslists, inplace=1):
                if char not in item and item in line:
                    disable = "# {}".format(item)
                    line = line.replace(item, disable)
                sys.stdout.write(line)
                fileinput.close()
        self.close()
        self.msg.setText("Your changes have been successfully applied")
        self.msg.exec_()

    def enableSelectedSources(self):
        for item in self.items:
            item = str(item)
            for line in fileinput.FileInput(self.sourceslists, inplace=1):
                if item in line and item.startswith("#"):
                    enable = "{}".format(item[2:])
                    line = line.replace(item, enable)
                sys.stdout.write(line)
                fileinput.close()
            self.close()
            self.msg.setText("Your changes have been successfully applied")
            self.msg.exec_()

    def removeSelectedSources(self):
        for item in self.items:
            x = sourceslist.SourceEntry(str(item))
            self.s.remove(x)
            self.s.save()
        self.close()
        self.msg.setText("Your changes have been successfully applied")
        self.msg.exec_()

    def searchItem(self, model, view):
        search_string = self.searchEditText.text()
        items = model.findItems(search_string, QtCore.Qt.MatchContains
                                or QtCore.Qt.MatchStartsWith)
        if len(items) > 0:
            for item in items:
                if item.row() == 0:
                    item.setFont(self.font)
                else:
                    item.setFont(self.font2)
                if search_string is not None:
                    item.setEnabled(True)
                    model.takeRow(item.row())
                    model.insertRow(0, item)
                    if len(search_string) == 0:
                        self.label.clear()
                        item.setFont(self.font2)
            view.scrollToTop()
        else:
            self.label.setText("source doesn't exist")
        view.show()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fileinput
import fnmatch
import os
import sys
from PyQt4 import QtCore, QtGui
from aptsources import sourceslist
from Tools import UsefulTools



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
        self.label.setPalette(palette)
        self.btnRemove.clicked.connect(self.removeSelectedSources)
        self.btDisable.clicked.connect(self.disableSelectedSources)
        self.btnEnable.clicked.connect(self.enableSelectedSources)
        self.msg = QtGui.QMessageBox()
        self.msg.setIcon(QtGui.QMessageBox.Information)
        self.msg.setWindowTitle("Success")
        self.msg.setText("Your changes have been successfully applied")
        self.btnClose.clicked.connect(self.close)
        self.s = sourceslist.SourcesList()
        self.sourceslists = []
        self.items = []

    def editSources(self, title, tip):
        self.setWindowTitle(title)
        list_view = QtGui.QListView(self)
        self.model = QtGui.QStandardItemModel(list_view)
        self.model.itemChanged.connect(self.setItems)
        self.setToolTip(tip)
        verticalLayout = QtGui.QVBoxLayout(self)
        verticalLayout.addWidget(self.searchEditText)
        verticalLayout.addWidget(list_view)
        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.setAlignment(QtCore.Qt.AlignRight)
        horizontalLayout.addWidget(self.label)
        horizontalLayout.addWidget(self.btDisable)
        horizontalLayout.addWidget(self.btnEnable)
        horizontalLayout.addWidget(self.btnRemove)
        horizontalLayout.addWidget(self.btnClose)
        verticalLayout.addLayout(horizontalLayout)
        self.searchEditText.textChanged.connect(lambda: self.searchItem(self.model, list_view))

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
        if item.checkState() == QtCore.Qt.Unchecked:
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
        for item in self.items:
            if item.checkState() == QtCore.Qt.Checked:
                self.model.removeRow(item.row())
                x = sourceslist.SourceEntry(str(item.text()))
                self.s.remove(x)
                self.s.save()

    def searchItem(self, model, view):
        search_string = self.searchEditText.text()
        items = model.findItems(search_string, QtCore.Qt.MatchContains or QtCore.Qt.MatchStartsWith)
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
            self.label.setText("Repository doesn't exist")
        view.show()

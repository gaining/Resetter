#!/usr/bin/env python
# -*- coding: utf-8 -*-

import apt
import textwrap
from PyQt5 import QtCore, QtGui

from ApplyDialog import Apply
from PyQt5.QtWidgets import *
from Tools import UsefulTools


class AppView(QDialog):

    def __init__(self, parent=None):
        super(AppView, self).__init__(parent)
        self.resize(600, 500)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.font2 = QtGui.QFont()
        self.font2.setBold(False)
        self.searchEditText = QLineEdit()
        self.searchEditText.setPlaceholderText("Search for packages")
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.label = QLabel()
        self.label.setPalette(palette)

    def closeview(self):
        self.cache.close()
        self.close()

    def showView(self, data, title, tip, start, width=None, height=None, check_state=None):
        self.setWindowTitle(title)
        self.setToolTip(tip)
        self.cache = apt.Cache()
        self.resize(400, 400)
        buttonBox = QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        list_view = QListView(self)
        verticalLayout = QVBoxLayout(self)
        verticalLayout.addWidget(self.searchEditText)
        verticalLayout.addWidget(list_view)
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.label)
        horizontalLayout.addWidget(buttonBox)
        verticalLayout.addLayout(horizontalLayout)
        if start:
            buttonBox.accepted.connect(self.startRemoval)
        else:
            buttonBox.accepted.connect(self.closeview)
        buttonBox.rejected.connect(self.closeview)
        model = QtGui.QStandardItemModel(list_view)
        mode = 1
        args = (model, list_view,  self.label, self.font, self.font2, mode)
        self.searchEditText.textChanged.connect(lambda: UsefulTools().searchItem(*args, self.searchEditText.text()))
        self.file_in = data

        if type(data) is str:
            with open(data) as f:
                for line in f:
                    try:
                        pkg = self.cache[line.strip()]
                        text = pkg.versions[0].description
                        item = QtGui.QStandardItem(line.strip())
                        item.setCheckState(QtCore.Qt.Checked)
                        item.setToolTip((textwrap.fill(text, 70)))
                    except KeyError:
                        continue
                    model.appendRow(item)
                list_view.setModel(model)
                list_view.show()

        elif type(data) is list:
            if width and height is not None:
                self.resize(width, height)
            for x in data:
                x = (str(x))
                item = QtGui.QStandardItem(x)
                item.setCheckable(False)
                if check_state:
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
                model.appendRow(item)
            list_view.setModel(model)
            list_view.show()

        else:
            word = 'deb'
            for x in data:
                m = (str(x))
                if m.startswith(word) or m.startswith('#') \
                        and m[2:].split(' ')[0][:3] == word:
                    item = QtGui.QStandardItem(m)
                    item.setCheckable(False)
                    item.setEditable(False)
                    item.setCheckState(QtCore.Qt.Checked)
                    model.appendRow(item)
            list_view.setModel(model)
            list_view.show()

    def startRemoval(self):
        self.close()
        self.apply = Apply(self.file_in)
        self.apply.show()
        self.apply.raise_()

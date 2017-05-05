#!/usr/bin/env python
# -*- coding: utf-8 -*-

import apt
import textwrap
from PyQt4 import QtCore, QtGui

from ApplyDialog import Apply


class AppView(QtGui.QDialog):
    def __init__(self, parent=None):
        super(AppView, self).__init__(parent)
        self.resize(600, 500)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.font2 = QtGui.QFont()
        self.font2.setBold(False)
        self.searchEditText = QtGui.QLineEdit()
        self.searchEditText.setPlaceholderText("Search for packages")
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.label = QtGui.QLabel()
        self.label.setPalette(palette)

    def searchItem(self, model, view):
        search_string = self.searchEditText.text()
        items = model.findItems(search_string, QtCore.Qt.MatchStartsWith)
        if len(items) > 0:
            for item in items:
                if search_string is not None:
                    item.setEnabled(True)
                    model.takeRow(item.row())
                    model.insertRow(0, item)

                    if item.text()[:3] == search_string:
                        item.setFont(self.font)
                        self.label.clear()

                    if len(search_string) == 0:
                        self.label.clear()
                        item.setFont(self.font2)
            view.scrollToTop()
        else:
            self.label.setText("Package doesn't exist")
        view.show()

    def closeview(self):
        self.cache.close()
        self.close()

    def showView(self, data, title, tip, start):
        self.setWindowTitle(title)
        self.setToolTip(tip)
        self.cache = apt.Cache()
        self.resize(400, 400)
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        list_view = QtGui.QListView(self)
        verticalLayout = QtGui.QVBoxLayout(self)
        verticalLayout.addWidget(self.searchEditText)
        verticalLayout.addWidget(list_view)
        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.addWidget(self.label)
        horizontalLayout.addWidget(buttonBox)
        verticalLayout.addLayout(horizontalLayout)
        if start:
            buttonBox.accepted.connect(self.startRemoval)
        else:
            buttonBox.accepted.connect(self.closeview)
        buttonBox.rejected.connect(self.closeview)
        model = QtGui.QStandardItemModel(list_view)
        self.searchEditText.textChanged.connect(lambda: self.searchItem(model, list_view))

        if type(data) is str:
            with open(data) as f:
                for line in f:
                    try:
                        pkg = self.cache[line.strip()]
                        text = pkg.versions[0].description
                        item = QtGui.QStandardItem(line)
                        item.setCheckState(QtCore.Qt.Checked)
                        item.setToolTip((textwrap.fill(text, 70)))
                    except KeyError:
                        continue
                    model.appendRow(item)
                list_view.setModel(model)
                list_view.show()

        elif type(data) is list:
            for x in data:
                x = (str(x))
                item = QtGui.QStandardItem(x)
                item.setCheckable(False)
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

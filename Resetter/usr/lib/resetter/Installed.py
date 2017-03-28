#!/usr/bin/python
import sys
from PyQt4 import QtCore, QtGui
import os
import apt
from ApplyDialog import Apply

class AppView(QtGui.QDialog):

    def __init__(self, parent=None):
        super(AppView, self).__init__(parent)
        self.resize(400, 400)
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

    def showInstalledList(self, install_list):
        self.setWindowTitle("Installed Package List")
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.listview = QtGui.QListView(self)
        verticalLayout = QtGui.QVBoxLayout(self)
        verticalLayout.addWidget(self.searchEditText)
        verticalLayout.addWidget(self.listview)
        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.addWidget(self.label)
        horizontalLayout.addWidget(buttonBox)
        verticalLayout.addLayout(horizontalLayout)
        buttonBox.accepted.connect(self.close)
        self.model = QtGui.QStandardItemModel(self.listview)
        self.searchEditText.textChanged.connect(lambda: self.searchItem(self.model, self.listview))
        with open(install_list) as input:
            if input is not None:
                item = input.readlines()
            for line in item:
                item = QtGui.QStandardItem(line)
                item.setCheckState(QtCore.Qt.PartiallyChecked)
                item.setSelectable(True)
                item.setEditable(False)
                self.model.appendRow(item)
        self.listview.setModel(self.model)
        self.listview.show()

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

    def showUninstallList(self, file_in):
        self.setWindowTitle("Packages To Remove")
        self.file_in = file_in
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        uninstall_view = QtGui.QListView(self)
        verticalLayout = QtGui.QVBoxLayout(self)
        verticalLayout.addWidget(self.searchEditText)
        verticalLayout.addWidget(uninstall_view)
        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.addWidget(self.label)
        horizontalLayout.addWidget(buttonBox)
        verticalLayout.addLayout(horizontalLayout)
        buttonBox.accepted.connect(self.startRemoval)
        buttonBox.rejected.connect(self.close)
        self.model2 = QtGui.QStandardItemModel(uninstall_view)
        self.searchEditText.textChanged.connect(lambda: self.searchItem(self.model2, uninstall_view))
        with open(self.file_in) as f:
            if f is not None:
                item = f.readlines()
            for line in item:
                item = QtGui.QStandardItem(line)
                item.setCheckState(QtCore.Qt.Checked)
                self.model2.appendRow(item)

        uninstall_view.setModel(self.model2)
        uninstall_view.show()

    def startRemoval(self):
        self.close()
        self.apply = Apply(self.file_in)
        self.apply.show()
        self.apply.raise_()



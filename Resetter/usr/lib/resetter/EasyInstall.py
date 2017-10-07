#!/usr/bin/env python
# -*- coding: utf-8 -*-
import apt
import os
import textwrap
from PyQt4 import QtCore, QtGui

from InstallMissingDialog import Install


class EasyInstaller(QtGui.QDialog):
    def __init__(self, parent=None):
        super(EasyInstaller, self).__init__(parent)
        self.setWindowTitle("Easy install")
        self.list_view = QtGui.QListView(self)
        self.list_view.setFixedWidth(380)
        self.EditText = QtGui.QLineEdit()
        self.EditText.setPlaceholderText("Search for applications")
        #self.setWindowFlags(QtCore.Qt.Window)
        self.model = QtGui.QStandardItemModel(self.list_view)
        self.setFixedSize(600, 350)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.font2 = QtGui.QFont()
        self.font2.setBold(False)
        self.EditText = QtGui.QLineEdit()
        self.EditText.setPlaceholderText("Add apps to install")
        self.btnRemove = QtGui.QPushButton()
        self.btnInstall = QtGui.QPushButton()
        self.btnBrowse = QtGui.QPushButton()
        self.btnBrowse.setFixedWidth(100)
        self.btnBrowse.clicked.connect(self.openBackup)
        self.btnBrowse.setText("Open Backup")
        self.btnRemove.setText("Remove From List")
        self.btnRemove.clicked.connect(self.removeItems)
        self.btnInstall.setText("Install Apps")
        self.btnInstall.clicked.connect(self.installPackages)
        self.btnadd = QtGui.QPushButton(self)
        self.btnadd.setText("Add App")
        self.btnClose = QtGui.QPushButton()
        self.btnClose.setText("Close")
        self.btnClose.clicked.connect(self.closeview)
        self.btnadd.clicked.connect(self.addItems)
        self.btnselect = QtGui.QPushButton()
        self.btnselect.setText("Select All")
        self.btnselect.clicked.connect(self.selectAll)
        self.comboBox = QtGui.QComboBox()
        self.comboBox.setVisible(False)
        self.comboBox.currentIndexChanged.connect(self.setText)
        miniLayout = QtGui.QVBoxLayout()
        miniLayout.addWidget(self.EditText)
        miniLayout.addWidget(self.comboBox)
        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.addLayout(miniLayout)
        horizontalLayout.addWidget(self.btnadd)
        horizontalLayout.addWidget(self.btnBrowse)
        horizontalLayout.setAlignment(QtCore.Qt.AlignRight)
        horizontalLayout2 = QtGui.QHBoxLayout()
        horizontalLayout2.addWidget(self.btnRemove)
        horizontalLayout2.addWidget(self.btnselect)
        horizontalLayout2.addWidget(self.btnInstall)
        horizontalLayout2.addWidget(self.btnClose)
        verticalLayout = QtGui.QVBoxLayout(self)
        verticalLayout.addLayout(horizontalLayout)
        verticalLayout.addWidget(self.list_view)
        verticalLayout.addLayout(horizontalLayout2)
        self.cache = apt.Cache()
        self.isWritten = False

    def addItems(self):
        package = str(self.EditText.text())
        try:
            pkg = self.cache[package.strip()]
            n = pkg.shortname
            v = pkg.versions[0].version
            desc = pkg.versions[0].description
            name = "{}: {}".format(n, v)
            if len(package) > 0 and pkg.is_installed is False:
                item = QtGui.QStandardItem(name)
                item.setCheckable(True)
                item.setSelectable(True)
                item.setToolTip((textwrap.fill(desc, 70)))
                item.setCheckState(QtCore.Qt.Unchecked)
                self.model.appendRow(item)
                self.list_view.setModel(self.model)
            else:
                self.alreadyInstalled(name)
            self.EditText.clear()
        except KeyError:
            self.showMessage(package)

    def setText(self):
        if self.comboBox.count() > 1:
            self.EditText.setText(self.comboBox.currentText())
        else:
            self.comboBox.setVisible(False)

    def removeItems(self):
        for row in xrange(self.model.rowCount()):
            item = self.model.item(row)
            if item and item.checkState() == QtCore.Qt.Checked:
                self.model.removeRow(row)
                self.removeItems()

    def selectAll(self):
        model = self.model
        for index in xrange(model.rowCount()):
            item = model.item(index)
            if item.isCheckable() and item.checkState() == QtCore.Qt.Unchecked:
                item.setCheckState(QtCore.Qt.Checked)
                self.btnselect.setText("Deselect all")
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
                self.btnselect.setText("Select all")

    def openBackup(self):
        try:
            dpath = os.path.abspath(os.path.join('Backup', '../../../'))
            backup = QtGui.QFileDialog.getOpenFileName(self, 'Choose Backup', dpath, '(*.rbf)')
            if os.path.isfile(backup):
                with open(backup, 'r') as bk:
                    for line in bk:
                        try:
                            pkg = self.cache[line.strip()]
                            n = pkg.shortname
                            v = pkg.versions[0].version
                            desc = pkg.versions[0].raw_description
                            name = "{}: {}".format(n, v)
                            if len(line) > 0 and pkg.is_installed is False:
                                item = QtGui.QStandardItem(name)
                                item.setCheckable(True)
                                item.setSelectable(True)
                                item.setToolTip((textwrap.fill(desc, 70)))
                                item.setCheckState(QtCore.Qt.Unchecked)
                                self.model.appendRow(item)
                                self.list_view.setModel(self.model)
                            self.EditText.clear()
                        except KeyError:
                            continue
        except IOError:
            pass

    def installPackages(self):
        self.btnInstall.setEnabled(False)
        model = self.model
        for index in xrange(model.rowCount()):
            item = model.item(index)
            if self.isWritten:
                mode = 'a'
            else:
                mode = 'w'
                self.isWritten = True
            if item.isCheckable() and item.checkState() == QtCore.Qt.Checked:
                with open('install', mode) as f_out:
                    to_install = str(item.text()).split(':')[0]
                    f_out.write('{}\n'.format(to_install))

        self.install = Install('install', 'Installing packages', True)
        self.install.show()
        self.install.exec_()
        self.cache.close()
        self.btnInstall.setEnabled(True)
        self.removeItems()

    def closeview(self):
        self.cache.close()
        self.close()

    def alreadyInstalled(self, package):
        msg = QtGui.QMessageBox(self)
        msg.setWindowTitle("Package already installed")
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("{} is already on your system".format(package))
        msg.exec_()

    def showMessage(self, package):
        self.comboBox.clear()
        self.comboBox.addItem("Did you mean?")
        i = 0
        for p in self.cache:
            if p.shortname.startswith(package) and len(package) > 0 and i < 12:
                i += 1
                self.comboBox.addItem(p.shortname)
        if self.comboBox.count() > 1:
            self.comboBox.setVisible(True)
        msg = QtGui.QMessageBox(self)
        msg.setWindowTitle("Package not found")
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("The package that you've tried to add is not found in the cache")
        msg.setDetailedText("If you've recently added a ppa containing this package, "
                            "please use [EasyPPA - refresh sources] feature, "
                            "then try adding the package again.")
        msg.exec_()

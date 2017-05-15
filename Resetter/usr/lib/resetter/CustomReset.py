#!/usr/bin/env python
# -*- coding: utf-8 -*-

import apt
import apt.package
import logging
import textwrap
from PyQt4 import QtCore, QtGui

from CustomApplyDialog import Apply


class AppRemovalPage(QtGui.QWizardPage):
    def __init__(self, parent=None):
        super(AppRemovalPage, self).__init__(parent=parent)
        self.setTitle('Packages To Remove')
        self.setSubTitle('For a proper system reset, all packages on this list should be checked for removal')
        self.uninstall_view = QtGui.QListView(self)
        self.uninstall_view.setMinimumSize(465, 200)
        self.select_button = QtGui.QPushButton(self)
        self.select_button.setText("Select All")
        self.select_button.setMaximumSize(QtCore.QSize(100, 100))
        self.select_button.clicked.connect(self.selectAll)
        self.checkBox = QtGui.QCheckBox('Remove old kernels')
        self.searchEditText = QtGui.QLineEdit()
        self.searchEditText.setPlaceholderText("Search for packages")
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.font2 = QtGui.QFont()
        self.font2.setBold(False)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.label = QtGui.QLabel()
        self.label.setPalette(palette)
        self.checkBox.stateChanged.connect(self.toggleCheckbox)
        self.searchEditText.textChanged.connect(self.searchItem)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.addWidget(self.label, 0, QtCore.Qt.AlignLeft)
        self.horizontalLayout.addWidget(self.checkBox, 0, QtCore.Qt.AlignRight)
        self.horizontalLayout.addWidget(self.select_button)
        self.verticalLayout.addWidget(self.searchEditText)
        self.verticalLayout.addWidget(self.uninstall_view)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.oldKernelRemoval = False
        self.isWritten = False
        self.items = []
        self.cache = apt.Cache()
        remove_list = "apps-to-remove"
        self.model = QtGui.QStandardItemModel(self.uninstall_view)
        self.model.itemChanged.connect(self.setItems)

        with open(remove_list) as f_in:
            for line in f_in:
                try:
                    pkg = self.cache[line.strip()]
                    text = (pkg.versions[0].description)
                    self.item = QtGui.QStandardItem(line)
                    self.item.setCheckable(True)
                    self.item.setCheckState(QtCore.Qt.Unchecked)
                    self.model.appendRow(self.item)
                    self.item.row()
                    self.item.setToolTip((textwrap.fill(text, 70)))
                except KeyError:
                    continue

            self.uninstall_view.setModel(self.model)

    def toggleCheckbox(self):
        if self.oldKernelRemoval is False:
            self.oldKernelRemoval = True
        else:
            self.oldKernelRemoval = False

    def searchItem(self):
        search_string = self.searchEditText.text()
        items = self.model.findItems(search_string, QtCore.Qt.MatchStartsWith)
        if len(items) > 0:
            for item in items:
                if search_string is not None:
                    item.setEnabled(True)
                    self.model.takeRow(item.row())
                    self.model.insertRow(0, item)
                    if item.text()[:3] == search_string:
                        item.setFont(self.font)
                        self.label.clear()
                    if len(search_string) == 0:
                        self.label.clear()
                        item.setFont(self.font2)
            self.uninstall_view.scrollToTop()
        else:
            self.label.setText("Package doesn't exist")

    def selectAll(self):
        model = self.model
        for index in range(model.rowCount()):
            item = model.item(index)
            if item.isCheckable() and item.checkState() == QtCore.Qt.Unchecked:
                item.setCheckState(QtCore.Qt.Checked)
                self.select_button.setText("Deselect all")
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
                self.select_button.setText("Select all")

    def setItems(self, item):
        if item.checkState() == QtCore.Qt.Checked:
            self.items.append(item)
        if item.checkState() == QtCore.Qt.Unchecked and len(self.items) > 0:
            self.items.remove(item)

    def selectedAppsRemoval(self):
        path = "custom-remove"
        mode = 'a' if self.isWritten else 'w'
        with open(path, mode) as f_out:
            for item in self.items:
                #print('{}'.format(item.text()))
                f_out.write(item.text())

    def closeCache(self):
        self.cache.close()


class AppInstallPage(QtGui.QWizardPage):
    def __init__(self, parent=None):
        super(AppInstallPage, self).__init__(parent=parent)
        self.setTitle('Packages to Install')
        self.setSubTitle('These are pre-installed packages that are missing from your system. '
                         'For a proper system reset, all of these packages should be checked for install')
        self.uninstall_view = QtGui.QListView(self)
        self.uninstall_view.setMinimumSize(465, 200)
        self.select_button = QtGui.QPushButton(self)
        self.select_button.setText("Select All")
        self.select_button.setMaximumSize(QtCore.QSize(100, 100))
        self.select_button.clicked.connect(self.selectAll)
        self.searchEditText = QtGui.QLineEdit()
        self.searchEditText.setPlaceholderText("Search for packages")
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.font2 = QtGui.QFont()
        self.font2.setBold(False)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.label = QtGui.QLabel()
        self.label.setPalette(palette)
        self.searchEditText.textChanged.connect(self.searchItem)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.addWidget(self.label, 0, QtCore.Qt.AlignLeft)
        self.horizontalLayout.addWidget(self.select_button)
        self.verticalLayout.addWidget(self.searchEditText)
        self.verticalLayout.addWidget(self.uninstall_view)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.oldKernelRemoval = False
        self.isWritten = False
        self.items = []
        install_list = "apps-to-install"
        self.model = QtGui.QStandardItemModel(self.uninstall_view)
        self.model.itemChanged.connect(self.setItems)
        self.cache = apt.Cache()

        with open(install_list) as f_in:
            for line in f_in:
                try:
                    pkg = self.cache[line.strip()]
                    text = (pkg.versions[0].description)
                    self.item = QtGui.QStandardItem(line)
                    self.item.setCheckable(True)
                    self.item.setCheckState(QtCore.Qt.Unchecked)
                    self.model.appendRow(self.item)
                    self.item.row()
                    self.item.setToolTip((textwrap.fill(text, 70)))
                except KeyError:
                    continue
            self.uninstall_view.setModel(self.model)

    def searchItem(self):
        search_string = self.searchEditText.text()
        items = self.model.findItems(search_string, QtCore.Qt.MatchStartsWith)
        if len(items) > 0:
            for item in items:
                if search_string is not None:
                    item.setEnabled(True)
                    self.model.takeRow(item.row())
                    self.model.insertRow(0, item)
                    if item.text()[:3] == search_string:
                        item.setFont(self.font)
                        self.label.clear()
                    if len(search_string) == 0:
                        self.label.clear()
                        item.setFont(self.font2)
            self.uninstall_view.scrollToTop()
        else:
            self.label.setText("Package doesn't exist")

    def closeCache(self):
        self.cache.close()

    def selectAll(self):
        model = self.model
        for index in range(model.rowCount()):
            item = model.item(index)
            if item.isCheckable() and item.checkState() == QtCore.Qt.Unchecked:
                item.setCheckState(QtCore.Qt.Checked)
                self.select_button.setText("Deselect all")
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
                self.select_button.setText("Select all")

    def setItems(self, item):
        if item.checkState() == QtCore.Qt.Checked:
            self.items.append(item)
        if item.checkState() == QtCore.Qt.Unchecked and len(self.items) > 0:
            self.items.remove(item)

    def selectedAppsInstall(self):
        path = "custom-install"
        mode = 'a' if self.isWritten else 'w'
        with open(path, mode) as f_out:
            for item in self.items:
                #print('{}'.format(item.text()))
                f_out.write(item.text())


class UserRemovalPage(QtGui.QWizardPage):
    def __init__(self, parent=None):
        super(UserRemovalPage, self).__init__(parent)
        self.setTitle('Delete Local users')
        self.setSubTitle('For a proper system reset, all users on this list should be checked for removal')
        self.isWrittenTo = False
        self.table = QtGui.QTableWidget()
        self.table.setGeometry(200, 200, 200, 200)

        self.configureTable(self.table)
        self.table.verticalHeader().hide()

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.horizontalLayout.addWidget(self.table)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName) - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.choice = []
        self.table.itemChanged.connect(self.setChoice)

    def configureTable(self, table):
        table.setColumnCount(3)
        table.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem("Users"))
        table.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem("Delete User"))
        table.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem("Delete User and Home"))
        header = table.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)

        users = open('users').read().splitlines()
        table.setRowCount(len(users))
        for i, line in enumerate(users):
            x = QtGui.QTableWidgetItem()
            x.setTextAlignment(QtCore.Qt.AlignCenter)
            table.setItem(i, 0, x)
            x.setText(line)

        for column in range(3):
            for row in range(table.rowCount()):
                if column % 3:
                    self.item = QtGui.QTableWidgetItem(column)
                    self.item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                                       QtCore.Qt.ItemIsEnabled)
                    self.item.setCheckState(QtCore.Qt.Unchecked)
                    table.setItem(row, column, self.item)

    def setChoice(self, item):
        if item.checkState() == QtCore.Qt.Checked:
            self.choice.append(item)
        if item.checkState() == QtCore.Qt.Unchecked:
            self.choice.remove(item)

    def printChecked(self):
        path = 'custom-users-to-delete.sh'
        mode = 'a' if self.isWrittenTo else 'w'
        user = self.table
        d = dict([(x, 0) for x in range(self.table.rowCount())])
        for item in self.choice:
            d[item.row()] += 2 ** (item.column() - 1)

        text = ""
        for row, value in d.iteritems():
            if value == 3:  # They are both checked
                print'{} is marked for {}'.format(user.item(row, 0).text(), user.horizontalHeaderItem(2).text())
                user.item(row, 1).setCheckState(QtCore.Qt.Unchecked)
                text += 'userdel -r -f {}\n'.format(user.item(row, 0).text())
                self.logger.debug(text)
            elif value == 2:  # only second is checked
                print'{} is marked for {}'.format(user.item(row, 0).text(), user.horizontalHeaderItem(2).text())
                text += 'userdel -r -f {}\n'.format(user.item(row, 0).text())
                self.logger.debug(text)
            elif value == 1:  # only first is checked
                print'{} is makred for {}'.format(user.item(row, 0).text(), user.horizontalHeaderItem(1).text())
                text += 'userdel -f {}\n'.format(user.item(row, 0).text())
                self.logger.debug(text)
        with open(path, mode) as f:
            f.write(text)


class AppWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        super(AppWizard, self).__init__(parent)
        self.setWindowTitle("Custom Reset")
        self.appremoval = AppRemovalPage()
        self.appinstall = AppInstallPage()
        self.addPage(self.appremoval)
        self.addPage(self.appinstall)
        self.userremoval = UserRemovalPage()
        self.addPage(self.userremoval)
        self.addPage(self.createConclusionPage())
        self.button(QtGui.QWizard.CancelButton).clicked.connect(self.appremoval.closeCache)
        self.button(QtGui.QWizard.NextButton).clicked.connect(self.appremoval.selectedAppsRemoval)
        self.button(QtGui.QWizard.CancelButton).clicked.connect(self.appinstall.closeCache)
        self.button(QtGui.QWizard.NextButton).clicked.connect(self.appinstall.selectedAppsInstall)
        self.button(QtGui.QWizard.NextButton).clicked.connect(self.userremoval.printChecked)
        self.button(QtGui.QWizard.FinishButton).clicked.connect(self.apply)

    def apply(self):
        self.close()
        self.custom_remove = Apply("custom-remove", self.appremoval.oldKernelRemoval)
        self.custom_remove.show()

    def createConclusionPage(self):
        page = QtGui.QWizardPage()
        page.setTitle("Apply Changes")
        label = QtGui.QLabel("Press the Finish button to start")
        label.setWordWrap(True)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        page.setLayout(layout)
        return page

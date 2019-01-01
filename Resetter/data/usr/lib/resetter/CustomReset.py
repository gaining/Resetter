#!/usr/bin/env python
# -*- coding: utf-8 -*-

import apt
import apt.package
import logging
import textwrap
from PyQt5 import QtCore, QtGui
from CustomApplyDialog import Apply
from PackageView import AppView
from Tools import UsefulTools
from PyQt5.QtWidgets import *


class AppRemovalPage(QWizardPage):

    def __init__(self, parent=None):
        super(AppRemovalPage, self).__init__(parent=parent)
        self.setTitle('Packages To Remove')
        #QApplication.setStyle("GTK")
        self.setSubTitle('For a proper system reset, all packages on this list should be checked for removal')
        self.uninstall_view = QListView(self)
        self.uninstall_view.setMinimumSize(465, 200)
        self.select_button = QPushButton(self)
        self.select_button.setText("Select All")
        self.select_button.setMaximumSize(QtCore.QSize(100, 100))
        self.select_button.clicked.connect(self.selectAll)
        self.searchEditText = QLineEdit()
        self.searchEditText.setPlaceholderText("Search for packages")
        self.checkBox = QCheckBox('Remove old kernels')
        self.checkBox.stateChanged.connect(self.toggleCheckbox)
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.font2 = QtGui.QFont()
        self.font2.setBold(False)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.label = QLabel()
        self.label.setPalette(palette)
        self.switchBox = QCheckBox('View dependent packages')
        self.switchBox.stateChanged.connect(self.toggleSwitch)
        self.switchBox.setToolTip(textwrap.fill
        ("Warning! Only use this for single packages for which you're curious about. Do not use the select all "
         "option while this is checked. Packages in this list will be removed whether you checked them or not.", 50))
        self.searchEditText.textChanged.connect(self.searchItem)
        self.verticalLayout = QVBoxLayout(self)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.addWidget(self.label, 0, QtCore.Qt.AlignLeft)
        self.horizontalLayout.addWidget(self.checkBox, 0, QtCore.Qt.AlignRight)
        self.horizontalLayout.addWidget(self.switchBox)
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
        self.switch = False
        self.count = 0
        self.items = []
        self.cache = apt.Cache()
        self.model = QtGui.QStandardItemModel(self.uninstall_view)
        self.model.itemChanged.connect(self.setItems)

        with open('apps-to-remove') as f_in:
            for line in f_in:
                try:
                    pkg = self.cache[line.strip()]
                    text = pkg.versions[0].description
                    item = QtGui.QStandardItem(line.strip())
                    item.setCheckable(True)
                    item.setCheckState(QtCore.Qt.Unchecked)
                    self.model.appendRow(item)
                    item.row()
                    item.setToolTip((textwrap.fill(text, 70)))
                except KeyError:
                    continue
            self.uninstall_view.setModel(self.model)

    def toggleCheckbox(self):
        if self.oldKernelRemoval is False:
            self.oldKernelRemoval = True
        else:
            self.oldKernelRemoval = False

    def toggleSwitch(self):
        if self.switch is False:
            self.switch = True
            if self.count == 0:  # show warning message only once
                text = ("Only use this option for single packages for which you're curious about. "
                            "<strong>Do not use the <i>Select All</i> option while this is checked</strong>")
                UsefulTools().showMessage("warning", text, QMessageBox.Warning)
            self.count += 1
        else:
            self.switch = False

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
        try:
            if item.checkState() == QtCore.Qt.Checked:
                self.items.append(item.text())
                if self.switch:
                    self.depPackages(item.text())
            if item.checkState() == QtCore.Qt.Unchecked and len(self.items) > 0:
                self.items.remove(item.text())
        except ValueError:
            pass

    def depPackages(self, item):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        package = self.cache[(str(item)).strip()]
        package.mark_delete(True, True)
        if len(self.cache.get_changes()) > 1:
            dep_view = AppView(self)
            text = "These packages depend on {} and they will also be REMOVED.".format(str(item))
            changes = []
            for package in self.cache.get_changes():
                if package.marked_delete:
                    changes.append(package)
            dep_view.showView(changes, 'Dependent packages',
                         text, False, width=370, height=200, check_state=1)
            dep_view.show()
        self.cache.clear()
        QApplication.restoreOverrideCursor()

    def selectedAppsRemoval(self):
        path = "custom-remove"
        mode = 'a' if self.isWritten else 'w'
        with open(path, mode) as f_out:
            for item in self.items:
                f_out.write(item + '\n')

    def closeCache(self):
        self.cache.close()


class AppInstallPage(QWizardPage):

    def __init__(self, parent=None):
        super(AppInstallPage, self).__init__(parent=parent)
        self.setTitle('Packages to Install')
        self.setSubTitle('These are pre-installed packages that are missing from your system. '
                         'For a proper system reset, all of these packages should be checked for install')
        self.uninstall_view = QListView(self)
        self.uninstall_view.setMinimumSize(465, 200)
        self.select_button = QPushButton(self)
        self.select_button.setText("Select All")
        self.select_button.setMaximumSize(QtCore.QSize(100, 100))
        self.select_button.clicked.connect(self.selectAll)
        self.searchEditText = QLineEdit()
        self.searchEditText.setPlaceholderText("Search for packages")
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.font2 = QtGui.QFont()
        self.font2.setBold(False)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.label = QLabel()
        self.label.setPalette(palette)
        self.searchEditText.textChanged.connect(self.searchItem)
        self.verticalLayout = QVBoxLayout(self)
        self.horizontalLayout = QHBoxLayout()
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
        self.model = QtGui.QStandardItemModel(self.uninstall_view)
        self.model.itemChanged.connect(self.setItems)
        self.cache = apt.Cache()

        with open('apps-to-install') as f_in:
            for line in f_in:
                try:
                    pkg = self.cache[line.strip()]
                    text = (pkg.versions[0].description)
                    item = QtGui.QStandardItem(line.strip())
                    item.setCheckable(True)
                    item.setCheckState(QtCore.Qt.Unchecked)
                    self.model.appendRow(item)
                    item.row()
                    item.setToolTip((textwrap.fill(text, 70)))
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
                f_out.write(item.text() + '\n')


class UserRemovalPage(QWizardPage):

    def __init__(self, parent=None):
        super(UserRemovalPage, self).__init__(parent)
        self.setTitle('Delete Local users')
        self.setSubTitle('For a proper system reset, all users on this list should be checked for removal')
        self.isWrittenTo = False
        self.table = QTableWidget()
        self.table.setGeometry(200, 200, 200, 200)

        self.configureTable(self.table)
        self.table.verticalHeader().hide()
        self.checkBox = QCheckBox('Remove non-default system users')
        self.checkBox.stateChanged.connect(self.toggleCheckbox)

        self.horizontalLayout = QHBoxLayout()
        self.verticalLayout = QVBoxLayout(self)
        self.horizontalLayout.addWidget(self.table)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.checkBox, 0, QtCore.Qt.AlignRight)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName) - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.choice = []
        self.table.itemChanged.connect(self.setChoice)
        self.remove_non_defaults = False

    def configureTable(self, table):
        table.setColumnCount(3)
        table.setHorizontalHeaderItem(0, QTableWidgetItem("Users"))
        table.setHorizontalHeaderItem(1, QTableWidgetItem("Delete User"))
        table.setHorizontalHeaderItem(2, QTableWidgetItem("Delete User and Home"))
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        users = open('users').read().splitlines()
        table.setRowCount(len(users))
        for i, line in enumerate(users):
            x = QTableWidgetItem()
            x.setTextAlignment(QtCore.Qt.AlignCenter)
            table.setItem(i, 0, x)
            x.setText(line)
        for column in range(3):
            for row in range(table.rowCount()):
                if column % 3:
                    item = QTableWidgetItem(column)
                    item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                                       QtCore.Qt.ItemIsEnabled)
                    item.setCheckState(QtCore.Qt.Unchecked)
                    table.setItem(row, column, item)

    def setChoice(self, item):
        if item.checkState() == QtCore.Qt.Checked:
            self.choice.append(item)
        if item.checkState() == QtCore.Qt.Unchecked:
            self.choice.remove(item)

    def toggleCheckbox(self):
        if self.remove_non_defaults is False:
            self.remove_non_defaults = True
        else:
            self.remove_non_defaults = False

    def printChecked(self):
        path = 'custom-users-to-delete.sh'
        mode = 'a' if self.isWrittenTo else 'w'
        user = self.table
        d = dict([(x, 0) for x in range(self.table.rowCount())])
        for item in self.choice:
            d[item.row()] += 2 ** (item.column() - 1)
        text = ""
        for row, value in d.items():
            if value == 3:  # They are both checked
                print('{} is marked for {}'.format(user.item(row, 0).text(), user.horizontalHeaderItem(2).text()))
                user.item(row, 1).setCheckState(QtCore.Qt.Unchecked)
                text += 'userdel -rf {}\n'.format(user.item(row, 0).text())
                self.logger.debug(text)
            elif value == 2:  # only second is checked
                print('{} is marked for {}'.format(user.item(row, 0).text(), user.horizontalHeaderItem(2).text()))
                text += 'userdel -rf {}\n'.format(user.item(row, 0).text())
                self.logger.debug(text)
            elif value == 1:  # only first is checked
                print('{} is makred for {}'.format(user.item(row, 0).text(), user.horizontalHeaderItem(1).text()))
                text += 'userdel -f {}\n'.format(user.item(row, 0).text())
                self.logger.debug(text)
        with open(path, mode) as f:
            f.write(text)

class AppWizard(QWizard):
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
        self.button(QWizard.CancelButton).clicked.connect(self.appremoval.closeCache)
        self.button(QWizard.NextButton).clicked.connect(self.appremoval.selectedAppsRemoval)
        self.button(QWizard.CancelButton).clicked.connect(self.appinstall.closeCache)
        self.button(QWizard.NextButton).clicked.connect(self.appinstall.selectedAppsInstall)
        self.button(QWizard.NextButton).clicked.connect(self.userremoval.printChecked)
        self.button(QWizard.FinishButton).clicked.connect(self.apply)

    def apply(self):
        self.close()
        self.custom_remove = Apply("custom-remove", self.appremoval.oldKernelRemoval,
                                   self.userremoval.remove_non_defaults)
        self.custom_remove.show()

    def createConclusionPage(self):
        page = QWizardPage()
        page.setTitle("Apply Changes")
        label = QLabel("Press the Finish button to start")
        label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(label)
        page.setLayout(layout)
        return page

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This class is responsible for setting up the main ui and generating files that other functions will need
# to work with.
import datetime
import logging
import os
import subprocess
import sys
import textwrap
import psutil


from PyQt5 import QtCore, QtGui, QtSvg
from PyQt5.QtWidgets import *

from AboutPage import About
from CustomReset import AppWizard
from EasyInstall import EasyInstaller
from EasyRepo import EasyPPAInstall
from PackageView import AppView
from SetEnvironment import Settings
from Sources import SourceEdit
from Tools import UsefulTools


class UiMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(UiMainWindow, self).__init__(parent)
        self.d_env = Settings()
        self.setWindowIcon(QtGui.QIcon('/usr/lib/resetter/data/icons/resetter-launcher.png'))
        self.setWindowTitle(self.d_env.window_title)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.resize(850, 685)
        palette = QtGui.QPalette()
        self.setPalette(palette)
        self.menubar = self.menuBar()
        self.menuFile = QMenu(self.menubar)
        self.menuView = QMenu(self.menubar)
        self.menuTools = QMenu(self.menubar)
        self.menuHelp = QMenu(self.menubar)
        self.actionOpen = QAction(self)
        self.actionOpenUserList = QAction(self)
        self.actionUpdateManifests = QAction(self)
        self.actionUpdateUserlists = QAction(self)

        self.actionSaveSnapshot = QAction(self)
        self.actionSaveSnapshot.setStatusTip('Save a snapshot of currently installed packages. '
                                             'It is best to save this file in a removable drive for later use.')
        self.actionOpen.triggered.connect(self.openManifest)
        self.actionOpenUserList.triggered.connect(self.openUserList)

        self.actionSaveSnapshot.triggered.connect(self.save)
        self.actionSaveSnapshot.setShortcut('Ctrl+S')

        self.actionExit = QAction(self)
        self.actionExit.setShortcut('Ctrl+Q')
        self.actionExit.setStatusTip('Exit application')
        self.actionExit.triggered.connect(qApp.quit)
        self.actionAbout = QAction(self)
        self.actionAbout.triggered.connect(self.about)
        self.actionEasyPPA = QAction(self)
        self.actionEasyPPA.triggered.connect(self.searchLaunchpad)
        self.actionEasyPPA.setStatusTip("The easiest way to get and install PPAs right from launchpad.net.")
        self.actionShow_Installed = QAction(self)
        self.actionShow_Installed.setStatusTip('Show list of installed packages')
        self.actionShow_Installed.triggered.connect(self.showInstalled)
        self.actionShow_missing = QAction(self)
        self.actionShow_missing.setStatusTip('Show removed packages from initial install')
        self.actionShow_missing.triggered.connect(self.showMissings)
        self.actionEditSources = QAction(self)
        self.actionEditSources.setStatusTip('Edit your sources list')
        self.actionEditSources.triggered.connect(self.editSourcesList)
        self.actionShowUsers = QAction(self)
        self.actionShowUsers.setStatusTip('View non-default system users')
        self.actionShowUsers.triggered.connect(self.showNonDefaultUsers)
        self.actionUpdateManifests.triggered.connect(lambda: UsefulTools().updateFiles('manifests'))
        self.actionUpdateUserlists.triggered.connect(lambda: UsefulTools().updateFiles('userlists'))

        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionOpenUserList)

        self.menuFile.addAction(self.actionSaveSnapshot)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuView.addAction(self.actionShow_missing)
        self.menuView.addAction(self.actionShow_Installed)
        self.menuView.addAction(self.actionShowUsers)
        self.menuTools.addAction(self.actionEasyPPA)
        self.menuTools.addAction(self.actionEditSources)
        self.menuHelp.addAction(self.actionUpdateManifests)
        self.menuHelp.addAction(self.actionUpdateUserlists)

        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.setTitle("File")
        self.menuView.setTitle("View")
        self.menuTools.setTitle("Tools")
        self.menuHelp.setTitle("Help")
        self.actionExit.setText("Exit")
        self.actionOpen.setText("Open manifest")
        self.actionOpenUserList.setText("Open default userlist")

        self.actionSaveSnapshot.setText('Save')
        self.actionAbout.setText("About")
        self.actionEasyPPA.setText("Easy PPA")
        self.actionShow_missing.setText("Show missing pre-installed packages")
        self.actionEditSources.setText("Edit Sources")
        self.actionShowUsers.setText("Show non-default system users and groups")
        self.actionShow_Installed.setText("Show installed list")
        self.actionUpdateManifests.setText("Update manifest files")
        self.actionUpdateUserlists.setText("Update userlist files")

        font = QtGui.QFont()
        font.setPointSize(25)
        button_style = ("""
        QPushButton {
        border: 2px solid #555;
        border-radius: 30px;
        padding: 5px;
        background: qradialgradient(cx: 0.5, cy: -0.6,
        fx: -0.5, fy: 0.6,
        radius: 1.35, stop: 0 #fff, stop: 1 #888);
        }

        QPushButton:hover {
        background: qradialgradient(cx: 0.5, cy: 0.3,
        fx: 0.5, fy: 0.3,
        radius: 1.35, stop: 0 #fff, stop: 1 #888);
        min-width: 80px;
        }

        QPushButton:pressed {
        background: qradialgradient(cx: 0.7, cy: -0.7,
        fx: 0.7, fy: -0.7,
        radius: 1.35, stop: 0 #fff, stop: 1 #888);
        }""")
        self.btnReset = QPushButton()
        self.btnReset.setText("Automatic Reset", )
        self.btnReset.setFixedHeight(100)

        self.btnReset.setFont(font)
        self.btnReset.setStyleSheet(button_style)
        self.btnReset.setIcon(QtGui.QIcon('/usr/lib/resetter/data/icons/auto-reset-icon.png'))
        auto_text = "By choosing this option, resetter will automatically choose which packages to remove. " \
                    "Your home directory and user account will also be removed. Choose the custom reset option if you'd" \
                    " like to keep your user account and select which packages to remove. "
        self.btnReset.setToolTip(textwrap.fill(auto_text, 70))
        self.btnReset.setIconSize(QtCore.QSize(80, 80))
        self.btnReset.clicked.connect(self.warningPrompt)
        self.btnCustomReset = QPushButton()
        self.btnCustomReset.setText("Custom Reset")
        self.btnCustomReset.setFixedHeight(100)
        self.btnCustomReset.setFont(font)
        self.btnCustomReset.setStyleSheet(button_style)
        self.btnCustomReset.clicked.connect(self.customReset)
        self.btnCustomReset.setIcon(QtGui.QIcon('/usr/lib/resetter/data/icons/custom-reset-icon.png'))
        self.btnCustomReset.setIconSize(QtCore.QSize(80, 80))
        custom_text = "Choose this option if you would like to control how your system gets reset"
        self.btnCustomReset.setToolTip(textwrap.fill(custom_text, 70))

        self.btnEasyInstall = QPushButton(self)
        self.btnEasyInstall.setText("Easy Install")
        self.btnEasyInstall.setFixedHeight(100)
        self.btnEasyInstall.setFont(font)
        self.btnEasyInstall.setStyleSheet(button_style)
        self.btnEasyInstall.clicked.connect(self.easyInstall)
        self.btnEasyInstall.setIcon(QtGui.QIcon('/usr/lib/resetter/data/icons/easy-install-icon.png'))
        self.btnEasyInstall.setIconSize(QtCore.QSize(60, 60))
        custom_text = "Choose this option if you would like to control how your system gets reset."
        self.btnCustomReset.setToolTip(textwrap.fill(custom_text, 70))
        self.centralWidget = QWidget()
        self.os_version_label = QLabel()
        self.os_name_label = QLabel()
        self.app_version = QLabel()
        self.os_codename_label = QLabel()
        self.os_d_env_label = QLabel()
        self.os_info = self.d_env.os_info
        self.manifest_label = QLabel()
        self.userlist_label = QLabel()
        dse = QGraphicsDropShadowEffect()
        dse.setBlurRadius(4)
        self.manifest = self.d_env.manifest
        self.userlist = self.d_env.userlist
        self.user = self.d_env.user
        self.desktop = self.d_env.desktop_environment
        self.app_version.setText('version: {}'.format(UsefulTools().getVersion()))
        self.os_name_label.setText('OS Name: ' + self.os_info['ID'])
        self.os_version_label.setText('OS version: ' + self.os_info['RELEASE'])
        self.os_name_label.setGraphicsEffect(dse)
        self.os_codename_label.setText('codename: ' + self.os_info['CODENAME'])
        self.non_defaults = []
        self.image_label = QLabel()
        if self.manifest is not None:
            self.manifest_label.setText("Manifest: {}".format(self.manifest.split('/')[-1]))
        else:
            self.manifest_label.setText("Manifest: ???")

        if self.userlist is not None:
            self.userlist_label.setText("Userlist: {}".format(self.userlist.split('/')[-1]))
        else:
            self.userlist_label.setText("Userlist: ???")

        if self.desktop is not None:
            self.os_d_env_label.setText("Desktop Environment: {}".format(self.desktop.split('/')[-1]))
        else:
            self.userlist_label.setText("Desktop Environment: ???")

        logo = QtSvg.QSvgWidget('/usr/lib/resetter/data/icons/resetter-logo.svg')

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout2 = QVBoxLayout()
        self.verticalLayout2.addWidget(logo)
        self.verticalLayout2.addWidget(self.os_name_label)
        self.verticalLayout2.addWidget(self.os_version_label)
        self.verticalLayout2.addWidget(self.os_codename_label)
        self.verticalLayout2.addWidget(self.os_d_env_label)
        self.verticalLayout2.addWidget(self.manifest_label)
        self.verticalLayout2.addWidget(self.userlist_label)
        self.verticalLayout2.addWidget(self.app_version)

        self.verticalLayout2.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.image_label)
        self.verticalLayout.addLayout(self.verticalLayout2)
        self.verticalLayout.addWidget(self.btnEasyInstall)
        self.verticalLayout.addWidget(self.btnReset)
        self.verticalLayout.addWidget(self.btnCustomReset)
        self.centralWidget.setLayout(self.verticalLayout)
        self.setCentralWidget(self.centralWidget)

    def openManifest(self):
        try:
            manifest, _ = QFileDialog.getOpenFileName(self, 'Choose manifest',
                                                      'manifests', "manifest file (*.manifest)")
            if os.path.isfile(manifest):
                self.manifest = manifest
                self.manifest_label.setText('Manifest: {}'.format(str(manifest).split('/')[-1]))
        except IOError:
            pass

    def openUserList(self):
        try:
            userList, _ = QFileDialog.getOpenFileName(self, 'Choose a userlist',
                                                      'userlists', "userlist file (*)")
            if os.path.isfile(userList):
                self.userlist = userList
                self.userlist_label.setText('Userlist: {}'.format(str(userList).split('/')[-1]))
        except IOError:
            pass

    def searchLaunchpad(self):
        easyppa = EasyPPAInstall(self)
        easyppa.show()

    def editSourcesList(self):
        text = "Edit your repository list"
        sources_edit = SourceEdit(self)
        sources_edit.editSources("Repository List", text)
        sources_edit.show()

    def showMissings(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.getMissingPackages()
        if UsefulTools().lineCount('apps-to-install') > 0:
            text = "These were pre-installed packages that are missing but due for install"
            view_missing = AppView(self)
            view_missing.showView("apps-to-install", "Missing pre-installed packages", text, False)
            view_missing.show()
            QApplication.restoreOverrideCursor()
        else:
            QApplication.restoreOverrideCursor()
            UsefulTools().showMessage('No missing pre-installed packages', "Nothing to Show :-)",
                                      QMessageBox.Information)

    def getMissingPackages(self):
        self.getInstalledList()
        self.processManifest()
        try:
            black_list = ('linux-image', 'linux-headers', 'linux-generic', 'linux-kernel-generic',
                           'openjdk-7-jre', 'grub', 'linux-modules')
            with open("apps-to-install", "w") as output, open("installed", "r") as installed, \
                    open(self.manifest, "r") as man:
                diff = set(man).difference(installed)
                for line in diff:
                    if not any(s in line for s in black_list):
                        output.writelines(line)
        except Exception as e:
            UsefulTools().showMessage('Error', "Error generating removable package list. Please see details",
                                      QMessageBox.Information, "Error: {}".format(e))

    def save(self):
        self.getInstalledList()
        now = datetime.datetime.now()
        time = '{}{}{}'.format(now.hour, now.minute, now.second)
        name = 'snapshot - {}'.format(time)
        filename, extension = QFileDialog.getSaveFileName(
            self, 'Save Backup file', '/home/{}/{}'.format(self.user, name), filter='.rbf')
        try:
            with open('installed', 'r') as inst, open(filename + extension, 'w') as backup:
                for line in inst:
                    backup.writelines(line)
        except IOError:
            pass

    def getOldKernels(self):
        try:
            self.logger.info("getting old kernels...")

            cmd = subprocess.check_output(['bash', '/usr/lib/resetter/data/scripts/remove-old-kernels.sh'])
            results = cmd.decode().splitlines(True)
            with open("Kernels", "w") as kernels:
                for line in results:
                    kernels.writelines(line)
            self.logger.info("getOldKernels() completed")
        except subprocess.CalledProcessError as e:
            self.logger.error("Error: {}".format(e.output))
            UsefulTools().showMessage("Error", "Error: {}".format(e.ouput), QMessageBox.Critical)

    def getLocalUserList(self):
        try:
            self.logger.info("getting local users...")

            cmd = subprocess.check_output(['bash', '/usr/lib/resetter/data/scripts/get-users.sh'])
            result = cmd.decode().splitlines(True)
            black_list = ['root']
            with open("users", "w") as output:
                for line in result:
                    if not any(s in line for s in black_list):
                        output.writelines(line)
            self.logger.info("getLocalUserList() completed")

        except (subprocess.CalledProcessError, Exception) as e:
            print("an error has occured while getting users, please check the log file")
            self.logger.error("Error comparing files: ".format(e), exc_info=True)

    def findNonDefaultUsers(self):
        try:
            self.logger.info("getting local users...")
            cmd = subprocess.check_output(['bash', '-c', 'compgen -u'])
            black_list = []
            with open(self.userlist, 'r') as userlist, open('users', 'r') as normal_users:
                for user in userlist:
                    black_list.append(user.strip())
                    for n_users in normal_users:
                        black_list.append(n_users.strip())
            with open('non-default-users', 'w') as output:
                for line in cmd.decode().splitlines(True):
                    if not any(s in line for s in black_list):
                        self.non_defaults.append(line.strip())
                        output.writelines(line)
            self.logger.info("getLocalUserList() completed")

        except (subprocess.CalledProcessError, Exception) as e:
            print("an error has occured while getting users, please check the log file")
            self.logger.error("Error comparing files: ".format(e), exc_info=True)

    def warningPrompt(self):
        choice = QMessageBox.warning \
            (self, 'RESET EVERYTHING?',
             "Reset Everything? \n\n This will reset your " + self.os_info['DESCRIPTION'] + " installation to its "
                                                                                            "factory defaults. Local user accounts and home directories will also be removed."
                                                                                            "\n\nAre you sure you\'d like to continue?",
             QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.logger.warning("auto reset chosen")
            self.getInstalledList()
            self.getMissingPackages()
            if UsefulTools().lineCount('apps-to-remove') > 0:
                self.getLocalUserList()
                self.findNonDefaultUsers()
                view = AppView(self)
                tip = "These packages will be removed"
                view.showView("apps-to-remove", "Packages To Remove", tip, True)
                view.show()
                QApplication.restoreOverrideCursor()

            else:
                UsefulTools().showMessage("Nothing left to remove",
                                          "All removable packages have already been removed, there are no more packages left",
                                          QMessageBox.Information)
                QApplication.restoreOverrideCursor()

        else:
            self.logger.info("auto reset cancelled")

    def getInstalledList(self):
        try:
            self.logger.info("getting installed list...")
            p1 = subprocess.Popen(['dpkg', '--get-selections'], stdout=subprocess.PIPE, bufsize=1)
            result = p1.stdout
            with open("installed", "w") as output:
                for i, line in enumerate(result):
                    output.write(line.decode().split('\t', 1)[0] + '\n')
            self.logger.debug("installed list was generated with {} apps installed".format(i))
        except subprocess.CalledProcessError as e:
            self.logger.error("Error: {}".format(e.ouput), exc_info=True)
            UsefulTools().showMessage("Error", "Installed list failed to generate or may not be complete: {}".format(e),
                                      QMessageBox.Critical)

    def about(self):
        about = About(self)
        about.show()

    def processManifest(self):
        try:
            self.logger.info("processing updated manifest...")
            with open(self.manifest) as f, open('processed-manifest', 'w') as output:
                for line in f:
                    line = line.split('\t', 1)[0]
                    if line.endswith('\n'):
                        line = line.strip()
                    output.write(line + '\n')
            self.logger.info("manifest processing complete")
            self.compareFiles()
        except Exception as e:
            self.logger.error("Manifest processing failed [{}]".format(e))
            UsefulTools().showMessage("Manifest Processing failed", e, QMessageBox.Critical)

    def compareFiles(self):
        try:
            black_list = (['linux-image', 'linux-headers', 'linux-generic', 'ca-certificates', 'pyqt4-dev-tools',
                           'python-apt', 'python-aptdaemon', 'python-qt4', 'python-qt4-doc', 'libqt',
                           'pyqt4-dev-tools', 'openjdk', 'python-sip', 'gksu', 'grub', 'linux-modules',
                           'python-bs4'])
            with open("apps-to-remove", "w") as output, open("installed", "r") as installed, \
                    open(self.manifest, "r") as pman:
                diff = set(installed).difference(pman)
                for line in diff:
                    if not any(s in line for s in black_list):
                        output.writelines(line)
        except Exception as e:
            self.logger.error("Error comparing files [{}]".format(e), exc_info=True)
            UsefulTools().showMessage("Error", "Error generating removable package list. Please see details",
                                      QMessageBox.Critical, detail=e)

    def showInstalled(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.getInstalledList()
        viewInstalled = AppView(self)
        text = "These packages are currently installed on your system"
        viewInstalled.showView("installed", "Installed List", text, False)
        viewInstalled.show()
        QApplication.restoreOverrideCursor()

    def showNonDefaultUsers(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.getLocalUserList()
        self.findNonDefaultUsers()
        if len(self.non_defaults) > 0:
            ndu = AppView(self)
            text = "These are non default users"
            ndu.showView(self.non_defaults, 'Non-default users and groups list', text, False)
            ndu.show()
            QApplication.restoreOverrideCursor()
        else:
            QApplication.restoreOverrideCursor()
            UsefulTools().showMessage("No non-default users or groups on your system found", "Nothing to show :-)",
                                      QMessageBox.Information)

    def customReset(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.getMissingPackages()
        self.getLocalUserList()
        self.getOldKernels()
        self.findNonDefaultUsers()
        custom_reset = AppWizard(self)
        custom_reset.show()
        QApplication.restoreOverrideCursor()

    def easyInstall(self):
        self.easy = EasyInstaller()
        self.easy.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UiMainWindow()
    resetter_inst = 0
    for p in psutil.process_iter():
        if "resetter" in p.name():
            resetter_inst += 1
            if resetter_inst > 1:
                message = '{} is already running'.format(p.name())
                print(message)
                UsefulTools().showMessage('Already running', message, QMessageBox.Information)
                sys.exit(1)
    window.show()
    sys.exit(app.exec_())





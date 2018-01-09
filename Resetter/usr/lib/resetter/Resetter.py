#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This class is responsible for setting up the main ui and generating files that other functions will need
# to work with.
import logging
import lsb_release
import os
import subprocess
import sys
import textwrap
import shutil
from PyQt4 import QtCore, QtGui
import datetime
from aptsources import sourceslist

from AboutPage import About
from CustomReset import AppWizard
from PackageView import AppView
from Sources import SourceEdit
from SetEnvironment import Settings
from Singleton import SingleApplication
from EasyRepo import EasyPPAInstall
from EasyInstall import EasyInstaller

class UiMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(UiMainWindow, self).__init__(parent)
        self.d_env = Settings()
        QtGui.QApplication.setStyle("GTK")
        self.setWindowIcon(QtGui.QIcon('/usr/lib/resetter/data/icons/resetter-launcher.png'))
        self.error_msg = QtGui.QMessageBox()
        self.error_msg.setIcon(QtGui.QMessageBox.Critical)
        self.error_msg.setWindowTitle("Error")
        self.setWindowTitle(self.d_env.window_title)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.resize(850, 650)
        palette = QtGui.QPalette()
        self.setPalette(palette)
        self.menubar = QtGui.QMenuBar(self)
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuTools = QtGui.QMenu(self.menubar)
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.actionOpen = QtGui.QAction(self)
        self.actionSaveSnapshot = QtGui.QAction(self)
        self.actionSaveSnapshot.setStatusTip('Save a snapshot of currently installed packages. '
                                             'It is best to save this file in a removable drive for later use.')
        self.actionOpen.triggered.connect(self.openManifest)
        self.actionSaveSnapshot.triggered.connect(self.save)
        self.actionSaveSnapshot.setShortcut('Ctrl+S')

        self.actionExit = QtGui.QAction(self)
        self.actionExit.setShortcut('Ctrl+Q')
        self.actionExit.setStatusTip('Exit application')
        self.actionExit.triggered.connect(QtGui.qApp.quit)
        self.actionAbout = QtGui.QAction(self)
        self.actionAbout.triggered.connect(self.about)
        self.actionEasyPPA = QtGui.QAction(self)
        self.actionEasyPPA.triggered.connect(self.searchLaunchpad)
        self.actionEasyPPA.setStatusTip("The easiest way to get and install PPAs right from launchpad.net.")
        self.actionShow_Installed = QtGui.QAction(self)
        self.actionShow_Installed.setStatusTip('Show list of installed packages')
        self.actionShow_Installed.triggered.connect(self.showInstalled)
        self.actionShow_missing = QtGui.QAction(self)
        self.actionShow_missing.setStatusTip('Show removed packages from initial install')
        self.actionShow_missing.triggered.connect(self.showMissings)
        self.actionShowSources = QtGui.QAction(self)
        self.actionShowSources.setStatusTip('Show your repository list')
        self.actionShowSources.triggered.connect(self.showSourcesList)
        self.actionEditSources = QtGui.QAction(self)
        self.actionEditSources.setStatusTip('Edit your sources list')
        self.actionEditSources.triggered.connect(self.editSourcesList)
        self.actionShowUsers = QtGui.QAction(self)
        self.actionShowUsers.setStatusTip('View non-default system users')
        self.actionShowUsers.triggered.connect(self.showNonDefaultUsers)

        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSaveSnapshot)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuView.addAction(self.actionShow_missing)
        self.menuView.addAction(self.actionShowSources)
        self.menuView.addAction(self.actionShow_Installed)
        self.menuView.addAction(self.actionShowUsers)
        self.menuTools.addAction(self.actionEasyPPA)
        self.menuTools.addAction(self.actionEditSources)

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
        self.actionSaveSnapshot.setText('Save')
        self.actionAbout.setText("About")
        self.actionEasyPPA.setText("Easy PPA")
        self.actionShow_missing.setText("Show missing pre-installed packages")
        self.actionEditSources.setText("Edit Sources")
        self.actionShowUsers.setText("Show non-default system users and groups")
        self.actionShowSources.setText("Show system repository list")
        self.actionShow_Installed.setText("Show installed list")
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
        self.btnReset = QtGui.QPushButton(self)
        self.btnReset.setText("Automatic Reset", )
        self.btnReset.setFixedHeight(100)

        self.btnReset.setFont(font)
        self.btnReset.setStyleSheet(button_style)
        self.btnReset.setIcon(QtGui.QIcon('/usr/lib/resetter/data/icons/auto-reset-icon.png'))
        auto_text = "By choosing this option, resetter will automatically choose which packages to remove. " \
                    "Your home directory and user account will also be removed. Choose the custom reset option if you'd" \
                    " like to keep your user account and select which packages to remove. "
        self.btnReset.setToolTip(textwrap.fill(auto_text, 70))
        self.btnReset.setIconSize(QtCore.QSize(130, 150))
        self.btnReset.clicked.connect(self.warningPrompt)
        self.btnCustomReset = QtGui.QPushButton(self)
        self.btnCustomReset.setText("Custom Reset")
        #self.btnCustomReset.resize(614, 110)
        self.btnCustomReset.setFixedHeight(100)
        self.btnCustomReset.setFont(font)
        self.btnCustomReset.setStyleSheet(button_style)
        self.btnCustomReset.clicked.connect(self.customReset)
        self.btnCustomReset.setIcon(QtGui.QIcon('/usr/lib/resetter/data/icons/custom-reset-icon.png'))
        self.btnCustomReset.setIconSize(QtCore.QSize(80, 80))
        custom_text = "Choose this option if you would like to control how your system gets reset"
        self.btnCustomReset.setToolTip(textwrap.fill(custom_text, 70))

        self.btnEasyInstall = QtGui.QPushButton(self)
        self.btnEasyInstall.setText("Easy Install")
        # self.btnCustomReset.resize(614, 110)
        self.btnEasyInstall.setFixedHeight(100)
        self.btnEasyInstall.setFont(font)
        self.btnEasyInstall.setStyleSheet(button_style)
        self.btnEasyInstall.clicked.connect(self.easyInstall)
        self.btnEasyInstall.setIcon(QtGui.QIcon('/usr/lib/resetter/data/icons/easy-install-icon.png'))
        self.btnEasyInstall.setIconSize(QtCore.QSize(80, 80))
        custom_text = "Choose this option if you would like to control how your system gets reset."
        self.btnCustomReset.setToolTip(textwrap.fill(custom_text, 70))
        self.centralWidget = QtGui.QWidget()
        self.os_version_label = QtGui.QLabel()
        self.os_name_label = QtGui.QLabel()
        self.os_codename_label = QtGui.QLabel()
        self.os_info = self.d_env.os_info#lsb_release.get_lsb_information()
        self.manifest_label = QtGui.QLabel()
        dse = QtGui.QGraphicsDropShadowEffect();
        dse.setBlurRadius(4)
        self.manifest = self.d_env.manifest
        self.userlist = self.d_env.userlist
        self.user = self.d_env.user

        self.os_name_label.setText('OS Name: '+self.os_info['ID'])
        self.os_version_label.setText('OS version: '+self.os_info['RELEASE'])
        self.os_name_label.setGraphicsEffect(dse)
        self.os_codename_label.setText('codename: '+self.os_info['CODENAME'])
        self.image_label = QtGui.QLabel()
        if self.manifest is not None:
            m = self.manifest.split('/')[-1]
            self.manifest_label.setText("Using: {}".format(m))
        self.pixmap = QtGui.QPixmap("/usr/lib/resetter/data/icons/resetter-logo.png")
        self.pixmap2 = self.pixmap.scaled(650, 200)
        self.image_label.setPixmap(self.pixmap2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout2 = QtGui.QVBoxLayout()
        self.verticalLayout2.addWidget(self.os_name_label)
        self.verticalLayout2.addWidget(self.os_version_label)
        self.verticalLayout2.addWidget(self.os_codename_label)
        self.verticalLayout2.addWidget(self.manifest_label)
        self.verticalLayout2.setAlignment(QtCore.Qt.AlignRight)
        self.verticalLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.image_label)
        self.verticalLayout.addLayout(self.verticalLayout2)
        self.verticalLayout.addWidget(self.btnEasyInstall)
        self.verticalLayout.addWidget(self.btnReset)
        self.verticalLayout.addWidget(self.btnCustomReset)
        self.centralWidget.setLayout(self.verticalLayout)
        self.setCentralWidget(self.centralWidget)
        self.center()

    def getConfigFiles(self):  # future method for dealing with config files {disabled}
        conf = '/home/{}/.config'.format(self.user)
        x = 'apps-to-remove'
        for f in os.listdir(conf):
            shutil.rmtree(f, ignore_errors=True)
            file_path = os.path.join(conf, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    def openManifest(self):
        try:
            manifest = QtGui.QFileDialog.getOpenFileName(self, 'Choose manifest',
                                            'manifests', "manifest file (*.manifest)")
            if os.path.isfile(manifest):
                self.manifest = manifest
                manifest = str(manifest).split('/')[-1]
                self.manifest_label.setText('using: {}'.format(manifest))
        except IOError:
            pass

    def searchLaunchpad(self):
        easyppa = EasyPPAInstall(self)
        easyppa.show()

    def showSourcesList(self):
        sources = sourceslist.SourcesList()
        text = "This is your repository list"
        sources_view = AppView(self)
        sources_view.showView(sources, "Repository List", text, False)
        sources_view.show()

    def editSourcesList(self):
        text = "Edit your repository list"
        sources_edit = SourceEdit(self)
        sources_edit.editSources("Repository List", text)
        sources_edit.show()

    def showMissings(self):
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.getMissingPackages()
        if self.lineCount('apps-to-install') > 0:
            text = "These were pre-installed packages that are missing but due for install"
            view_missing = AppView(self)
            view_missing.showView("apps-to-install", "Missing pre-installed packages", text, False)
            view_missing.show()
            QtGui.QApplication.restoreOverrideCursor()
        else:
            QtGui.QApplication.restoreOverrideCursor()
            self.error_msg.setWindowTitle("No missing pre-installed packages")
            self.error_msg.setIcon(QtGui.QMessageBox.Information)
            self.error_msg.setText("Nothing to show :-)")
            self.error_msg.exec_()

    def getMissingPackages(self):
        self.getInstalledList()
        self.processManifest()
        try:
            if self.os_info['RELEASE'] == '17.3':
                word = "vivid"
            else:
                word = None
            black_list = (['linux-image', 'linux-headers', 'linux-generic', 'linux-kernel-generic',
                          'openjdk-7-jre', 'grub'])
            with open("apps-to-install", "w") as output, open("installed", "r") as installed, \
                    open(self.manifest, "r") as man:
                diff = set(man).difference(installed)
                for line in diff:
                    if word is not None and word in line:
                        black_list.append(line)
                    if not any(s in line for s in black_list):
                        output.writelines(line)
        except Exception as e:
            self.logger.error("Error comparing files [{}]".format(e), exc_info=True)
            self.error_msg.setText("Error generating removable package list. Please see details")
            self.error_msg.setDetailedText("Error: {}".format(e))
            self.error_msg.exec_()

    def save(self):
        self.getInstalledList()
        now = datetime.datetime.now()
        time = '{}{}{}'.format(now.hour, now.minute, now.second)
        name = 'snapshot - {}'.format(time)
        filename, extension = QtGui.QFileDialog.getSaveFileNameAndFilter(
            self, 'Save Backup file', '/home/{}/{}'.format(self.user, name), filter=self.tr('.rbf'))
        try:
            with open('installed', 'r') as inst, open(filename + extension, 'w') as backup:
                for line in inst:
                    backup.writelines(line)
        except IOError:
            pass

    def getOldKernels(self):
        try:
            self.logger.info("getting old kernels...")
            cmd = subprocess.Popen(['bash', '/usr/lib/resetter/data/scripts/remove-old-kernels.sh'],
                                   stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            cmd.wait()
            results = cmd.stdout
            with open("Kernels", "w") as kernels:
                for line in results:
                    kernels.writelines(line)
            self.logger.info("getOldKernels() completed")
        except subprocess.CalledProcessError, e:
            self.logger.error("Error: {}".format(e.output))
            self.error_msg.showMessage(str("Error: ", e.ouput))
            self.error_msg.exec_()
            print e.output

    def warningPrompt(self):
        choice = QtGui.QMessageBox.warning \
            (self, 'RESET EVERYTHING?',
             "Reset Everything? \n\n This will reset your " + str(self.os_info['DESCRIPTION']) + " installation to its "
             "factory defaults. Local user accounts and home directories will also be removed."
                "\n\nAre you sure you\'d like to continue?",
             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.logger.warning("auto reset chosen")
            self.getInstalledList()
            self.getMissingPackages()
            if self.lineCount("apps-to-remove") != 0:
                self.getLocalUserList()
                self.findNonDefaultUsers()
                view = AppView(self)
                tip = "These packages will be removed"
                view.showView("apps-to-remove", "Packages To Remove", tip, True)
                view.show()
                QtGui.QApplication.restoreOverrideCursor()

            else:
                self.error_msg.setWindowTitle("Nothing left to remove")
                self.error_msg.setIcon(QtGui.QMessageBox.Information)
                self.error_msg.setText(
                    "All removable packages have already been removed, there are no more packages left")
                QtGui.QApplication.restoreOverrideCursor()
                self.error_msg.exec_()
        else:
            self.logger.info("auto reset cancelled")

    def getInstalledList(self):
        try:
            self.logger.info("getting installed list...")
            p1 = subprocess.Popen(['dpkg', '--get-selections'], stdout=subprocess.PIPE, bufsize=1)
            result = p1.stdout
            tab = '\t'
            with open("installed", "w") as output:
                for i, line in enumerate(result):
                    line = line.split(tab, 1)[0]
                    output.write(line + '\n')
            self.logger.debug("installed list was generated with {} apps installed".format(i))
        except subprocess.CalledProcessError as e:
            self.logger.error("Error: {}".format(e.ouput), exc_info=True)
            self.error_msg.setText("Installed list failed to generate or may not be complete: {}".format(e))
            self.error_msg.exec_()

    def about(self):
        about = About(self)
        about.show()

    def processManifest(self):
        try:
            self.logger.info("processing updated manifest...")
            with open(self.manifest) as f, open("processed-manifest", "w") as output:
                for line in f:
                    tab = '\t'
                    line = line.split(tab, 1)[0]
                    if line.endswith('\n'):
                        line = line.strip()
                    output.write(line + '\n')
            self.logger.info("manifest processing complete")
            self.compareFiles()
        except Exception as e:
            self.logger.error("Manifest processing failed [{}]".format(e))
            self.error_msg.setText("Manifest processing failed")
            self.error_msg.setDetailedText("{}".format(e))
            self.error_msg.exec_()

    def lineCount(self, f_in):
        p = subprocess.Popen(['wc', '-l', f_in], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        result, err = p.communicate()
        if p.returncode != 0:
            raise IOError(err)
        return int(result.strip().split()[0])

    def compareFiles(self):
        try:
            black_list = (['linux-image', 'linux-headers', 'linux-generic', 'ca-certificates', 'pyqt4-dev-tools',
                          'python-apt', 'python-aptdaemon', 'python-qt4', 'python-qt4-doc', 'libqt',
                          'pyqt4-dev-tools', 'openjdk', 'python-sip', 'gksu', 'grub', 'python-mechanize', 'python-bs4'])
            with open("apps-to-remove", "w") as output, open("installed", "r") as installed, \
                    open(self.manifest, "r") as pman:
                diff = set(installed).difference(pman)
                for line in diff:
                    if not any(s in line for s in black_list):
                        output.writelines(line)
        except Exception as e:
            self.logger.error("Error comparing files [{}]".format(e), exc_info=True)
            self.error_msg.setText("Error generating removable package list. Please see details")
            self.error_msg.setDetailedText("Error: {}".format(e))
            self.error_msg.exec_()

    def showInstalled(self):
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.getInstalledList()
        viewInstalled = AppView(self)
        text = "These packages are currently installed on your system"
        viewInstalled.showView("installed", "Installed List", text, False)
        viewInstalled.show()
        QtGui.QApplication.restoreOverrideCursor()

    def showNonDefaultUsers(self):
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.getLocalUserList()
        self.findNonDefaultUsers()
        if len(self.non_defaults) > 0:
            ndu = AppView(self)
            text = "These are non default users"
            ndu.showView(self.non_defaults, 'Non-default users and groups list', text, False)
            ndu.show()
            QtGui.QApplication.restoreOverrideCursor()
        else:
            QtGui.QApplication.restoreOverrideCursor()
            self.error_msg.setIcon(QtGui.QMessageBox.Information)
            self.error_msg.setWindowTitle("No non-default users or groups on your system found")
            self.error_msg.setText("Nothing to show :-)")
            self.error_msg.exec_()

    def getLocalUserList(self):
        try:
            self.logger.info("getting local users...")
            cmd = subprocess.Popen(['bash', '/usr/lib/resetter/data/scripts/get-users.sh'], stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE)
            cmd.wait()
            result = cmd.stdout
            black_list = ['root']
            with open("users", "w") as output:
                for line in result:
                    if not any(s in line for s in black_list):
                        output.writelines(line)
            self.logger.info("getLocalUserList() completed")

        except (subprocess.CalledProcessError, Exception) as e:
            print ("an error has occured while getting users, please check the log file")
            self.logger.error("Error comparing files: ".format(e), exc_info=True)

    def findNonDefaultUsers(self):
        try:
            self.logger.info("getting local users...")
            cmd = subprocess.check_output(['bash', '-c', 'compgen -u'])
            black_list = []
            self.non_defaults = []
            with open(self.userlist, 'r') as userlist, open('users', 'r') as normal_users:
                for user in userlist:
                    black_list.append(user.strip())
                    for n_users in normal_users:
                        black_list.append(n_users.strip())
            with open('non-default-users', 'w') as output:
                for line in cmd.splitlines():
                    if not any(s in line for s in black_list):
                        self.non_defaults.append(line)
                        output.writelines(line + '\n')
            self.logger.info("getLocalUserList() completed")

        except (subprocess.CalledProcessError, Exception) as e:
            print ("an error has occured while getting users, please check the log file")
            self.logger.error("Error comparing files: ".format(e), exc_info=True)

    def customReset(self):
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.getMissingPackages()
        self.getLocalUserList()
        self.getOldKernels()
        self.findNonDefaultUsers()
        custom_reset = AppWizard(self)
        custom_reset.show()
        QtGui.QApplication.restoreOverrideCursor()

    def easyInstall(self):
        self.easy = EasyInstaller()
        self.easy.show()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

if __name__ == '__main__':
    key = 'Resetter'
    app = SingleApplication(sys.argv, key)
    window = UiMainWindow()
    if app.isRunning():
        message = QtGui.QMessageBox()
        message.setWindowTitle("Already Running")
        message.setText("{} is already running".format(key))
        print('{} is already running'.format(key))
        message.exec_()
        sys.exit(1)
    else:
        window.show()

    sys.exit(app.exec_())

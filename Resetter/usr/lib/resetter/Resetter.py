#!/usr/bin/python
import errno
import logging
import lsb_release
import os
import pwd
import shutil
import subprocess
import sys
import textwrap
from PyQt4 import QtCore, QtGui
from time import gmtime, strftime

from AboutPage import About
from CustomReset import AppWizard
from PackageView import AppView
from singleton import SingleApplication


class UiMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(UiMainWindow, self).__init__(parent)
        QtGui.QApplication.setStyle("GTK")
        self.setWindowIcon(QtGui.QIcon('/usr/lib/resetter/data/icons/resetter-launcher.png'))
        self.error_msg = QtGui.QMessageBox()
        self.error_msg.setIcon(QtGui.QMessageBox.Critical)
        self.error_msg.setWindowTitle("Error")
        self.euid = os.geteuid()
        self.detectRoot()
        self.directory = ".resetter/data"
        logdir = "/var/log/resetter"
        self.manifests = "/usr/lib/resetter/data/manifests"
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        if 'PKEXEC_UID' in os.environ:
            self.logger.debug('Program was called via pkexec')
            self.user = pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
            working_dir = '/home/{}'.format(self.user)
            os.chdir(working_dir)
        elif self.euid == 0 and 'PKEXEC_UID' not in os.environ:
            self.user = os.environ["SUDO_USER"]
            self.logger.debug("program was called via sudo or gksu")
        self.createDirs()
        os.chdir(self.directory)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.resize(850, 650)
        self.setFixedSize(850, 650)
        palette = QtGui.QPalette()

        self.setPalette(palette)
        self.menubar = QtGui.QMenuBar(self)
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuTools = QtGui.QMenu(self.menubar)
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.actionOpen = QtGui.QAction(self)
        self.actionSaveSnapshot = QtGui.QAction(self)
        self.actionSaveSnapshot.setStatusTip('Save a snapshot of currently installed packages')
        self.actionOpen.triggered.connect(self.openManifest)
        self.actionSaveSnapshot.triggered.connect(self.save)
        self.actionExit = QtGui.QAction(self)
        self.actionExit.setShortcut('Ctrl+Q')
        self.actionExit.setStatusTip('Exit application')
        self.actionExit.triggered.connect(QtGui.qApp.quit)
        self.actionAbout = QtGui.QAction(self)
        self.actionAbout.triggered.connect(self.about)
        self.actionShow_Installed = QtGui.QAction(self)
        self.actionShow_Installed.setStatusTip('Show list of installed packages')
        self.actionShow_Installed.triggered.connect(self.showInstalled)
        self.actionShow_missing = QtGui.QAction(self)
        self.actionShow_missing.setStatusTip('Show removed packages from initial install')
        self.actionShow_missing.triggered.connect(self.showMissings)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSaveSnapshot)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuTools.addAction(self.actionShow_missing)
        self.menuTools.addAction(self.actionShow_Installed)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.setTitle("File")
        self.menuTools.setTitle("Tools")
        self.menuHelp.setTitle("Help")
        self.actionExit.setText("Exit")
        self.actionOpen.setText("Open manifest")
        self.actionSaveSnapshot.setText('Save')
        self.actionAbout.setText("About")
        self.actionCustom_Reset = QtGui.QAction(self)
        self.menuTools.addAction(self.actionCustom_Reset)
        self.actionCustom_Reset.setText("Custom Reset")
        self.actionCustom_Reset.setStatusTip('Custom Reset')
        self.actionShow_missing.setText("Show missing pre-installed packages")
        self.actionCustom_Reset.triggered.connect(self.customReset)
        self.actionShow_Installed.setText("Show installed")
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
                    }

                    """)
        self.btnReset = QtGui.QPushButton(self)
        self.btnReset.setText("Automatic Reset", )
        self.btnReset.setFixedSize(614, 110)
        self.btnReset.setFont(font)
        self.btnReset.setStyleSheet(button_style)
        self.btnReset.setIcon(QtGui.QIcon('/usr/lib/resetter/data/icons/auto-reset-icon.png'))
        auto_text = "By choosing this option, resetter will automatically choose which packages to remove. " \
                    "Your home directory and user account will also be removed. Choose the custom reset option if you'd" \
                    "like to keep your user account and choose which packages to remove. "
        self.btnReset.setToolTip(textwrap.fill(auto_text, 70))
        self.btnReset.setIconSize(QtCore.QSize(130, 150))
        self.btnReset.clicked.connect(self.warningPrompt)
        self.btnCustomReset = QtGui.QPushButton(self)
        self.btnCustomReset.setText("Custom Reset")
        self.btnCustomReset.setFixedSize(614, 110)
        self.btnCustomReset.setFont(font)
        self.btnCustomReset.setStyleSheet(button_style)
        self.btnCustomReset.clicked.connect(self.customReset)
        self.btnCustomReset.setIcon(QtGui.QIcon('/usr/lib/resetter/data/icons/custom-reset-icon.png'))
        self.btnCustomReset.setIconSize(QtCore.QSize(80, 80))
        custom_text = "Choose this option if you would like to control how your system gets reset"
        self.btnCustomReset.setToolTip(textwrap.fill(custom_text, 70))
        self.centralWidget = QtGui.QWidget()
        self.os_version_label = QtGui.QLabel()
        self.os_name_label = QtGui.QLabel()
        self.os_codename_label = QtGui.QLabel()
        self.os_info = lsb_release.get_lsb_information()
        self.manifest_label = QtGui.QLabel()
        dse = QtGui.QGraphicsDropShadowEffect();
        dse.setBlurRadius(5)
        self.manifest = self.detectOS()
        self.os_name_label.setText('OS Name: '+self.os_info['ID'])
        self.os_version_label.setText('OS version: '+self.os_info['RELEASE'])
        self.os_name_label.setGraphicsEffect(dse)
        self.os_codename_label.setText('codename: '+self.os_info['CODENAME'])
        self.image_label = QtGui.QLabel()
        if self.manifest is not None:
            m = self.manifest.split('/')[-1]
            self.manifest_label.setText("Using: {}".format(m))
        self.pixmap = QtGui.QPixmap("/usr/lib/resetter/data/icons/resetter-logo.png")

        self.pixmap2 = self.pixmap.scaled(650, 226)
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
        self.verticalLayout.addWidget(self.btnReset)
        self.verticalLayout.addWidget(self.btnCustomReset)
        self.centralWidget.setLayout(self.verticalLayout)
        self.setCentralWidget(self.centralWidget)
        self.center()

    #create working directory with local user permmissions
    def createDirs(self):
        uidChange = pwd.getpwnam(self.user).pw_uid
        gidChange = pwd.getpwnam(self.user).pw_gid
        pidx = os.fork()
        if pidx == 0:
            try:
                os.setgid(gidChange)
                os.setuid(uidChange)
                if not os.path.exists(self.directory):
                    os.makedirs(self.directory)
                os.chdir(self.directory)
                data_dir = os.path.abspath("manifests")
                self.copy(self.manifests, data_dir)
            finally:
                os._exit(0)
        os.waitpid(pidx, 0)

    def detectRoot(self):
        if self.euid != 0:
            print "need to be root to run this program"
            self.logger.error("Not root, program exited")
            self.error_msg.setText("You need to be root to run this program")
            self.error_msg.setDetailedText("You won't be able to run this program unless you're root")
            self.error_msg.exec_()
            exit(1)

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

    def copy(self, source, destination):
        try:
            shutil.copytree(source, destination)
        except OSError as e:
            if e.errno == errno.ENOTDIR:
                shutil.copy(source, destination)
            else:
               pass

    def showMissings(self):
        self.getMissingPackages()
        text = "These were pre-installed packages that are missing but due for install"
        view_missing = AppView(self)
        view_missing.showView("apps-to-install", "Missing pre-installed packages", text, False)
        view_missing.show()

    def getMissingPackages(self):
        self.getInstalledList()
        self.processManifest()
        try:
            self.logger.info("generating install list")
            self.setCursor(QtCore.Qt.WaitCursor)
            cmd = subprocess.Popen(['grep', '-vxf', 'installed', 'processed-manifest'], stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE)
            cmd.wait()
            result = cmd.stdout
            if self.os_info['RELEASE'] == '17.3':
                word = "vivid"
            else:
                word = None
            black_list = ['linux-image', 'linux-headers', "openjdk-7-jre"]
            with open("apps-to-install", "w") as output:
                for line in result:
                    if word is not None and word in line:
                        black_list.append(line)
                    if not any(s in line for s in black_list):
                        output.writelines(line)
            self.logger.info("getmissingPackages() Completed")
            self.unsetCursor()
        except (subprocess.CalledProcessError, Exception) as e:
            self.unsetCursor()
            self.logger.error("Error comparing files [{}]".format(e), exc_info=True)
            self.error_msg.setText("Error generating removable package list. Please see details")
            self.error_msg.setDetailedText("Error: {}".format(e))
            self.error_msg.exec_()

    def save(self):
        self.getInstalledList()
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        file_name= "snapshot - {}".format(time)
        self.copy("installed", file_name)

    def detectOS(self):
        self.logger.info("OS is {}".format(self.os_info['DESCRIPTION']))
        if self.os_info['ID'] == ('LinuxMint'):
            if self.os_info['RELEASE'] == '17.3':
                self.setWindowTitle(self.os_info['ID'] + " Resetter")
                manifest = "manifests/mint-17.3-cinnamon.manifest"
                if os.path.isfile(manifest):
                    return manifest
                else:
                    self.manifestNotFound()
            elif self.os_info['RELEASE'] == '18':
                self.setWindowTitle(self.os_info['ID'] + " Resetter")
                manifest = "manifests/mint-18-cinnamon.manifest"
                if os.path.isfile(manifest):
                    return manifest
                else:
                    self.manifestNotFound()
            elif self.os_info['RELEASE'] == '18.1':
                self.setWindowTitle(self.os_info['ID'] + " Resetter")
                manifest = "manifests/mint-18.1-cinnamon.manifest"
                if os.path.isfile(manifest):
                    return manifest
                else:
                    self.manifestNotFound()
        elif self.os_info['ID'] == ('Ubuntu'):
            if self.os_info['RELEASE'] == '14.04':
                self.setWindowTitle(self.os_info['ID'] + " Resetter")
                manifest = 'manifests/ubuntu-14.04-unity.manifest'
                if os.path.isfile(manifest):
                    return manifest
                else:
                    self.manifestNotFound()
            elif self.os_info['RELEASE'] == '16.04':
                self.setWindowTitle(self.os_info['ID'] + " Resetter")
                manifest = 'manifests/ubuntu-16.04-unity.manifest'
                if os.path.isfile(manifest):
                    return manifest
                else:
                    self.manifestNotFound()

            elif self.os_info['RELEASE'] == '16.10':
                self.setWindowTitle(self.os_info['ID'] + " Resetter")
                manifest = 'manifests/ubuntu-16.10-unity.manifest'
                if os.path.isfile(manifest):
                    return manifest
                else:
                    self.manifestNotFound()
        else:
            self.error_msg.setText("Your distro isn't supported at the moment.")
            self.error_msg.setDetailedText(
                "If your distro is debian based, please send an email to gaining7@outlook.com for further support")
            self.error_msg.exec_()
            sys.exit(1)

    def manifestNotFound(self):
        self.error_msg.setText(
            "Manifest could not be found, please choose a manifest for your system if you have one")
        self.error_msg.setDetailedText("without a system manifest, this program won't function")
        self.error_msg.show()

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
             "factory defaults. local user accounts and home directories will also be removed."
                "\n\nAre you sure you\'d like to continue?",
             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            self.logger.warning("auto reset chosen")
            self.getInstalledList()
            self.getMissingPackages()
            if self.lineCount("apps-to-remove") != 0:
                self.getLocalUserList()
                view = AppView(self)
                tip = "These packages will be removed"
                view.showView("apps-to-remove", "Packages To Remove", tip, True)
                view.show()
            else:
                self.error_msg.setWindowTitle("Nothing left to remove")
                self.error_msg.setIcon(QtGui.QMessageBox.Information)
                self.error_msg.setText(
                    "All removable packages have already been removed, there are no more packages left")
                self.error_msg.exec_()
        else:
            self.logger.info("auto reset cancelled")

    def getInstalledList(self):
        try:
            self.logger.info("getting installed list...")
            self.setCursor(QtCore.Qt.BusyCursor)
            p1 = subprocess.Popen(['dpkg', '--get-selections'], stdout=subprocess.PIPE, bufsize=1)
            self.unsetCursor()
            result = p1.stdout
            i = 0
            with open("installed", "w") as output:
                for line in result:
                    i += 1
                    tab = '\t'
                    line = line.split(tab, 1)[0]
                    output.write(line + '\n')
            self.logger.debug("installed list was generated with {} apps installed".format(i))
        except (subprocess.CalledProcessError) as e:
            self.unsetCursor()
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
            self.unsetCursor()
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
            self.logger.info("comparing updated manifest and installed list...")
            self.setCursor(QtCore.Qt.WaitCursor)
            cmd = subprocess.Popen(['grep', '-vxf', 'processed-manifest', 'installed'], stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE)
            cmd.wait()
            result = cmd.stdout
            black_list = ['linux-image', 'linux-headers', 'ca-certificates', 'pyqt4-dev-tools',
                          'python-apt', 'python-aptdaemon', 'python-qt4', 'python-qt4-doc', 'libqt',
                          'pyqt4-dev-tools', 'openjdk', 'python-sip', 'snap', 'gksu', 'resetter']
            with open("apps-to-remove", "w") as output:
                for line in result:
                    if not any(s in line for s in black_list):
                        output.writelines(line)
            self.logger.info("CompareFiles() Completed")
            self.unsetCursor()
        except (subprocess.CalledProcessError, Exception) as e:
            self.unsetCursor()
            self.logger.error("Error comparing files [{}]".format(e), exc_info=True)
            self.error_msg.setText("Error generating removable package list. Please see details")
            self.error_msg.setDetailedText("Error: {}".format(e))
            self.error_msg.exec_()
            self.exit(1)

    def showInstalled(self):
        self.getInstalledList()
        viewInstalled = AppView(self)
        text = "These packages are currently installed on your system"
        viewInstalled.showView("installed", "Installed List", text, False)
        viewInstalled.show()

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
            print "an error has occured while getting users, please check the log file"
            self.logger.error("Error comparing files: ".format(e), exc_info=True)

    def customReset(self):
        self.getMissingPackages()
        self.getLocalUserList()
        self.getOldKernels()
        custom_reset = AppWizard(self)
        custom_reset.show()

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
        message.exec_()
        print('%s is already running' % key)
        sys.exit(1)
    else:
        window.show()

    sys.exit(app.exec_())

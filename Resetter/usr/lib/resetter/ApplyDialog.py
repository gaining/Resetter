#!/usr/bin/env python
# -*- coding: utf-8 -*-

import apt
import apt.package
import logging
import os
import subprocess
from PyQt4 import QtCore, QtGui
from AptProgress import UIAcquireProgress, UIInstallProgress
from InstallMissingDialog import Install


class ProgressThread(QtCore.QThread):

    conclude_op = QtCore.pyqtSignal()

    def __init__(self, file_in, install):
        QtCore.QThread.__init__(self)
        self.cache = apt.Cache(None)
        self.cache.open()
        self.file_in = file_in
        self.isDone = False
        self.error_msg = QtGui.QMessageBox()
        self.error_msg.setIcon(QtGui.QMessageBox.Critical)
        self.error_msg.setWindowTitle("Error")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.install = install

        self.aprogress = UIAcquireProgress(False)
        self.thread1 = QtCore.QThread()
        self.aprogress.moveToThread(self.thread1)
        self.thread1.started.connect(lambda: self.aprogress.play(0.0, False, ""))
        self.aprogress.finished.connect(self.thread1.quit)

        self.iprogress = UIInstallProgress()
        self.thread2 = QtCore.QThread()
        self.iprogress.moveToThread(self.thread2)
        self.thread2.started.connect(lambda: self.iprogress.play(0.0, ""))
        self.iprogress.finished.connect(self.thread2.quit)

        self.broken_list = []

    def lineCount(self, appfile):
        try:
            p = subprocess.Popen(['wc', '-l', appfile], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            result, err = p.communicate()
            return int(result.strip().split()[0])
        except subprocess.CalledProcessError:
            pass

    def removePackages(self):
        self.logger.info("Removing Programs")
        try:
            package = self.cache['snapd']
            package.mark_delete(True, True)
            self.logger.info("Keep Count before commit: {}".format(self.cache.keep_count))
            self.logger.info("Delete Count before commit: {}".format(self.cache.delete_count))
            self.logger.info("Broken Count before commit: {}".format(self.cache.broken_count))
            self.cache.commit(self.aprogress, self.iprogress)
            self.logger.info("Broken Count after commit: {}".format(self.cache.broken_count))
        except Exception as e:
            self.logger.error("Error: [{}]".format(e, exc_info=True))
            error = e.message
            text = "Package removal failed"
            self.emit(QtCore.SIGNAL('showError(QString, QString)'), error, text)

    def run(self):
        if self.lineCount(self.file_in) != 0:
            loading = 0
            x = float(100) / self.lineCount(self.file_in)
            with open(self.file_in) as packages:
                for pkg_name in packages:
                    try:
                        loading += x
                        self.pkg = self.cache[pkg_name.strip()]
                        self.pkg.mark_delete(True, True)
                        self.emit(QtCore.SIGNAL('updateProgressBar(int, bool)'), loading, self.isDone)
                    except (KeyError, SystemError) as error:
                        self.logger.error("{}".format(error))
                        if self.pkg.is_inst_broken or self.pkg.is_now_broken:
                            self.broken_list.append(self.pkg.fullname)
                            self.logger.critical("{}".format(error))
                            continue
                        else:
                            self.logger.critical("{}".format(error, exc_info=True))
                            error = error.message
                            text = "Package removal failed"
                            self.emit(QtCore.SIGNAL('showError(QString, QString)'), error, text)
                            break
                self.thread1.start()
                self.thread2.start()
                self.removePackages()
                self.conclude_op.emit()

        else:
            print "All removable packages are already removed"
            self.emit(QtCore.SIGNAL('updateProgressBar(int, bool)'), 100, True)


class Apply(QtGui.QDialog):
    def __init__(self, file_in, parent=None):
        super(Apply, self).__init__(parent)
        self.setMinimumSize(400, 250)
        self.file_in = file_in
        self.setWindowTitle("Applying")
        self.error_msg = QtGui.QMessageBox()
        self.error_msg.setIcon(QtGui.QMessageBox.Critical)
        self.error_msg.setWindowTitle("Error")
        self.buttonCancel = QtGui.QPushButton()
        self.buttonCancel.setText("Cancel")
        self.buttonCancel.clicked.connect(self.finished)
        self.progress = QtGui.QProgressBar()
        self.progress2 = QtGui.QProgressBar()
        self.progress2.setVisible(False)
        self.lbl1 = QtGui.QLabel()
        gif = os.path.abspath("/usr/lib/resetter/data/icons/chassingarrows.gif")
        self.movie = QtGui.QMovie(gif)
        self.movie.setScaledSize(QtCore.QSize(20, 20))
        self.pixmap = QtGui.QPixmap("/usr/lib/resetter/data/icons/checkmark.png")
        self.pixmap2 = self.pixmap.scaled(20, 20)
        verticalLayout = QtGui.QVBoxLayout(self)
        verticalLayout.addWidget(self.lbl1)
        verticalLayout.addWidget(self.progress)
        verticalLayout.addWidget(self.progress2)
        gridLayout = QtGui.QGridLayout()
        self.labels = {}
        for i in range(1, 7):
            for j in range(1, 3):
                self.labels[(i, j)] = QtGui.QLabel()
                self.labels[(i, j)].setMinimumHeight(20)
                gridLayout.addWidget(self.labels[(i, j)], i, j)
        gridLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.labels[(1, 2)].setText("Loading packages")
        self.labels[(2, 2)].setText("Removing packages")
        self.labels[(3, 2)].setText("Cleaning Up")
        self.labels[(4, 2)].setText("Installing packages")
        self.labels[(5, 2)].setText("Deleting Users")

        verticalLayout.addSpacing(20)
        verticalLayout.addLayout(gridLayout)
        verticalLayout.addWidget(self.buttonCancel, 0, QtCore.Qt.AlignRight)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.progressView = ProgressThread(self.file_in, False)
        self.connect(self.progressView, QtCore.SIGNAL("updateProgressBar(int, bool)"), self.updateProgressBar)
        self.connect(self.progressView.aprogress, QtCore.SIGNAL("updateProgressBar2(int, bool, QString)"), self.updateProgressBar2)
        self.connect(self.progressView.iprogress, QtCore.SIGNAL("updateProgressBar2(int, bool, QString)"), self.updateProgressBar2)
        self.connect(self.progressView, QtCore.SIGNAL("showError(QString, QString)"), self.showError)
        self.addUser()
        self.start()

    def addUser(self):
        try:
            self.logger.info("Adding default user...")
            p = subprocess.check_output(['bash', '/usr/lib/resetter/data/scripts/new-user.sh'])
            print p
            self.logger.info("Default user added")
        except subprocess.CalledProcessError as e:
            self.logger.error("unable to add user Error: {}".format(e.output))

    def updateProgressBar(self, percent, isdone):
        self.lbl1.setText("Loading Package List")
        self.progress.setValue(percent)
        self.labels[(1, 1)].setMovie(self.movie)
        self.movie.start()
        if isdone:
            self.movie.stop()

    def updateProgressBar2(self, percent, isdone, status):
        self.progress.setVisible(False)
        self.progress2.setVisible(True)
        self.labels[(1, 1)].setPixmap(self.pixmap2)
        self.lbl1.setText(status)
        self.labels[(2, 1)].setMovie(self.movie)
        self.movie.start()
        self.progress2.setValue(percent)
        if isdone:
            self.progressView.conclude_op.connect(self.finished)
            self.labels[(2, 1)].setPixmap(self.pixmap2)
            self.movie.stop()
            self.fixBroken()

    def fixBroken(self):
        self.labels[(3, 1)].setMovie(self.movie)
        self.movie.start()
        self.lbl1.setText("Cleaning up...")
        self.logger.info("Cleaning up...")
        self.progress2.setRange(0, 0)
        self.setCursor(QtCore.Qt.BusyCursor)
        self.process = QtCore.QProcess()
        self.process.finished.connect(self.onFinished)
        self.process.start('bash', ['/usr/lib/resetter/data/scripts/fix-broken.sh'])

    def onFinished(self, exit_code, exit_status):
        if exit_code or exit_status != 0:
            self.progress2.setRange(0, 1)
            self.logger.error("fixBroken() finished with exit code: {} and exit_status {}."
                              .format(exit_code, exit_status))
        else:
            self.progress2.setRange(0, 1)
            self.progress2.setValue(1)
            self.logger.debug("Cleanup finished with exit code: {} and exit_status {}.".format(exit_code, exit_status))
            self.labels[(3, 1)].setPixmap(self.pixmap2)
            self.unsetCursor()
            self.lbl1.setText("Done Cleanup")
            self.installPackages()

    def installPackages(self):
        self.logger.info("Starting installations...")
        self.labels[(4, 1)].setMovie(self.movie)
        if self.progressView.lineCount('apps-to-install') > 0:
            self.install = Install('apps-to-install', 'Installing packages', True)
            self.install.show()
            self.install.exec_()
            self.labels[(4, 1)].setPixmap(self.pixmap2)
            self.removeUsers()

        else:
            self.labels[(4, 1)].setPixmap(self.pixmap2)
            self.removeUsers()

    def start(self):
        self.progressView.start()

    @QtCore.pyqtSlot()
    def finished(self):
        self.logger.warning("finished apt operation")
        self.progressView.thread1.finished.connect(self.progressView.thread1.exit)
        self.progressView.thread2.finished.connect(self.progressView.thread2.exit)
        self.progressView.conclude_op.connect(self.progressView.exit)
        self.close()

    def removeUsers(self):
        self.logger.info("Starting user removal")
        self.labels[(5, 1)].setMovie(self.movie)
        with open('users') as f_in, open('non-default-users', 'r') as ndu, open("users-to-delete.sh", "w") as output:
            for line in f_in:
                line = ('userdel -rf ', line)
                output.writelines(line)
            for s_user in ndu:
                s_user = ('userdel -rf ', s_user)
                output.writelines(s_user)
        try:
            subprocess.Popen(['bash', 'users-to-delete.sh'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print "error: {}".format(e.output)
        else:
            self.movie.stop()
            self.labels[(5, 1)].setPixmap(self.pixmap2)
            self.lbl1.setText("Finished")
            self.showUserInfo()

    def getDependencies(self):
        try:
            self.setCursor(QtCore.Qt.WaitCursor)
            sq = '\''
            col = ':'
            with open("deplist2", "w") as dl:
                for pkg in self._cache.get_changes():
                    dependencies = pkg.versions[0].dependencies
                    for dependency in dependencies:
                        dependency = str(dependency).split(sq, 1)[1].split(sq, 1)[0]
                        if col in dependency:
                            dependency = dependency.split(col, 1)[0]
                        dl.write('{}\n'.format(dependency))
            with open("keep", "w") as output, open("deplist2", "r") as dl, open(self.file_in, "r") as apps:
                diff = set(dl).difference(apps)
                for line in diff:
                    output.writelines(line)
            self.unsetCursor()
        except Exception as e:
            self.unsetCursor()
            self.logger.error("getting Dependencies failed: {}".format(e))

    def rebootMessage(self):
        choice = QtGui.QMessageBox.information \
            (self, 'Please reboot to complete system changes',
             "Reboot now?",
             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            self.logger.info("system rebooted after package removals")
            os.system('reboot')
        else:
            self.logger.info("reboot was delayed.")

    def showMessage(self):
        msg = QtGui.QMessageBox(self)
        msg.setWindowTitle("Packages kept back")
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("These packages could cause problems if removed so they've been kept back.")
        text = "\n".join(self.progressView.broken_list)
        msg.setInformativeText(text)
        msg.exec_()

    def showError(self, error, m_type):
        msg = QtGui.QMessageBox(self)
        msg.setWindowTitle(m_type)
        msg.setIcon(QtGui.QMessageBox.Critical)
        text = "If you're running another package manager such as synaptic or USC please close them and try again."
        msg.setText(text)
        msg.setDetailedText(error)
        msg.exec_()

    def showUserInfo(self):
        msg = QtGui.QMessageBox(self)
        msg.setWindowTitle("User Credentials")
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("Please use these credentials the next time you log-in")
        msg.setInformativeText("USERNAME: <b>default</b><br/> PASSWORD: <b>NewLife3!</b>")
        msg.setDetailedText("This username was automatically created as your backup user")
        msg.exec_()
        self.logger.info("Credential message info shown")
        self.rebootMessage()


#!/usr/bin/python
import apt
import apt.package
import logging
import os
import subprocess
import sys
import time
from PyQt4 import QtCore, QtGui
from AptProgress import UIAcquireProgress, UIInstallProgress
import apt_pkg


class ProgressThread(QtCore.QThread):

    end_of_thread = QtCore.pyqtSignal()

    def __init__(self, file_in):
        QtCore.QThread.__init__(self)
        self.op_progress = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self._cache = apt.Cache(self.op_progress)
        self._cache.open()
        self.file_in = file_in
        self.isDone = False
        apt_pkg.init()

    def file_len(self):
        try:
            if os.path.exists(self.file_in):
                p = subprocess.Popen(['wc', '-l', self.file_in], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                result, err = p.communicate()
                return int(result.strip().split()[0])
            else:
                print "remove file does not exist"
        except subprocess.CalledProcessError as e:
            rc = e.returncode
            print "{}".format(e)
            if rc != 0:
                logging.log("error: {} {}".format(e, rc))

    def run(self):
        print self.file_len()
        if self.file_len() != 0:
            print("removing packages")
            loading = 0
            x = float(100) / self.file_len()
            with open(self.file_in) as packages:
                    for pkg_name in packages:
                        try:
                            loading += x
                            self.pkg = self._cache[pkg_name.strip()]
                            self.pkg.mark_delete(True, purge=True)
                            print "{} will be removed".format(self.pkg)
                            self.emit(QtCore.SIGNAL('updateProgressBar(int, bool)'), loading, self.isDone)
                        except KeyError as error:
                            self.logger.error("{}".format(error))
                            continue
                    self.logger.info("finished loading packages into cache")
                    self.isDone = True
                    self.emit(QtCore.SIGNAL('updateProgressBar(int, bool)'), 100, self.isDone)
        else:
            self.isDone = True
            print "All removable packages are already removed"
            self.emit(QtCore.SIGNAL('updateProgressBar(int, bool)'), 100, self.isDone)

class Apply(QtGui.QDialog):

    def __init__(self, file_in, parent=None):
        super(Apply, self).__init__(parent)
        self.setMinimumSize(400, 250)
        self.setWindowTitle("Applying")
        self.buttonCancel = QtGui.QPushButton()
        self.buttonCancel.setText("Cancel")
        self.progress = QtGui.QProgressBar(self)
        self.lbl1 = QtGui.QLabel()
        gif = os.path.abspath("/usr/lib/resetter/data/icons/chassingarrows.gif")
        self.movie = QtGui.QMovie(gif)
        self.movie.setScaledSize(QtCore.QSize(20, 20))
        self.pixmap = QtGui.QPixmap("/usr/lib/resetter/data/icons/checkmark.png")
        self.pixmap2 = self.pixmap.scaled(20, 20)
        verticalLayout = QtGui.QVBoxLayout(self)
        gridLayout = QtGui.QGridLayout()
        self.labels = {}
        for i in range(1, 6):
            for j in range(1, 3):
                self.labels[(i, j)] = QtGui.QLabel()
                self.labels[(i, j)].setMinimumHeight(20)
                gridLayout.addWidget(self.labels[(i, j)], i, j)
        gridLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.labels[(1, 2)].setText("Loading Apps")
        self.labels[(2, 2)].setText("Removing Apps")
        self.labels[(3, 2)].setText("Deleting Users")
        self.labels[(4, 2)].setText("Cleaning Up")
        verticalLayout.addWidget(self.lbl1)
        verticalLayout.addWidget(self.progress)
        verticalLayout.addSpacing(20)
        verticalLayout.addLayout(gridLayout)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.error_msg = QtGui.QMessageBox()
        self.error_msg.setIcon(QtGui.QMessageBox.Critical)
        self.error_msg.setWindowTitle("Error")
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        verticalLayout.addWidget(self.buttonCancel, 0, QtCore.Qt.AlignRight)
        self.file_in = file_in
        self.buttonCancel.clicked.connect(self.cancel)
        self.progressView = ProgressThread(self.file_in)
        self.connect(self.progressView, QtCore.SIGNAL("updateProgressBar(int, bool)"), self.updateProgressBar)
        self._cache = self.progressView._cache
        self.aprogress = UIAcquireProgress(self.progress, self.lbl1)
        self.iprogress = UIInstallProgress(self.progress, self.lbl1)
        self.start()

    @QtCore.pyqtSlot()
    def updateProgressBar(self, percent, isDone):
        self.lbl1.setText("Loading Package List")
        self.progress.setValue(percent)
        self.labels[(1,1)].setMovie(self.movie)

        self.movie.start()
        if isDone:
            self.buttonCancel.setDisabled(True)
            #self.progressView.end_of_thread.disconnect()
            #self.progressView = None
            self.movie.stop()
            self.labels[(1, 1)].setPixmap(self.pixmap2)
            self.removePackages()

    def start(self):
        #self.progressView.end_of_thread.connect(self.updateProgressBar)
        self.progressView.start()

    def cancel(self):
        self.logger.warning("Progress thread was cancelled")
        self.progressView.terminate()
        self.close()

    def removeUsers(self):
        self.logger.info("Starting user removal")
        self.labels[(3, 1)].setMovie(self.movie)
        self.movie.start()

        with open("users") as f_in, open("users-to-delete.sh", "w") as output:
            for line in f_in:
                line = ("userdel -rf ", line)
                output.writelines(line)
        try:
            subprocess.Popen(['bash', 'users-to-delete.sh'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError, e:
                print "error: {}".format(e.output)
        self.movie.stop()
        self.labels[(3, 1)].setPixmap(self.pixmap2)

    def removePackages(self):
        print "removing packages..."
        self.labels[(2,1)].setMovie(self.movie)
        self.movie.start()
        try:
            self.logger.info("Removing packages...")
            dep_list = "deplist"
            with open(dep_list, "w") as dl:
                for self.pkg in self._cache.get_changes():
                    if self.pkg != self.pkg.name:
                        dl.write('{}\n'.format(self.pkg))
            self.getDependencies()
            self.logger.info("Keep Count before commit: {}".format(self._cache.keep_count))
            self.logger.info("Delete Count before commit: {}".format(self._cache.delete_count))
            self._cache.commit(self.aprogress, self.iprogress)
            self.movie.stop()
            self.labels[(2, 1)].setPixmap(self.pixmap2)
            self.progress.setValue(int(100))
            self.addUser()
            self.fixBroken()
            self.removeUsers()
            self.showUserInfo()
            self.lbl1.setText("Finished")

        except Exception as arg:
            self.logger.error("Package removal failed [{}]".format(str(arg)))
            self.error_msg.setText("Something went wrong... please check details")
            self.error_msg.setDetailedText("Package removal failed [{}]".format(str(arg)))
            self.error_msg.exec_()

    def fixBroken(self):
        self.logger.info("Cleaning up..." )
        self.lbl1.setText("Cleaning up...")
        self.labels[(4, 1)].setMovie(self.movie)
        self.movie.start()
        self.setCursor(QtCore.Qt.BusyCursor)
        self.prcs = QtCore.QProcess()
        self.prcs.finished.connect(self.onFinished)
        self.prcs.start('bash', ['/usr/lib/resetter/data/scripts/fix-broken.sh'])
        self.prcs.waitForFinished(-1)

    def onFinished(self, exit_code, exit_status):
        if exit_code or exit_status != 0:
            self.logger.error("fixBroken() finished with exit code: {} and exit_status {}."
                              .format(exit_code, exit_status))
        else:
            self.logger.debug("Cleanup finished with exit code: {} and exit_status {}.".format(exit_code, exit_status))
            self.movie.stop()
            self.labels[(4, 1)].setPixmap(self.pixmap2)
            self.unsetCursor()
            self.lbl1.setText("Cleanup done.")

    def getDependencies(self):
        try:
            self.setCursor(QtCore.Qt.WaitCursor)
            cmd = subprocess.Popen(['grep', '-vxf', 'apps-to-remove', 'deplist'],
                                   stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            cmd.wait()
            result = cmd.stdout
            self.unsetCursor()
            with open("keep", "w") as output:
                for l in result:
                    try:
                        self.pkg = self._cache[l.strip()]
                        self.pkg.mark_keep()
                        output.writelines(l)
                    except KeyError as ke:
                        self.logger.error("{}".format(ke))
                        continue
        except subprocess.CalledProcessError as e:
            print "error: {}".format(e.output)
            self.logger.error("getting Dependencies failed: {}".format(e.output))

    def addUser(self):
        self.lbl1.setText("Creating Default user")
        try:
            self.logger.info("Adding default user...")
            p = subprocess.Popen(['bash', '/usr/lib/resetter/data/scripts/new-user.sh'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            p.wait()
            self.logger.info("Default user added")
        except subprocess.CalledProcessError as e:
            self.logger.error("unable to add user Error: {}".format(e.output))

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

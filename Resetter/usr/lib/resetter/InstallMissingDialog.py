#!/usr/bin/python
import apt
import apt.package
import logging
import os
import subprocess
import sys
import threading
import time
from PyQt4 import QtCore, QtGui

import apt_pkg
from AptProgress import UIAcquireProgress, UIInstallProgress


class ProgressThread(QtCore.QThread):
    def __init__(self, file_in, install):
        QtCore.QThread.__init__(self)
        self.op_progress = None
        self._cache = apt.Cache(self.op_progress)
        self._cache.open()
        self.file_in = file_in
        self.install = install
        self.isDone = False
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        QtGui.qApp.processEvents()
        self.resolver = apt.cache.ProblemResolver(self._cache)
        apt_pkg.init()
        self.broken_list = []

    def lineCount(self):
        try:
            p = subprocess.Popen(['wc', '-l', self.file_in], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            result, err = p.communicate()
            return int(result.strip().split()[0])
        except subprocess.CalledProcessError:
            pass

    def run(self):
        if self.lineCount() != 0:
            loading = 0
            x = float(100) / self.lineCount()
            with open(self.file_in) as packages:
                for pkg_name in packages:
                    try:
                        loading += x
                        self.pkg = self._cache[pkg_name.strip()]
                        if not self.install:
                            self.pkg.mark_delete(True, True)
                            print "{} will be removed".format(self.pkg)
                        else:
                            self.pkg.mark_install()
                            print "{} will be installed ".format(self.pkg.shortname)
                            self.emit(QtCore.SIGNAL('updateProgressBar(int, bool)'), loading, self.isDone)
                    except (KeyError, SystemError) as error:
                        # if resolver cannot find a way to cleanly install packages, move it to the broken list
                        if self.pkg.is_inst_broken:
                            self.broken_list.append(self.pkg.fullname)
                        self.logger.critical("{}".format(error))
                        continue
                self.emit(QtCore.SIGNAL('updateProgressBar(int, bool)'), 100, True)
        else:
            print "All removable packages are already removed"
            self.emit(QtCore.SIGNAL('updateProgressBar(int, bool)'), 100, True)


class Install(QtGui.QDialog):
    def __init__(self, file_in, action, action_type, parent=None):
        super(Install, self).__init__(parent)
        self.setMinimumSize(305, 100)
        self.file_in = file_in
        self.setWindowTitle("Working...")
        QtGui.QApplication.setStyle("GTK")
        self.error_msg = QtGui.QMessageBox()
        self.error_msg.setIcon(QtGui.QMessageBox.Critical)
        self.error_msg.setWindowTitle("Error")
        self.buttonCancel = QtGui.QPushButton()
        self.buttonCancel.setText("Cancel")
        self.buttonCancel.clicked.connect(self.cancel)
        self.progress = QtGui.QProgressBar(self)
        self.lbl1 = QtGui.QLabel()
        gif = os.path.abspath("/usr/lib/resetter/data/icons/chassingarrows.gif")
        self.movie = QtGui.QMovie(gif)
        self.movie.setScaledSize(QtCore.QSize(20, 20))
        self.pixmap = QtGui.QPixmap("/usr/lib/resetter/data/icons/checkmark.png")
        self.pixmap2 = self.pixmap.scaled(20, 20)
        verticalLayout = QtGui.QVBoxLayout(self)
        verticalLayout.addWidget(self.lbl1)
        verticalLayout.addWidget(self.progress)
        gridLayout = QtGui.QGridLayout()
        self.labels = {}
        for i in range(1, 3):
            for j in range(1, 3):
                self.labels[(i, j)] = QtGui.QLabel()
                self.labels[(i, j)].setMinimumHeight(20)
                gridLayout.addWidget(self.labels[(i, j)], i, j)
        gridLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.labels[(1, 2)].setText("Loading packages")
        self.labels[(2, 2)].setText(action)
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
        self.installProgress = ProgressThread(file_in, action_type)
        self.connect(self.installProgress, QtCore.SIGNAL("updateProgressBar(int, bool)"), self.updateProgressBar)
        self.install_cache = self.installProgress._cache
        self.aprogress = UIAcquireProgress(self.progress, self.lbl1)
        self.iprogress = UIInstallProgress(self.progress, self.lbl1)
        self.start()

    def updateProgressBar(self, percent, isdone):
        self.lbl1.setText("Loading Package List")
        self.progress.setValue(percent)
        self.labels[(1, 1)].setMovie(self.movie)
        self.movie.start()
        if isdone:
            self.labels[(1, 1)].setPixmap(self.pixmap2)
            self.movie.stop()
            self.labels[(2, 1)].setMovie(self.movie)
            self.movie.start()
            self.installPackages()

    def cancel(self):
        self.logger.warning("Progress thread was cancelled")
        self.installProgress.terminate()
        self.close()

    # experimental way of installing missing pre-installed packages n
    def installPackages(self):
        try:
            self.logger.info("treating Packages")
            self.movie.start()
            self.setCursor(QtCore.Qt.BusyCursor)
            self.install_cache.commit(self.aprogress, self.iprogress)
            self.progress.setValue(100)
            self.labels[(2, 1)].setPixmap(self.pixmap2)
            if len(self.installProgress.broken_list) > 0:
                self.showMessage()
            self.close()
            self.unsetCursor()
        except Exception as arg:
            self.logger.error("package install failed [{}]".format(str(arg)))
            print "Sorry, package install failed [{}]".format(str(arg))

    def start(self):
        self.installProgress.start()

    def showMessage(self):
        msg = QtGui.QMessageBox(self)
        msg.setWindowTitle("Packages kept back")
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("These packages could cause problems if installed so they've been kept back.")
        text = "\n".join(self.installProgress.broken_list)
        msg.setInformativeText(text)
        msg.exec_()

if __name__ == '__main__':
    file = "apps-to-install"
    app = QtGui.QApplication(sys.argv)
    install = Install(file, True)
    install.show()
    sys.exit(app.exec_())

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import apt
import apt.package
import logging
import os
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from AptProgress import UIAcquireProgress, UIInstallProgress
from Tools import UsefulTools


class ProgressThread(QtCore.QThread):
    end_of_threads = QtCore.pyqtSignal()
    start_op = QtCore.pyqtSignal(str, str)  # Error string transmitter
    start_op1 = QtCore.pyqtSignal(int, bool)  # Loading progress transmitter


    def __init__(self, file_in, install):
        QtCore.QThread.__init__(self)
        self.cache = apt.Cache(None)
        self.cache.open()
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
        self.resolver = apt.cache.ProblemResolver(self.cache)
        self.aprogress = UIAcquireProgress(False)
        self.thread1 = QtCore.QThread()
        self.aprogress.moveToThread(self.thread1)
        self.thread1.started.connect(lambda: self.aprogress.play(0.0, False, ""))
        self.aprogress.finished.connect(self.thread1.quit)

        self.thread2 = QtCore.QThread()
        self.iprogress = UIInstallProgress()
        self.iprogress.moveToThread(self.thread2)
        self.thread2.started.connect(lambda: self.iprogress.play(0.0, ""))
        self.iprogress.finished.connect(self.thread2.quit)
        self.broken_list = []

    def run(self):
        lc = UsefulTools().lineCount(self.file_in)
        if lc > 0:
            loading = 0
            x = float(100) / lc
            with open(self.file_in) as packages:
                for pkg_name in packages:
                    try:
                        loading += x
                        self.pkg = self.cache[pkg_name.strip()]
                        if not self.install:
                            self.pkg.mark_delete(True, True)
                            print ("{} will be removed".format(self.pkg))
                        else:
                            self.pkg.mark_install()
                            print ("{} will be installed ".format(self.pkg.shortname))
                        self.start_op1.emit(loading, self.isDone)
                    except (KeyError, SystemError) as error:
                        # if resolver cannot find a way to cleanly install packages, move it to the broken list
                        if self.pkg.is_inst_broken:
                            self.broken_list.append(self.pkg.fullname)
                            self.logger.critical("{}".format(error), exc_info=True)
                            continue
                        else:
                            text = "Error loading apps"
                            error2 = "Problems trying to install: {}\n{}".format(self.pkg.fullname, error.message)
                            self.logger.critical("{} {}".format(error, error2, exc_info=True))
                            self.start_op.emit(error2, text)
                            break
                self.thread1.start()
                self.thread2.start()
                self.installPackages()
                self.end_of_threads.emit()
        else:
            print ("All removable packages are already removed")
            self.start_op1.emit(100, True)

    def installPackages(self):
        try:
            self.logger.info("treating Packages")
            self.cache.commit(self.aprogress, self.iprogress)
        except Exception as e:
            self.logger.error("Action on package failed. Error: [{}]".format(e, exc_info=True))
            error = str(e)
            if self.install:
                text = "Package install failed"
                self.start_op.emit(error, text)
            else:
                text = "Package removal failed"
                self.start_op.emit(error, text)


class Install(QDialog):

    def __init__(self, file_in, action, action_type, parent=None):
        super(Install, self).__init__(parent)
        self.setMinimumSize(400, 100)
        self.file_in = file_in
        self.setWindowTitle("Working...")
        self.buttonCancel = QPushButton()
        self.buttonCancel.setText("Cancel")
        self.buttonCancel.clicked.connect(self.cancel)
        self.progress = QProgressBar()
        self.progress2 = QProgressBar()
        self.progress2.setVisible(False)
        self.lbl1 = QLabel()
        gif = os.path.abspath("/usr/lib/resetter/data/icons/chassingarrows.gif")
        self.movie = QtGui.QMovie(gif)
        self.movie.setScaledSize(QtCore.QSize(20, 20))
        self.pixmap = QtGui.QPixmap("/usr/lib/resetter/data/icons/checkmark.png")
        self.pixmap2 = self.pixmap.scaled(20, 20)
        verticalLayout = QVBoxLayout(self)
        verticalLayout.addWidget(self.lbl1)
        verticalLayout.addWidget(self.progress)
        verticalLayout.addWidget(self.progress2)
        gridLayout = QGridLayout()
        self.labels = {}
        for i in range(1, 3):
            for j in range(1, 3):
                self.labels[(i, j)] = QLabel()
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
        self.installProgress.start_op1.connect(self.updateProgressBar)
        self.installProgress.aprogress.run_op.connect(self.updateProgressBar2)
        self.installProgress.iprogress.run_op.connect(self.updateProgressBar2)
        self.installProgress.start_op.connect(self.showError)
        self.start()

    @QtCore.pyqtSlot(int, bool)
    def updateProgressBar(self, percent, isdone):
        self.lbl1.setText("Loading Package List")
        self.progress.setValue(percent)
        self.labels[(1, 1)].setMovie(self.movie)
        self.movie.start()
        if isdone:
            self.movie.stop()

    @QtCore.pyqtSlot(int, bool, str)
    def updateProgressBar2(self, percent, isdone, status):
        self.progress.setVisible(False)
        self.progress2.setVisible(True)
        self.labels[(1, 1)].setPixmap(self.pixmap2)
        self.lbl1.setText(status)
        self.labels[(2, 1)].setMovie(self.movie)
        self.movie.start()
        self.progress2.setValue(percent)
        if isdone:
            self.installProgress.end_of_threads.connect(self.finished)
            self.labels[(2, 1)].setPixmap(self.pixmap2)
            self.close()

    @QtCore.pyqtSlot(str, str)
    def showError(self, error, m_type):
        self.movie.stop()
        UsefulTools().showMessage(m_type, "Something went wrong, please check the details.", QMessageBox.Critical,
                                  error)
    def cancel(self):
        self.logger.warning("Progress thread was cancelled")
        self.installProgress.thread1.finished.connect(self.installProgress.thread1.exit)
        self.installProgress.thread2.finished.connect(self.installProgress.thread2.exit)
        self.installProgress.end_of_threads.connect(self.installProgress.exit)
        self.close()

    @QtCore.pyqtSlot()
    def finished(self):
        self.movie.stop()
        self.installProgress.thread1.finished.connect(self.installProgress.thread1.exit)
        self.installProgress.thread2.finished.connect(self.installProgress.thread2.exit)
        self.installProgress.end_of_threads.connect(self.installProgress.exit)
        self.installProgress.thread1 = None
        self.installProgress.thread2 = None
        self.installProgress = None
        self.close()

    def start(self):
        self.installProgress.start()


if __name__ == '__main__':
    file = "apps-to-install"
    app = QApplication(sys.argv)
    install = Install(file, True)
    install.show()
    sys.exit(app.exec_())


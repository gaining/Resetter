#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from apt.progress.base import InstallProgress, AcquireProgress
import os
import apt_pkg

apt_pkg.init_config()
apt_pkg.config.set("DPkg::Options::", "--force-confnew")
apt_pkg.config.set('APT::Get::Assume-Yes', 'true')
apt_pkg.config.set('APT::Get::force-yes', 'true')
os.putenv("DEBIAN_FRONTEND", "gnome")


class UIAcquireProgress(AcquireProgress, QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, other):
        AcquireProgress.__init__(self)
        QtCore.QObject.__init__(self)
        self.other = other

    def pulse(self, owner):
        done = False
        current_item = self.current_items + 1
        if current_item > self.total_items:
            current_item = self.total_items
        if self.other:
            status = "Updating source {} of {}".format(current_item, self.total_items)
            percent = (float(self.current_items) / self.total_items) * 100

        else:
            if self.current_cps == 0:
                status = "Downloading package {} of {} at - MB/s".format(current_item, self.total_items)
            else:
                status = "Downloading package {} of {} at {:.2f} MB/s".format(current_item, self.total_items,
                                                                        (float(self.current_cps) / 10 ** 6))
            percent = (((self.current_bytes + self.current_items) * 100.0) /
                       float(self.total_bytes + self.total_items))
        self.play(percent, done, status)
        return True

    def play(self, percent, done, status):
        self.emit(QtCore.SIGNAL('updateProgressBar2(int, bool, QString)'), percent, done, status)

    def stop(self):
        self.finished.emit()

    def done(self, item):
        print "{} [Downloaded]".format(item.shortdesc)

    def fail(self, item):
        print "{} Failed".format(item.shortdesc)

    def ims_hit(self, item):
        print "{} [Hit]".format(item.shortdesc)


class UIInstallProgress(InstallProgress, QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self):
        InstallProgress.__init__(self)
        QtCore.QObject.__init__(self)
        self.last = 0.0
        self.done = False
        self.message = QtGui.QMessageBox()
        self.message.setIcon(QtGui.QMessageBox.Information)
        self.message.setWindowTitle("Message")

    def status_change(self, pkg, percent, status):
        if self.last >= percent:
            return
        self.last = percent
        self.play(percent, status)

    def play(self, percent, status):
        self.emit(QtCore.SIGNAL('updateProgressBar2(int, bool, QString)'), percent, self.done, status)

    def pulse(self):
        return InstallProgress.pulse(self)

    def finish_update(self):
        self.done = True
        self.finished.emit()
        self.emit(QtCore.SIGNAL('updateProgressBar2(int, bool, QString)'), 100, self.done, "Finished")
        print "Finished"

    def processing(self, pkg, stage):
        print "starting {} stage for {}".format(stage, pkg)

    def conffile(self, current, new):
        print "new config file automatically accepted"

    def error(self, errorstr):
        print "ERROR: {}".format(errorstr)
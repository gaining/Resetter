#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import apt_pkg
from PyQt4 import QtGui
from apt.progress.base import InstallProgress, OpProgress, AcquireProgress

apt_pkg.init_config()
apt_pkg.config.set("DPkg::Options::", "--force-confnew")
apt_pkg.config.set('APT::Get::Assume-Yes', 'true')
apt_pkg.config.set('APT::Get::force-yes', 'true')
os.putenv("DEBIAN_FRONTEND", "gnome")


class UIOpProgress(OpProgress):
    def __init__(self, pbar):
        OpProgress.__init__(self)
        self.pbar = pbar

    def update(self, percent):
        self.pbar.setValue(int(percent))
        QtGui.qApp.processEvents()
        OpProgress.update(self, percent)

    def done(self):
        OpProgress.done(self)


class UIAcquireProgress(AcquireProgress):
    def __init__(self, pbar, status_label, other):
        AcquireProgress.__init__(self)
        self.pbar = pbar
        self.status_label = status_label
        self.percent = 0.0
        self.other = other

    def pulse(self, owner):
        current_item = self.current_items + 1
        if current_item > self.total_items:
            current_item = self.total_items
        if self.other:
            text = "Updating source {} of {}".format(current_item, self.total_items)
            percent = (float(self.current_items) / self.total_items) * 100
        else:
            text = "Downloading package {} of {} at {:.2f} MB/s".format(current_item, self.total_items,
                                                                        (float(self.current_cps) / 10 ** 6))
            percent = (((self.current_bytes + self.current_items) * 100.0) /
                       float(self.total_bytes + self.total_items))
        self.pbar.setValue(int(percent))
        self.status_label.setText(text)
        QtGui.qApp.processEvents()
        return True

    def start(self):
        QtGui.qApp.processEvents()

    def stop(self):
        self.status_label.setText("Finished")
        QtGui.qApp.processEvents()

    def done(self, item):
        print "{} [Downloaded]".format(item.shortdesc)
        QtGui.qApp.processEvents()

    def fail(self, item):
        print "{} Failed".format(item.shortdesc)

    def ims_hit(self, item):
        print "{} [Hit]".format(item.shortdesc)
        self.status_label.setText("{} [Hit]".format(item.shortdesc))
        QtGui.qApp.processEvents()


class UIInstallProgress(InstallProgress):
    def __init__(self, pbar, status_label):
        InstallProgress.__init__(self)
        self.pbar = pbar
        self.status_label = status_label
        self.last = 0.0
        os.putenv("DEBIAN_FRONTEND", "gnome")


    def status_change(self, pkg, percent, status):
        if self.last >= percent:
            return
        self.status_label.setText((status))
        self.pbar.setValue(int(percent))
        self.last = percent
        QtGui.qApp.processEvents()

    def pulse(self):
        QtGui.qApp.processEvents()
        return InstallProgress.pulse(self)

    def finish_update(self):
        pass

    def processing(self, pkg, stage):
        print "starting {} stage for {}".format(stage, pkg)

    def conffile(self, current, new):
        print "new config file automatically accepted"

    def error(self, errorstr):
        print "ERROR: {}".format(errorstr)

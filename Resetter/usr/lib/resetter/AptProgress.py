#!/usr/bin/python
from PyQt4 import QtCore, QtGui
from apt.progress.base import InstallProgress, OpProgress, AcquireProgress
import apt_pkg


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
    def __init__(self, pbar, status_label):
        AcquireProgress.__init__(self)
        self.pbar = pbar
        self.status_label = status_label
        self.percent = 0.0

    def pulse(self, owner):
        current_item = self.current_items + 1
        if current_item > self.total_items:
            current_item = self.total_items
        if self.current_cps > 0:
            text = (("Downloading file %(current)li of %(total)li with "
                      "%(speed)s/s") %
                    {"current": current_item,
                     "total": self.total_items,
                     "speed": apt_pkg.size_to_str(self.current_cps)})
        else:
            text = (("Downloading file %(current)li of %(total)li") %
                    {"current": current_item,
                     "total": self.total_items})
        self.status_label.setText(text)
        percent = (((self.current_bytes + self.current_items) * 100.0) /
                   float(self.total_bytes + self.total_items))
        self.pbar.setValue(int(percent))
        QtGui.qApp.processEvents()
        return True

    def start(self):
        QtGui.qApp.processEvents()

    def stop(self):
        self.status_label.setText("Finished downloading.")
        QtGui.qApp.processEvents()

    def done(self, item):
        print "[Fetched] %s" % item.shortdesc
        self.status_label.setText("[Fetched] %s" % item.shortdesc)
        QtGui.qApp.processEvents()

    def fail(self, item):
        print "[Failed] %s" % item.shortdesc

    def ims_hit(self, item):
        print "[Hit] %s" % item.shortdesc
        self.status_label.setText("[Hit] %s" % item.shortdesc)
        QtGui.qApp.processEvents()

    def media_change(self, media, drive):
        print "[Waiting] Please insert media '%s' in drive '%s'" % (
            media, drive)


class UIInstallProgress(InstallProgress):
    def __init__(self, pbar, status_label):
        InstallProgress.__init__(self)
        self.pbar = pbar
        self.status_label = status_label
        self.last = 0.0

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
        print "starting '%s' stage for %s" % (stage, pkg)

    def conffile(self, current, new):
        print "WARNING: conffile prompt: %s %s" % (current, new)

    def error(self, errorstr):
        print "ERROR: got dpkg error: '%s'" % errorstr

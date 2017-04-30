#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Single application instance uses a shared memory and key in order to allow only one instance of resetter to run.

from PyQt4 import QtCore, QtGui


class SingleApplication(QtGui.QApplication):

    def __init__(self, argv, key):
        QtGui.QApplication.__init__(self, argv)
        self._memory = QtCore.QSharedMemory(self)
        self._memory.setKey(key)
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(self._memory.errorString())

    def isRunning(self):
        return self._running

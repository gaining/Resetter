#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This class contains function tools that are often used by other classes
import sys
import os
import pwd

from PyQt4 import QtGui, QtCore


class UsefulTools(object):
    def __init__(self):
        self.version = '2.1.0'

    def showMessage(self, title, message, icon, detail=None):  # Method for showing various message types to user
        self.msg = QtGui.QMessageBox()
        self.msg.setIcon(icon)
        self.msg.setWindowTitle(title)
        self.msg.setText(message)
        if detail is not None:
            self.msg.setDetailedText(detail)
        self.msg.exec_()

    def getVersion(self):  # version getter
        return self.version

    def lineCount(self, file_path):  # line counter
        lc = open(file_path).readlines()
        return len(lc)
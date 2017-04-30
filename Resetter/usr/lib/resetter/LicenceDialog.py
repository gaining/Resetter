#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore


class Licence(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Licence, self).__init__(parent)
        self.resize(350, 300)
        self.setWindowTitle("Licence")
        licence_text = QtGui.QTextBrowser(self)
        close_button = QtGui.QPushButton(self)
        text = open('/usr/share/doc/resetter/copyright').read()
        licence_text.setPlainText(text)
        close_button.setText('close')
        close_button.clicked.connect(self.close)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(licence_text)
        self.verticalLayout.addWidget(close_button, 0, QtCore.Qt.AlignRight)

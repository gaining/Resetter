#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtCore, QtSvg
from LicenceDialog import Licence
from Tools import UsefulTools
from PyQt5.QtWidgets import *


class About(QDialog):
    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        self.resize(550, 385)
        self.setWindowTitle("About")

        logo = QtSvg.QSvgWidget('/usr/lib/resetter/data/icons/resetter-logo.svg')

        about_font = QtGui.QFont()
        about_font.setBold(True)
        about_label = QLabel(self)
        desc_label = QLabel(self)
        desc_label.setAlignment(QtCore.Qt.AlignCenter)
        desc_label.setWordWrap(True)
        cr_label = QLabel(self)
        cr_label.setAlignment(QtCore.Qt.AlignCenter)
        donate_label = QLabel(self)
        donate_label.setAlignment(QtCore.Qt.AlignCenter)
        donate_label.setWordWrap(True)
        more_label = QLabel(self)
        more_label.setAlignment(QtCore.Qt.AlignCenter)
        more_label.setWordWrap(True)
        donate_label.setToolTip("Right click to copy link")
        more_label.setToolTip("Right Click to copy link")
        version_label = QLabel(self)
        version_label.setAlignment(QtCore.Qt.AlignCenter)
        about_label.setAlignment(QtCore.Qt.AlignCenter)
        cr_text = u"© 2019 Jonathan Soivilus"
        desc_text = "Built With Python3/PyQt5\n\n " \
                    "This is a great utility software that will help you reset your Linux installation its stock state" \
                    " among other things."
        version = UsefulTools().getVersion()
        version_text = "Version: {}-stable".format(version)
        donate_text = 'If you liked my project, please ' \
                      '<a href="https://github.com/gaining/Resetter/blob/master/DONATE.md">Donate </a>'
        more_text = 'To find out more about this project, please visit my github:' \
                    ' <a href="https://github.com/gaining/resetter"> Resetter</a>'
        desc_label.setText(desc_text)
        cr_label.setText(cr_text)
        donate_label.setText(donate_text)
        more_label.setText(more_text)
        version_label.setText(version_text)
        self.close_button = QPushButton()
        self.close_button.setText("Close")
        self.close_button.setMaximumSize(QtCore.QSize(100, 30))
        self.close_button.clicked.connect(self.close)
        self.liscence_button = QPushButton(self)
        self.liscence_button.setText("License")
        self.liscence_button.clicked.connect(self.showLicence)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(logo)
        self.verticalLayout.addWidget(about_label)
        self.verticalLayout.addWidget(desc_label)
        self.verticalLayout.addWidget(donate_label)
        self.verticalLayout.addWidget(more_label)
        self.verticalLayout.addWidget(version_label)
        self.verticalLayout.addWidget(cr_label)
        self.verticalLayout.addWidget(self.close_button, 0, QtCore.Qt.AlignRight)
        self.verticalLayout.addWidget(self.liscence_button, 0, QtCore.Qt.AlignRight)


    def showLicence(self):
        lic = Licence(self)
        lic.show()

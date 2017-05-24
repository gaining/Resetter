#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import sys
import subprocess
import crypt
import random
import logging

class AccountDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(AccountDialog, self).__init__(parent)
        AccountDialog.resize(self, 375, 150)
        AccountDialog.setWindowTitle(self, "Set Custom user and password")
        self.buttonOk = QtGui.QPushButton(self)
        self.buttonOk.setText("OK")
        self.buttonCancel = QtGui.QPushButton(self)
        self.buttonCancel.setText("Cancel")
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font2 = QtGui.QFont()
        font2.setBold(True)
        font2.setPixelSize(20)
        font2.setWeight(75)
        self.textEditUser = QtGui.QLineEdit(self)
        self.textEditUser.setFocus()
        self.textEditUser.setFont(font2)
        self.textEditUser.setFixedWidth(280)
        self.textEditPassword = QtGui.QLineEdit(self)
        self.textEditPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.textEditPassword.setFixedWidth(280)
        self.textEditPassword.setFont(font2)
        self.label = QtGui.QLabel(self)
        self.label.setFont(font)
        self.label.setText("Please set your username and password")
        self.label.setWordWrap(True)
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setText("Password")
        self.label_3 = QtGui.QLabel(self)
        self.label_3.setText("Username")
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.label)
        self.h1 = QtGui.QHBoxLayout()
        self.h1.addWidget(self.label_2)
        self.h1.addWidget(self.textEditPassword)
        self.h2 = QtGui.QHBoxLayout()
        self.h2.setAlignment(QtCore.Qt.AlignRight)
        self.h2.addWidget(self.buttonCancel)
        self.h2.addWidget(self.buttonOk)
        self.h3 = QtGui.QHBoxLayout()
        self.h3.addWidget(self.label_3)
        self.h3.addWidget(self.textEditUser)
        self.verticalLayout.addLayout(self.h3)
        self.verticalLayout.addLayout(self.h1)
        self.verticalLayout.addLayout(self.h2)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.buttonOk.clicked.connect(self.custom_user)
        self.buttonCancel.clicked.connect(self.close)
        self.user = 'default'
        self.password = 'NewLife3!'

    def salt(self):
        saltchars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return random.choice(saltchars) + random.choice(saltchars)

    def custom_user(self):
        self.user = self.textEditUser.text()
        self.password = self.textEditPassword.text()
        hashed_pw = crypt.crypt(str(self.password), "$6$"+self.salt())

        new_user = "/usr/lib/resetter/data/scripts/new-user.sh"
        with open(new_user, "r") as f,  open("custom-user.sh", "w") as out:
            for line in f:
                if line.startswith("PASSWORD"):
                    #line = ("PASSWORD=""\'{}\'\n".format(hashed_pw))
                    line = ("PASSWORD=""\'{}\'\n".format(self.password))
                if line.startswith("USERNAME"):
                    line = ("USERNAME=""\"{}\"\n".format(self.user))
                out.write(line)
        self.close()

        try:
            subprocess.Popen(['bash', 'custom-user.sh'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            self.logger.info("Custom user creation complete")
        except subprocess.CalledProcessError, e:
            self.logger.error("unable to add custom user [{}]".format(e.output))
            print "error: {}".format(e.output)

    def getUser(self):
        return self.user

    def getPassword(self):
        return self.password


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    auth = AccountDialog()
    auth.show()
    sys.exit(app.exec_())

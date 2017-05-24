#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This class sets up distro specific settings and working directory

import errno
import logging
import lsb_release
import os
import pwd
import shutil
import sys
import sqlite3
from PyQt4 import QtGui


class Settings(object):

    def __init__(self):
        super(Settings, self).__init__()
        self.directory = ".resetter/data"
        self.os_info = lsb_release.get_lsb_information()
        self.euid = os.geteuid()
        self.error_msg = QtGui.QMessageBox()
        self.error_msg.setIcon(QtGui.QMessageBox.Critical)
        self.error_msg.setWindowTitle("Error")
        self.detectRoot()
        logdir = "/var/log/resetter"
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('/var/log/resetter/resetter.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.manifests = '/usr/lib/resetter/data/manifests'
        self.userlists = '/usr/lib/resetter/data/userlists'
        if 'PKEXEC_UID' in os.environ:
            self.user = pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
            working_dir = '/home/{}'.format(self.user)
            os.chdir(working_dir)
        elif self.euid == 0 and 'PKEXEC_UID' not in os.environ:
            self.user = os.environ["SUDO_USER"]
        self.createDirs()
        os.chdir(self.directory)

        self.manifest = self.detectOS()[0]
        self.userlist = self.detectOS()[1]
        self.window_title = self.detectOS()[2]
        self.filesExist(self.manifest, self.userlist)

    def detectRoot(self):  # root detection function
        if self.euid != 0:
            print "Need to be root to run this program"
            self.error_msg.setText("You need to be root to run this program")
            self.error_msg.setDetailedText("You won't be able to run this program unless you're root")
            self.error_msg.exec_()
            exit(1)

    def createDirs(self):
        uid_change = pwd.getpwnam(self.user).pw_uid
        gid_change = pwd.getpwnam(self.user).pw_gid
        pidx = os.fork()
        if pidx == 0:
            try:
                os.setgid(gid_change)
                os.setuid(uid_change)
                if not os.path.exists(self.directory):
                    os.makedirs(self.directory)
                os.chdir(self.directory)
                man_dir = os.path.abspath("manifests")
                userlists_dir = os.path.abspath("userlists")
                self.copy(self.manifests, man_dir)
                self.copy(self.userlists, userlists_dir)
            finally:
                os._exit(0)
        os.waitpid(pidx, 0)

    def copy(self, source, destination):
        try:
            shutil.copytree(source, destination)
        except OSError as e:
            if e.errno == errno.ENOTDIR:
                shutil.copy(source, destination)
            else:
               pass

    def detectOS(self):
        compat_os = (['LinuxMint', 'Ubuntu', 'elementary', 'Deepin'])
        compat_releases = (['17.3', '17.04', '18.1', '18', '14.04','16.04', '16.10', '0.4', '15.4'])
        if self.os_info['ID'] in compat_os and self.os_info['RELEASE'] in compat_releases:
            if self.os_info['ID'] == ('LinuxMint'):
                if self.os_info['RELEASE'] == '17.3':
                    windowTitle = self.os_info['ID'] + " Resetter"
                    manifest = "manifests/mint-17.3-cinnamon.manifest"
                    userlist = "userlists/mint-17.3-defaultuserlist"
                    return manifest, userlist, windowTitle

                elif self.os_info['RELEASE'] == '18':
                    windowTitle = self.os_info['ID'] + " Resetter"
                    manifest = "manifests/mint-18-cinnamon.manifest"
                    userlist = "userlists/mint-18.1-default-userlist"
                    return manifest, userlist, windowTitle

                elif self.os_info['RELEASE'] == '18.1':
                    windowTitle = self.os_info['ID'] + " Resetter"
                    manifest = 'manifests/mint-18.1-cinnamon.manifest'
                    userlist = 'userlists/mint-18.1-default-userlist'
                    return manifest, userlist, windowTitle

            elif self.os_info['ID'] == 'Ubuntu':
                if self.os_info['RELEASE'] == '14.04':
                    windowTitle = self.os_info['ID'] + " Resetter"
                    manifest = 'manifests/ubuntu-14.04-unity.manifest'
                    userlist = "userlists/ubuntu-14.04-default-userlist"
                    return manifest, userlist, windowTitle

                elif self.os_info['RELEASE'] == '16.04':
                    windowTitle = self.os_info['ID'] + " Resetter"
                    manifest = 'manifests/ubuntu-16.04-unity.manifest'
                    userlist = "userlists/ubuntu-16.04-default-userlist"
                    return manifest, userlist, windowTitle

                elif self.os_info['RELEASE'] == '16.10':
                    windowTitle = self.os_info['ID'] + " Resetter"
                    manifest = 'manifests/ubuntu-16.10-unity.manifest'
                    userlist = 'userlists/ubuntu-16.10-default-userlist'
                    return manifest, userlist, windowTitle

                elif self.os_info['RELEASE'] == '17.04':
                    windowTitle = self.os_info['ID'] + " Resetter"
                    manifest = 'manifests/ubuntu-17.04-unity.manifest'
                    userlist = 'userlists/ubuntu-17.04-default-userlist'
                    return manifest, userlist, windowTitle

            elif self.os_info['ID'] == 'elementary':
                if self.os_info['RELEASE'] == '0.4':
                    windowTitle = self.os_info['ID'] + " Resetter"
                    manifest = 'manifests/eos-0.4.manifest'
                    userlist = 'userlists/eos-0.4-default-userlist'
                    return manifest, userlist, windowTitle

            elif self.os_info['ID'] == 'Deepin':
                if self.os_info['RELEASE'] == '15.4':
                    windowTitle = self.os_info['ID'] + " Resetter"
                    manifest = 'manifests/deepin-15.4.manifest'
                    userlist = 'userlists/deepin-15.4-default-userlist'
                    return manifest, userlist, windowTitle
        else:
            self.error_msg.setText("Your distro ({}) isn't supported at the moment.".format(self.os_info['DESCRIPTION']))
            self.error_msg.setDetailedText(
                "If your distro is debian based, please send an email to gaining7@outlook.com for further support")
            self.error_msg.exec_()
            sys.exit(1)

    def filesExist(self, manifest, userlist):
        if not os.path.isfile(manifest):
            self.error_msg.setText(
                "Manifest could not be found, please choose a manifest for your system if you have one")
            self.error_msg.setDetailedText("without a system manifest, this program won't function")
            self.error_msg.exec_()
            self.error_msg.close()
        if not os.path.isfile(userlist):
            self.error_msg.setText(
                "userlist could not be found, features requiring this file will not work.")
            self.error_msg.setDetailedText("This is not a big issue")
            self.error_msg.exec_()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    about = Settings()
    sys.exit(app.exec_())
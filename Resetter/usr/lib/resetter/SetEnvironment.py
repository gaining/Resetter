#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This class sets up distro specific settings and working directory

import errno
import logging
import os
import platform
import pwd
import re
import shutil
import time
import urllib.request
from distutils.version import StrictVersion

import lsb_release
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup

from Tools import UsefulTools


class Settings(object):
    finished = QtCore.pyqtSignal()

    def __init__(self):
        super(Settings, self).__init__()
        self.directory = '.resetter/data'
        self.os_info = lsb_release.get_distro_information()
        self.euid = os.geteuid()
        self.version = UsefulTools().getVersion()
        self.checkForUpdate()
        self.detectRoot()
        logdir = '/var/log/resetter'

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
            self.user = pwd.getpwuid(int(os.environ['PKEXEC_UID'])).pw_name
            working_dir = '/home/{}'.format(self.user)
            os.chdir(working_dir)
        elif self.euid == 0 and 'PKEXEC_UID' not in os.environ:
            self.user = os.environ['SUDO_USER']
        else:
            self.user = pwd.getpwuid(os.getuid())[0]
        self.createDirs()
        os.chdir(self.directory)
        self.desktop_environment = self.detectDesktopEnviron()
        self.manifest = 'manifests/{}'.format(self.detectOS()[0])
        self.userlist = 'userlists/{}'.format(self.detectOS()[1])
        self.window_title = self.detectOS()[2]
        self.filesExist(self.manifest, self.userlist)

    def detectRoot(self):  # root detection function
        if self.euid != 0:
            print ("Need to be root to run this program")
            UsefulTools().showMessage("Permission Error", "You need to be root to run this program",
                                      QMessageBox.Warning,
                                      "You won't be able to run this program unless you're root, try running 'sudo resetter' from the terminal")
            exit(1)

    def detectDesktopEnviron(self):
        try:
            desktop_session = open("/home/{}/desktop_session".format(self.user)).readline()
        except IOError:
            pass
        else:
            return desktop_session.strip()

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
        apt_locations = ('/usr/bin/apt', '/usr/lib/apt', '/etc/apt', '/usr/local/bin/apt')
        if any(os.path.exists(f) for f in apt_locations):
            manifest = '_'.join((self.os_info['ID'], self.os_info['RELEASE'], self.desktop_environment,
                                 platform.architecture()[0], '.manifest'))
            userlist = '_'.join((self.os_info['ID'], self.os_info['RELEASE'], 'default-userlist',
                                 self.desktop_environment, platform.architecture()[0]))
            window_title = self.os_info['ID'] + ' Resetter'
            return manifest, userlist, window_title
        else:
            UsefulTools().showMessage("APT Not Found",
                             "APT could not be found, your distro does not appear to be Debian based.",
                             QMessageBox.Warning)
            exit(1)

    def checkForUpdate(self):
        splash_pix = QtGui.QPixmap('/usr/lib/resetter/data/icons/resetter-logo.svg')
        splash = QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint| QtCore.Qt.FramelessWindowHint)
        splash.setMask(splash_pix.mask())
        splash.show()
        start = time.time()
        while time.time() - start < 0.3:
            qApp.processEvents()
        try:
            page = urllib.request.urlopen('https://github.com/gaining/resetter/tags')
            soup = BeautifulSoup(page, 'html.parser')
            found_version = re.search('v(\d+\.)?(\d+\.)?(\d+)', str(soup.select('h4'))).group()[1:]
            current_version = StrictVersion(self.version)
            valid = self.validateSiteVersion(found_version)
            if valid is not None and valid > current_version:
                splash.close()
                msg = ("There's a new version of Resetter available.\n\n"
                                       "Grab Resetter v{} at "
                                       "github.com/gaining/Resetter/releases/latest".format(valid))
                UsefulTools().showMessage("Update Available", msg, QMessageBox.Information)
            else:
                if valid is not None:
                    print("Running most recent version of Resetter")
        except urllib.request.URLError:
            pass

    def validateSiteVersion(self, sitev):
        pattern = re.compile('^(\d+\.)?(\d+\.)?(\d+)')
        if sitev is not None:
            if pattern.fullmatch(sitev):
                return sitev
            else:
                return None

    def filesExist(self, manifest, userlist):
        if not os.path.isfile(manifest):
            self.manifest = None
            UsefulTools().showMessage("File Not Found",
                                      "Manifest could not be found, please choose a manifest for your system if you have one",
                                      QMessageBox.Critical, "without a system manifest, this program won't function")
        if not os.path.isfile(userlist):
            self.userlist = None
            UsefulTools().showMessage("File Not Found",
                                      "UserList could not be found",
                                      QMessageBox.Warning,
                                      "It isn't a really big deal")

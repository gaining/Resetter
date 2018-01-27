#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This class sets up distro specific settings and working directory

import errno
import logging
import lsb_release
import os
import pwd
import shutil
from PyQt4 import QtGui
import urllib2
from bs4 import BeautifulSoup
from distutils.version import StrictVersion
from AboutPage import About
from Tools import UsefulTools


class Settings(object):

    def __init__(self):
        super(Settings, self).__init__()
        self.directory = '.resetter/data'
        self.os_info = lsb_release.get_distro_information()
        self.euid = os.geteuid()
        self.version = About().getVersion()
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
        self.createDirs()
        os.chdir(self.directory)

        self.manifest = ("manifests/{}").format(self.detectOS()[0])
        self.userlist = ("userlists/{}").format(self.detectOS()[1])
        self.window_title = self.detectOS()[2]
        self.filesExist(self.manifest, self.userlist)

    def detectRoot(self):  # root detection function
        if self.euid != 0:
            print "Need to be root to run this program"
            UsefulTools().showMessage("Permission Error", "You need to be root to run this program",
                                      QtGui.QMessageBox.Warning,
                                      "You won't be able to run this program unless you're root, try running 'sudo resetter' from the terminal")
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
        apt_locations = ('/usr/bin/apt', '/usr/lib/apt', '/etc/apt', '/usr/local/bin/apt')
        if any(os.path.exists(f) for f in apt_locations):
            manifest = self.os_info['ID'] + self.os_info['RELEASE'] + '.manifest'
            userlist = self.os_info['ID'] + self.os_info['RELEASE'] + '-default-userlist'
            window_title = self.os_info['ID']
            return manifest, userlist, window_title
        else:
            UsefulTools().showMessage("Apt Not Found",
                             "Apt could not be found, Your distro does not appear to be Debian based, the.",
                             QtGui.QMessageBox.Warning)

    def checkForApt(self):
        apt_locations = ('/usr/bin/apt', '/usr/lib/apt', '/etc/apt', '/usr/local/bin/apt')
        if not any(os.path.exists(f) for f in apt_locations):
            self.showMessage("Apt Not Found",
                             "Apt could not be found, Your distro does not appear to be Debian based.",
                             QtGui.QMessageBox.Warning)

    def checkForUpdate(self):
        try:
            page = urllib2.urlopen('https://github.com/gaining/Resetter/tags')
            soup = BeautifulSoup(page, 'html.parser')
            versions = soup.find('span', attrs={'class': 'tag-name'})
            versions_tag = str(versions).strip()
            site_version = versions_tag[24:].split('-', 1)[0]
            current_version = StrictVersion(self.version)
            if site_version > current_version:
                self.error_msg.setIcon(QtGui.QMessageBox.Information)
                self.error_msg.setWindowTitle("Update Available")
                self.error_msg.setText("There's a new version of Resetter available.\n\n"
                                       "Grab Resetter v{} at "
                                       "https://github.com/gaining/Resetter/releases".format(site_version))
                self.error_msg.exec_()
            else:
                print("Running most recent version of Resetter")
        except urllib2.URLError:
            pass

    def filesExist(self, manifest, userlist):
        if not os.path.isfile(manifest):
            self.manifest = None
            UsefulTools().showMessage("File Not Found",
                                      "Manifest could not be found, please choose a manifest for your system if you have one",
                                      QtGui.QMessageBox.Critical, "without a system manifest, this program won't function")
        if not os.path.isfile(userlist):
            self.userlist = None
            UsefulTools().showMessage("File Not Found",
                                      "UserList could not be found",
                                      QtGui.QMessageBox.Warning,
                                      "It isn't a really big deal")

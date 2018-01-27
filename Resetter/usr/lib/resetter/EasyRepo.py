#!/usr/bin/env python
# -*- coding: utf-8 -*-
import apt
import lsb_release
import mechanize
import subprocess
import sys
import textwrap
from PyQt4 import QtCore, QtGui
from aptsources import sourceslist
from bs4 import BeautifulSoup

from AptProgress import UIAcquireProgress
from PackageView import AppView
from Tools import UsefulTools


class EasyPPAInstall(QtGui.QDialog):
    def __init__(self, parent=None):
        super(EasyPPAInstall, self).__init__(parent)
        self.setWindowTitle("Easy PPA Install")
        self.searchEditText = QtGui.QLineEdit()
        self.searchEditText.setPlaceholderText("Search for applications")
        self.searchEditText.setMaximumWidth(200)
        self.searchbutton = QtGui.QPushButton()
        self.error_msg = QtGui.QMessageBox()
        self.error_msg.setIcon(QtGui.QMessageBox.Critical)
        self.error_msg.setWindowTitle("Error")
        self.closebutton = QtGui.QPushButton()
        self.closebutton = QtGui.QPushButton()
        self.closebutton.setText('Close')
        self.closebutton.setMaximumWidth(150)
        self.closebutton.clicked.connect(self.close)
        self.searchbutton.setText("Search")
        self.searchbutton.setMaximumWidth(100)
        self.progressbar = QtGui.QProgressBar()
        self.lbl1 = QtGui.QLabel()
        self.buttonRefresh = QtGui.QPushButton()
        self.buttonRefresh.setText("Refresh sources")
        self.isWrittenTo = False
        self.table = QtGui.QTableWidget()
        self.configureTable(self.table)
        self.searchbutton.clicked.connect(lambda: self.searchForPPA(self.table))
        self.buttonRefresh.clicked.connect(self.updateSources)
        self.table.verticalHeader().hide()
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.addWidget(self.searchEditText)
        self.horizontalLayout.addWidget(self.searchbutton)
        self.horizontalLayout.setAlignment(QtCore.Qt.AlignRight)
        self.horizontalLayout2 = QtGui.QHBoxLayout()
        self.horizontalLayout2.setAlignment(QtCore.Qt.AlignRight)
        self.horizontalLayout2.addWidget(self.progressbar)
        self.horizontalLayout2.addWidget(self.buttonRefresh)
        self.horizontalLayout2.addWidget(self.closebutton)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.table)
        self.verticalLayout.addWidget(self.lbl1)
        self.verticalLayout.addLayout(self.horizontalLayout2)
        self.os_info = lsb_release.get_distro_information()
        self.sources = sourceslist.SourcesList()

        self.aprogress = UIAcquireProgress(True)
        self.thread1 = QtCore.QThread()
        self.aprogress.moveToThread(self.thread1)
        self.thread1.started.connect(lambda: self.aprogress.play(0.0, False, ""))
        self.aprogress.finished.connect(self.thread1.quit)
        self.connect(self.aprogress, QtCore.SIGNAL("updateProgressBar2(int, bool, QString)"), self.updateProgressBar2)

        self.ppa = []
        self.table_data = []

    def updateProgressBar2(self, percent, isdone, status):
        self.lbl1.setText(status)
        self.progressbar.setValue(percent)
        if isdone:
            self.installProgress.end_of_threads.connect(self.finished)
            self.labels[(2, 1)].setPixmap(self.pixmap2)
            self.close()

    def configureTable(self, table):
        table.setColumnCount(4)
        table.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem("Description"))
        table.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem("PPA"))
        table.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem("View Packages within this ppa"))
        table.setHorizontalHeaderItem(3, QtGui.QTableWidgetItem("Add this PPA to your sources"))
        table.setMinimumHeight(200)
        table.setMinimumWidth(700)
        header = table.horizontalHeader()
        header.setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)

    def searchForPPA(self, table):
        if self.isThereInternet() is False:
            self.close()
        else:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.searchbutton.setEnabled(False)
            del self.ppa[:]
            del self.table_data[:]
            browser = mechanize.Browser()
            browser.set_handle_robots(False)
            browser.open('https://launchpad.net/')
            browser.addheaders = [("User-agent", "Mozilla/5.0")]
            browser.select_form(nr=0)
            search_string = self.searchEditText.text()
            found_links = []
            browser['field.text'] = search_string  # use the proper input type=text name
            browser.submit()
            match = "+archive"
            exclude = (["+packages", "+build", "+sourcepub"])

            for link in browser.links():
                if not any(s in link.url for s in exclude) and match in link.url:
                    found_links.append(link)
                    QtGui.qApp.processEvents()
            r = len(found_links)
            if r == 0:
                self.lbl1.setText("No results found")
            else:
                self.lbl1.setText("Found {} results".format(r))

            table.setRowCount(r)
            self.displayLinks(found_links, table, browser)
            QtGui.QApplication.restoreOverrideCursor()
            self.searchbutton.setEnabled(True)

    def updateSources(self):
        self.buttonRefresh.setEnabled(False)
        cache = apt.Cache()
        cache.update(self.aprogress)
        self.buttonRefresh.setEnabled(True)
        self.lbl1.setText("Update Complete!")
        cache.close()

    def displayLinks(self, found_links, table, browser):
        loading = 0
        x = float(100) / len(found_links) if len(found_links) != 0 else 0
        try:
            for i, link in enumerate(found_links):
                desc = QtGui.QTableWidgetItem()
                ppa = QtGui.QTableWidgetItem()
                buttonAddPPA = QtGui.QPushButton()
                buttonAddPPA.setText("Install this PPA")
                buttonAddPPA.clicked.connect(lambda: self.addPPA(self.ppa))
                buttonPackageDetails = QtGui.QPushButton()
                buttonPackageDetails.setText("View packages")
                buttonPackageDetails.setEnabled(True)
                buttonPackageDetails.clicked.connect(lambda: self.showPackages(self.table_data))
                htmltext = browser.open(link.url).read()
                soup = BeautifulSoup(htmltext, 'html.parser')
                ppaTag = soup.find('strong', attrs={'class': 'ppa-reference'})
                if ppaTag is not None:
                    ppa_name = ppaTag.text.strip()
                    ppa.setText(ppa_name)
                b = QtCore.QByteArray.fromPercentEncoding(link.text)
                text = b.data().decode('utf8')
                desc.setText(textwrap.fill(text, 20))
                table.setItem(i, 0, desc)
                QtGui.qApp.processEvents()
                table.setItem(i, 1, ppa)
                QtGui.qApp.processEvents()
                table.setCellWidget(i, 2, buttonPackageDetails)
                QtGui.qApp.processEvents()
                table.setCellWidget(i, 3, buttonAddPPA)
                QtGui.qApp.processEvents()
                repo = soup.find('pre', attrs={'class': 'wrap'})
                if repo is not None:
                    repo_name = repo.text.strip()
                raw = soup.find('code')
                if raw is not None:
                    raw_key = raw.text.strip()
                select_node = soup.findAll('select', attrs={'name': 'field.series_filter'})
                if select_node is not None:
                    self.isCompatible(select_node, repo_name, raw_key)
                sauce = soup.find('table', attrs={'class': 'listing sortable'})
                if sauce is not None:
                    self.getTableData(sauce)
                loading += x
                self.progressbar.setValue(int(loading))
                QtGui.qApp.processEvents()
        except Exception as e:
            QtGui.QApplication.restoreOverrideCursor()
            self.error_msg.setText("Error, please try again.")
            self.error_msg.setDetailedText("If this keeps happening, it means easy repo stumbled upon an empty or "
                                           "forbidden link. You might need to change your search string")
            self.error_msg.exec_()

    def isThereInternet(self):
        try:
            mechanize.urlopen('http://google.com', timeout=1)
        except mechanize.URLError as e:
            print "There is no internet: {}".format(e)
            self.error_msg.setText("You are not connected to the internet")
            self.error_msg.setDetailedText("This feature will not work without an internet connection. ")
            self.error_msg.exec_()
            return False
        else:
            return True

    def codeName(self):
        xenial_fam = (['serena', 'sarah', 'loki', 'sonya'])
        if self.os_info['CODENAME'] == 'rosa':
            return 'trusty'
        elif self.os_info['CODENAME'] in xenial_fam:
            return 'xenial'
        else:
            return self.os_info['CODENAME']

    def isCompatible(self, node, repo, raw):
        options = []
        compatible = bool
        signing_key = str(raw[6:]).split('<', 1)[0]
        if node:
            for option in node[0].findAll('option'):
                option = option.text.strip().lower()
                options.append(option)
                if self.codeName() in options:
                    compatible = True
                else:
                    compatible = False
        result = [repo, compatible, signing_key]
        self.ppa.append(result)

    def addPPA(self, ppa):
        button = QtGui.qApp.focusWidget()
        index = self.table.indexAt(button.pos())
        if index.isValid() and ppa[index.row()][1]:
            try:
                QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                x = str(ppa[index.row()])
                y = str(x[7:]).split(' ', 1)[0]
                entry = ('deb', y, self.codeName(), ['main'])
                self.sources.add(*entry)
                self.sources.save()
                p = subprocess.check_output(
                    ['apt-key', 'adv', '--keyserver', 'keyserver.ubuntu.com', '--recv-keys', ppa[index.row()][2]]
                )
                print p
                QtGui.QApplication.restoreOverrideCursor()
            except Exception as e:
                QtGui.QApplication.restoreOverrideCursor()
                UsefulTools().showMessage("Unable to fetch PPA key", "Error: {}".format(e), QtGui.QMessageBox.Critical)
            else:
                UsefulTools().showMessage("PPA added", "This ppa has been successfully added to your sources list",
                                  QtGui.QMessageBox.Information)
        else:
            UsefulTools().showMessage("PPA not compatible", "This PPA is not compatible with your system because it's "
                                                            "not available for {}".format(self.os_info['DESCRIPTION']),
                                      QtGui.QMessageBox.Information)
    def getTableData(self, sauce):
        pasta = []
        for i in sauce.select('tr'):
            data = i.select('td')
            if data:
                package = data[0].text.strip()
                version = ' '.join(data[1].text.strip().split())
                pasta_sauce = "{}: {}".format(package, version)
                pasta.append(pasta_sauce)
        self.table_data.append(pasta)

    def showPackages(self, sauce):
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        button = QtGui.qApp.focusWidget()
        index = self.table.indexAt(button.pos())
        if index.isValid():
            available = AppView(self)
            text = "These packages are available from the selected ppa"
            if len(sauce) >= index.row():
                available.showView(sauce[index.row()], "PPA Packages", text, False)
                available.show()
        QtGui.QApplication.restoreOverrideCursor()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    about = EasyPPAInstall()
    about.show()
    sys.exit(app.exec_())

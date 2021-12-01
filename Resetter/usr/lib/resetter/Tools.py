#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This class contains function tools that are often used by other classes


import difflib
import urllib.request

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup


class UsefulTools(object):

    def __init__(self):
        self.version = '3.0.0'

    def showMessage(self, title, message, icon, detail=None):  # Method for showing various message types to user
        self.msg = QMessageBox()
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

    def getKeyByValue(self, dictionary, item):
        for key, val in dictionary.items():
            if item == val:
                return key

    def searchItem(self, model, view, label, font, font2, mode, search_string):
        if mode:
            items = model.findItems(search_string, QtCore.Qt.MatchStartsWith)
        else:
            items = model.findItems(search_string, QtCore.Qt.MatchContains or QtCore.Qt.MatchStartsWith)
        if len(items) > 0:
            for item in items:
                if search_string:
                    case = {}
                    for entry in items:
                        case = {entry.text(): difflib.SequenceMatcher(None, entry.text(), search_string).ratio()}
                    pop_item1 = max(case.values())
                    pop_item2 = self.getKeyByValue(case, pop_item1)
                    if pop_item2 == item.text():
                        item.setEnabled(True)
                        model.takeRow(item.row())
                        model.insertRow(0, item)
                        if pop_item1 == 1.0:
                            item.setFont(font)
                            label.clear()
                if len(search_string) == 0:
                    label.clear()
                    item.setFont(font2)
            view.scrollToTop()
        else:
            label.setText("Package doesn't exist")
        view.show()

    def removeItems(self, model):
        for row in range(model.rowCount()):
            item = model.item(row)
            if item and item.checkState() == QtCore.Qt.Checked:
                model.removeRow(row)
                self.removeItems()

    def updateFiles(self, d_name):  # Manifest and Userlist grabber
        try:
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            page = urllib.request.urlopen(
                'https://github.com/gaining/Resetter/tree/master/Resetter/usr/lib/resetter/data/' + d_name)
            soup = BeautifulSoup(page, 'html.parser', from_encoding=page.info().get_param('charset'))
            data = soup.findAll('tr', attrs={'class': 'js-navigation-item'})
            for link in data:
                real_link = link.findAll('a')
                for a in real_link:
                    if 'blob' in str(a):
                        fname = str(a['href']).split('/')[-1]
                        print(fname)
                        file_data = urllib.request.urlopen(
                            "https://raw.githubusercontent.com/gaining/Resetter/master/Resetter"
                            "/usr/lib/resetter/data/" + d_name + "/" + fname)
                        output = file_data.read().decode()
                        with open(d_name + "/" + fname, 'w') as f:
                            f.write(output)
        except urllib.request.URLError as e:
            QApplication.restoreOverrideCursor()
            UsefulTools().showMessage("Failed", "Could not update " + d_name + " " + str(e.reason),
                                      QMessageBox.Critical)
        else:
            QApplication.restoreOverrideCursor()
            UsefulTools().showMessage("Done!", d_name + " directory has been updated",
                                      QMessageBox.Information)


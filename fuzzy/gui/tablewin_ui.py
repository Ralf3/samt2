# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tablewin.ui'
#
# Created: Wed Nov 18 13:59:40 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_tablewin(object):
    def setupUi(self, tablewin):
        tablewin.setObjectName(_fromUtf8("tablewin"))
        tablewin.resize(822, 262)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("icons/area.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        tablewin.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(tablewin)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.table = QtGui.QTableWidget(self.centralwidget)
        self.table.setColumnCount(8)
        self.table.setObjectName(_fromUtf8("table"))
        self.table.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(7, item)
        self.verticalLayout.addWidget(self.table)
        tablewin.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(tablewin)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        tablewin.setStatusBar(self.statusbar)

        self.retranslateUi(tablewin)
        QtCore.QMetaObject.connectSlotsByName(tablewin)

    def retranslateUi(self, tablewin):
        tablewin.setWindowTitle(_translate("tablewin", "SAMT Fuzzy  Active Rules", None))
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("tablewin", "Nr.", None))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("tablewin", "Rule", None))
        item = self.table.horizontalHeaderItem(2)
        item.setText(_translate("tablewin", "Mu", None))
        item = self.table.horizontalHeaderItem(3)
        item.setText(_translate("tablewin", "Input1", None))
        item = self.table.horizontalHeaderItem(4)
        item.setText(_translate("tablewin", "Input2", None))
        item = self.table.horizontalHeaderItem(5)
        item.setText(_translate("tablewin", "Input3", None))
        item = self.table.horizontalHeaderItem(6)
        item.setText(_translate("tablewin", "Output", None))
        item = self.table.horizontalHeaderItem(7)
        item.setText(_translate("tablewin", "Entire Output", None))


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rulesform.ui'
#
# Created: Mon Nov 30 10:53:57 2015
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

class Ui_rulesform(object):
    def setupUi(self, rulesform):
        rulesform.setObjectName(_fromUtf8("rulesform"))
        rulesform.resize(829, 242)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("icons/area.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        rulesform.setWindowIcon(icon)
        self.horizontalLayout = QtGui.QHBoxLayout(rulesform)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.table = QtGui.QTableWidget(rulesform)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
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
        self.table.verticalHeader().setVisible(False)
        self.horizontalLayout.addWidget(self.table)

        self.retranslateUi(rulesform)
        QtCore.QMetaObject.connectSlotsByName(rulesform)

    def retranslateUi(self, rulesform):
        rulesform.setWindowTitle(_translate("rulesform", "Samt Fuzzy  ---  Active Rules", None))
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("rulesform", "Nr.", None))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("rulesform", "Rule", None))
        item = self.table.horizontalHeaderItem(2)
        item.setText(_translate("rulesform", "Mu", None))
        item = self.table.horizontalHeaderItem(3)
        item.setText(_translate("rulesform", "Input1", None))
        item = self.table.horizontalHeaderItem(4)
        item.setText(_translate("rulesform", "Input2", None))
        item = self.table.horizontalHeaderItem(5)
        item.setText(_translate("rulesform", "Input3", None))
        item = self.table.horizontalHeaderItem(6)
        item.setText(_translate("rulesform", "Output", None))
        item = self.table.horizontalHeaderItem(7)
        item.setText(_translate("rulesform", "Entire Output", None))


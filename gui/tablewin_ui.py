# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tablewin.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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
        tablewin.resize(255, 489)
        tablewin.setWindowTitle(_fromUtf8(""))
        self.centralwidget = QtGui.QWidget(tablewin)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.main_frame = QtGui.QWidget(self.centralwidget)
        self.main_frame.setMinimumSize(QtCore.QSize(206, 408))
        self.main_frame.setObjectName(_fromUtf8("main_frame"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.main_frame)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.tblwid = QtGui.QTableWidget(self.main_frame)
        self.tblwid.setMinimumSize(QtCore.QSize(206, 408))
        self.tblwid.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tblwid.setAlternatingRowColors(True)
        self.tblwid.setColumnCount(2)
        self.tblwid.setObjectName(_fromUtf8("tblwid"))
        self.tblwid.setRowCount(0)
        self.tblwid.horizontalHeader().setDefaultSectionSize(105)
        self.tblwid.horizontalHeader().setStretchLastSection(True)
        self.tblwid.verticalHeader().setVisible(False)
        self.horizontalLayout_2.addWidget(self.tblwid)
        self.verticalLayout.addWidget(self.main_frame)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lbl_tipp = QtGui.QLabel(self.centralwidget)
        self.lbl_tipp.setObjectName(_fromUtf8("lbl_tipp"))
        self.horizontalLayout.addWidget(self.lbl_tipp)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_save_yxz = QtGui.QPushButton(self.centralwidget)
        self.btn_save_yxz.setMinimumSize(QtCore.QSize(71, 31))
        self.btn_save_yxz.setMaximumSize(QtCore.QSize(71, 16777215))
        self.btn_save_yxz.setObjectName(_fromUtf8("btn_save_yxz"))
        self.horizontalLayout.addWidget(self.btn_save_yxz)
        self.btn_save_ijz = QtGui.QPushButton(self.centralwidget)
        self.btn_save_ijz.setMinimumSize(QtCore.QSize(71, 31))
        self.btn_save_ijz.setMaximumSize(QtCore.QSize(71, 31))
        self.btn_save_ijz.setObjectName(_fromUtf8("btn_save_ijz"))
        self.horizontalLayout.addWidget(self.btn_save_ijz)
        self.btn_ok = QtGui.QPushButton(self.centralwidget)
        self.btn_ok.setMinimumSize(QtCore.QSize(71, 31))
        self.btn_ok.setMaximumSize(QtCore.QSize(61, 31))
        self.btn_ok.setObjectName(_fromUtf8("btn_ok"))
        self.horizontalLayout.addWidget(self.btn_ok)
        self.verticalLayout.addLayout(self.horizontalLayout)
        tablewin.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(tablewin)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 255, 30))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        tablewin.setMenuBar(self.menubar)

        self.retranslateUi(tablewin)
        QtCore.QMetaObject.connectSlotsByName(tablewin)

    def retranslateUi(self, tablewin):
        self.lbl_tipp.setText(_translate("tablewin", ".", None))
        self.btn_save_yxz.setText(_translate("tablewin", "Save  y x z", None))
        self.btn_save_ijz.setText(_translate("tablewin", "Save  i j z", None))
        self.btn_ok.setText(_translate("tablewin", "OK", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    tablewin = QtGui.QMainWindow()
    ui = Ui_tablewin()
    ui.setupUi(tablewin)
    tablewin.show()
    sys.exit(app.exec_())


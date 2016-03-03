# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plotwin.ui'
#
# Created: Wed Nov 18 13:08:24 2015
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

class Ui_plotwin(object):
    def setupUi(self, plotwin):
        plotwin.setObjectName(_fromUtf8("plotwin"))
        plotwin.resize(661, 485)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("icons/area.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        plotwin.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(plotwin)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.main_frame = matplotlibWidget(self.centralwidget)
        self.main_frame.setGeometry(QtCore.QRect(12, 2, 641, 431))
        self.main_frame.setMinimumSize(QtCore.QSize(480, 360))
        self.main_frame.setObjectName(_fromUtf8("main_frame"))
        plotwin.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(plotwin)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 661, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        plotwin.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(plotwin)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        plotwin.setStatusBar(self.statusbar)

        self.retranslateUi(plotwin)
        QtCore.QMetaObject.connectSlotsByName(plotwin)

    def retranslateUi(self, plotwin):
        plotwin.setWindowTitle(_translate("plotwin", "MainWindow", None))

from matplotlibwidgetFile import matplotlibWidget

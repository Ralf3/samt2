# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plotwin.ui'
#
# Created: Mon Jun 30 10:29:16 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_plotwin(object):
    def setupUi(self, plotwin):
        plotwin.setObjectName(_fromUtf8("plotwin"))
        plotwin.resize(661, 485)
        self.centralwidget = QtGui.QWidget(plotwin)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.main_frame = matplotlibWidget(self.centralwidget)
        self.main_frame.setGeometry(QtCore.QRect(12, 2, 641, 431))
        self.main_frame.setMinimumSize(QtCore.QSize(480, 360))
        self.main_frame.setObjectName(_fromUtf8("main_frame"))
        plotwin.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(plotwin)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 661, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        plotwin.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(plotwin)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        plotwin.setStatusBar(self.statusbar)

        self.retranslateUi(plotwin)
        QtCore.QMetaObject.connectSlotsByName(plotwin)

    def retranslateUi(self, plotwin):
        plotwin.setWindowTitle(QtGui.QApplication.translate("plotwin", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))

from matplotlibwidgetFile import matplotlibWidget

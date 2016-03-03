# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plotwin3d.ui'
#
# Created: Wed Feb 25 16:22:48 2015
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

class Ui_plotwin3d(object):
    def setupUi(self, plotwin3d):
        plotwin3d.setObjectName(_fromUtf8("plotwin3d"))
        plotwin3d.resize(661, 485)
        self.centralwidget = QtGui.QWidget(plotwin3d)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.main_frame = matplotlibWidget(self.centralwidget)
        self.main_frame.setGeometry(QtCore.QRect(12, 2, 641, 431))
        self.main_frame.setMinimumSize(QtCore.QSize(480, 360))
        self.main_frame.setObjectName(_fromUtf8("main_frame"))
        plotwin3d.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(plotwin3d)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 661, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        plotwin3d.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(plotwin3d)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        plotwin3d.setStatusBar(self.statusbar)

        self.retranslateUi(plotwin3d)
        QtCore.QMetaObject.connectSlotsByName(plotwin3d)

    def retranslateUi(self, plotwin3d):
        plotwin3d.setWindowTitle(_translate("plotwin3d", "MainWindow", None))

from mplwidgetFile3d import matplotlibWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    plotwin3d = QtGui.QMainWindow()
    ui = Ui_plotwin3d()
    ui.setupUi(plotwin3d)
    plotwin3d.show()
    sys.exit(app.exec_())


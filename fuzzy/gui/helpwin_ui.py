# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'helpwin.ui'
#
# Created: Fri Feb  5 15:59:05 2016
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

class Ui_helpwin(object):
    def setupUi(self, helpwin):
        helpwin.setObjectName(_fromUtf8("helpwin"))
        helpwin.resize(960, 599)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("icons/area.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        helpwin.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(helpwin)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.textBrowser = QtGui.QTextBrowser(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        font.setPointSize(11)
        self.textBrowser.setFont(font)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.verticalLayout.addWidget(self.textBrowser)
        helpwin.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(helpwin)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 960, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        helpwin.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(helpwin)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        helpwin.setStatusBar(self.statusbar)
        self.toolbar = QtGui.QToolBar(helpwin)
        self.toolbar.setObjectName(_fromUtf8("toolbar"))
        helpwin.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar)
        self.actionHome = QtGui.QAction(helpwin)
        self.actionHome.setObjectName(_fromUtf8("actionHome"))
        self.actionBack = QtGui.QAction(helpwin)
        self.actionBack.setObjectName(_fromUtf8("actionBack"))
        self.actionForward = QtGui.QAction(helpwin)
        self.actionForward.setObjectName(_fromUtf8("actionForward"))
        self.actionTop = QtGui.QAction(helpwin)
        self.actionTop.setObjectName(_fromUtf8("actionTop"))
        self.actionSpacer = QtGui.QAction(helpwin)
        self.actionSpacer.setObjectName(_fromUtf8("actionSpacer"))
        self.toolbar.addAction(self.actionHome)
        self.toolbar.addAction(self.actionSpacer)
        self.toolbar.addAction(self.actionBack)
        self.toolbar.addAction(self.actionForward)
        self.toolbar.addAction(self.actionTop)
        self.toolbar.addSeparator()

        self.retranslateUi(helpwin)
        QtCore.QMetaObject.connectSlotsByName(helpwin)

    def retranslateUi(self, helpwin):
        helpwin.setWindowTitle(_translate("helpwin", "SAMT2 - Fuzzy  -----  Manual", None))
        self.textBrowser.setHtml(_translate("helpwin", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.toolbar.setWindowTitle(_translate("helpwin", "toolBar", None))
        self.actionHome.setText(_translate("helpwin", "Home", None))
        self.actionBack.setText(_translate("helpwin", "Back", None))
        self.actionForward.setText(_translate("helpwin", "Forward", None))
        self.actionTop.setText(_translate("helpwin", "Top", None))
        self.actionTop.setStatusTip(_translate("helpwin", "Back to top", None))
        self.actionTop.setWhatsThis(_translate("helpwin", "Top", None))
        self.actionSpacer.setText(_translate("helpwin", "Spacer", None))
        self.actionSpacer.setToolTip(_translate("helpwin", "Spacer", None))


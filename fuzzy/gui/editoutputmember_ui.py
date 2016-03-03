# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'editoutputmember.ui'
#
# Created: Thu Jan 21 11:09:27 2016
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

class Ui_outputDialog(object):
    def setupUi(self, outputDialog):
        outputDialog.setObjectName(_fromUtf8("outputDialog"))
        outputDialog.resize(310, 150)
        outputDialog.setMinimumSize(QtCore.QSize(310, 150))
        outputDialog.setMaximumSize(QtCore.QSize(310, 150))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        outputDialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/area.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        outputDialog.setWindowIcon(icon)
        outputDialog.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.gridlayout = QtGui.QGridLayout(outputDialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label_2 = QtGui.QLabel(outputDialog)
        self.label_2.setMinimumSize(QtCore.QSize(120, 30))
        self.label_2.setMaximumSize(QtCore.QSize(120, 30))
        self.label_2.setSizeIncrement(QtCore.QSize(0, 0))
        self.label_2.setText(_fromUtf8("Value"))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.hboxlayout.addWidget(self.label_2)
        self.valueLE = QtGui.QLineEdit(outputDialog)
        self.valueLE.setMinimumSize(QtCore.QSize(165, 30))
        self.valueLE.setMaximumSize(QtCore.QSize(165, 30))
        self.valueLE.setObjectName(_fromUtf8("valueLE"))
        self.hboxlayout.addWidget(self.valueLE)
        self.gridlayout.addLayout(self.hboxlayout, 1, 0, 1, 1)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.label = QtGui.QLabel(outputDialog)
        self.label.setMinimumSize(QtCore.QSize(120, 30))
        self.label.setMaximumSize(QtCore.QSize(120, 30))
        self.label.setText(_fromUtf8("Singleton Name"))
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout1.addWidget(self.label)
        self.outLE = QtGui.QLineEdit(outputDialog)
        self.outLE.setMinimumSize(QtCore.QSize(165, 30))
        self.outLE.setMaximumSize(QtCore.QSize(165, 30))
        self.outLE.setObjectName(_fromUtf8("outLE"))
        self.hboxlayout1.addWidget(self.outLE)
        self.gridlayout.addLayout(self.hboxlayout1, 0, 0, 1, 1)
        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setObjectName(_fromUtf8("hboxlayout2"))
        spacerItem = QtGui.QSpacerItem(131, 31, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem)
        self.okButton = QtGui.QPushButton(outputDialog)
        self.okButton.setMinimumSize(QtCore.QSize(80, 30))
        self.okButton.setMaximumSize(QtCore.QSize(80, 30))
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.hboxlayout2.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton(outputDialog)
        self.cancelButton.setMinimumSize(QtCore.QSize(80, 30))
        self.cancelButton.setMaximumSize(QtCore.QSize(80, 30))
        self.cancelButton.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.cancelButton.setText(_fromUtf8("Cancel"))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.hboxlayout2.addWidget(self.cancelButton)
        self.gridlayout.addLayout(self.hboxlayout2, 2, 0, 1, 1)

        self.retranslateUi(outputDialog)
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL(_fromUtf8("clicked()")), outputDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(outputDialog)
        outputDialog.setTabOrder(self.outLE, self.valueLE)
        outputDialog.setTabOrder(self.valueLE, self.okButton)
        outputDialog.setTabOrder(self.okButton, self.cancelButton)

    def retranslateUi(self, outputDialog):
        outputDialog.setWindowTitle(_translate("outputDialog", "Edit Output Membership Functions", None))
        self.okButton.setText(_translate("outputDialog", "OK", None))


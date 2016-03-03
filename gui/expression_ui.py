# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'expression.ui'
#
# Created: Fri Apr 24 08:21:37 2015
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

class Ui_expression(object):
    def setupUi(self, expression):
        expression.setObjectName(_fromUtf8("expression"))
        expression.resize(707, 436)
        expression.setWindowTitle(_fromUtf8(""))
        self.centralwidget = QtGui.QWidget(expression)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.main_frame = QtGui.QFrame(self.centralwidget)
        self.main_frame.setMinimumSize(QtCore.QSize(206, 400))
        self.main_frame.setFrameShape(QtGui.QFrame.Panel)
        self.main_frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.main_frame.setLineWidth(1)
        self.main_frame.setMidLineWidth(0)
        self.main_frame.setObjectName(_fromUtf8("main_frame"))
        self.ledit_res = QtGui.QLineEdit(self.main_frame)
        self.ledit_res.setGeometry(QtCore.QRect(80, 50, 251, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.ledit_res.setFont(font)
        self.ledit_res.setCursorPosition(0)
        self.ledit_res.setObjectName(_fromUtf8("ledit_res"))
        self.label_6 = QtGui.QLabel(self.main_frame)
        self.label_6.setGeometry(QtCore.QRect(40, 60, 31, 20))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_5 = QtGui.QLabel(self.main_frame)
        self.label_5.setGeometry(QtCore.QRect(470, 20, 21, 18))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_4 = QtGui.QLabel(self.main_frame)
        self.label_4.setGeometry(QtCore.QRect(240, 20, 16, 18))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.ledit_exp = QtGui.QLineEdit(self.main_frame)
        self.ledit_exp.setGeometry(QtCore.QRect(80, 90, 601, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.ledit_exp.setFont(font)
        self.ledit_exp.setCursorPosition(0)
        self.ledit_exp.setObjectName(_fromUtf8("ledit_exp"))
        self.label_3 = QtGui.QLabel(self.main_frame)
        self.label_3.setGeometry(QtCore.QRect(10, 20, 21, 18))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_2 = QtGui.QLabel(self.main_frame)
        self.label_2.setGeometry(QtCore.QRect(10, 140, 531, 18))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_7 = QtGui.QLabel(self.main_frame)
        self.label_7.setGeometry(QtCore.QRect(10, 95, 60, 18))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.layoutWidget = QtGui.QWidget(self.main_frame)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 360, 671, 36))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_clear = QtGui.QPushButton(self.layoutWidget)
        self.btn_clear.setMinimumSize(QtCore.QSize(81, 31))
        self.btn_clear.setMaximumSize(QtCore.QSize(81, 31))
        self.btn_clear.setLocale(QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Germany))
        self.btn_clear.setText(_fromUtf8("Clear Expr"))
        self.btn_clear.setObjectName(_fromUtf8("btn_clear"))
        self.horizontalLayout.addWidget(self.btn_clear)
        spacerItem1 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btn_calc = QtGui.QPushButton(self.layoutWidget)
        self.btn_calc.setMinimumSize(QtCore.QSize(81, 31))
        self.btn_calc.setMaximumSize(QtCore.QSize(81, 31))
        self.btn_calc.setText(_fromUtf8("Calc"))
        self.btn_calc.setObjectName(_fromUtf8("btn_calc"))
        self.horizontalLayout.addWidget(self.btn_calc)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.lbl_a = QtGui.QLabel(self.main_frame)
        self.lbl_a.setGeometry(QtCore.QRect(30, 20, 181, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lbl_a.setFont(font)
        self.lbl_a.setFrameShape(QtGui.QFrame.Panel)
        self.lbl_a.setFrameShadow(QtGui.QFrame.Sunken)
        self.lbl_a.setText(_fromUtf8(""))
        self.lbl_a.setObjectName(_fromUtf8("lbl_a"))
        self.lbl_b = QtGui.QLabel(self.main_frame)
        self.lbl_b.setGeometry(QtCore.QRect(260, 20, 181, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lbl_b.setFont(font)
        self.lbl_b.setFrameShape(QtGui.QFrame.Panel)
        self.lbl_b.setFrameShadow(QtGui.QFrame.Sunken)
        self.lbl_b.setText(_fromUtf8(""))
        self.lbl_b.setObjectName(_fromUtf8("lbl_b"))
        self.lbl_c = QtGui.QLabel(self.main_frame)
        self.lbl_c.setGeometry(QtCore.QRect(490, 20, 171, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lbl_c.setFont(font)
        self.lbl_c.setFrameShape(QtGui.QFrame.Panel)
        self.lbl_c.setFrameShadow(QtGui.QFrame.Sunken)
        self.lbl_c.setText(_fromUtf8(""))
        self.lbl_c.setObjectName(_fromUtf8("lbl_c"))
        self.tblwid = QtGui.QTableWidget(self.main_frame)
        self.tblwid.setGeometry(QtCore.QRect(10, 170, 681, 186))
        self.tblwid.setFrameShape(QtGui.QFrame.Panel)
        self.tblwid.setFrameShadow(QtGui.QFrame.Raised)
        self.tblwid.setLineWidth(1)
        self.tblwid.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tblwid.setDragEnabled(True)
        self.tblwid.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.tblwid.setAlternatingRowColors(False)
        self.tblwid.setShowGrid(True)
        self.tblwid.setGridStyle(QtCore.Qt.DotLine)
        self.tblwid.setRowCount(6)
        self.tblwid.setColumnCount(8)
        self.tblwid.setObjectName(_fromUtf8("tblwid"))
        self.tblwid.horizontalHeader().setVisible(False)
        self.tblwid.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.main_frame)
        expression.setCentralWidget(self.centralwidget)
        self.statusBar = QtGui.QStatusBar(expression)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        expression.setStatusBar(self.statusBar)

        self.retranslateUi(expression)
        QtCore.QMetaObject.connectSlotsByName(expression)

    def retranslateUi(self, expression):
        self.label_6.setText(_translate("expression", "result", None))
        self.label_5.setText(_translate("expression", "c_", None))
        self.label_4.setText(_translate("expression", "b_", None))
        self.label_3.setText(_translate("expression", "a_", None))
        self.label_2.setText(_translate("expression", "<html>\n"
"<style>\n"
"     .g      { color: blue; font-weight: bold;}\n"
"    </style>\n"
"<head/><body><p>Numpy mathematical functions:  &nbsp;np.f  &nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;   e.g.: &nbsp; \n"
" < span class=\"g\">a_</span>+ 50 * < span class=\"g\">b_</span>*np.sin( < span class=\"g\">c_</span>+ 2.0)</p></body></html>\n"
"\n"
"", None))
        self.label_7.setText(_translate("expression", "Expression:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    expression = QtGui.QMainWindow()
    ui = Ui_expression()
    ui.setupUi(expression)
    expression.show()
    sys.exit(app.exec_())


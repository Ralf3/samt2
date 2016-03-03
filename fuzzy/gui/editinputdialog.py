#!/usr/bin/env python
# -*- coding: utf-8 -*-              
import sys
import os
sys.path.append(os.environ['SAMT2MASTER']+'/fuzzy/gui')   

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from editinputmember_ui import Ui_InputDialog

class EditInputDialog(QtGui.QDialog):
    def __init__(self, parent=None):
	QtGui.QWidget.__init__(self,parent)  
	#super(EditInputDialog, self).__init__(parent)  
	###QtGui.QDialog.__init__(self,parent)  
	self.ui = Ui_InputDialog()       
	self.ui.setupUi(self)
	
	self.quelle = ""
	self.old_type = ""
	self.rett1 = ""
	self.rett2 = ""
	self.rett3 = ""
	self.rett4 = ""
	self.existingMfType = []
	self.existingMfNames = []
	
	self.ui.p1LE.setValidator(QtGui.QDoubleValidator(self))
	self.ui.p2LE.setValidator(QtGui.QDoubleValidator(self))
	self.ui.p3LE.setValidator(QtGui.QDoubleValidator(self))
	self.ui.p4LE.setValidator(QtGui.QDoubleValidator(self))
	self.ui.p1LE.setEnabled(False)
	self.ui.p2LE.setEnabled(False)
	self.ui.p3LE.setEnabled(True)
	self.ui.p4LE.setEnabled(True)
	
	self.ui.typComboBox.clear()
	self.ui.typComboBox.addItem("left", 0)		# 0 is hidden
	self.ui.typComboBox.addItem("triangular", 1)
	self.ui.typComboBox.addItem("trapeze", 2)
	self.ui.typComboBox.addItem("right", 3)
	
	self.connect(self.ui.typComboBox, SIGNAL('currentIndexChanged(int)'),
			    self.combo_typ_changed)
	self.connect(self.ui.typComboBox, SIGNAL('activated(int)'),
			    self.combo_typ_leftright)		    
	self.connect(self.ui.nameLE, SIGNAL('textChanged(QString)'),
			    self.ignoreWhiteSpace)		    
	self.connect(self.ui.okButton, SIGNAL('clicked()'),
			    self.okButton_clicked)		    
			    
    #-------------------------------------------------------------------
    def set_source(self, q): 
	self.quelle = q     # New or Edit
	if q == "Edit":
	    self.ui.nameLE.setText("selected name")
	    self.ui.nameLE.setEnabled(False)
	else:
	    self.ui.nameLE.setEnabled(True)
    
    #-------------------------------------------------------------------
    def rett_default_values(self):
	#called by: start.py: newMembership, editMembership
	self.rett1 = self.ui.p1LE.text()
	self.rett2 = self.ui.p2LE.text()
	self.rett3 = self.ui.p3LE.text()
	self.rett4 = self.ui.p4LE.text()
	#print "rett_default_values() r1=%s, r2=%s, r3=%s, r4=%s" % (
			#self.rett1, self.rett2, self.rett3, self.rett4)
    
    #-------------------------------------------------------------------
    def setAllTypesInComboBox(self, qtyplist2):  
	# call from editMembership
	# qtyplist2 = self.mfTypeList
	del self.existingMfType [:]		# clear
	for item in qtyplist2:
	    self.existingMfType.append(item)    # for combobox_changed()
	#print "setAllTypesInComboBox:: self.existingMfType=", self.existingMfType
	self.ui.typComboBox.clear()
	self.ui.typComboBox.addItem("left", 0)
	self.ui.typComboBox.addItem("triangular", 1)
	self.ui.typComboBox.addItem("trapeze", 2)
	self.ui.typComboBox.addItem("right", 3)		

    #-------------------------------------------------------------------
    def setTypComboBox(self, typlist):		#QStringList *typlist)
	# called by newMenbership
	#print "setTypComboBox typlist=", typlist
	#print "setTypComboBox self.existingMfType=",self.existingMfType 
	
	self.ui.typComboBox.clear()
	if typlist[0] != "left":   	# ohne left
	    if len(typlist) > 0:
		#print "PROBLEM?????"
		# Problem wenn left deleted wurde ????
		

		#combobox starts with trapeze or triang. ,P1,P2 enabled
		if self.ui.p1LE.isEnabled() == False:
		    self.ui.p1LE.setEnabled(True)
		    self.ui.p1LE.setText(self.rett1)
		if self.ui.p2LE.isEnabled() == False:
		    self.ui.p2LE.setEnabled(True)
		    self.ui.p2LE.setText(self.rett2)
	    else:
		#typidx=0, unabh. von mgl. selektierbaren typen in combo
		self.ui.typComboBox.addItem("left", 0)    
		if self.ui.p1LE.isEnabled():
		    self.ui.p1LE.clear()
		    self.ui.p1LE.setDisabled(True)
		if self.ui.p2LE.isEnabled():
		    self.ui.p2LE.clear()
		    self.ui.p2LE.setDisabled(True)
		if self.ui.p3LE.isEnabled() == False:
		    self.ui.p3LE.setEnabled(True)
		    self.ui.p3LE.setText(self.rett1)
		if self.ui.p4LE.isEnabled() == False:
		    self.ui.p4LE.setEnabled(True)
		    self.ui.p4LE.setText(self.rett2)

	else:    # left schon benutzt
	    #  triangular ist 1. item in comboBox
	    self.ui.p1LE.setEnabled(True)
	    self.ui.p1LE.setText(self.rett1)
	    self.ui.p2LE.setEnabled(True)
	    self.ui.p2LE.setText(self.rett2)
	    self.ui.p3LE.setEnabled(True)
	    self.ui.p4LE.setEnabled(True)
    	self.ui.typComboBox.addItem("triangular", 1)
	self.ui.typComboBox.addItem("trapeze", 2)
	if typlist[-1] != "right":
	    self.ui.typComboBox.addItem("right", 3)

    #-------------------------------------------------------------------
    def set_old_type(self, orig):
	# call by editMembership
	self.old_type = orig     # QString
    
    #-------------------------------------------------------------------
    def combo_typ_changed(self, idx):
	#print "SLOT currentIndexChanged:: combo_typ_changed: idx=",idx
	if idx == -1:
	    return
	ok = True
	txt = self.ui.typComboBox.itemText(idx)
	# oder : hiddval = int(self.ui.typComboBox.itemData(idx))
	
	#print "SLOT: combo_typ__changed:: quelle=%s, txt=%s, 
		#old_type=%s" % (self.quelle, txt, self.old_type) 
	#print "SLOT: combo_typ__changed:: rett1=%s, rett2=%s, 
	#rett3=%s, rett4=%s"%(self.rett1,self.rett2,self.rett3,self.rett4)
	
	if ok == True:
	    if self.quelle == "New":
		#print "SLOT: combo_typ__changed New:: rett1=%s, 
		#rett2=%s, rett3=%s, rett4=%s" % (self.rett1, 
		#self.rett2, self.rett3, self.rett4)
		
		# write the last two points into p1 and p2
		if txt == "triangular":  # if idx=1 
		    self.ui.p1LE.setEnabled(True)
		    self.ui.p2LE.setEnabled(True)
		    if self.old_type == "right":
			self.ui.p3LE.clear()
		    elif self.old_type == "left":
			if self.ui.p3LE.text() != "":
			    self.ui.p1LE.setText(self.ui.p3LE.text())
			    self.ui.p2LE.setText(self.ui.p4LE.text())
		    self.ui.p3LE.setEnabled(True)
		    self.ui.p4LE.clear()
		    self.ui.p4LE.setEnabled(False)
		    self.old_type="triangular"
		elif txt == "trapeze":      #if idx = 2
		    self.ui.p1LE.setEnabled(True)
		    self.ui.p2LE.setEnabled(True)
		    if self.old_type=="right":
			self.ui.p1LE.setText(self.ui.p3LE.text())
			self.ui.p2LE.setText(self.ui.p4LE.text())
			self.ui.p3LE.clear()
		    elif self.old_type == "left":
			self.ui.p1LE.setText(self.ui.p3LE.text())
			self.ui.p2LE.setText(self.ui.p4LE.text())
		    self.ui.p3LE.setEnabled(True)
		    self.ui.p4LE.clear()
		    self.ui.p4LE.setEnabled(True)
		    self.old_type="trapeze"
		elif txt == "left":    #idx == 0:
		    #left        P1 and P2 clear and grey!
		    self.ui.p1LE.clear()
		    self.ui.p1LE.setEnabled(False)
		    self.ui.p2LE.clear()
		    self.ui.p2LE.setEnabled(False)
		    self.ui.p3LE.clear()
		    self.ui.p3LE.setEnabled(True)
		    self.ui.p4LE.clear()
		    self.ui.p4LE.setEnabled(True)
		    self.old_type="left"
		elif txt == "right":     #idx == 3:
		    #right    P3 and P4 clear and grey !
		    self.ui.p1LE.setEnabled(True)
		    self.ui.p2LE.setEnabled(True)
		    if self.ui.p4LE.text() != "":
			self.ui.p1LE.setText(self.ui.p3LE.text())
			self.ui.p2LE.setText(self.ui.p4LE.text())
		    else:
			if self.ui.p3LE.text() != "":
			    self.ui.p1LE.setText(self.ui.p2LE.text())
			    self.ui.p2LE.setText(self.ui.p3LE.text())
		    self.ui.p3LE.clear()
		    self.ui.p3LE.setEnabled(False)
		    self.ui.p4LE.clear()
		    self.ui.p4LE.setEnabled(False)
		    self.old_type="right"
	    else:
		# quelle "Edit"
		if txt == "triangular":        #idx == 1 
		    self.ui.p1LE.setEnabled(True)
		    self.ui.p2LE.setEnabled(True)
		    if self.old_type=="right":
			self.ui.p3LE.clear()
		    elif self.old_type == "left": 
			if self.ui.p3LE.text() != "":
			    self.ui.p1LE.setText(self.rett3)
			    self.ui.p2LE.setText(self.rett4)
		    self.ui.p3LE.setEnabled(True)
		    self.ui.p4LE.clear()
		    self.ui.p4LE.setEnabled(False)
		elif txt == "trapeze":      #idx == 2 
		    if self.ui.p1LE.isEnabled() == False:
			self.ui.p1LE.setEnabled(True)
			self.ui.p1LE.setText(self.rett1)
		    if self.ui.p2LE.isEnabled() == False:
		    	self.ui.p2LE.setEnabled(True)
			self.ui.p2LE.setText(self.rett2)
		    if self.ui.p3LE.isEnabled() == False:
			self.ui.p3LE.setEnabled(True)
		    if not self.ui.p4LE.isEnabled():
			self.ui.p4LE.setEnabled(True)
		elif txt == "left":       #idx == 0: 
		    # P1 and P2 clear and grey!
		    if self.ui.p1LE.isEnabled() == True:
			self.ui.p1LE.clear()
			self.ui.p1LE.setEnabled(False)
		    self.ui.p4LE.setEnabled(True)
		    if self.old_type =="triangular":
			self.ui.p4LE.setText(self.ui.p3LE.text())
		    else:
			if self.old_type =="trapeze":
			   self.ui.p4LE.setText(self.rett4)
			else:
			   self.ui.p4LE.setText(self.rett2)
		    self.ui.p3LE.setEnabled(True)
		    if self.old_type =="triangular":
			self.ui.p3LE.setText(self.ui.p2LE.text())
		    else:
			if self.old_type =="trapeze":
			   self.ui.p3LE.setText(self.rett3)
			else:
			   self.ui.p3LE.setText(self.rett1)
		    if self.ui.p2LE.isEnabled() == True:
			self.ui.p2LE.clear()
			self.ui.p2LE.setDisabled(True)
		elif txt == "right":      #idx == 3: 
		    #print "combo_typ_changed: idx=right" 
		    # P3 and P4 clear and grey !
		    if self.ui.p1LE.isEnabled() == False:
			self.ui.p1LE.setEnabled(True)
			self.ui.p1LE.setText(self.rett1)
		    if self.ui.p2LE.isEnabled() == False:
			self.ui.p2LE.setEnabled(True)
			self.ui.p2LE.setText(self.rett2)
		    if self.ui.p3LE.isEnabled() == True:
		    	self.ui.p3LE.clear()
			self.ui.p3LE.setEnabled(False)
		    if self.ui.p4LE.isEnabled() == True:
			self.ui.p4LE.clear()
			self.ui.p4LE.setEnabled(False)

    #-------------------------------------------------------------------
    def combo_typ_leftright(self):
	#print  "SLOT combo_typ activated:: combo_typ_leftright()"
	ok = True
	s = str(self.ui.typComboBox.currentText())
	if s == "left" or s == "right":
	    if s in self.existingMfType:
		ok = False
		self.info(self.ui.typComboBox.currentText())
		self.old_type = "right"
		self.ui.typComboBox.setCurrentIndex(
			self.ui.typComboBox.findText(self.old_type))
    
    #-------------------------------------------------------------------
    def okButton_clicked(self):
	# SLOT, called by: okButton   alt: controllInputs()
	# controlls whether the membership function was correct edited
	hiddval = int(self.ui.typComboBox.itemData(
			self.ui.typComboBox.currentIndex()).toString())
	if self.ui.nameLE.text().isEmpty():
	    self.info("Name of membership function expected")
	    return
	ok = True
	p1 = 0.0	# ok?  wenn New left or right ??
	p2 = 0.0
	p3 = 0.0
	p4 = 0.0	
	if self.ui.p1LE.text().trimmed() != "":
	    p1 = float(self.ui.p1LE.text())
	if self.ui.p2LE.text().trimmed() != "":
	    p2 = float(self.ui.p2LE.text())
	if self.ui.p3LE.text().trimmed() != "":
	    p3 = float(self.ui.p3LE.text())
	if self.ui.p4LE.text().trimmed() != "":
	    p4 = float(self.ui.p4LE.text())
	if ok == True:
	    if hiddval == 1: 	# triangle   test if p1<p2<p3
		if (p1>=p2 or p2>=p3 or p1>=p3):
		    ok = False
		    print "triangle points not allowed"
	    elif hiddval == 2:  #trapez
		if p1>=p2 or p1>=p3 or p1>=p4 or p2>=p3 or p2>=p4 or p3>=p4:
		    ok = False
		    print "trapez: points not allowed"
	    elif hiddval == 0:  # left
		if (p3>=p4):
		    ok = False
		    print "left: points not allowed"
	    elif hiddval == 3:  # right
		if (p1>=p2):
		    ok =False
		    print "right: points not allowed"
	if ok == True:
	    self.accept()

    #-------------------------------------------------------------------
    def info(self, msg):
	QtGui.QMessageBox.information(self, "Warning", msg)

    #-------------------------------------------------------------------
    def ignoreWhiteSpace(self):
	# SLOT replaces a "space" within the name
	s = self.ui.nameLE.text()
	pos = s.indexOf(" ",0,Qt.CaseSensitive)
	if (pos>=0):
	    s=s.replace(pos,1,"_")
	self.ui.nameLE.setText(s)

########################################################################
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    dialog = EditInputDialog() 
    dialog.show()
    sys.exit(app.exec_())


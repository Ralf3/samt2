#!/usr/bin/env python
# -*- coding: utf-8 -*-              
import sys
import os
sys.path.append(os.environ['SAMT2MASTER']+'/fuzzy/gui')   

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from editoutputmember_ui import Ui_outputDialog

class EditOutputDialog(QtGui.QDialog):
    def __init__(self, parent=None):
	QtGui.QWidget.__init__(self,parent)  
	#super(EditOutputDialog, self).__init__(parent)  
	###QtGui.QDialog.__init__(self,parent)  
	self.ui = Ui_outputDialog()       
	self.ui.setupUi(self)

	self.ui.valueLE.setValidator(QtGui.QDoubleValidator(self))
	
	self.connect(self.ui.outLE, SIGNAL('textChanged(QString)'),
			    self.ignoreWhiteSpace)		    
	self.connect(self.ui.okButton, SIGNAL('clicked()'),
			    self.okButton_clicked)		    
			    
  
    #-------------------------------------------------------------------
    def okButton_clicked(self):
	# SLOT, called by: okButton   alt: controllInputs()
	# controls whether the output was correct edited
	ok = True
	if self.ui.outLE.text().isEmpty():
	    self.info("Name of output expected !")
	    ok = False
	    return
	if self.ui.valueLE.text().isEmpty():
	    self.info("Singleton value expected !")
	    ok = False
	    return
	# is value a correct formatted number?
	s = self.ui.valueLE.text().trimmed()
	if self.is_number(s) == True:
	    val = float(self.ui.valueLE.text())
	    ok = True
	    self.accept()
	else:
	    self.info("Singleton value must be a number !")
	if ok == True:
	    self.accept()

    #-------------------------------------------------------------------
    def ignoreWhiteSpace(self):
	# SLOT replaces a "space" within the name
	s = self.ui.outLE.text()
	pos = s.indexOf(" ",0,Qt.CaseSensitive)
	if (pos >= 0):
	    s = s.replace(pos,1,"_")
	self.ui.outLE.setText(s)
    
    #-------------------------------------------------------------------
    def is_number(self, s):
	try:
	    float(s)		# s is string
	    return True    
	except ValueError:
	    pass
     	try:
	    import unicodedata
	    unicodedata.numeric(s)
	    return True
	except (TypeError, ValueError):
	    pass
     	return False
	
    #-------------------------------------------------------------------
    def info(self, msg):
	QtGui.QMessageBox.information(self, "Warning", msg)
	
    #-------------------------------------------------------------------

########################################################################
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    dialog = EditOutputDialog() 
    dialog.show()
    sys.exit(app.exec_())


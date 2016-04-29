#!/usr/bin/env python
# -*- coding: utf-8 -*-              
import sys
import os
import locale
import math
import csv
import timeit

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.lines as line
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_qt4agg  \
		    import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg \
		    import NavigationToolbar2QT as NavigationToolbar
# forms
from form1_ui import *   
from editinputmember_ui import Ui_InputDialog
from plotwin_ui import Ui_plotwin
from tablewin_ui import Ui_tablewin
from rulesform_ui import Ui_rulesform

sys.path.append(os.environ['SAMT2MASTER']+'/fuzzy/gui')
import worker
import editinputdialog
import editoutputdialog
import paintwidget
import paintoutput
import painttrain

########################################################################

class MyForm(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
    	print "========================================================"
	print "========================================================"
	QtGui.QWidget.__init__(self,  parent)
	self.ui = Ui_MainWindow()
	self.ui.setupUi(self)
	
	env = os.environ['SAMT2MASTER']+'/fuzzy/gui'
	self.env = env		
	imag = env+'/icons/area.png'
	self.icon1 = QIcon()
	self.icon1.addFile(imag, QSize(), QIcon.Normal, QIcon.Off)
	imag = env+'/icons/spacer.png'
	self.icon2 = QIcon()
	self.icon2.addFile(imag, QSize(), QIcon.Normal, QIcon.Off)
	self.setWindowIcon(QIcon(env+'/icons/area.png'))
	
	# path to .fis 
	self.path_samt2_model = os.environ['SAMT2DATEN'] 
	self.path_save_data=self.path_samt2_model # writes fileOpen only
	
	self.open_modelname = None	# writes fileOpen,fileNew only
	self.openedModelPath = '' 	# writes fileOpen only
		
	# Toolbar
	self.ui.fileNewAction.setIcon(QIcon(env+'/icons/filenew.png'))
	self.ui.fileOpenAction.setIcon(QIcon(env+'/icons/fileopen.png'))
	self.ui.fileSaveAction.setIcon(QIcon(env+'/icons/filesave.png'))
	self.ui.fileSave_AsAction.setIcon(QIcon(env+'/icons/filesaveas.png'))
	self.ui.helpContentsAction.setIcon(QIcon(env+'/icons/contents.png'))
	
	# other class-objects
	self.work = worker.worker()
	self.editInpWin = None   	#editinputdialog
	self.editOutWin = None   	#editoutputdialog
	self.helpwin = None
	
	# variables
	self.mfTitleList = []    # Title of mfs
	self.d_in1_mfname_idx = {}
	self.d_in2_mfname_idx = {}
	self.d_in3_mfname_idx = {}
	self.mfTypeList = []     # Type of mfs
	self.rangeListInp = []	 # ['', ...]  items from mfTable
	self.rangeListOut = []	 # ['', ...]  items from outputTable
	self.outTitleList = []   # Title of outputs
	self.li_popups = []
	self.li_input_names = []
	
	self.numInput = 1     # number of Inputs			
	self.numMf = 0        # number of Memberships
	self.numPoints = 0    # number of Xpoints of all Mfs
	self.xMf = []         # x-vertices of the mfs
	self.yMf = []         # y-vertices of the mfs  
	
	self.changed = False  # is True, if there are made changes
	self.mfGrid = True
	self.filename = ""
	self.mfwidth = self.ui.paintwid.width()   # 760 W. of mfdiagramm	
	self.mfheight = self.ui.paintwid.height() # 335 H. of mfdiagramm
	self.xname = ""	     # xAxis-Title
	
	# --------- input page init
	self.ui.memb1Table.hideColumn(3)  #  sort col
	self.ui.memb2Table.hideColumn(3)
	self.ui.memb3Table.hideColumn(3)
	self.ui.lbl_fisname.setText("") 
 	
	# ------- output page init
	self.xOut = []         	# singleton -values of output   
	self.yOut = []    	# dummy
	self.outGrid = False
	self.ui.outputTable.hideColumn(2)
	self.ui.outnameLE.setEnabled(False)
	
	# ------ rules page init
	self.flag_inter_method = 0
	
	# ------ analyse page init ------------------
	self.ui.outminLE.setReadOnly(True)
	self.ui.outmaxLE.setReadOnly(True)
	self.contour = False
	self.dragging = False 		 
	self.isLine = False    	  # set True only in draw_line()
	self.line1 = None
	self.startPoint = (0,0)
	self.endPoint = (0,0)
	self.startPointC = (0,0)  # copy of startPoint
	self.endPointC = (0,0)	  # copy of endPoint (only for Line)
	self.li_X = [0,0]
	self.li_Y = [0,0]
	self.pickedX = 0
	self.pickedY = 0

	# mplwid_ana
	vbox = QVBoxLayout()
        vbox.addWidget(self.ui.mplwid_ana.canvas)
 	self.ui.mplwid_ana.setLayout(vbox)
	self.w_wid_orig = 481   # mplwid_ana.width()
	self.h_wid_orig = 501   # mplwid_ana.height()
	self.cbar = None	# mpl colorbar 
	
	self.xmin = []   		
	self.xmax = []	 		
	self.xmin.append(0)   
	self.xmax.append(1)           # input1 range (min max)
	self.xmin.append(0)    
	self.xmax.append(1)           # input2 range 
	self.xmin.append(0)    
	self.xmax.append(1)           # input3 range 
	self.actCombo = 1
	self.index0 = 0               # x-axis input
	self.index1 = 1               # y axis input
	self.index2 = 2               # third input z

	# ------ calculation page init ------------------------
	self.ui.btn_value.setIcon(QIcon(env+'/icons/fileopen.png'))
	self.ui.btn_path.setIcon(QIcon(env+'/icons/fileopen.png'))
	#self.ui.btn_calc_fuzzy.setIcon(QIcon(env+'/icons/exec.png'))
	self.ui.btn_calc_fuzzy.setDisabled(True)
	self.value_path = None	# target, if resultLE has only 
				# a filename, not a full path
	
	# ------ training page init ------------------------
	self.ui.btn_trainPath.setIcon(QIcon(env+'/icons/fileopen.png'))
	self.modelTrained = False
	self.trainedOutputList = []
	self.lastModifiedVals = []
	self.origOutputVals = []
	
	# ------ rules training page init ------------------
	self.ui.btn_rtrainPath.setIcon(QIcon(env+'/icons/fileopen.png'))
	self.ui.le_alpha.setText('0.75')
	self.ui.le_alpha.setValidator(QDoubleValidator(self.ui.le_alpha))
	
	
	self.setup_connections()
	self.ui.tabwid.setCurrentIndex(0)
	self.ui.tabwid.setTabIcon(0,self.icon1) 
    
    #------------------------------------------------------------------
    def setup_connections(self):
    	#------ allgemein 
	self.connect(self.ui.statusbar,SIGNAL('messageChanged(QString)'), 
			self.statusbar_msg_changed)
	self.connect(self.ui.tabwid, SIGNAL('currentChanged(int)'),
				self.switchTab)
				
	#------- Input 
  	self.connect(self.ui.numInSpin, SIGNAL('valueChanged(int)'),
				self.numInSpin_changed)
	self.connect(self.ui.inputCombo, SIGNAL('activated(int)'),
				self.switchInputs)
	self.connect(self.ui.inputCombo, SIGNAL('editTextChanged(QString)'),
				self.newInputName)			
	self.connect(self.ui.memb1Table, SIGNAL('cellDoubleClicked(int,int)'),
				self.editMembership)
	self.connect(self.ui.memb2Table, SIGNAL('cellDoubleClicked(int,int)'),
				self.editMembership)
	self.connect(self.ui.memb3Table, SIGNAL('cellDoubleClicked(int,int)'),
				self.editMembership)
	self.connect(self.ui.editInPB,SIGNAL('clicked()'),
				self.editMembership)
	self.connect(self.ui.newInPB, SIGNAL('clicked()'),
				self.newMembership)
	self.connect(self.ui.deleteInPB, SIGNAL('clicked()'),
				self.deleteMembership)
	self.connect(self.ui.mfGridCheck,SIGNAL('toggled(bool)'),
				self.setMfGrid)
				
	#------- Output 
	self.connect(self.ui.outputTable, SIGNAL('cellDoubleClicked(int,int)'),
				self.editOutput)
	self.connect(self.ui.outGridCheck,SIGNAL('toggled(bool)'),
				self.setOutGrid)
	self.connect(self.ui.newOutputPB, SIGNAL('clicked()'),
				self.newOutput)
	self.connect(self.ui.editOutputPB,SIGNAL('clicked()'),
				self.editOutput)
	self.connect(self.ui.deleteOutputPB, SIGNAL('clicked()'),
				self.deleteOutput)
	self.connect(self.ui.outputLE, SIGNAL('textEdited(QString)'),
				self.ignoreSpaceOut)
	self.connect(self.ui.outputLE, SIGNAL('returnPressed()'),
				self.newOutputName)
	
	#------- Rules 
	self.connect(self.ui.rulesTable, SIGNAL('itemChanged(QTableWidgetItem)'),
				self.controllCf)
	self.connect(self.ui.rulesPB, SIGNAL('clicked()'),
				self.generateRules)
	self.connect(self.ui.btn_cf, SIGNAL('clicked()'),
				self.set_cf_column)
	
	#------- Analyse 
	self.connect(self.ui.input1Combo, SIGNAL('activated(int)'),
				self.actCombo1)
	self.connect(self.ui.input2Combo, SIGNAL('activated(int)'),
				self.actCombo2)
	self.connect(self.ui.xgridLE, SIGNAL('returnPressed()'),
				self.test_grids)
	self.connect(self.ui.ygridLE, SIGNAL('returnPressed()'),
				self.test_grids)
  	self.connect(self.ui.in1minLE, SIGNAL('returnPressed()'),
				self.test_range)
	self.connect(self.ui.in1maxLE, SIGNAL('returnPressed()'),
				self.test_range)
	self.connect(self.ui.in2minLE, SIGNAL('returnPressed()'),
				self.test_range)
	self.connect(self.ui.in2maxLE, SIGNAL('returnPressed()'),
				self.test_range)
	self.connect(self.ui.in3LE, SIGNAL('returnPressed()'),
				self.test_range)
	self.connect(self.ui.cb_contour, SIGNAL('toggled(bool)'),
				self.showContour)
	self.connect(self.ui.cb_line, SIGNAL('toggled(bool)'),
				self.draw_line)
	
	#------- Calculation
	self.connect(self.ui.btn_value, SIGNAL('clicked()'),
				self.btn_value_clicked)
	self.connect(self.ui.btn_calc_fuzzy, SIGNAL('clicked()'),
				self.btn_calc_fuzzy)
	self.connect(self.ui.btn_path, SIGNAL('clicked()'),
				self.btn_path_clicked)
	self.connect(self.ui.radio_same, SIGNAL('toggled(bool)'),
				self.radio_same_check)
				
	#-------Training 
	self.connect(self.ui.btn_trainPath, SIGNAL('clicked()'),
				self.btn_trainPath_clicked)	
	self.connect(self.ui.btn_startTraining, SIGNAL('clicked()'),
				self.btn_trainStart_clicked)	
	self.connect(self.ui.btn_clear, SIGNAL('clicked()'),
				self.btn_clear_clicked)	
	self.connect(self.ui.btn_restore_orig, SIGNAL('clicked()'),
				self.btn_restore_orig_clicked)	
				
	#------- Rules Training 
	self.connect(self.ui.btn_rtrainPath, SIGNAL('clicked()'),
				self.btn_rules_trainPath_clicked)	
	self.connect(self.ui.btn_start_rulesTrain, SIGNAL('clicked()'),
				self.btn_rules_trainStart_clicked)
	self.connect(self.ui.btn_rules_save, SIGNAL('clicked()'),
				self.btn_rules_save_clicked)
	self.connect(self.ui.btn_rules_discard, SIGNAL('clicked()'),
				self.btn_rules_discard_clicked)		
	
	#------- File In/Out
	self.connect(self.ui.fileNewAction, SIGNAL('activated()'),
				self.fileNew)
	self.connect(self.ui.fileOpenAction, SIGNAL('activated()'),
				self.fileOpen)
	self.connect(self.ui.fileSaveAction, SIGNAL('activated()'),
				self.fileSave)
	self.connect(self.ui.fileSave_AsAction, SIGNAL('activated()'),
				self.fileSaveAs)
	self.connect(self.ui.fileExitAction, SIGNAL('activated()'),
				self.fileExit)
				
	#------- Help
	self.connect(self.ui.helpContentsAction, SIGNAL('activated()'),
				self.help_manual)
	self.connect(self.ui.helpAboutAction, SIGNAL('activated()'),
				self.help_about)
				
	# ----- mouseEvents 
	self.ui.mplwid_ana.canvas.mpl_connect(
			     'button_press_event', self.on_press)
        self.ui.mplwid_ana.canvas.mpl_connect(
			     'motion_notify_event', self.on_motion)
	self.ui.mplwid_ana.canvas.mpl_connect(
			    'button_release_event', self.on_release)
    
    #-------------------------------------------------------------------
    def initialize(self, q):
	#print "initialize:: called by fileNew or fileOpen"
	# q = 1 --> caller: fileOpen
	# q = 2 -->         fileNew
	
	#clear input page
	self.deleteAllMfs()         #deletes all rows in the mf-tables
	self.numInput = 1
	self.ui.numInSpin.setValue(1)
	self.mfGrid = True
	self.ui.mfGridCheck.setChecked(True)
	self.ui.tabwid.setCurrentIndex(0)
	self.ui.paintwid.dia.clear_plot()  # delete old plot
	del self.xMf[:]	  # x-value vector of the memberships
	del self.yMf[:]	  # y    " 
	self.numMf = 0
	self.showMembership()
	# clear output page - diagramm
	self.ui.outputwid.dia.clear_plot()  # delete old plot
	del self.xOut [:]	# x-vertices of singleton
	# ende 5.2.
	
	# --- input page
	numItem = self.ui.inputCombo.count()
	if numItem == 2:
	    self.ui.inputCombo.removeItem(1);
	    self.ui.input3LE.setDisabled(True)
	    self.ui.in3TextLabel.setDisabled(True)
	elif numItem == 3:
	    self.ui.inputCombo.removeItem(2)
	    self.ui.input1Combo.removeItem(1)	# analysis: 1.combobox

	self.ui.inputCombo.setCurrentIndex(0)  # input page: combobox
	self.ui.input1Combo.setCurrentIndex(0) # analyse page: 1.combobx
	self.newInputName("Input1")            # actualize the combobox
    
	# --- output page
	self.ui.outGridCheck.setChecked(True)
	self.deleteOutputTable()        	# clear the table
	self.ui.outGrid = True
	
	# --- rules page
	self.deleteAllRules()           	# clear the table
	self.ui.mulCombo.setCurrentIndex(1)
	
	# --- analyse page
	self.clear_mplwid_complet()
	
	self.ui.xgridLE.setText("250") 
	self.ui.ygridLE.setText("250")
	self.ui.cb_contour.setEnabled(True)
	self.ui.cb_line.setEnabled(False) 
	if q == 1:
	    self.ui.cb_contour.setChecked(True)
	    self.contour = True
	    self.ui.cb_line.setChecked(False)
	    self.isLine = False
	    
	self.ui.cb_absolut.setEnabled(False)
	self.ui.in1minLE.clear() 
	self.ui.in1maxLE.clear()
	self.ui.in2minLE.clear() 
	self.ui.in2maxLE.clear()
	self.ui.in3LE.clear()
	self.ui.input1Combo.setItemText(self.ui.input1Combo.currentIndex(),"Input1")
	self.ui.input2Combo.setItemText(self.ui.input2Combo.currentIndex(),"Input2")
	self.ui.input3LE.setText("Input3")
	self.ui.in3TextLabel.setText("[0;1]")
	self.ui.outmaxLE.clear()
	self.ui.outminLE.clear()
	self.ui.outnameLE.setText(self.ui.outputLE.text())
	self.index0 = 0
	self.index1 = 1 
	self.index2 = 2

	# --- calculation page
	self.ui.includeLE.clear()
	self.ui.calcTextEdit.clear()
	self.ui.btn_calc_fuzzy.setDisabled(True)
	self.ui.resultLE.clear()
	
	# --- training page 
	self.modelTrained = False
	del self.trainedOutputList[:]
	self.clear_Training_page()
	
	# --- rules training page
	row = self.ui.trainedRulesTbl.rowCount()
	for k in range(row):
	    self.ui.trainedRulesTbl.removeRow(0)
	self.ui.lbl_sep_rtrain.setText('')
	self.ui.rtrainPathEdit.clear()
	self.ui.rtrainDataEdit.clear()
	self.ui.rtrainHeaderSpinBox.setValue(1)
	self.ui.le_alpha.setText('0.75')
	

    #===================================================================
    #===================================================================
    #===================================================================
    #------ INPUT ------------------------------------------------
    #===================================================================
    
    def load_member(self, li_memb, inp):
	# called by:  fileOpen,   fills MfTable
	#print "load_member:: input_%d: li_memb = %s" % (inp,li_memb) 
	
	#self.initialize(1)  # clear table and set defaults
	
	# fill one memberTable per input
	if inp == 0:
	    table = "memb1Table"
	elif inp == 1:
	    table = "memb2Table"
	else:
	    table = "memb3Table"

	for j in range(len(li_memb)):
	    name = li_memb[j][5]
	    typ  = li_memb[j][4]   	# Type
	    if typ == "trapez":
		typ = "trapeze"
	    lu = float(li_memb[j][0])	#a
	    lo = float(li_memb[j][1])	#b
	    ro = float(li_memb[j][2])	#c
	    ru = float(li_memb[j][3])	#d
	    if int(lu) > -9999 and int(ru) > -9999:
		# trapeze oder triangular
		if lo == ro:
		    # triangular
		    range_ = "%.3f %.3f %.3f" % (lu,lo,ru)
		else:
		    range_ = "%.3f %.3f %.3f %.3f" % (lu,lo,ro,ru)

	    elif int(lu) == -9999 and typ == 'left':
		diff = ru-ro
		lo = ro-diff
		lu = lo-diff    #lo+diff
		#range_ = "%.3f %.3f" % (ro,ru)  # ausblenden der -9999
		range_ = "%.3f %.3f %.3f %.3f" % (lu,lo,ro,ru)
	    
	    elif int(ru) == -9999 and typ == 'right':
		diff = lo-lu
		ro = lo+diff
		ru = ro+diff
		#range_ = "%.3f %.3f" % (lu,lo)	# ausblenden der -9999
		range_ = "%.3f %.3f %.3f %.3f" % (lu,lo,ro,ru)
	    #print "load_member:: insertMfTable:: table=%s name=%s typ=%s range=%s" % (table,name,typ,range_)
	    
	    self.insertMfTable(table, name, typ, range_)
	
	lae = self.ui.memb1Table.rowCount()
	self.ui.memb1Table.setVerticalHeaderLabels(["%d" %i for i in range(lae)]) 
	lae = self.ui.memb2Table.rowCount()
	self.ui.memb2Table.setVerticalHeaderLabels(["%d" %i for i in range(lae)])
	lae = self.ui.memb3Table.rowCount()
	self.ui.memb3Table.setVerticalHeaderLabels(["%d" %i for i in range(lae)]) 
            
    #-------------------------------------------------------------------
    def setMfGrid(self):
	# SLOT if gridCheckBox is activated
	self.mfGrid = self.ui.mfGridCheck.isChecked() 
	self.showMembership()
	
    #-------------------------------------------------------------------
    def editMembership(self):
	#print "editMembership clicked"
	# called from: Button Edit, SLOT cellDoubleClicked in tbl
	# opens window for editing a membership"
	
	self.editInpWin = editinputdialog.EditInputDialog()
	self.editInpWin.set_source(QString("Edit"))
	if len(self.mfTypeList) > 0:
	    self.editInpWin.setAllTypesInComboBox(self.mfTypeList)
	row = 0
	tp = None
	#get values of the mf from the table
	index = self.ui.inputCombo.currentIndex()    # actual input
	if index == 0:
	    row= self.ui.memb1Table.rowCount()
	    if (row<=0):
		return
	    row= self.ui.memb1Table.currentRow()
	    if (row<0):
		return
	    name= self.ui.memb1Table.item(row,0).text()
	    type_= self.ui.memb1Table.item(row,1).text()
	    range_= self.ui.memb1Table.item(row,2).text()

	elif index == 1:
	    row= self.ui.memb2Table.rowCount()
	    if (row<=0):
		return
	    row= self.ui.memb2Table.currentRow()
	    if (row<0):
		return
	    name= self.ui.memb2Table.item(row,0).text()
	    type_= self.ui.memb2Table.item(row,1).text()
	    range_=self.ui.memb2Table.item(row,2).text()

	elif index == 2:
	    row= self.ui.memb3Table.rowCount()
	    if (row<=0):
		return
	    row= self.ui.memb3Table.currentRow()
	    if (row<0):
		return
	    name= self.ui.memb3Table.item(row,0).text()
	    type_= self.ui.memb3Table.item(row,1).text()
	    range_= self.ui.memb3Table.item(row,2).text()

	if type_=="triangular":
	    tp=1
	elif type_=="trapeze":
	    tp=2
	elif type_=="left":
	    tp=0
	else:    #right
	    tp=3

	qli = range_.split(" ")     #QStringList 
	# QStringlist --> python list
	rangelist = str(qli.join("\n")).split("\n")	

	for i in range(len(rangelist)):
	    # iterate
	    # insert the values of the selected row in the NewMemberForm
	    self.editInpWin.ui.nameLE.setText(name)
	    self.editInpWin.ui.typComboBox.setCurrentIndex(tp)
	    self.editInpWin.set_old_type(type_)  

	    if tp == 1:  # triangle
		self.editInpWin.ui.p1LE.setEnabled(True)
		self.editInpWin.ui.p2LE.setEnabled(True)
		self.editInpWin.ui.p3LE.setEnabled(True)
		self.editInpWin.ui.p4LE.setEnabled(False)
		self.editInpWin.ui.p1LE.setText(rangelist[i])   
		self.editInpWin.ui.p2LE.setText(rangelist[i+1])
		self.editInpWin.ui.p3LE.setText(rangelist[i+2])
		break  # for
	    elif tp == 2:  # trapeze
		self.editInpWin.ui.p1LE.setEnabled(True)
		self.editInpWin.ui.p2LE.setEnabled(True)
		self.editInpWin.ui.p3LE.setEnabled(True)
		self.editInpWin.ui.p4LE.setEnabled(True)
		self.editInpWin.ui.p1LE.setText(rangelist[i])
		self.editInpWin.ui.p2LE.setText(rangelist[i+1])
		self.editInpWin.ui.p3LE.setText(rangelist[i+2])
		self.editInpWin.ui.p4LE.setText(rangelist[i+3])
		break
	    elif tp == 0:   # left
		self.editInpWin.ui.p1LE.setEnabled(False)
		self.editInpWin.ui.p2LE.setEnabled(False)
		self.editInpWin.ui.p3LE.setEnabled(True)
		self.editInpWin.ui.p4LE.setEnabled(True)
		if (type_== "triangular"):     
		    # vom vorgaengertyp triangular alten P2 holen als 
		    # P3 im neuen type left, überspringe P1
		    self.editInpWin.ui.p3LE.setText(rangelist[i+1]) 
		    self.editInpWin.ui.p4LE.setText(rangelist[i+2])
		else:
		    self.editInpWin.ui.p1LE.setText(rangelist[i])
		    self.editInpWin.ui.p2LE.setText(rangelist[i+1])
		    self.editInpWin.ui.p3LE.setText(rangelist[i+2])
		    self.editInpWin.ui.p4LE.setText(rangelist[i+3])
		break
	    elif tp == 3:   # right
		self.editInpWin.ui.p1LE.setEnabled(True)
		self.editInpWin.ui.p2LE.setEnabled(True)
		self.editInpWin.ui.p3LE.setEnabled(False)
		self.editInpWin.ui.p4LE.setEnabled(False)
		self.editInpWin.ui.p1LE.setText(rangelist[i])
		self.editInpWin.ui.p2LE.setText(rangelist[i+1])
		self.editInpWin.ui.p3LE.setText(rangelist[i+2])
		self.editInpWin.ui.p4LE.setText(rangelist[i+3])
		break

	self.editInpWin.rett_default_values()  

	oldname = name  #QString 
  
	if self.editInpWin.exec_():
	    # get values of the edited mf
	    name = self.editInpWin.ui.nameLE.text()
	    typ =  self.editInpWin.ui.typComboBox.currentIndex()
	    type_= self.editInpWin.ui.typComboBox.currentText()
	    if type_=="triangular":
		a = self.editInpWin.ui.p1LE.text()
		b = self.editInpWin.ui.p2LE.text()
		c = self.editInpWin.ui.p3LE.text()
		range_=QString( "%1 %2 %3" ).arg(a).arg(b).arg(c)
	    else:
		if type_=="trapeze":
		    a = self.editInpWin.ui.p1LE.text()
		    b = self.editInpWin.ui.p2LE.text()
		    c = self.editInpWin.ui.p3LE.text()
		    d = self.editInpWin.ui.p4LE.text()
		    range_=QString("%1 %2 %3 %4").arg(a).arg(b).arg(c).arg(d)
		else:
		    if type_=="left":
			p3= float(self.editInpWin.ui.p3LE.text())
			p4= float(self.editInpWin.ui.p4LE.text())
			diff=p4-p3
			p2=p3-diff
			p1=p2-diff
			s1=QString("%5").arg(p1)
			s2=QString("%6").arg(p2)
			s3= self.editInpWin.ui.p3LE.text()
			s4= self.editInpWin.ui.p4LE.text()
			range_=QString("%1 %2 %3 %4").arg(s1).arg(s2).arg(s3).arg(4)
		    else:                          # right
			p1= float(self.editInpWin.ui.p1LE.text())
			p2= float(self.editInpWin.ui.p2LE.text())
			diff=p2-p1
			p3=p2+diff
			p4=p3+diff
			s3=QString("%5").arg(p3)
			s4=QString("%6").arg(p4)
			s1= self.editInpWin.ui.p1LE.text()
			s2= self.editInpWin.ui.p2LE.text()
			range_=QString("%1 %2 %3 %4").arg(s1).arg(s2 ).arg(s3).arg(s4)
	
	# UPDATE memb123Table mit neuen Werten aus editInputDialog
	nameItem = QtGui.QTableWidgetItem("Name")	
	typeItem = QtGui.QTableWidgetItem("Type")
	rangeItem = QtGui.QTableWidgetItem("Range")
	nameItem = 0
	typeItem = 0
	rangeItem = 0
	# actual input
	if index == 0:
	    nameItem = self.ui.memb1Table.item(row,0)
	    typeItem = self.ui.memb1Table.item(row,1)
	    rangeItem = self.ui.memb1Table.item(row,2)
	elif index == 1:
	    nameItem = self.ui.memb2Table.item(row,0)
	    typeItem = self.ui.memb2Table.item(row,1)
	    rangeItem = self.ui.memb2Table.item(row,2)
	elif index == 2:
	    nameItem = self.ui.memb3Table.item(row,0)
	    typeItem = self.ui.memb3Table.item(row,1)
	    rangeItem = self.ui.memb3Table.item(row,2)

	if (oldname != name):
	    nameItem.setText(name)
	typeItem.setText(type_)
	rangeItem.setText(range_)
	
	# rulesTable: change name of the edited mf
	if oldname != name:
	    ruleRow = self.ui.rulesTable.rowCount()
	    if ruleRow >= 0:
		# search the column after the old input name
		for i in range(ruleRow):
		    if self.ui.rulesTable.item(i,index).text()==oldname:
			self.ui.rulesTable.item(i,index).setText(name)

	self.setCorrectMfValues()
	self.showMembership()
	self.changed = True
	del self.editInpWin
	
    #-------------------------------------------------------------------
    def newMembership(self):
	#print "newMembership:: mfTypeList=", self.mfTypeList 
	# window for a new memberhip"
	self.editInpWin = editinputdialog.EditInputDialog()
	self.editInpWin.set_source(QString("New"))
    	if len(self.mfTypeList) > 0:
	    self.editInpWin.setTypComboBox(self.mfTypeList)
	row=0
	index = self.ui.inputCombo.currentIndex()
	
	if self.numPoints > 0:
	    default1 = self.xMf[self.numPoints-2]  
	    default2 = self.xMf[self.numPoints-1]
	    self.editInpWin.ui.p1LE.setText(QString("%1").arg(default1))
	    self.editInpWin.ui.p2LE.setText(QString("%1").arg(default2))
	    self.editInpWin.rett_default_values() 
	    
    	if self.editInpWin.exec_() :
	    # OK-Button in self.editInpWin.ui clicked
	    # get values for the mf and actualize the mf-table
	    name = self.editInpWin.ui.nameLE.text()
	    type_ = self.editInpWin.ui.typComboBox.currentText()
	    
	    # concatenate all vertices to one string that could be 
	    # added in the mf-table
	    if type_ == "triangular":
		s1 = self.editInpWin.ui.p1LE.text()
		s2 = self.editInpWin.ui.p2LE.text()
		s3 = self.editInpWin.ui.p3LE.text()
		range_ = QString("%1 %2 %3").arg(s1).arg(s2).arg(s3)
	    elif type_ == "trapeze":
		s1 = self.editInpWin.ui.p1LE.text()
		s2 = self.editInpWin.ui.p2LE.text()
		s3 = self.editInpWin.ui.p3LE.text()
		s4 = self.editInpWin.ui.p4LE.text()
		range_ = QString("%1 %2 %3 %4").arg(s1).arg(s2).arg(s3).arg(s4)
	    elif type_ =="left":
		p3 = float(self.editInpWin.ui.p3LE.text())
		p4 = float(self.editInpWin.ui.p4LE.text())
		diff = p4-p3
		p2 = p3-diff
		p1 = p2-diff
		s1 = QString("%5").arg(p1)
		s2 = QString("%6").arg(p2)
		s3 = self.editInpWin.ui.p3LE.text()
		s4 = self.editInpWin.ui.p4LE.text()
		range_ = QString("%1 %2 %3 %4").arg(s1).arg(s2).arg(s3).arg(s4)
		#print "newMembership: left range= ", range_
	    else:                              
		# right
		p1 = float(self.editInpWin.ui.p1LE.text())
		p2 = float(self.editInpWin.ui.p2LE.text())
		diff = p2-p1
		p3 = p2+diff
		p4 = p3+diff
		s1 = self.editInpWin.ui.p1LE.text()
		s2 = self.editInpWin.ui.p2LE.text()
		s3 = QString("%5").arg(p3)
		s4 = QString("%6").arg(p4)
		range_ = QString("%1 %2 %3 %4").arg(s1).arg(s2).arg(s3).arg(s4)
		#print "newMembership: right range= ", range_
	    
	    # test if there exist already a mf with the same name,
	    # test if there exist already a type with the same name,  
	    # only for left and rigth
	    ok_type = False
	    ok_name = False
	    # actual input     
	    if index == 0:
	        ok_name = self.testMfName(0,name)
		if type_=="left" or type_=="right":
		    ok_type = self.testMfType(0,type_)
		else:
		    ok_type = True
		if ok_type and ok_name :
		    self.insertMfTable("memb1Table",name,type_,range_)
		elif type_=="left" or type_=="right":
		    self.info(QString(" '%1' or '%2' already exists!").
			    arg(name).arg(type_))
		    return
		else:
		    self.info(QString(" '%1' already exists!").
			    arg(name))
		    return
	    elif index == 1:
		ok_name = self.testMfName(1,name)
		if type_=="left" or type_=="right":
		    ok_type = self.testMfType(1,type_)
		else:
		    ok_type = True
		if ok_type and ok_name:
		    self.insertMfTable("memb2Table",name,type_,range_)
		elif type_=="left" or type_=="right":
		    self.info(QString(" '%1' or '%2' already exists!").arg(name).arg(type_))
		    return
		else:
		    self.info(QString(" '%1' already exists!").arg(name))
		    return
	    elif index == 2:
	        ok_name = self.testMfName(2,name)
	        if type_=="left" or type_=="right":
		    ok_type = self.testMfType(2,type_)
	        else:
		    ok_type = True
		if ok_type and ok_name:
		    self.insertMfTable("memb3Table",name,type_,range_)
		elif type_=="left" or type_=="right":
		    self.info(QString(" '%1' or '%2' already exists!").arg(name).arg(type_))
		    return
		else:
		    self.info(QString(" '%1' already exists!").arg(name))
		    return
	
	    #self.sortMfTable()
	    self.insertMfIntoRulesTable(index, name)

	self.setCorrectMfValues()	# incl. getMfVector
	self.showMembership()
	
	anz_inp = self.ui.inputCombo.count()
	anz_outp = self.ui.outputTable.rowCount()
	anz_rules = self.ui.rulesTable.rowCount()
	#print "newMembship:: anz_inp = %d, anz_outp= %d, anz_rules= %d"
	# % (anz_inp,anz_outp,anz_rules)
	
	self.changed = True
	del self.editInpWin

    #-------------------------------------------------------------------
    def deleteMembership(self):
	#print "deleteMembership() "
	# call from deletePB"
	# delete current row in the membership table
	idx = self.ui.inputCombo.currentIndex()
	if idx == 0:
	    row = self.ui.memb1Table.currentRow()
	    name = self.ui.memb1Table.item(row,0).text()   
	    # remember name for deleting the associated rules
	    self.ui.memb1Table.removeRow(row)
	elif idx == 1:
	    row = self.ui.memb2Table.currentRow()
	    name = self.ui.memb2Table.item(row,0).text()   
	    self.ui.memb2Table.removeRow(row)
	elif idx == 2:
	    row = self.ui.memb3Table.currentRow()
	    name = self.ui.memb3Table.item(row,0).text()    
	    self.ui.memb3Table.removeRow(row)

	# adjust the mf functions in the diagramm
	self.setCorrectMfValues()
	
	# bestehende Regeln aktualisieren -------- ungetestet !!!!!!!!!!
	if self.ui.rulesTable.rowCount() != 0:
	    # remember the deleting rows in a list
	    li_deleted = []  # self. ???
	    for i in range(self.ui.rulesTable.rowCount()):
		if name == self.ui.rulesTable.item(i,idx).text():
		    li_deleted.append(i)
	    
	    # delete the remembered rows in the rules table
	    while len(li_deleted) > 0:
		value = int(li_deleted[-1])	# last list-element
		self.ui.rulesTable.removeRow(value)
		del li_deleted[-1]	
	#print "li_deleted:", li_deleted
	self.showMembership()
	self.changed = True
	
    #-------------------------------------------------------------------
    def showMembership(self):
	# called by: init,resizeEv,fileOpen,fileNew,setMfGrid,
	#	newMembership, editMembersh.,switchInputs, switchTabs
	# plots the membership functions in the diagramm frame
	self.ui.paintwid.dia.clear_plot()  # delete old plot
	self.getMfVector()  		   # get xMf, yMf...
	self.numCurves = len(self.mfTypeList)  
	self.numPoints = len(self.xMf)   	
	self.ui.paintwid.dia.setLists(self.mfTitleList, self.mfTypeList,
					self.xMf, self.yMf, 
					self.numCurves, self.numPoints,
					self.xname, self.mfGrid, self)
	self.ui.paintwid.dia.plot()
	self.ui.newInPB.setEnabled(True)
	leftright = 0
	for typ in self.mfTypeList:
	    if typ == "left":
		leftright += 1
	    elif typ == "right":
		leftright += 2
	if leftright == 3:
	    self.ui.newInPB.setEnabled(False)
    
    #-------------------------------------------------------------------
    def insertMfTable(self, table1, name1, typ1, range1):
	# call from fileOpen
	# inserts a name, type and range into the mf-table
	table = table1   # which table shall be edited
	name = name1     # name of added membershipfunction
	typ = typ1       # type of mf
	range_ = range1  # range of mf
        
	nameItem = QtGui.QTableWidgetItem(name)
	nameItem.setText(name)
	nameItem.setTextAlignment(Qt.AlignCenter)
	nameItem.setFlags(nameItem.flags() & ~Qt.ItemIsEditable)
	
	typItem = QtGui.QTableWidgetItem(typ)
	typItem.setText(typ)
	typItem.setTextAlignment(Qt.AlignCenter)
	typItem.setFlags(typItem.flags() & ~Qt.ItemIsEditable)
        
	rangeItem = QtGui.QTableWidgetItem(range_)
	rangeItem.setText(range_)
	rangeItem.setTextAlignment(Qt.AlignCenter)
	rangeItem.setFlags(rangeItem.flags() & ~Qt.ItemIsEditable)
	sortItem = QtGui.QTableWidgetItem("sort")

	if table == "memb1Table": 
	    row = self.ui.memb1Table.rowCount()
	    self.ui.memb1Table.insertRow(row)
	    self.ui.memb1Table.setItem(row,0,nameItem)
	    self.ui.memb1Table.setItem(row,1,typItem)
	    self.ui.memb1Table.setItem(row,2,rangeItem)
	    sortItem.setText(str(row))  
	    self.ui.memb1Table.setItem(row,3,sortItem)
	    self.ui.memb1Table.resizeColumnToContents(2)
	    self.ui.membershipStack.setCurrentIndex(0)
  
	elif table == "memb2Table":
	    row = self.ui.memb2Table.rowCount()
	    self.ui.memb2Table.insertRow(row)
	    self.ui.memb2Table.setItem(row,0,nameItem)
	    self.ui.memb2Table.setItem(row,1,typItem)
	    self.ui.memb2Table.setItem(row,2,rangeItem)
	    sortItem.setText(str(row))
	    self.ui.memb2Table.setItem(row,3,sortItem)
	    self.ui.memb2Table.resizeColumnToContents(2)
	    self.ui.membershipStack.setCurrentIndex(1)

	elif table == "memb3Table":
	    row = self.ui.memb3Table.rowCount()
	    self.ui.memb3Table.insertRow(row)
	    self.ui.memb3Table.setItem(row,0,nameItem)
	    self.ui.memb3Table.setItem(row,1,typItem)
	    self.ui.memb3Table.setItem(row,2,rangeItem)
	    sortItem.setText(str(row))
	    self.ui.memb3Table.setItem(row,3,sortItem)
	    self.ui.memb3Table.resizeColumnToContents(2)
	    self.ui.membershipStack.setCurrentIndex(2)
	self.changed = True
	self.switchInputs()   
    
    #-------------------------------------------------------------------
    def switchInputs(self):
	# called by: SLOT for inputCombo activated, insertMfTable 
	self.ui.membershipStack.setCurrentIndex(
				    self.ui.inputCombo.currentIndex())    
	# show correct table
	self.xname = self.ui.inputCombo.currentText()
	#self.sortMfTable()   
	self.showMembership() 
	
    #-------------------------------------------------------------------
    def getMfName(self, table, mf):
	# needed for  loading a fuzzy modell -> expects a number of a mf
	# table = 0,1,2   mf = row of table
	
	# optimieren mit Pyfuzzy i.getn   !!!!!!!
	
	if table == 0:
	    mfName = self.ui.memb1Table.item(mf,0).text()
	elif table == 1:
	    mfName = self.ui.memb2Table.item(mf,0).text()
	elif table == 2:
	    mfName = self.ui.memb3Table.item(mf,0).text()
	return(mfName)

    #-------------------------------------------------------------------
    def getMfNumber(self, inp, name):
	# needed for saving fuzzy models 
	# inp int,  name QString
	# returns the according number
	# searching the table , if "name" found , return the row of its
	if inp == 1:
	    # 1. Input
	    for i in range(self.ui.memb1Table.rowCount()):
		if name == self.ui.memb1Table.item(i,0).text():
		    return(i)
	elif inp == 2:
	    # 2. Input
	    for i in range(self.ui.memb2Table.rowCount()):
	      if name == memb2Table.item(i,0).text():
		return(i)
	elif inp == 3:
	    # 3. Input
	    for i in range(self.ui.memb3Table.rowCount()):
	      if name == memb3Table.item(i,0).text():
		return(i)
	else:
	    return(0)
	
    #-------------------------------------------------------------------
    def newInputName(self, name):
	""" Changes text of widgets in the analyses page.
	    * SLOT: if user edits an item in the inputComboBox.
	    * @param name New name of current input.
	"""
	index = self.ui.inputCombo.currentIndex()
	# remove space character
	pos = QString(name).indexOf(" ", 0, Qt.CaseSensitive)
	if pos >= 0:
	    name = name.replace(pos,1,"_")
	# input page
	self.ui.inputCombo.setItemText(index,name)
	# analyse page: 1.combobox
	self.ui.input1Combo.setItemText(index,name)  
	if index == 1:
	    self.ui.input2Combo.setItemText(0,name)  
	# analyse page: 2.combobox
	if index == 2:
	    self.ui.input2Combo.setItemText(1,name)
	    # analyse page: 3.input
	    self.ui.input3LE.setText(name)    
	self.changed = True

    #-------------------------------------------------------------------
    def numInSpin_changed(self):
	""" Slot is called if user changes number of inputs.
	    According to the number edited in the number of input spinbox
	    items are added/removed in the input combobox.
	"""
	self.numInput = self.ui.numInSpin.value()
	#print "SLOT numInSpin_changed:: self.numInput=", self.numInput
	numItem = self.ui.inputCombo.count()
	#print "numItem =", numItem
	numItem1 = self.ui.input1Combo.count()  # analyse page: 1.combo 
	numItem2 = self.ui.input2Combo.count()  # analyse page: 2.combo
	if self.numInput == 1:
	    # input page --> There could be only one item in combobox
	    if numItem ==2:
		self.ui.inputCombo.removeItem(1)
	    if numItem ==3:
		self.ui.inputCombo.removeItem(2)
	    # rules page
	    self.ui.rulesTable.hideColumn(1)
	    self.ui.rulesTable.hideColumn(2)
	    # analyse page --> Comboboxes update
	    if (numItem1==2):
		self.ui.input1Combo.removeItem(1)
	    if (numItem1==3):
		self.ui.input1Combo.removeItem(2)
	    self.ui.input2Combo.setDisabled(True)
	    self.ui.in2minLE.setDisabled(True)
	    self.ui.in2maxLE.setDisabled(True)
	    if self.ui.input3LE.isEnabled():
		self.ui.input3LE.setDisabled(True)
	    if self.ui.in3TextLabel.isEnabled():
		self.ui.in3TextLabel.setDisabled(True)
	    self.ui.in3LE.setDisabled(True)
	    # calculating page

	    self.ui.btn_calc_fuzzy.setDisabled(True)
	
	elif self.numInput == 2:
	    # input page
	    if numItem==1:
		self.ui.inputCombo.insertItem(1,"Input2")
	    if numItem==3:
		self.ui.inputCombo.removeItem(2)
	    # rules page
	    self.ui.rulesTable.showColumn(1)
	    self.ui.rulesTable.hideColumn(2)
	    # analyse page --> Comboboxes update
	    if numItem1==1:
		self.ui.input1Combo.insertItem(1,"Input2")
	    if numItem1==3:
		self.ui.input1Combo.removeItem(2)
	    if numItem2==2:
		self.ui.input2Combo.removeItem(1)
	    self.ui.input2Combo.setEnabled(True)
	    self.ui.in2minLE.setEnabled(True)
	    self.ui.in2maxLE.setEnabled(True)
	    self.ui.input3LE.setDisabled(True)
	    self.ui.in3LE.setDisabled(True)
	    self.ui.in3TextLabel.setDisabled(True)
	    
	elif self.numInput == 3:
	    # input page
	    if numItem  ==  1:
	      self.ui.inputCombo.insertItem(1,"Input2")
	      self.ui.inputCombo.insertItem(2,"Input3")
	    if numItem == 2:
		self.ui.inputCombo.insertItem(2,"Input3")
	    # rules page
	    self.ui.rulesTable.showColumn(1)
	    self.ui.rulesTable.showColumn(2)
	    # analyse page --> Comboboxes update
	    if numItem1 == 1:
	      self.ui.input1Combo.insertItem(1,"Input2")
	      self.ui.input1Combo.insertItem(2,"Input3")
	    if numItem1 == 2:
		self.ui.input1Combo.insertItem(2,"Input3")
	    if numItem2 == 1:
		self.ui.input2Combo.insertItem(1,"Input3")
	    self.ui.input2Combo.setEnabled(True)
	    self.ui.in2minLE.setEnabled(True)
	    self.ui.in2maxLE.setEnabled(True)
	    self.ui.in3LE.setEnabled(True)
	    self.ui.input3LE.setEnabled(True)
	    self.ui.input3LE.setReadOnly(True)
	    self.ui.in3TextLabel.setEnabled(True)

	self.changed = True
	index = self.ui.inputCombo.currentIndex()
	if index >= self.numInput:
	    #raise input1 properties
	    self.ui.membershipStack.setCurrentIndex(index-1) 
	    self.ui.inputCombo.setCurrentIndex(index-1)
    
    #-------------------------------------------------------------------
    def setCorrectMfValues(self):
	# called by: fileOpen, editMembership, newMembership
	# adjust vertices so that all mfs will overlap in a correct way
    	self.ui.memb1Table.sortItems(3)
	self.ui.memb2Table.sortItems(3)
	self.ui.memb3Table.sortItems(3)
	
	self.getMfVector()   # set numMf, numPoints, xMf,...

	if self.numPoints > 4:
	    for i in range(self.numPoints):
		#print "222  i=", i	
		if (i==1) and (self.yMf[i+1]==0):
		    # first mf=triangular
		    self.xMf[i+2] = self.xMf[i]     	
		#if (i == self.numMf-2) and (self.yMf[i-1] == 0):
		if (i == self.numPoints-2) and (self.yMf[i-1] == 0):
		    # last Mf=triangular
		    self.xMf[i-2] = self.xMf[i]
		#if (i>1 and i< self.numMf-2): 
		if (i>1 and i< self.numPoints-2): 
		    # other Mfs
		    if (self.yMf[i]==1) and (self.yMf[i+1]==0) and (self.yMf[i-1]==0): 
			# top of an triangle
			self.xMf[i+2] = self.xMf[i]
			self.xMf[i-2] = self.xMf[i]
		    if (self.yMf[i]==1) and (self.yMf[i+1]==1):
			# left vertex of an trapeze
			self.xMf[i-2] = self.xMf[i] 	
		    if (self.yMf[i]==1) and (self.yMf[i-1]==1):
			# right vertex of an trapeze
			self.xMf[i+2] = self.xMf[i] 
	#print "setCorrectMfValues:: xMf NEU: ", self.xMf
	self.actualizeMfTable()		# writes rows from xMf into tbl
    
    #-------------------------------------------------------------------
    def getMfVector(self):
	# called by: setCorrectMfValues(), showMembership()
	# get x-vertices and y-vertices of all membership functions
	# of the actual input in GUI-Table Page Input
	# delete old vertice-vector, type-list or title-list 
	# print "getMfVector():: makes lists  self.xMf, self.yMf, ..."
	xMf = []
	yMf = []
	mfTitleList = []   
	mfTypeList = []		
	mfRangeList = []
	self.d_in1_mfname_idx.clear()
	self.d_in2_mfname_idx.clear()	
	self.d_in3_mfname_idx.clear()
	row = 0
	anz = 0
	curr = self.ui.inputCombo.currentIndex()	# curr input
	#anz_inp = self.ui.inputCombo.count()
	
	# get values and put them in the special lists
	if curr == 0:
	    row = self.ui.memb1Table.rowCount()
	    #print "getMfVector:: mfTable=0, row1=", row
	    if row>0:
		for i in range(row):
		    #split the range-string and put the separat values in the rangelist
		    range_ = self.ui.memb1Table.item(i,2).text()# QString
		    qli = range_.split(" ")			# QStringList
		    pyli = str(qli.join("\n")).split("\n")	# pylist
		    mfRangeList.append(pyli)
		    type_ = self.ui.memb1Table.item(i,1).text()
		    mfTypeList.append(str(type_))
		    name = str(self.ui.memb1Table.item(i,0).text())
		    mfTitleList.append(name)
		    
		    self.d_in1_mfname_idx[name] = i
		# die 2 andern dicts füllen aus memb2Table und memb3Tbl
		row2 = self.ui.memb2Table.rowCount()
		#print "getMfVector:: row2=", row2
		if row2 > 0:
		    for j in range(row2):
			name = str(self.ui.memb2Table.item(j,0).text())
			self.d_in2_mfname_idx[name] = j
		row3 = self.ui.memb3Table.rowCount()
		#print "getMfVector:: row3=", row3
		if row3 > 0:
		    for j in range(row3):
			name = str(self.ui.memb3Table.item(j,0).text())
			self.d_in3_mfname_idx[name] = j
		    

	elif curr == 1:
	    row= self.ui.memb2Table.rowCount()
	    #print "getMfVector:: mfTable=1,  row1=", row
	    if row>0:
		for i in range(row):
		    range_= self.ui.memb2Table.item(i,2).text()
		    qli = range_.split(" ")			
		    pyli = str(qli.join("\n")).split("\n")	
		    mfRangeList.append(pyli)
		    type_ = self.ui.memb2Table.item(i,1).text()
		    mfTypeList.append(str(type_))
		    name = str(self.ui.memb2Table.item(i,0).text())
		    mfTitleList.append(name)
		    
		    self.d_in2_mfname_idx[name] = i
		# die 2 anderen dicts füllen aus memb1Table und memb3Tbl
		row1 = self.ui.memb1Table.rowCount()
		if row1 > 0:
		    for j in range(row1):
			name = str(self.ui.memb1Table.item(j,0).text())
			self.d_in1_mfname_idx[name] = j
		row3 = self.ui.memb3Table.rowCount()
		if row3 > 0:
		    for j in range(row3):
			name = str(self.ui.memb3Table.item(j,0).text())
			self.d_in3_mfname_idx[name] = j
		     
		    
	elif curr == 2:
	    row= self.ui.memb3Table.rowCount()
	    #print "getMfVector:: mfTable=2,  row1=", row
	    if row>0:
		for i in range(row):
		    range_ = self.ui.memb3Table.item(i,2).text()
		    qli = range_.split(" ")			
		    pyli = str(qli.join("\n")).split("\n")	
		    mfRangeList.append(pyli)
		    type_ = self.ui.memb3Table.item(i,1).text()
		    mfTypeList.append(str(type_))
		    name = str(self.ui.memb3Table.item(i,0).text())
		    mfTitleList.append(name)
		    
		    self.d_in3_mfname_idx[name] = i
		# die 2 andern dicts füllen aus memb1Tbl und memb2Tbl
		row1 = self.ui.memb1Table.rowCount()
		if row1 > 0:
		    for j in range(row1):
			name = str(self.ui.memb1Table.item(j,0).text())
			self.d_in1_mfname_idx[name] = j
		row2 = self.ui.memb2Table.rowCount()
		if row2 > 0:
		    for j in range(row2):
			name = str(self.ui.memb2Table.item(j,0).text())
			self.d_in2_mfname_idx[name] = j
		    
	# put values of the list in the arrays
	for li in mfRangeList:
	    for v in li:
		xMf.append(float(v))
	for typ in mfTypeList:
	    if (typ == "triangular"):
		yMf.append(0)
		yMf.append(1)
		yMf.append(0)
	    else:
		yMf.append(0)
		yMf.append(1)
		yMf.append(1)
		yMf.append(0)
	# umspeichern
	self.numMf = len(mfTypeList)   
	self.xMf = xMf
	self.yMf = yMf
	self.mfTitleList = mfTitleList
	self.mfTypeList  = mfTypeList
	self.numPoints = len(xMf)
	self.mfRangeList = mfRangeList
	#print "getMfVector: mfTypeList: ", mfTypeList
	#print "getMfVector: mfTitleList: ", mfTitleList
	
	#print "getMfVector: d_in1_mfname_idx", self.d_in1_mfname_idx.items()
	#print "getMfVector: d_in2_mfname_idx", self.d_in2_mfname_idx.items()
	#print "getMfVector: d_in3_mfname_idx", self.d_in3_mfname_idx.items()		
	
	#print "getMfVector: mfRangeList:  ", self.mfRangeList
	##print "getMfVector: xMf[]: ", self.xMf
	##print "getMfVector: yMf[]: ", self.yMf
	#print "getMfVector: nr_inp=%d, numMf= %d, numPoints =%d" % (act+1, self.numMf, self.numPoints)
    
    #-------------------------------------------------------------------
    def actualizeMfTable(self):
    	# called by: setCorrectMfValues,   paintwid.mouseReleaseEv
	# Actualize the MfTable depending to the plot
	# takes values from the xMf-array and put them into a string 
	# that is put into the MfTable
	
	#print "actualizeMfTable:: mit xMf : ", self.xMf
	index = 0
	act = self.ui.inputCombo.currentIndex()
	if act == 0:
	    # 1. Input
	    anz = self.ui.memb1Table.rowCount()
	    for i in range(anz):
		type_= self.ui.memb1Table.item(i,1).text()
		
		if type_ == "triangular":
		    range_ = "%.3f %.3f %.3f" % (float(self.xMf[index]),
					    float(self.xMf[index+1]), 
					    float(self.xMf[index+2]))
		    index += 3
		else: 
		    range_ = "%.3f %.3f %.3f %.3f" % (float(self.xMf[index]),
					float(self.xMf[index+1]),
					float(self.xMf[index+2]),
					float(self.xMf[index+3]))
		    index += 4

		rangeItem = QtGui.QTableWidgetItem(self.ui.memb1Table.item(i,2))
		#print i,". TableVal alt:", rangeItem.text()
		rangeItem.setText(range_)
		rangeItem.setTextAlignment(Qt.AlignCenter)
		rangeItem.setFlags(rangeItem.flags() & ~Qt.ItemIsEditable)
		self.ui.memb1Table.item(i,2).setText(range_)
		#print i,". neuer range_:", range_
	elif act == 1:
	    # 2.Input
	    anz = self.ui.memb2Table.rowCount()
	    for i in range(anz):
		type_= self.ui.memb2Table.item(i,1).text()
		if type_== "triangular":
		    range_ = "%.3f %.3f %.3f" % (float(self.xMf[index]),
						 float(self.xMf[index+1]),
						 float(self.xMf[index+2]))
		    index += 3
		else:
		    range_ = "%.3f %.3f %.3f %.3f" % (float(self.xMf[index]),
						float(self.xMf[index+1]),
						float(self.xMf[index+2]),
						float(self.xMf[index+3]))
		    index += 4
		rangeItem = QtGui.QTableWidgetItem(self.ui.memb2Table.item(i,2))
		#print i,". TableVal alt:", rangeItem.text()
		rangeItem.setText(range_)
		rangeItem.setTextAlignment(Qt.AlignCenter)
		rangeItem.setFlags(rangeItem.flags() & ~Qt.ItemIsEditable)
		self.ui.memb2Table.item(i,2).setText(range_)
		#print i,". neuer range_:", range_
	elif act == 2:
	    # 3. Input
	    anz = self.ui.memb3Table.rowCount()
	    for i in range(anz):
		type_= self.ui.memb3Table.item(i,1).text()
		if type_=="triangular":
		    range_ = "%.3f %.3f %.3f" % (float(self.xMf[index]),
						 float(self.xMf[index+1]),
						 float(self.xMf[index+2]))
		    index += 3
		else:
		    range_ = "%.3f %.3f %.3f %.3f" % (float(self.xMf[index]),
						float(self.xMf[index+1]),
						float(self.xMf[index+2]),
						float(self.xMf[index+3]))
		    index+=4
		rangeItem = QtGui.QTableWidgetItem(self.ui.memb3Table.item(i,2))
		#print i,". TableVal alt:", rangeItem.text()
		rangeItem.setText(range_)
		rangeItem.setTextAlignment(Qt.AlignCenter)
		rangeItem.setFlags(rangeItem.flags() & ~Qt.ItemIsEditable)
		self.ui.memb3Table.item(i,2).setText(range_)
		#print i,". neuer range_:", range_

	self.getMfVector()   # edited vals save in mfRangeList, usw.
	
	#print "actualizeMfTable:: self.mfRangeList=", self.mfRangeList
    	changed = True

    #-------------------------------------------------------------------
    def testMfName(self,k,n):
	# int k: Input_index, Qstring n: typ
	# call from newMembership, editMembership
	# tests whether two mfs have the same name -. is not allowed
	name = ""  # QString
	ok = True
	if k == 0:
	    # 1. input
	    row = self.ui.memb1Table.rowCount()
	    if row == 0:
		return(True)
	    for i in range(row):
		name = self.ui.memb1Table.item(i,0).text()
		if name == n:
		    return(False)
	elif k == 1:
	    #2.Input
	    row = self.ui.memb2Table.rowCount()
	    if row == 0:
		return(True)
	    for i in range(row):
		name = self.ui.memb2Table.item(i,0).text()
		if name == n:
		    return(False)
	elif k == 2:
	    #3.Input
	    row = self.ui.memb3Table.rowCount()
	    if row == 0:
		return(True)
	    for i in range(row):
		name = self.ui.memb3Table.item(i,0).text()
		if name == n:
		    return(False)
	return(ok)
	
    #-------------------------------------------------------------------   
    def testMfType(self,k,n):
	# int k, QString n
	# call from newMembership, editMembership
	# tests whether two mfs have the same type in col1 (left, right)
	#  --> is not allowed
	#print "testMfType"
	type_ = ""
	ok = True
	if k == 0:
	    row = self.ui.memb1Table.rowCount()
	    if row == 0: 
		return(True)
	    for i in range(row):
		type_ = self.ui.memb1Table.item(i,1).text()
		if type_ == n:
		    return(False)
	elif k == 1:
	    row = self.ui.memb2Table.rowCount()
	    if row == 0: 
		return(True)
	    for i in range(row):
		type_ = self.ui.memb2Table.item(i,1).text()
		if type_ == n:
		    return(False)
	elif k == 2:
	    row = self.ui.memb3Table.rowCount()
	    if row == 0: 
		return(True)
	    for i in range(row):
		type_ = self.ui.memb3Table.item(i,1).text()
		if type_ == n:
		    return(False)
	return(ok)

    #-------------------------------------------------------------------
    def deleteAllMfs(self):
	# called from: initialize
	row = self.ui.memb1Table.rowCount()
        if row != 0:
	    for i in range(row, -1, -1):
		self.ui.memb1Table.removeRow(i)
	    self.ui.memb1Table.setRowCount(0)
	
	row = self.ui.memb2Table.rowCount()
	if row != 0:
	    for i in range(row, -1, -1):
		self.ui.memb2Table.removeRow(i)
	    self.ui.memb2Table.setRowCount(0)
      
        row = self.ui.memb3Table.rowCount()
	if row != 0:
	    for i in range(row, -1, -1):
		self.ui.memb3Table.removeRow(i)
	    self.ui.memb3Table.setRowCount(0)
	#print "fertig : deleteAllMfs"    
    

    #===================================================================
    #===================================================================
    #===================================================================
    #------ Output   ---------------------------------------------------
    #===================================================================
    
    def insertOutputTable(self, name, val):
	# call by: fileOpen
	nameItem = QtGui.QTableWidgetItem(name)
	nameItem.setText(name)
	nameItem.setTextAlignment(Qt.AlignCenter)
	nameItem.setFlags(nameItem.flags() & ~Qt.ItemIsEditable)
	valItem = QtGui.QTableWidgetItem(val)
	valItem.setText(str(val))
	valItem.setTextAlignment(Qt.AlignCenter)
	valItem.setFlags(valItem.flags() & ~Qt.ItemIsEditable)
	sortItem = QtGui.QTableWidgetItem("sort")
	
	self.ui.outputTable.setColumnWidth(0, 100)
	self.ui.outputTable.setColumnWidth(1, 100)
	row = self.ui.outputTable.rowCount()
	self.ui.outputTable.insertRow(row)
	self.ui.outputTable.setItem(row,0,nameItem)
	self.ui.outputTable.setItem(row,1,valItem)
	sortItem.setText(str(row))  
	self.ui.outputTable.setItem(row,2,sortItem)
	#self.ui.outputTable.resizeColumnToContents(0)

    #-------------------------------------------------------------------
    def sortOutputTable(self):
    	# sorts the output Table --> lowest at the top
	# called by: newOutput, editOutput
	row = self.ui.outputTable.rowCount()
	val= []
	for i in range(row):
	    val.append(float(self.ui.outputTable.item(i,1).text()))
	h = 0
	for i in range(row-1):
	    k = i+1
	    for j in range(k, row): 
		if val[i] >= val[j]: 
		    h = val[i]
		    val[i] = val[j]
		    val[j] = h
		    tmp = self.ui.outputTable.item(i,2).text()  # sort
		    self.ui.outputTable.item(i,2).setText(self.ui.outputTable.item(j,2).text())
		    self.ui.outputTable.item(j,2).setText(tmp)
		    self.ui.outputTable.sortItems(2)
    
    #-------------------------------------------------------------------
    def setOutGrid(self):
	self.outGrid = self.ui.outGridCheck.isChecked()
	self.showOutput()
	#self.changed = True
    
    #-------------------------------------------------------------------
    def getOutputVector(self):
	# called by: showOutput, showTrainedOutputs, switchTab=3 Analysis
	# read the GUI Table in Page Output
	del self.outTitleList[:]
	del self.xOut[:] 
	del self.yOut[:]    # dummy f. koordsystem
	row = self.ui.outputTable.rowCount()
	if row > 0:
	    for i in range(row):
		self.outTitleList.append(str(self.ui.outputTable.item(i,0).text()))
		self.xOut.append(round(float(self.ui.outputTable.item(i,1).text()), 2))
		self.yOut.append(0)   # dummy
	#print "getOutputVector:: outTitleList", self.outTitleList
	#print "getOutputVector:: xOut", self.xOut
	#print "getOutputVector:: yOut", self.yOut
	
    #------------------------------------------------------------------
    def showOutput(self):
	# called by: switchTabs, setOutGrid, editOutput, "
	# plots the singletons of the output

	# delete old graphic
	self.ui.outputwid.dia.clear_plot()   
	self.numOut = self.ui.outputTable.rowCount()
	# get actual singleton values from the outputTable
	self.getOutputVector()
	   
	self.numCurves = len(self.mfTypeList)  
	self.numPoints = len(self.xMf)   	
	xname = str(self.ui.outputLE.text())
	#print "showOutput:: xname=", xname
	
	# outputwid was mapped in GUI the file paintoutput.py 
	# has: class PaintOutput and class DiagrOut
	self.ui.outputwid.dia.setLists(self.outTitleList,
				    self.xOut, self.yOut, self.numOut,
				    xname, self.outGrid, self)
	self.ui.outputwid.dia.plot()
	
    #-------------------------------------------------------------------
    def deleteOutputTable(self):
	# called by: initialize
	row = self.ui.outputTable.rowCount()
        if row != 0:
	    for i in range(row, -1, -1):
		self.ui.outputTable.removeRow(i)
	    self.ui.outputTable.setRowCount(0)
    
    #-------------------------------------------------------------------
    def newOutput(self):
	# called by: Button 'New'
	self.editOutWin = editoutputdialog.EditOutputDialog()
	if self.editOutWin.exec_():
	    # get name and singleton value from editing window
	    out = self.editOutWin.ui.outLE.text()
	    value = self.editOutWin.ui.valueLE.text()
	
	    # test if there already exist a output with same name
	    ok = self.testOutputName(out)
	    # put name and singleton value into the outputTable
	    row = self.ui.outputTable.rowCount()
	    if ok == True:
		valueItem = QTableWidgetItem(value)
		valueItem.setText(value)
		valueItem.setTextAlignment(Qt.AlignCenter)
		valueItem.setFlags(valueItem.flags() & ~Qt.ItemIsEditable)
		nameItem = QTableWidgetItem(out)
		nameItem.setText(out)
		nameItem.setTextAlignment(Qt.AlignCenter)
		nameItem.setFlags(nameItem.flags() & ~Qt.ItemIsEditable)
		sortItem = QTableWidgetItem(QString.number(row))
		
		self.ui.outputTable.insertRow(row)
		self.ui.outputTable.setItem(row,0,nameItem)
		self.ui.outputTable.setItem(row,1,valueItem)
		self.ui.outputTable.setItem(row,2,sortItem)
	    else:
		self.info(QString(" '%1' already exists!").arg(out))
		return
	self.sortOutputTable()
	self.setRuleCombo() # adjust ComboTableItem in the rulesTable
	self.showOutput()
	del self.editOutWin
	self.changed = True
    
    #-------------------------------------------------------------------
    def editOutput(self):
	# called by: Button Edit and SLOT cellDoubleClicked in outputTbl
	# selected tblrow  
	row = self.ui.outputTable.currentRow()
	if row == -1:
	    return
	# opens window for editing an output"
	self.editOutWin = editoutputdialog.EditOutputDialog()
	anz = self.ui.outputTable.rowCount()
	if (anz<=0):
	    return
	# put all outputs into an array 
	outList = []  
	for i in range(anz):
	    outList.append(self.ui.outputTable.item(i,0).text())
	    #value= self.ui.outputTable.item(i,1).text()

	# get values of the selected output
	out_orig = QString()
	out_orig = self.ui.outputTable.item(row,0).text()
	value = self.ui.outputTable.item(row,1).text()
	
	# put output-values into the fields
	self.editOutWin.ui.outLE.setText(out_orig)
	self.editOutWin.ui.valueLE.setText(value)
	if self.editOutWin.exec_():
	    # get new values
	    out_new = QString()
	    out_new  = self.editOutWin.ui.outLE.text()	# edited name
	    value = self.editOutWin.ui.valueLE.text()	# edited value
	    nameItem = QTableWidgetItem("Singleton")	
	    valueItem = QTableWidgetItem("Value")
	    nameItem = 0
	    valueItem = 0
	    nameItem = self.ui.outputTable.item(row,0)
	    valueItem = self.ui.outputTable.item(row,1)
	    valueItem.setText(value)
	    self.sortOutputTable() 
	
	    # test if new name already exist
	    if out_new != out_orig:
		ok = self.testOutputName(out_new)
		if ok == True:
		    nameItem.setText(out_new)
		else:
		    self.info(QString(" '%1' already exists !").arg(out_orig))
		    return
	    
	    # put all output into a new QStringList
	    outs = QStringList()    
	    for i in range(self.ui.outputTable.rowCount()):
		outs.append(self.ui.outputTable.item(i,0).text())
	    
	    # rulesTable: actualize the ComboBox
	    o = QString()
	    for i in range(self.ui.rulesTable.rowCount()):
		box = self.ui.rulesTable.cellWidget(i,3) 
		o = box.currentText()	
		idx = box.currentIndex()
		if o == out_orig: 
		    o = out_new
		box.clear()
		box.addItems(outs) #fill with QStringList, default idx=0
		index = box.findText(o)
		box.setCurrentIndex(index)
	
	del self.editOutWin	
	self.sortOutputTable()
	self.changed = True
	self.showOutput()

    #-------------------------------------------------------------------
    def deleteOutput(self):
	# SLOT Button 'Remove'
	#print "deleteOutput"
	row = self.ui.outputTable.currentRow()
	self.ui.outputTable.removeRow(row)
	# adjust the comboTableItem of the rules Table
	self.setRuleCombo()
	self.showOutput()
	self.changed = True

    #-------------------------------------------------------------------
    def testOutputName(self, name):
	# called by: editOutput
	# tests, if two outputs have the same name
	ok = False
	row = self.ui.outputTable.rowCount()
	if row == 0:
	    return(True)
	else:
	    # searching the table for name
	    for i in range(row):
		n = self.ui.outputTable.item(i,0).text()
		if n == name:
		    return(False)
		else:
		    ok = True
	return ok

    #-------------------------------------------------------------------
    def actualizeOutputTable(self):
	# called by: paintoutput.py
	# actualize changes in the table made in the plot by mouse
	row = self.ui.outputTable.rowCount()
	range_ = QString()
	for index in range(row):
	    # get actual vertices from vertex-array
	    range_ = "%.3f" % (float(self.xOut[index]))
	    # put values in the outputTable
	    rangeItem = QtGui.QTableWidgetItem(self.ui.outputTable.item(index,1))
	    rangeItem.setText(range_)
	    rangeItem.setTextAlignment(Qt.AlignCenter)
	    rangeItem.setFlags(rangeItem.flags() & ~Qt.ItemIsEditable)
	    self.ui.outputTable.item(index,1).setText(range_)
	    #~ #outItem = self.ui.outputTable.item(i,1)
	    #~ #outItem.setText(range_);
	self.getOutputVector()   # save edited values
	self.changed=True

    #-------------------------------------------------------------------
    def newOutputName(self):
	# SLOT of outputLE: activated by outputLineEdit (enter pressed)
	name = self.ui.outputLineEdit.text()
	if name.isEmpty():
	    self.info("Output name missed!")
	    self.ui.outputLineEdit.setText("Output")
	self.showOutput()
    
    #-------------------------------------------------------------------
    def ignoreSpaceOut(self):
	# SLOT of outputLE: replaces a "space" within the name
	s = self.ui.outputLE.text()
	pos = s.indexOf(" ",0,Qt.CaseSensitive)
	if pos >= 0:
	    s = s.replace(pos,1,"_")
	self.ui.outputLE.setText(s)
    
     
    #===================================================================
    #===================================================================
    #===================================================================
    #---------   RULES -------------------------------------------------
    #===================================================================

    def insertRulesTable(self, outList, tupel):
	# called by: fileOpen
	# tupel = (x, (y,) (z,) o, cf)   (inp1, inp2, inp3, out, cf)
	#print "outList= ", outList 		# ['s', 'ms',....]
	#print "tupel= ", tupel
	#print "self.numInput= ", self.numInput
	
	# put rules into rulesTable
	row = self.ui.rulesTable.rowCount()
	self.ui.rulesTable.insertRow(row)
	self.ui.rulesTable.setRowHeight(row, 24)
	# create ComboTableItem for output-column in the rulesTable
	cb = QtGui.QComboBox(self.ui.rulesTable)
	cb.setObjectName("cbobj")
	cb.addItems(outList)
	
	# put values into table
	if self.numInput == 1: 
	    #input
	    x = tupel[0]
	    mfX = self.getMfName(0,x)
	    item = QtGui.QTableWidgetItem('input1')
	    item.setText(mfX)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable) # readOnly
	    self.ui.rulesTable.setItem(row,0,item)
	    #output
	    o = tupel[1]
	    cb.setCurrentIndex(o)
	    self.ui.rulesTable.setCellWidget(row, 3, cb)
	    #cf
	    cf = tupel[2]
	    item = QtGui.QTableWidgetItem('cf')
	    item.setText(str(cf))
	    item.setTextAlignment(Qt.AlignCenter)
	    self.ui.rulesTable.setItem(row,4,item)
	    # set colums hidden
	    self.ui.rulesTable.hideColumn(1)
	    self.ui.rulesTable.hideColumn(2)
	
	elif self.numInput == 2:
	    x = tupel[0]
	    mfX = self.getMfName(0,x)
	    item = QtGui.QTableWidgetItem('input1')
	    item.setText(mfX)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.rulesTable.setItem(row,0,item)		    
	    # input2
	    y = tupel[1]
	    mfY = self.getMfName(1,y)
	    item = QtGui.QTableWidgetItem('input2')
	    item.setText(mfY)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.rulesTable.setItem(row,1,item)
	    #output
	    o = tupel[2]
	    cb.setCurrentIndex(o)
	    self.ui.rulesTable.setCellWidget(row, 3, cb)
	    #cf
	    cf = tupel[3]
	    item = QtGui.QTableWidgetItem("cf")
	    item.setText(str(cf))
	    item.setTextAlignment(Qt.AlignCenter)
	    self.ui.rulesTable.setItem(row,4,item)
	    self.ui.rulesTable.showColumn(1)
	    self.ui.rulesTable.hideColumn(2)
	    
	elif self.numInput == 3:
	    #input1
	    x = tupel[0]
	    mfX = self.getMfName(0,x)
	    item = QtGui.QTableWidgetItem('input1')
	    item.setText(mfX)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.rulesTable.setItem(row,0,item)		    
	    # input2
	    y = tupel[1]
	    mfY = self.getMfName(1,y)
	    item = QtGui.QTableWidgetItem('input2')
	    item.setText(mfY)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.rulesTable.setItem(row,1,item)
	    #input3
	    z = tupel[2]
	    mfZ = self.getMfName(2,z)
	    item = QtGui.QTableWidgetItem("input3")
	    item.setText(mfZ)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.rulesTable.setItem(row,2,item)
	    #output
	    o = tupel[3]
	    cb.setCurrentIndex(o)
	    self.ui.rulesTable.setCellWidget(row, 3, cb)
	    #cf
	    cf = tupel[4]
	    item =  QTableWidgetItem("cf")
	    item.setText(str(cf))
	    item.setTextAlignment(Qt.AlignCenter)
	    self.ui.rulesTable.setItem(row, 4, item)
	    self.ui.rulesTable.showColumn(1)
	    self.ui.rulesTable.showColumn(2)
	self.setRulesTableLabel()
	    
    #-------------------------------------------------------------------
    def insertMfIntoRulesTable(self, ind, name):
    	# called by: 	newMembership
	# int ind: 	index of current Input
	# QString name:	name of current Input

	if self.ui.rulesTable.rowCount() == 0:
	    return
	#QStringList input1, input2, input3, output 
	# lists include all edited mf or output
	input1 = []
	input2 = []
	input3 = []
	output = []
	for i in range(self.ui.memb1Table.rowCount()): 
	    input1.append(str(self.ui.memb1Table.item(i,0).text()))
	for i in range(self.ui.memb2Table.rowCount()): 
	    input2.append(str(self.ui.memb2Table.item(i,0).text()))
	for i in range(self.ui.memb3Table.rowCount()): 
	    input3.append(str(self.ui.memb3Table.item(i,0).text()))
	for i in range(self.ui.outputTable.rowCount()):
	    output.append(str(self.ui.outputTable.item(i,0).text()))
	row = self.ui.rulesTable.rowCount()
	
	# add rules  (ind=actual input)
	if self.numInput == 1:  # IF mf1 THEN output
	    self.ui.rulesTable.insertRow(row)
	    self.ui.rulesTable.setRowHeight(row, 24)
	    # input1
	    item = QTableWidgetItem("input1")
	    item.setText(name)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.rulesTable.setItem(row,0,item)
	    # output
	    box = QComboBox(self.ui.rulesTable)
	    box.addItems(output)
	    self.ui.rulesTable.setCellWidget(row,3,box)
	    # CF
	    cfItem = QTableWidgetItem("cf")
	    cfItem.setText("1.0")
	    cfItem.setTextAlignment(Qt.AlignCenter)
	    self.ui.rulesTable.setItem(row,4,cfItem)
	    
	elif self.numInput == 2:
	    if ind == 0:   # rule (IF name AND mf2 THEN output)
		for nam2 in input2:
		    self.ui.rulesTable.insertRow(row)
		    self.ui.rulesTable.setRowHeight(row, 24)
		    # input1
		    item = QTableWidgetItem("input1")
		    item.setText(name)
		    item.setTextAlignment(Qt.AlignCenter)
		    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
		    self.ui.rulesTable.setItem(row,0,item)
		    # input2
		    item = QTableWidgetItem("input2")
		    item.setText(nam2)
		    item.setTextAlignment(Qt.AlignCenter)
		    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
		    self.ui.rulesTable.setItem(row,1,item)
		    # output
		    box = QComboBox(self.ui.rulesTable)	# new combo
		    box.addItems(output)
		    self.ui.rulesTable.setCellWidget(row,3,box)
		    # cf
		    cfItem = QTableWidgetItem("cf")
		    cfItem.setText("1.0")
		    cfItem.setTextAlignment(Qt.AlignCenter)
		    self.ui.rulesTable.setItem(row,4,cfItem)
		    row += 1
	    else:
		# rule (IF mf1 AND name THEN output)
		for nam1 in input1:
		    self.ui.rulesTable.insertRow(row)
		    self.ui.rulesTable.setRowHeight(row, 24)
		    # input 1
		    item = QTableWidgetItem("input1")
		    item.setText(nam1)
		    item.setTextAlignment(Qt.AlignCenter)
		    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
		    self.ui.rulesTable.setItem(row,0,item)
		    # input 2
		    item = QTableWidgetItem("input2")
		    item.setText(name)
		    item.setTextAlignment(Qt.AlignCenter)
		    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
		    self.ui.rulesTable.setItem(row,1,item)
		    # output
		    box = QComboBox(self.ui.rulesTable)
		    box.addItems(output)
		    self.ui.rulesTable.setCellWidget(row,3,box)
		    # cf
		    cfItem = QTableWidgetItem("cf")
		    cfItem.setText("1.0")
		    cfItem.setTextAlignment(Qt.AlignCenter)
		    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
		    self.ui.rulesTable.setItem(row,4,cfItem)
		    row += 1

	elif self.numInput == 3:
	    if ind == 0:
		# rule (IF name AND mf2 AND mf3 THEN output)
		for nam2 in input2:
		    for nam3 in input3:
			self.ui.rulesTable.insertRow(row)
			self.ui.rulesTable.setRowHeight(row, 24)
			# input1
			item = QTableWidgetItem("input1")
			item.setText(name)
			item.setTextAlignment(Qt.AlignCenter)
			item.setFlags(item.flags() & ~Qt.ItemIsEditable)
			self.ui.rulesTable.setItem(row,0,item)
			# input2
			item = QTableWidgetItem("input2")
			item.setText(nam2)
			item.setTextAlignment(Qt.AlignCenter)
			item.setFlags(item.flags() & ~Qt.ItemIsEditable)
			self.ui.rulesTable.setItem(row,1,item)
			# input3
			item = QTableWidgetItem("input3")
			item.setText(nam3)
			item.setTextAlignment(Qt.AlignCenter)
			item.setFlags(item.flags() & ~Qt.ItemIsEditable)
			self.ui.rulesTable.setItem(row,2,item)
			# output
			box = QComboBox(self.ui.rulesTable)
			box.addItems(output)
			self.ui.rulesTable.setCellWidget(row,3,box)
			# cf
			cfItem = QTableWidgetItem("cf")
			cfItem.setText("1.0")
			cfItem.setTextAlignment(Qt.AlignCenter)
			self.ui.rulesTable.setItem(row,4,cfItem)
			row += 1
	    elif ind == 1:
		#rule (IF mf1 AND name AND mf3 THEN output)
		for nam1 in input1:
		    for nam3 in input3:
			self.ui.rulesTable.insertRow(row)
			self.ui.rulesTable.setRowHeight(row, 24)
			# input 1
			item = QTableWidgetItem("input1")
			item.setText(nam1)
			item.setTextAlignment(Qt.AlignCenter)
			item.setFlags(item.flags() & ~Qt.ItemIsEditable)
			self.ui.rulesTable.setItem(row,0,item)
			# input 2
			item = QTableWidgetItem("input2")
			item.setText(name)
			item.setTextAlignment(Qt.AlignCenter)
			item.setFlags(item.flags() & ~Qt.ItemIsEditable)
			self.ui.rulesTable.setItem(row,1,item)
			# input3
			item = QTableWidgetItem("input3")
			item.setText(nam3)
			item.setTextAlignment(Qt.AlignCenter)
			item.setFlags(item.flags() & ~Qt.ItemIsEditable)
			self.ui.rulesTable.setItem(row,2,item)
			# output
			box = QComboBox(self.ui.rulesTable)
			box.addItems(output)
			self.ui.rulesTable.setCellWidget(row,3,box)
			# cf
			cfItem = QTableWidgetItem("cf")
			cfItem.setText("1.0")
			cfItem.setTextAlignment(Qt.AlignCenter)
			self.ui.rulesTable.setItem(row,4,cfItem)
			row += 1
	    elif ind == 2:
		#rule (IF mf1 AND mf2 AND name THEN output)
		for nam1 in input1:
		    for nam2 in input2:
			self.ui.rulesTable.insertRow(row)
			self.ui.rulesTable.setRowHeight(row, 24)
			# input 1
			item = QTableWidgetItem("input1")
			item.setText(nam1)
			item.setTextAlignment(Qt.AlignCenter)
			item.setFlags(item.flags() & ~Qt.ItemIsEditable)
			self.ui.rulesTable.setItem(row,0,item)
			# input 2
			item = QTableWidgetItem("input2")
			item.setText(nam2)
			item.setTextAlignment(Qt.AlignCenter)
			item.setFlags(item.flags() & ~Qt.ItemIsEditable)
			self.ui.rulesTable.setItem(row,1,item)
			# input3
			item = QTableWidgetItem("input3")
			item.setText(name)
			item.setTextAlignment(Qt.AlignCenter)
			item.setFlags(item.flags() & ~Qt.ItemIsEditable)
			self.ui.rulesTable.setItem(row,2,item)
			# output
			box = QComboBox(self.ui.rulesTable)
			box.addItems(output)
			self.ui.rulesTable.setCellWidget(row,3,box)
			# cf
			cfItem = QTableWidgetItem("cf")
			cfItem.setText("1.0")
			cfItem.setTextAlignment(Qt.AlignCenter)
			self.ui.rulesTable.setItem(row,4,cfItem)
			row += 1 

    #-------------------------------------------------------------------
    def setRuleCombo(self):
	# called by: newOutput
	# if new rules were generated because of editing an mf  
	# insert a comboTableItem into the ruleTable (output)
	# get all mf-names of the output
	outs = []
	for i in range(self.ui.outputTable.rowCount()):
	    outs.append(self.ui.outputTable.item(i,0).text())

	# insert new ComboTableItem into the rulesTable
	#o = QString()
	for i in range(self.ui.rulesTable.rowCount()):
	    box = self.ui.rulesTable.cellWidget(i,3)
	    o = box.currentText()     
	    # remember current item
	    box.clear()
	    box.addItems(outs)
	    index = box.findText(o)
	    box.setCurrentIndex(index)
	self.changed = True

    #-------------------------------------------------------------------
    def setRulesTableLabel(self):
	# called by: switchTab, generateRules, insertRulesTable...
	#sets the horizontal header of the rulesTable
	self.ui.rulesTable.resizeColumnToContents(2)
	self.ui.rulesTable.resizeColumnToContents(3)
	if self.numInput >= 1:
	    item1 = self.ui.rulesTable.horizontalHeaderItem(0)
	    item1.setText(self.ui.inputCombo.itemText(0))
	    self.ui.rulesTable.resizeColumnToContents(0)
	    self.ui.rulesTable.resizeColumnToContents(1)
	if self.numInput >= 2:
	    item2 = self.ui.rulesTable.horizontalHeaderItem(1)
	    item2.setText(self.ui.inputCombo.itemText(1))
	    self.ui.rulesTable.resizeColumnToContents(2)
  	if self.numInput == 3:
	    item3 = self.ui.rulesTable.horizontalHeaderItem(2)
	    item3.setText(self.ui.inputCombo.itemText(2))
	    self.ui.rulesTable.resizeColumnToContents(3)
	outputItem = self.ui.rulesTable.horizontalHeaderItem(3)
	outputItem.setText(self.ui.outputLE.text())
	cfItem = self.ui.rulesTable.horizontalHeaderItem(4)
	cfItem.setText("cf")
    
    #-------------------------------------------------------------------
    def controllCf(self):	
	# SLOT if cf value is changed in the rulesTable 
	col = self.ui.rulesTable.currentColumn()
	row = self.ui.rulesTable.currentRow()
    	# tests if conversion of cf -value from table is correct
	# test 0 <= cf <= 1
	print "controllCf: col=", col
	if (col == 4):
	    cfItem = self.ui.rulesTable.item(row,col)
	    try:
		cf = float(self.ui.rulesTable.item(row,col).text())
		if (cf<=0):
		    cfItem.setText("0")
		if (cf>=1):
		    cfItem.setText("1.0")
	    except:
		cfItem.setText("1.0")
		
    #-------------------------------------------------------------------
    def set_cf_column(self):
	# called by: btn_cf 
	# overwrite cf in column, to use after Rules Training
	anz = self.ui.rulesTable.rowCount()
	for row in xrange(anz):
	    cf = '1.0'
	    item = QTableWidgetItem('cf')
	    item.setText(cf)   
	    item.setTextAlignment(Qt.AlignCenter)
	    #item.setTextAlignment(Qt.AlignVCenter)
	    self.ui.rulesTable.setItem(row,4,item)
   
    #-------------------------------------------------------------------
    def generateRules(self):
	# called by rulesPB - generates rules for a edited fuzzy model
	row = self.ui.rulesTable.rowCount()
	if row!=0:
	    ans = QtGui.QMessageBox.warning(self,"Warning",
		"Do you really want to generate  Rules? \nActual Rules will be lost!",
		QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes) 
	    if ans  == QtGui.QMessageBox.No:
		return
	
	# clear rulesTable complete
	for k in range(row):
	    self.ui.rulesTable.removeRow(0)
    
	# put edited membership functions and output-singletons into lists
	input1 = []
	input2 = []
	input3 = []
	output = []
	# input 1
	row1 = self.ui.memb1Table.rowCount()
	for i in range(row1):
	    input1.append(self.ui.memb1Table.item(i,0).text())
    	input1.reverse()   		# Reihenfolge umkehren
	# input 2
	row2 = self.ui.memb2Table.rowCount()
	for i in range(row2):
	    input2.append(self.ui.memb2Table.item(i,0).text())
	input2.reverse()
	# input 3
	row3 = self.ui.memb3Table.rowCount()
	for i in range(row3):
	    input3.append(self.ui.memb3Table.item(i,0).text())
	input3.reverse()
	# output
	rowOut = self.ui.outputTable.rowCount()
	for i in range(rowOut):
	    output.append(self.ui.outputTable.item(i,0).text())
        
	# Generates rules depending on number of inputs
	row=0
	if self.numInput == 1:
	    if row1 == 0:
		info("There must be defined a membershipfunction for input1 !")
	    else:
		val1 = []
		for i in range(len(input1)):
		    val1.append(input1[i])
		    self.ui.rulesTable.insertRow(row)
		    self.ui.rulesTable.setRowHeight(row, 24)
		    inputItem = QTableWidgetItem("input1")
		    inputItem.setText(val1[i])
		    inputItem.setTextAlignment(Qt.AlignCenter)
		    self.ui.rulesTable.setItem(row,0,inputItem)
		    #output
		    box = QtGui.QComboBox(self.ui.rulesTable)
		    box.addItems(output)   # default idx=0
		    self.ui.rulesTable.setCellWidget(row,3,box)
		    # cf
		    cfItem = QTableWidgetItem("cf")
		    cfItem.setText("1.0")
		    cfItem.setTextAlignment(Qt.AlignCenter)
		    self.ui.rulesTable.setItem(row,4,cfItem)
	elif self.numInput == 2:
	    if row2 == 0: 
		info("There must be defined a membershipfunction for each input")
	    else:
		val1 = []
		val2 = []
		for i in range(len(input1)):
		    #iterator1
		    val1.append(input1[i])
		    for j in range(len(input2)):
			#iterator2
			val2.append(input2[j])
			self.ui.rulesTable.insertRow(row)
			self.ui.rulesTable.setRowHeight(row, 24)
			input1Item = QTableWidgetItem("input1")
			input1Item.setText(val1[i])
			input1Item.setTextAlignment(Qt.AlignCenter)
			self.ui.rulesTable.setItem(row,0,input1Item)
			# input2
			input2Item =  QTableWidgetItem("input2")
			input2Item.setText(val2[j])
			input2Item.setTextAlignment(Qt.AlignCenter)
			self.ui.rulesTable.setItem(row,1,input2Item)
			# output
			box = QtGui.QComboBox(self.ui.rulesTable) # create new combo
			box.addItems(output)	# default idx=0
			self.ui.rulesTable.setCellWidget(row,3,box) # set it 
			# cf
			cfItem = QTableWidgetItem("cf")
			cfItem.setText("1.0")
			cfItem.setTextAlignment(Qt.AlignCenter)
			self.ui.rulesTable.setItem(row,4,cfItem)
	elif self.numInput == 3:
	    if row2== 0 or row3 == 0: 
		info("There must be defined a membershipfunction for each input")
	    else:
		val1 = []
		val2 = []
		val3 = []
		for i in range(len(input1)):
		    #iterator1
		    val1.append(input1[i])
		    for j in range(len(input2)):
			#iterator2
			val2.append(input2[j])
			for k in range(len(input3)):
			    #iterator3
			    val3.append(input3[k])
			    self.ui.rulesTable.insertRow(row)
			    self.ui.rulesTable.setRowHeight(row, 24)
			    # input1
			    input1Item = QTableWidgetItem("input1")
			    input1Item.setText(val1[i])
			    input1Item.setTextAlignment(Qt.AlignCenter)
			    self.ui.rulesTable.setItem(row,0,input1Item)
			    # input2
			    input2Item = QTableWidgetItem("input2")
			    input2Item.setText(val2[j])
			    input2Item.setTextAlignment(Qt.AlignCenter)
			    self.ui.rulesTable.setItem(row,1,input2Item)
			    # input3
			    input3Item = QTableWidgetItem("input3")
			    input3Item.setText(val3[k])
			    input3Item.setTextAlignment(Qt.AlignCenter)
			    self.ui.rulesTable.setItem(row,2,input3Item)
			    # output
			    box = QtGui.QComboBox(self.ui.rulesTable)
			    box.addItems(output)
			    self.ui.rulesTable.setCellWidget(row,3,box)
			    # cf		    
			    cfItem = QTableWidgetItem("cf")
			    cfItem.setText("1.0")
			    cfItem.setTextAlignment(Qt.AlignCenter)
			    self.ui.rulesTable.setItem(row,4,cfItem)
	self.setRulesTableLabel()   # horizontalHeader 
	self.changed = True
    
    #-------------------------------------------------------------------
    def getRulesVector(self):
	# called by: switchTabs 3=Analyse, 4=Calcul. 5=Train
	# read the GUI Table in Page Rules
	li_rules = []
	rows = self.ui.rulesTable.rowCount()
	anz_inp = self.ui.inputCombo.count()
	cbox = QComboBox()
	for i in range(rows):
	    li_val = []
	    if anz_inp == 1:
		# col 1 and 2 hidden
		cols = 3
		name = str(self.ui.rulesTable.item(i,0).text())
		li_val.append(self.d_in1_mfname_idx[name])  # idx
	    if anz_inp > 1:
		cols = 4
		name = str(self.ui.rulesTable.item(i,0).text())
		li_val.append(self.d_in1_mfname_idx[name])  
		name = str(self.ui.rulesTable.item(i,1).text())
		li_val.append(self.d_in2_mfname_idx[name])  
	    if anz_inp == 3:
		cols = 5
		name = self.ui.rulesTable.item(i,2).text() 
		if name.isEmpty():	
		    name = "%s" % ""	
		    li_val.append(self.d_in3_mfname_idx[name]) 
		else:
		   li_val.append(self.d_in3_mfname_idx[str(name)])  

	    cbox = self.ui.rulesTable.cellWidget(i,3)
	    output = cbox.currentIndex()    
	    li_val.append(output)
	    cf =  round(float(self.ui.rulesTable.item(i,4).text()),1)
	    li_val.append(cf) 
	    li_rules.append(li_val)  
	return li_rules
	# [0, 0, 6, 1.0]   in1,in2,out,cf
	# [0, 1, 6, 1.0]
	# [0, 2, 5, 1.0]
	# [1, 0, 6, ...]
	
    #-------------------------------------------------------------------
    def deleteAllRules(self):
	# called from: initialize
	row = self.ui.rulesTable.rowCount()
        if row != 0:
	    for i in range(row, -1, -1):
		self.ui.rulesTable.removeRow(i)
	    self.ui.rulesTable.setRowCount(0)

    #======== END Rules ================================================
    #===================================================================
    
    
    #===================================================================    
    #========== Menu and ToolBar =======================================
    #===================================================================
    
    #---- FILE ---------------------------------------------------------
    def fileNew(self):
	# called by: fileNewAction
	# clear all table and set default values
	if self.okToSave() == False:
	    return
	self.initialize(2)
	self.filename = ""
	self.setWindowTitle("SAMT2 - Fuzzy ")
	self.ui.inputCombo.setItemText(0,"Input1")
	
	# initialization of input page - diagramm
	self.ui.paintwid.dia.clear_plot()  # delete old plot
	del self.xMf[:]	  # x-value vector of the memberships
	del self.yMf[:]	  # y    " 
	self.numMf = 0
	self.showMembership()
	
	# initialization of output page - diagramm
	self.ui.outputwid.dia.clear_plot()  # delete old plot
	del self.xOut [:]	# x-vertices of singleton
	
	# initialization of analysis page - diagramm ?
    
    #-------------------------------------------------------------------
    def fileOpen(self):
	# self.openedModelPath write only here
	if self.okToSave() == False:
	    return
	modelname = ""
	fname = ""
	try:
	    fname = QtGui.QFileDialog.getOpenFileName(self, 
			    "SAMT2 - Fuzzy ----- File Open", 
			    self.path_save_data,
			    "Fuzzy Model Files (*.fis);;All Files (*)")
	except IOError:
	    self.ui.statusbar.showMessage("Error: File Open abandoned",2000)
	
	if fname.isEmpty(): 
	    self.openedModelPath = QString("")	 # write only here ! 
	else:
	    if self.ui.memb1Table.rowCount() > 0:
		# it's not the first fileOpen
		# clear all table and set default values
		self.initialize(1)

	    self.path_save_data, self.open_modelname = os.path.split(str(fname))
	    self.openedModelPath = fname  # write only here !
	    self.ui.inputCombo.clear()
	    li2 = self.open_modelname.split('.')   
	    modelname = self.work.add_model_fuz(str(fname), str(li2[0]))
	    print "modelname=", modelname
	    
	    # list of input-obj
	    li_inp,li_outp,li_rule = self.work.get_lists_in_out_rule(modelname)  
	    
	    del self.xMf[:]
	    del self.yMf[:]
	    del self.xOut[:]
	    # load members 
	    for i in range(len(li_inp)):
		nam = self.work.get_name_of_input(modelname, i)
		self.ui.inputCombo.addItem(nam)  
		li_memb = self.work.get_members_of_input(li_inp[i])
		# fills xMf, yMf, membertables
		self.load_member(li_memb, i) 
	    self.numInput = len(li_inp)		
	    self.ui.numInSpin.setValue(i+1)
	    
	    # load outputs
	    oname = self.work.get_name_of_output()
	    self.ui.outputLE.setText(oname) 	# only 1 output 
	    outList = []
	    for o in li_outp:
		name = self.work.get_outp_name_singleton(o)
		val  = self.work.get_outp_val(o)
		val = "%.3f" % val
		outList.append(name) # for Output-Combobox in rulesTable
		self.insertOutputTable(name,val)
	    self.upd_verticalHeaderLabel(self.ui.outputTable, len(li_outp))
	    
	    # load rules
	    for r in li_rule:
		tupel = self.work.get_rule(r)  
		self.insertRulesTable(outList, tupel)
	    self.upd_verticalHeaderLabel(self.ui.rulesTable, len(li_rule))
		
	self.ui.lbl_fisname.setText(modelname) 
	self.setWindowTitle(QString("SAMT2 - Fuzzy ----- %1").arg(fname))
	msg = "Loaded: %s" % fname
	self.ui.statusbar.showMessage(msg, 3000)
	self.changed = False
	self.setCorrectMfValues() 
	self.showMembership()     
    
    #-------------------------------------------------------------------
    def okToSave(self):
	#tests if fuzzy model can be saved
	if self.changed:
	    fname = self.openedModelPath	# wrote in fileOpen only
	    if fname == '':
		msg = QString("Unnamed Fuzzysets ")
	    else:
		msg = QString( "Fuzzy '%1'\n" ).arg(QString(fname))
	    msg += QString( "has been changed." )
	    ans = QMessageBox.warning(self,"Fuzzy Tool -- Unsaved Changes",
				msg, "&Save", "Cancel", "&Abandon", 0,1)
	    if ans == 0:
		self.fileSave()
	    elif ans == 1:
		return False
	    return True

    #-------------------------------------------------------------------
    def fileSave(self):
	# called by: menu, action, okToSave, fileSaveAs
	fname = self.openedModelPath
	if QString(fname).isEmpty():    # == None or fname == '':	
	    self.fileSaveAs()
	    return		
	    
	self.fuzzy_refresh()	
		
	if self.isModelComplete() == False:
	    print "fileSave::  isModelComplete = False "
	    return
    
	if self.work.model_file_store(fname) == True:
	    print "fileSave:: " + fname + " was saved "
	else:
	    print "Error fileSave:: while store_model ", fname
    
    #-------------------------------------------------------------------
    def isModelComplete(self):
	# check, if fuzzy model is complete
	# complete means: not less then 2 members per Input and
	#	    	  not less then 2 Outputs       
	li = self.work.get_inpu()
	genug = False
	i = 1
	for inp in li:
	    li_memb = self.work.get_members_of_input(inp)
	    if len(li_memb) > 1:
		genug = True
	    else:
		genug = False
		break
	    i += 1
	    
	if genug == False:
	    print "isModelComplete:: Error: less then 2 members in the %d. Input" % i
	    return False
	
	anz_out = self.work.get_len_outp()       
	if anz_out < 2:
	    print "isModelComplete:: error: less then 2 Outputs"
	    return False
	return True
	
    #-------------------------------------------------------------------
    def fileSaveAs(self):
	# called by: menu, action, fileSave (if fileNew)
	fname = ""
	try:
	    fname = QFileDialog.getSaveFileName(self,
			"SAMT2 - Fuzzy ----- Save File As",	    
			self.path_save_data,
			"Fuzzy Files (*.fis);;All Files (*)")
	except IOError:
	    self.ui.statusbar.showMessage("Error: File SaveAs abandoned",2000)
	if not fname.isEmpty():
	    
	    self.fuzzy_refresh()	# ab 1.2.
	    
	    if self.isModelComplete() == False:
		print "Error fileSaveAs::  Model is not complete"
		return
	
	    if self.work.model_file_store(fname) == True:
		print "fileSaveAs:: " + fname + " was saved "
	    else:
		print "Error fileSaveAs:: while store_model ", fname

    #-------------------------------------------------------------------
    def fileExit(self):
	if self.okToSave() == False:
	    return False
	self.close()
	return True
	

    #---  HELP -------------------------------------------------------
    def help_manual(self):
	path = 'python '+self.env+'/helpwin.py &'
	os.system(path)

    #-------------------------------------------------------------------
    def help_about(self):
	QMessageBox.information(self, "About",
	    "SAMT2 - Fuzzy\t\t03.02.2016\n\n"
	    "by:\n\n"
	    "Dr. Ralf Wieland:\tScientific Leader\n\n"
	    "Dr. Xenia Specka:\tDeveloper\n\n"
	    "Dipl.-Ing. Karin Groth:\tDesign and GUI\n\n")
	    
    #========== END  Menu and ToolBar ==================================
    #===================================================================
    
    def switchTab(self,idx):
	for i in range(7):
	    if i == idx:
		self.ui.tabwid.setTabIcon(i,self.icon1)
	    else:
		self.ui.tabwid.setTabIcon(i,self.icon2)
	if idx == 0:   # Input page
	    self.mfheight = self.ui.paintwid.height()
	    self.mfwidth = self.ui.paintwid.width()
	    self.mfGrid = self.ui.mfGridCheck.isChecked()
	elif idx == 1:	# Output page
	    self.outheight = self.ui.outputwid.height()
	    self.outwidth = self.ui.outputwid.width()
	    self.outGrid = self.ui.outGridCheck.isChecked()
	    self.showOutput()
	elif idx == 2:	# Rules page
	    self.setRulesTableLabel()
	elif idx == 3:  # Analysis page 
	    QtGui.QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
	    # returns, if no full fuzzy modell is edited
	    # mindestens. 2 member pro Input
	    if self.numInput==2 and self.ui.memb2Table.rowCount()<=1:
		print "AnalysisPage: return because Inp2 has only 1 member "
		return
	    if self.numInput==3 and self.ui.memb3Table.rowCount()<=1:
		print "AnalysisPage: return because Inp3 has only 1 member "
		return
	    if self.numInput==1:
		self.ui.cb_line.setEnabled(False)
		self.ui.cb_absolut.setEnabled(False)
		self.ui.cb_absolut.setChecked(False)
		self.ui.cb_contour.setEnabled(False) 
		self.ui.cb_contour.setChecked(False) 
	    else:
		self.ui.cb_line.setEnabled(True)
		if self.ui.cb_line.isChecked() == True:
		    self.ui.cb_absolut.setEnabled(True)
		self.ui.cb_absolut.setChecked(False)
		self.ui.cb_contour.setEnabled(True) 
		self.ui.cb_contour.setChecked(True) 
	    self.fuzzy_refresh()
	    QtGui.QApplication.restoreOverrideCursor()
	    if self.ui.memb1Table.rowCount()==0:
		return		
	    oname = self.ui.outputLE.text()
	    self.ui.outnameLE.setText(oname)
	    self.ui.outnameLE.setEnabled(True)
	    self.ui.outnameLE.setReadOnly(True)
	    if len(self.xOut) > 0:		
		v = "%.3f" % min(self.xOut)
		self.ui.outminLE.setText(str(v))
		v = "%.3f" %  max(self.xOut)
		self.ui.outmaxLE.setText(str(v))
	    if self.ui.rulesTable.rowCount() != 0:
		self.combinate_inputCombos()  
	
	elif idx == 4:    # Calc page 
	    self.fuzzy_refresh()
	
	elif idx == 5:    # Training page
	    self.fuzzy_refresh()
	    if self.ui.rulesTable.rowCount() != 0:
		# The LAST MODIFIED Outputs = the original Outputs NOW
		# get outputs from fuzzy, not from gui table
		li = self.work.get_outputs()
		if len(li) == 0:
		    print "Error - no outputs found"
		    return
		for o in li:
		    name = self.work.get_outp_name_singleton(o)
		    val  = self.work.get_outp_val(o)
		    val = "%.3f" % val
		    self.lastModifiedVals.append(val)
		# umspeichern
		del self.origOutputVals[:]
		for v in self.lastModifiedVals:
		    self.origOutputVals.append(v)
		del self.lastModifiedVals[:]
	
	elif idx == 6:    # Rules Training page
	    if self.ui.trainedRulesTbl.rowCount() == 0:
		self.fuzzy_refresh()


    #-------------------------------------------------------------------
    def fill_input_lists_for_new_fuz(self):
	# called by switchTab idx=3 Analysis
	modelname = self.ui.lbl_fisname.text()
	list_inpnames = []		
	row = 0
	anz = 0
	anz_inp = self.ui.inputCombo.count()
	
	self.work.create_fx_neu(modelname)
	
	for j in range(anz_inp):
	    mfTitleList = []   
	    mfTypeList  = []		
	    mfRangeList = []
	    if j == 0:
		row = self.ui.memb1Table.rowCount()
		if row>0:
		    for i in range(row):
			#split the range-string and put the separat values in the rangelist
			range_ = self.ui.memb1Table.item(i,2).text()
			qli = range_.split(" ")			# QStringList
			pyli = str(qli.join("\n")).split("\n")	# pylist
			mfRangeList.append(pyli)
			type_ = self.ui.memb1Table.item(i,1).text()
			mfTypeList.append(str(type_))
			mfTitleList.append(str(self.ui.memb1Table.item(i,0).text()))
	    elif j == 1:
		row= self.ui.memb2Table.rowCount()
		if row>0:
		    for i in range(row):
			range_= self.ui.memb2Table.item(i,2).text()
			qli = range_.split(" ")			
			pyli = str(qli.join("\n")).split("\n")	
			mfRangeList.append(pyli)
			type_ = self.ui.memb2Table.item(i,1).text()
			mfTypeList.append(str(type_))
			mfTitleList.append(str(self.ui.memb2Table.item(i,0).text()))
	    elif j == 2:
		row= self.ui.memb3Table.rowCount()
		if row>0:
		    for i in range(row):
			range_ = self.ui.memb3Table.item(i,2).text()
			qli = range_.split(" ")			
			pyli = str(qli.join("\n")).split("\n")	
			mfRangeList.append(pyli)
			type_ = self.ui.memb3Table.item(i,1).text()
			mfTypeList.append(str(type_))
			mfTitleList.append(str(self.ui.memb3Table.item(i,0).text()))
	    
	    list_inpnames.append(str(self.ui.inputCombo.itemText(j)))

	    self.work.fill_new_fuz_with_inputs(mfRangeList,
						mfTitleList,
						mfTypeList,
						list_inpnames[j],
						anz_inp)  
						
    #-------------------------------------------------------------------
    def fuzzy_refresh(self):
	# called by: fileSave, fileSaveAs,  switchTab
	#	      btn_trainStart, btn_restore_orig
    	# initialization of the fuzzy system
	# write all lists with the content of 
	# Page Input, Output, Rules into fx_neu 
	# to use it in Analyse, Calculation, Training
	
	# Inputs
	self.fill_input_lists_for_new_fuz()  # create self.fx_neu
	
	# Output 
	self.getOutputVector()
	
	# Output Name
	oname = str(self.ui.outputLE.text())	
	self.work.fill_new_fuz_with_outputs(oname,self.outTitleList,self.xOut)
	
	# Rules
	li_rules = self.getRulesVector()
	self.work.fill_new_fuz_with_rules(li_rules)
	
	# nachdem alle listen des akt.fx ---> an fx_neu
	# delete akt.fx und setze akt.fx=fx_neu
	self.work.refresh_fx() 
    
    
    
    #===================================================================
    #===================================================================
    #===================================================================
    #------ Analyse ----------------------------------------------------
    #===================================================================

    def showAnalyse(self, q):
	# called by: click Reiter Analyse only
	# q = 1 --> caller: combine_inputCombos (q nur zur Kontrolle)
	# q = 2 -->         showContour
	# q = 3 -->         test_range
	# q = 4 -->         test_grids
	# self.index0,1,2 was wrote in combinate_inputCombos 
	
	self.ui.mplwid_ana.canvas.ax.clear()
	li_retu = []
	mx = None
	oname = self.work.get_name_of_output()
	in1 = str(self.ui.input1Combo.currentText())
	if self.numInput == 1:
	    in2 = oname   # title y-achse
	    self.ui.xgridLE.setReadOnly(True)
	    self.ui.ygridLE.setReadOnly(True)
	else:
	    in2 = str(self.ui.input2Combo.currentText())
	    self.ui.xgridLE.setReadOnly(False)
	    self.ui.ygridLE.setReadOnly(False)
	in3 = str(self.ui.input3LE.text())
	
	if self.ui.in3LE.text().isEmpty():
	    in3const = 0.0  # ?????
	else:
	    in3const = float(str(self.ui.in3LE.text()))
	if self.ui.xgridLE.text().isEmpty():
	    print "Error: xgrids is empty!"
	    return
	xgrids = int(self.ui.xgridLE.text())
	if self.ui.ygridLE.text().isEmpty():
	    print "Error: ygrids is empty!"
	    return
	ygrids = int(self.ui.ygridLE.text())
	if self.ui.in1minLE.text().isEmpty():
	    #print "showAna:: in1minLE.text().isEmpty --> return"
	    return
	
	if self.ui.in1minLE.text().isEmpty():
	    print "Error: min. Input1 is empty!"
	    return
	xmi = float(self.ui.in1minLE.text())
	if self.ui.in1maxLE.text().isEmpty():
	    print "Error: max. Input1 is empty!"
	    return
	xma = float(self.ui.in1maxLE.text())
	if self.numInput == 1:
	    if self.ui.outminLE.text().isEmpty():
		print "Error: min. output is empty!"
		return
	    ymi = float(self.ui.outminLE.text())
	    if self.ui.outmaxLE.text().isEmpty():
		print "Error: max. output is empty!"
		return
	    yma = float(self.ui.outmaxLE.text())
	else:
	    if self.ui.in2minLE.text().isEmpty():
		print "Error: min. Input2t is empty!"
		return
	    ymi = float(self.ui.in2minLE.text())
	    if self.ui.in2maxLE.text().isEmpty():
		print "Error: max. Input2 is empty!"
		return
	    yma = float(self.ui.in2maxLE.text())

	if self.numInput == 1:
	    li_retu = self.work.get_mx_inp1(xgrids,ygrids,xmi,xma)
	    #retu: y, mi, ma, x
	else:
	    li_retu = self.work.get_mx(self.numInput,xgrids,ygrids,
					self.index0,self.index1,self.index2,
					in3const,xmi,xma,ymi,yma)
	    #retu: y, mi, ma, contour

	if len(li_retu) == 0:
	    print "show_ana:: mx von fx ist leer - Abort"
	    return
	
	# diese vals alle aus Reiter Analyse füllen, wenn editiert ???????
	mx = li_retu[0] 	# for numInp=1  y-values (output)
	mxmi = li_retu[1]	# nur f. Kontrolle, ob mx leer ist
	mxma = li_retu[2]	#   "
	if mxmi == mxma:
	    print "showAnalyse:: mx ist leer  remove analyse plot"

	self.w_wid = self.ui.mplwid_ana.width()
	self.h_wid = self.ui.mplwid_ana.height() 
	
	li_ol = []	# float, needed if the model has only 1 input
	self.flag_inter_method = self.ui.mulCombo.currentIndex() 
	
	if (self.ui.rulesTable.rowCount()==0) or (self.ui.outputTable.rowCount()<=1):
	    return

	if self.numInput == 2:
	    # no full fuzzy model -> return
	    if ((self.ui.memb1Table.rowCount()==0) or 
		(self.ui.memb2Table.rowCount()==0)):
		return
	elif self.numInput == 3:
	    if ((self.ui.memb1Table.rowCount()==0) or 
		(self.ui.memb2Table.rowCount()==0) or 
		(self.ui.memb3Table.rowCount()==0)):
		return
	# for mouseEvents
	self.xmi = xmi  
	self.xma = xma
	self.ymi = ymi
	self.yma = yma
	self.xgrids = xgrids
	self.ygrids = ygrids
	self.mx = mx		

	# --- clear old mplwid_ana complete 
	if self.cbar is not None:
	    self.clear_mplwid_complet()
	    
	pax = self.ui.mplwid_ana.canvas.ax  # pax is figure with subplot
 
	# delete x, y-axis incl. ticks
	self.ui.mplwid_ana.canvas.fig.set_frameon(False) 
	# remove border incl tick labels
	pax.set_axis_off()   
	self.ui.mplwid_ana.canvas.fig.subplots_adjust(
			    left=0.12, right=1, top=0.98,bottom=0.09)
	# axis names
	pax.set_xlabel(in1) 
	pax.set_ylabel(in2) 
	pax.set_axis_on()
	#colormap
	cmap = mpl.cm.get_cmap('RdYlGn')  	
	cmap.set_under('white')		# NoData-Werte
	
	if self.numInput == 1:
	    # plot output curve  x, y
	    pax.plot(li_retu[3], mx, color='blue')	
	    liy = mx		  # y value
	    lix = li_retu[3]      # x value
	    ymin = self.ymi 
	    i = 0 
	    for x in lix: 
		xmin = x
		ymax = mx[i]
		if i == 0:
		    # normalize colors --> [0,1]
		    # norm = mpl.colors.Normalize(ymin,max(mx)) 
		    norm = mpl.colors.Normalize(int(ymin),int(self.yma))
		# make a colorbar
		if self.cbar == None:
		    cmmapable = mpl.cm.ScalarMappable(norm, cmap)
		    
		    if self.ui.cb_absolut.isChecked():
			# absolute scala (default)
			cmmapable.set_array(range(int(self.ymi), int(self.yma)))  
		    else:
			# relative scala
			cmmapable.set_array(range(int(self.ymi), int(max(mx))))
		    
		    self.cbar = self.ui.mplwid_ana.canvas.fig.colorbar(cmmapable)
		color_i = cmap(norm(mx[i]) )  # rgba value
		
		# plot colored lines from bottom until curve point
		pax.plot((xmin,xmin),(ymin,ymax),color=color_i,linewidth=2.0)
		i += 1
	    pax.set_ylim(int(self.ymi), int(self.yma))  # ???? Do
	    self.ui.mplwid_ana.canvas.ax.grid(True)
	    self.ui.mplwid_ana.canvas.draw()
	    return	# without contour
	
	# numInput > 1 :
	img = pax.imshow(mx, extent=(xmi,xma,ymi,yma),
			    cmap=cmap, aspect='auto')  
	self.cbar = self.ui.mplwid_ana.canvas.fig.colorbar(img, 
				aspect=20, pad=0.04,
				shrink=1.0, orientation='vertical') 
	# contour
	if self.ui.cb_contour.isChecked()==True:
	    cset = pax.contour(mx,li_retu[3],
				extent=(xmi,xma,yma,ymi),
				linewidths=1, colors='k')
	    pax.clabel(cset, inline=True, fmt='%1.3f', fontsize=10)
	self.ui.mplwid_ana.canvas.draw()
    
    #-------------------------------------------------------------------
    def clear_mplwid_complet(self):
	# clear old mplwid_ana incl. colorbar if exists
	# called by: initialize, showAnalyse
	self.ui.mplwid_ana.close()   # delete all
	self.ui.mplwid_ana = matplotlibWidget(self.ui.tab_4)
	self.ui.mplwid_ana.setMinimumSize(QtCore.QSize(481, 501))
	self.ui.mplwid_ana.setObjectName("mplwid_ana")
	self.ui.horizontalLayout_8.addWidget(self.ui.mplwid_ana)
	
	# mplwid_ana.close() makes that layout is None
	hbox = QHBoxLayout()
	hbox.addWidget(self.ui.mplwid_ana.canvas)
	self.ui.mplwid_ana.setLayout(hbox)
	
	# refresh connections for mouse events on canvas
	self.ui.mplwid_ana.canvas.mpl_connect(
			 'button_press_event', self.on_press)
	self.ui.mplwid_ana.canvas.mpl_connect(
			     'motion_notify_event', self.on_motion)
	self.ui.mplwid_ana.canvas.mpl_connect(
			    'button_release_event', self.on_release)
    
    #-------------------------------------------------------------------
    def draw_line(self, yesno):
	# called by: cb_line toggled
	if yesno == True:
	    if int(self.ui.xgridLE.text())<250 or int(self.ui.ygridLE.text())<250:
		self.checked = False
		self.isLine = False
		self.ui.cb_absolut.setEnabled(False)
		self.isNodata = False
		msg = QString("Error: xgrid or ygrid < 250,  Not Line possible to draw")
		self.ui.statusbar.showMessage(msg, 5000)
		self.ui.cb_line.setChecked(False)
	    else:
		self.checked = True
		self.isLine = True    # only here set True
		self.ui.cb_absolut.setEnabled(True)
		self.clear_old_line()
		self.ui.mplwid_ana.canvas.draw()
		self.set_default_new_line()
	else:
	    # delete the line
	    self.checked = True
	    self.isLine = False
	    self.ui.cb_absolut.setEnabled(False)
	    self.clear_old_line()
	    self.ui.mplwid_ana.canvas.draw()

    #-------------------------------------------------------------------
    def draw_line_end(self):
	# called from: on_release  
	# prepare plot transect
	i0 = self.startPointC[1]	# wrote in on_releaseEv
	j0 = self.startPointC[0]
	i1 = self.endPointC[1]
	j1 = self.endPointC[0]
	mx = None
	t = None
	mx, t = self.work.get_mx_transect(i0,j0,i1,j1)
	oname = self.ui.outnameLE.text()
	if mx==None or t==None:
	    msg = self.tr("Error: while Line End")
	    self.ui.statusbar.showMessage(msg,2000)
	    return
	if self.ui.cb_absolut.isChecked() == True:
	    absolut = True
	    max_out = float(self.ui.outmaxLE.text())
	    min_out = float(self.ui.outminLE.text())
	    popup = Popup_transect( t, mx,
				    self.li_X, self.li_Y,
				    oname, absolut,
				    max_out, min_out)
	else:
	    absolut = False
	    popup = Popup_transect( t, mx, 
				    self.li_X, self.li_Y,
				    oname, absolut)
	popup.show()
	self.li_popups.append(popup)
	self.ui.cb_absolut.setChecked(False) 
	
    #-------------------------------------------------------------------
    def clear_old_line(self):
	# called by: slot draw_line, (init ana oder showAnalyse)
	lae = len(self.ui.mplwid_ana.canvas.ax.lines)
	for i in range(lae):
	    self.ui.mplwid_ana.canvas.ax.lines.pop(0)

    #-------------------------------------------------------------------
    def set_default_new_line(self):
        # called by: draw_line
	self.startPoint = (0,0)
	self.endPoint = (0,0)
	self.li_X = [0,0]
	self.li_Y = [0,0]
	self.line1 = line.Line2D([], [], color='black', linewidth=0.5)
	
    #-------------------------------------------------------------------
    def combinate_inputCombos(self):
	# called by: switchTab 3=Analysis, actCombo1, actCombo2
	# set the opportunities to choose items from the comboboxes 
	# depending on the current item of the first combobox

	QtGui.QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
	item1 = self.ui.input1Combo.currentIndex()
	item2 = self.ui.input2Combo.currentIndex()
	self.index0 = item1  # x axis input, self.index0 wrote in init

	mi = self.work.get_min_inp(self.index0)
	if mi == None:
	    return
	mi = "%.3f" % mi
	self.ui.in1minLE.setText(str(mi))       	
	
	ma = self.work.get_max_inp(self.index0)
	if ma == None:
	    return
	ma = "%.3f" % ma
 	self.ui.in1maxLE.setText(str(ma))
	
	#  1 input
	if self.numInput==1:
	    self.ui.input1Combo.setItemText(0, self.ui.inputCombo.itemText(0))

	# 2 inputs
	elif self.numInput == 2:
	    self.index1 = 1-self.index0
	    # set all input names into the combobox
	    self.ui.input1Combo.setItemText(0,self.ui.inputCombo.itemText(0))
	    self.ui.input1Combo.setItemText(1,self.ui.inputCombo.itemText(1))
	    #raise the other input
	    self.ui.input2Combo.setItemText(self.ui.input2Combo.currentIndex(),
				self.ui.inputCombo.itemText(1-item1))
	    # set range for y axis input
	    mi = self.work.get_min_inp(1-item1)
	    if mi == None:
		return
	    mi = "%.3f" % mi
	    self.ui.in2minLE.setText(str(mi))
	    ma = self.work.get_max_inp(1-item1)
	    if ma == None:
		return
	    ma = "%.3f" % ma
	    self.ui.in2maxLE.setText(str(ma))
	    
	# 3 inputs
	elif self.numInput == 3:
	    self.index1 = (3+self.index0+1)%3  	# y axis input
	    self.index2 = (3+self.index0+2)%3  	# z - input
    	    # set all input names into the first combobox
	    self.ui.input1Combo.setItemText(0,self.ui.inputCombo.itemText(0))
	    self.ui.input1Combo.setItemText(1,self.ui.inputCombo.itemText(1))
	    self.ui.input1Combo.setItemText(2,self.ui.inputCombo.itemText(2))
	    # set the names of the two other inputs into the combobox
	    self.ui.input2Combo.setItemText(0,self.ui.inputCombo.itemText(self.index1))
	    self.ui.input2Combo.setItemText(1,self.ui.inputCombo.itemText(self.index2))
	    mi = self.work.get_min_inp(2)
	    if mi == None:
		return
	    mi = "%.2f" % mi
	    ma = self.work.get_max_inp(2)
	    if ma == None:
		return
	    ma = "%.2f" % ma
	    self.ui.in3TextLabel.setText(QString("[%1;%2]").arg(mi).arg(ma))
    
	    # if current item of 1. combobox was chosen (default)
	    if self.actCombo == 1:
		# set y and z axis inputs
		self.ui.input2Combo.setCurrentIndex(0)
		self.ui.input3LE.setText(self.ui.inputCombo.itemText(self.index2))

		mi = self.work.get_min_inp(self.index1)
		if mi == None:
		    return
		mi1 = "%.3f" % mi
		ma = self.work.get_max_inp(self.index1)
		if ma == None:
		    return
		ma1 = "%.3f" % ma
		
		mi = self.work.get_min_inp(self.index2)
		if mi == None:
		    return
		mi2 = "%.3f" % mi
		ma = self.work.get_max_inp(self.index2)
		if ma == None:
		    return
		ma2 = "%.3f" % ma
		self.ui.in3TextLabel.setText(QString("[%1;%2]").arg(mi2).arg(ma2))
		# set range of y axis input
		self.ui.in2minLE.setText(QString("%1").arg(mi1))
		self.ui.in2maxLE.setText(QString("%1").arg(ma1))
		# set minimum z - value   
		min_ = mi2   	
		max_ = ma2
		v = mi+((ma-mi)/2)
		self.ui.in3LE.setText(QString("%1").arg(v))

	    # if current item of the 2. combobox was chosen 
	    # --> swap y and z input (2. combo=z)
	    if self.actCombo == 2:
		if item2 == 1:
		    h = self.index1
		    self.index1 = self.index2
		    self.index2 = h
		# set y axis range
		mi = self.work.get_min_inp(self.index1)
		if mi == None:
		    return
		mi1 = "%.3f" % mi
		ma = self.work.get_max_inp(self.index1)
		if ma == None:
		    return
		ma1 = "%.3f" % ma
		mi = self.work.get_min_inp(self.index2)
		if mi == None:
		    return
		mi2 = "%.3f" % mi
		ma = self.work.get_max_inp(self.index2)
		if ma == None:
		    return
		ma2 = "%.3f" % ma
		
		self.ui.in2minLE.setText(QString("%1").arg(mi1))
		self.ui.in2maxLE.setText(QString("%1").arg(ma1))
		self.ui.in3TextLabel.setText(QString("[%1;%2]").arg(mi2).arg(ma2))
		# set z-name and z-value
		self.ui.input3LE.setText(self.ui.inputCombo.itemText(self.index2))
		min_ = mi2	
		max_ = ma2
		#v = "%.3f" % min_+((max_-min_)/2)
		v = mi+((ma-mi)/2)
		self.ui.in3LE.setText(QString("%1").arg(v))
	QtGui.QApplication.restoreOverrideCursor()	
	self.showAnalyse(1)
	
    #-------------------------------------------------------------------
    def showContour(self):
	#print " SLOT checkbox cb_contour"
	ygr = int(self.ui.ygridLE.text()) 
	xgr = int(self.ui.xgridLE.text())
	if xgr >=50 and ygr >=50:
	    self.contour = self.ui.cb_contour.isChecked()
	    #print "self.contour: ", self.contour
	    self.showAnalyse(2)
	else:
	    self.ui.cb_contour.setChecked(False)
    
    #-------------------------------------------------------------------
    def test_range(self):
	print "test_range "
	# called by: SIGNALe
	self.test_x_min()
	self.test_x_max()
	if self.numInput > 1:
	    self.test_y_min()
	    self.test_y_max()
	    if self.numInput > 2:
		self.test_z_value()
	self.showAnalyse(3)
    
    #-------------------------------------------------------------------    
    def test_x_min(self):
	# called by: SLOT test_range()
	# test if xmin<=value<=xmax
	val = round(float(self.ui.in1minLE.text()), 3)
	sval = "%.3f" % val
	mi = self.work.get_min_inp(self.index0) # float
	if mi == None:
	    return
	s1 = "%.3f" % round(mi,3)
	ma = self.work.get_max_inp(self.index0)	
	if ma == None:
	    return
	s2 = "%.3f" % round(ma,3)

	if val < mi: 
	    self.ui.in1minLE.setText(s1)
	elif val > ma:
	    self.ui.in1minLE.setText(s2)
	elif val >= float(self.ui.in1maxLE.text()):
	    self.ui.in1minLE.setText(s1)  
	    self.ui.in1maxLE.setText(s2)
	else:
	    self.ui.in1minLE.setText(sval)
	    
    #-------------------------------------------------------------------
    def test_x_max(self):
	# called by: SLOT test_range()
	# test if xmin<=value<=xmax
	val = round(float(self.ui.in1maxLE.text()) ,3)
	sval = "%.3f" % val
	mi = self.work.get_min_inp(self.index0)	# float
	if mi == None:
	    return
	s1 = "%.3f" % round(mi,3)
	ma = self.work.get_max_inp(self.index0)	
	if ma == None:
	    return
	s2 = "%.3f" % round(ma,3)
	if val < mi: 
	    s = "%.3f" % mi
	    self.ui.in1maxLE.setText(s1)
	elif val > ma:
	    s = "%.3f" % ma
	    self.ui.in1maxLE.setText(s2)
	elif val <= float(self.ui.in1minLE.text()):
	    self.ui.in1minLE.setText(s1)
	    self.ui.in1maxLE.setText(s2)
	else:
	    self.ui.in1maxLE.setText(sval)    
	    
    #-------------------------------------------------------------------
    def test_y_min(self):
	# called by: SLOT test_range()
	#print " test_y_min:  if ymin<=value<=ymax"
	val = round(float(self.ui.in2minLE.text()), 3)
    	sval = "%.3f" % val
	mi = self.work.get_min_inp(self.index1)	# float
	if mi == None:
	    return
	s1 = "%.3f" % round(mi,3)
	ma = self.work.get_max_inp(self.index1)	
	if ma == None:
	    return
	s2 = "%.3f" % round(ma,3)
	if val < mi: 
	    self.ui.in2minLE.setText(s1)
	elif val > ma:
	    self.ui.in2minLE.setText(s2)
	elif val >= float(self.ui.in2maxLE.text()):
	    self.ui.in2minLE.setText(s1)  
	    self.ui.in2maxLE.setText(s2) 
	else:
	    self.ui.in2minLE.setText(sval)    

    #-------------------------------------------------------------------
    def test_y_max(self):
	# called by: SLOT test_range()
	#print "test_y_max"
	val = round(float(self.ui.in2maxLE.text()), 3)
    	sval = "%.3f" % val
	mi = self.work.get_min_inp(self.index1)	# float
	if mi == None:
	    return
	s1 = "%.3f" % round(mi,3)
	ma = self.work.get_max_inp(self.index1)	
	if ma == None:
	    return
	s2 = "%.3f" % round(ma,3)
	if val < mi:
	    self.ui.in2maxLE.setText(s1)
	elif val > ma:
	    self.ui.in2maxLE.setText(s2)
	elif val <= float(self.ui.in2minLE.text()):
	    self.ui.in2minLE.setText(s1)
	    self.ui.in2maxLE.setText(s2)
	else:
	    self.ui.in2maxLE.setText(sval)    
    
    #-------------------------------------------------------------------
    def test_z_value(self):
	# called by: SLOT test_range()
	#print "test_z_value"
	#test if value is in the range of the input
	val = round(float(self.ui.in3LE.text()), 3)
    	sval = "%.3f" % val
	mi = self.work.get_min_inp(self.index2)	# float
	if mi == None:
	    return
	s1 = "%.3f" % round(mi,3)
	ma = self.work.get_max_inp(self.index2)	
	if ma == None:
	    return
	s2 = "%.3f" % round(ma,3)
	if val < mi:
	    self.ui.in3LE.setText(s1)
	if val > ma:
	    self.ui.in3LE.setText(s2)

    #-------------------------------------------------------------------
    def test_grids(self):
	# SLOT,  test if (5 <= grid <= 250)
	if int(self.ui.ygridLE.text()) <= 5:     
	    self.ui.ygridLE.setText("5")
	if int(self.ui.ygridLE.text()) >= 250:   
	    self.ui.ygridLE.setText("250")
	if int(self.ui.xgridLE.text()) <= 5:     
	    self.ui.xgridLE.setText("5")
	if int(self.ui.xgridLE.text()) >= 250:   
	    self.ui.xgridLE.setText("250")
    
	# Disable cb_contour
	if (int(self.ui.xgridLE.text())<50 or int(self.ui.ygridLE.text())<50 or self.numInput==1): 
	    self.ui.cb_contour.setChecked(False)
	    self.ui.cb_contour.setDisabled(True)
	    self.contour = False
	else:
	    self.ui.cb_contour.setEnabled(True)

	# Disables cb_line
	if (int(self.ui.xgridLE.text()<250 or int(self.ui.ygridLE.text())<250)): 
	    self.ui.cb_line.setEnabled(False)
	else:
	    self.ui.cb_line.setEnabled(True)
	self.showAnalyse(4)
        
    #-------------------------------------------------------------------
    def actCombo1(self):
	# SLOT, set index of activeCombo to 1
	self.actCombo = 1
	self.combinate_inputCombos()

    #-------------------------------------------------------------------
    def actCombo2(self):
	# SLOT, set index of activeCombo to 2
	self.actCombo = 2
	self.combinate_inputCombos()
    
    
    ####################################################################
    ###             Mouse-Events 
    ####################################################################
    
    def on_press(self, event):
	# leftButton only
	if event.button != 1:
	    return
	if self.ui.tabwid.currentIndex() == 3:  # only in Analyse
	    X = event.xdata   # float   col or j
	    Y = event.ydata   # float   row or i
	    if X==None or Y==None:
		# pressed out of border - Abort"
		return
	    #print "on press: X val=%.3f, Y val=%.3f" % (X,Y) 
	    
	    row, col = self.scale_picked_point(X,Y)
	    
	    if row<0 or row>self.ygrids-1:
		print "pressed outside canvas ! - Abort"
		return
	    if col<0 or col>self.xgrids-1:
		print "pressed outside canvas! - Abort"
		return
	    
	    self.startPoint = [col, row]   
	    
	    if self.numInput == 1:
		s = "i0, j0:  [%d, %d]" % (self.mx[col],col)
	    else:		    
		s = "i0, j0:  [%d, %d]" % (row,col)
	    msg =self.tr(s)
	    self.ui.statusbar.showMessage(msg, 3000) 
	    if self.isLine: 
		self.dragging = True
		self.li_X[0] = X    # only for line plotting
		self.li_Y[0] = Y    
		self.line1.set_data(self.li_X, self.li_Y)
	    else:
		self.dragging = False
    
    #-------------------------------------------------------------------
    def scale_picked_point(self, X, Y): 
	# oberer linker Eckpunkt of matrix:[col=0,row=0] 
	diffx = self.xma -self.xmi
	diffy = self.yma - self.ymi
	# yAchse
	v1 = Y-self.ymi
	v2 = diffy / self.ygrids
	v = v1/v2  
	row = int(v)
	row = self.ygrids-row   
	# xAchse
	v1 = X-self.xmi
	v2 = diffx / self.xgrids
	v = v1/v2
	col = int(v)
	#print "scale_picked_point:: xAchse col=%s, yAchse: row=%s" % (col,row)
	return(row, col)   
    
    #-------------------------------------------------------------------
    def on_motion(self, event):
	if self.ui.tabwid.currentIndex()!= 3:  # 3= Analyse
	    return
	if self.dragging:   
	    X = event.xdata    	
	    Y = event.ydata
	    if X==None or Y==None:
		return
	    row, col = self.scale_picked_point(X,Y)   
	    
	    if row<0 or row>self.ygrids-1:
		return
	    if col<0 or col>self.xgrids-1:
		return
	    
	    # out only for statusbar
	    #~ out = self.work.get_mx_val(row,col)  	
	    #~ print "moved: X: %.3f, Y: %.3f" % (X,Y)
	    
	    s = "X=%.3f   Y=%.3f" % (X,Y)
	    msg = self.tr(s)
	    self.ui.statusbar.showMessage(msg)
	    if self.isLine:
		#~ if self.check_nodata(Y,X):
		    #~ return
		self.endPoint = [col,row]   #[X,Y]
		self.clear_old_line()
		self.ui.mplwid_ana.canvas.draw()
		# new line self.line1 started in on_press
		self.li_X[1] = X        
		self.li_Y[1] = Y        
		self.line1.set_data(self.li_X, self.li_Y)
		self.ui.mplwid_ana.canvas.ax.add_line(self.line1)
		self.ui.mplwid_ana.canvas.draw()   
     			
    #-------------------------------------------------------------------
    def on_release(self, event):
	if self.ui.tabwid.currentIndex() != 3:  # 3= Analyse
	    return
	if event.button != 1:
	    print "on_release:: falscher MausButton"
	    self.dragging = False
	    return
	in3const = 0.0
	X = event.xdata   
	Y = event.ydata 
	if X==None or Y==None:
	    # oder if self.check_nodata(Y,X)==True:
	    return

	row, col = self.scale_picked_point(X,Y)
	# test outside the canvas
	if row<0 or row>self.ygrids-1:
	    return
	if col<0 or col>self.xgrids-1:
	    return
	
	# out only for test
	#out = self.work.get_mx_val(row,col) 	
	
	if self.numInput == 1:
	    s = "X=%.3f   Y=%.3f" % (X,self.mx[col]) 
	else:	
	    s = "X=%.3f   Y=%.3f" % (X,Y)
	msg =self.tr(s)
	self.ui.statusbar.showMessage(msg)
	
	#print "on_relea: startPoint=", self.startPoint
	self.endPoint = [col,row]    #[X,Y]
	#print "on_relea: endPoint  =", self.endPoint
	
	if self.startPoint[0] == col and self.startPoint[1] == row:  
	    # prepaire Popup_active_rules window
	    anz_inp = self.ui.inputCombo.count()
	    self.get_input_names() 	# writes li_input_names
	    li_col_header = ['Nr.','Rule','Mu']
	    li_outval = []
	    
	    if anz_inp == 1:
		s = "x1=%s" % self.ui.input1Combo.currentText()
		li_col_header.append(s)
		li_col_header.append("inp2 dummy")
		li_col_header.append("inp3 dummy")
		su1,ruleList,muList,outputList = self.work.get_calct1(X)
		ifthenList = self.fill_ifthenList(ruleList,1)
	    
	    elif anz_inp == 2:
		s = "x1=%s" % self.ui.input1Combo.currentText()
		li_col_header.append(s)
		s = "x2=%s" % self.ui.input2Combo.currentText()
		li_col_header.append(s)
		li_col_header.append("inp3 dummy")
		su1,ruleList,muList,outputList = self.work.get_calct2(X,Y)
		# fill ifthenList for Popup_active_rules
		ifthenList = self.fill_ifthenList(ruleList,2)
	    
	    elif anz_inp == 3:
		s = "x1=%s" % self.ui.input1Combo.currentText()
		li_col_header.append(s)
		s = "x2=%s" % self.ui.input2Combo.currentText()
		li_col_header.append(s)
		s = "x3=%s" % str(self.ui.input3LE.text())
		li_col_header.append(s)
		if self.ui.in3LE.text().isEmpty():
		    in3const = 0.0   # ?
		else:
		    in3const = float(str(self.ui.in3LE.text()))
		su1, ruleList,muList,outputList = self.work.get_calct3(X,Y,in3const)
		ifthenList = self.fill_ifthenList(ruleList,3)

	    li_col_header.append(str(self.ui.outnameLE.text()))
	    li_col_header.append('Entire Output')
	    
	    # opens window with active_rules
	    popup = Popup_active_rules(X,Y, su1,
				    ruleList, muList,outputList, 
				    ifthenList, li_col_header,
				    anz_inp, in3const)
	    popup.show()
	    self.li_popups.append(popup)
	
	if self.isLine:
	    # draw the line
	    self.dragging = True
	    self.li_X[1] = X   # 2 values     
	    self.li_Y[1] = Y   #   "
	    self.line1.set_data(self.li_X, self.li_Y)
	    self.ui.mplwid_ana.canvas.ax.add_line(self.line1)
	    # save copy for draw_line_end
	    self.startPointC = self.startPoint
	    self.endPointC = self.endPoint
	    self.ui.mplwid_ana.canvas.draw()  
	
	if self.ui.cb_line.isChecked():
	    # remove next 4 lines to show the line for a longer time 
	    self.dragging = False   
	    self.ui.cb_line.setChecked(False)
	    self.ui.cb_absolut.setEnabled(False)
	    self.isLine = False 
	    self.draw_line_end()  # --> opens window with transect
	    
    #-------------------------------------------------------------------
    def fill_ifthenList(self, ruleList, anz_inp):
	li = []
	for nr in ruleList:
	    ifthen = QString("IF ")
	    in1 = self.ui.rulesTable.item(nr,0).text()
	    ss = "<strong>x1=<font color='mediumblue'>%s</font></strong>" % in1
	    ifthen.append(ss)   #(in1)
	    if anz_inp >= 2:
		ifthen.append(" AND ")
		in2 = self.ui.rulesTable.item(nr,1).text()
		ss = "<strong>x2=<font color='mediumblue'>%s</font></strong>" % in2
		ifthen.append(ss)
		if anz_inp == 3:
		    ifthen.append(" AND ")
		    in3 = self.ui.rulesTable.item(nr,2).text()
		    ss = "<strong>x3=<font color='mediumblue'>%s</font></strong>" % in3
		    ifthen.append(ss)
	    ifthen.append(" THEN ")
	    cbox = QComboBox()
	    cbox = self.ui.rulesTable.cellWidget(nr,3)
	    output = cbox.currentText() 
	    ss = "<font color='darkred'><strong>%s</strong></font>" % output				
	    ifthen.append(ss)
	    cf = self.ui.rulesTable.item(nr,4).text()
	    ifthen.append(" (")
	    ifthen.append(cf)
	    ifthen.append(")")
	    li.append(ifthen)
	return li
    #-------------------------------------------------------------------
	    
    def get_input_names(self):
	# called by: on_release (mouse) 
	# list for Popup_active_rules  (colHeader in table)
	del self.li_input_names[:]
	for idx in range(self.ui.inputCombo.count()):
	    item = self.ui.inputCombo.itemText(idx)
	    self.li_input_names.append(item)
	return self.li_input_names

    ############### end mouse events ##################################
 

    #===================================================================
    #===================================================================
    #===================================================================
    #------ Calculation ------------------------------------------------
    #===================================================================
    
    def btn_value_clicked(self):
	# called by: btn_value in Reiter Calculation/ 
	modelname = ""
	self.ui.lbl_sep_calc.setText('')
	fname = ""
	try:
	    fname = QFileDialog.getOpenFileName(self,
		    "SAMT2 - Fuzzy ----- Open Data File",	    
		    self.path_save_data,
		    "All Files (*)")
		    #"Data Files (*.txt *.csv);;All Files (*)")
	except IOError:
	    self.ui.statusbar.showMessage("Error: File Open abandoned",2000)
	
	if not fname.isEmpty(): 
	    self.value_path, datei = os.path.split(str(fname))
	    # search the separator
	    self.ui.includeLE.setText(fname)
	    sep = self.get_separator(fname, self.ui.headerSpin.value()) 
	    if sep == None:
		self.ui.statusbar.showMessage("Separator missed!",5000)
		self.ui.calcTextEdit.clear()
		self.ui.lbl_sep_calc.setText('')
		return
	    self.ui.lbl_sep_calc.setText(sep)
	    # open new and read all into TextEdit  
	    try:
		file_ = QFile(fname)
		if file_.open(QIODevice.ReadOnly):
		    stream = QTextStream(file_)
		    txt = stream.readAll()
		    self.ui.calcTextEdit.setPlainText(txt)
		    self.ui.btn_calc_fuzzy.setEnabled(True)
		    file_.close()
	    except IOError:
		print "can not open:", fname
		self.ui.statusbar.showMessage("File Open abandoned",2000)
		return False

    #-------------------------------------------------------------------
    def get_separator(self, filename, headerrows):
	# called by: btn_value, btn_trainPath
	#print "get_separator with headerrows:", headerrows
	sep = None
	try:
	    fobj = open(filename, 'r')
	except IOError:
	    print "can not open:", filename
	    return False
	reader = csv.reader(fobj)   
 	i = 0
	for row in reader:
	    if i < headerrows:
		i += 1
		continue
	    if i > headerrows+5:
		#print "found:: sep = %s" % sep
		fobj.close()
		return sep
	    # wenn komma exist zw. mehreren teilstrings, dann join
	    # sep=komma ist nur in str erkennbar, nicht in liste
	    srow = ','.join(row)	
	    li = [' ', '\t', ';', '#', '|', ',', ':']	
	    for sepa in li:
		anz_delim = srow.count(sepa)
		if anz_delim==self.numInput-1 or anz_delim==self.numInput:
		    sep = sepa
		    break  
	    i += 1	
	    
    #-------------------------------------------------------------------
    def btn_calc_fuzzy(self):
	sep = str(self.ui.lbl_sep_calc.text())
	col_num = -1
	numHeaderlines = self.ui.headerSpin.value()
	sameFile = self.ui.radio_same.isChecked()
	if sameFile == False:
	    fname_to_save = self.ui.resultLE.text()
	    if fname_to_save.isEmpty():
		QtGui.QMessageBox.information(self, 
			self.tr("Samt-Fuzzy Info"), 
			self.tr(u" Missed filename for separat file"))
		return
	
	anz_inp = self.ui.inputCombo.count()
	self.flag_inter_method = self.ui.mulCombo.currentIndex() 
	self.work.set_flag_inter(self.flag_inter_method)
	try:
	    # read file and calculate fuzzy value v, and save it
	    li_result = []	# collect all calculated fuzzy results
	    fname = self.ui.includeLE.text()
	    file_ = QFile(fname)
	    if file_.open(QIODevice.ReadOnly):
		stream = QTextStream(file_)
		# skip headerlines
		for i in xrange(numHeaderlines):
		    rowstr = stream.readLine()
		rowstr = stream.readLine()	# first data line
		while rowstr.isEmpty() == False:
		    li = QStringList()
		    li = rowstr.split(sep)
		    col_num = li.count()
		    if col_num < anz_inp:
			print "Not enough input value columns in data file!"
			return
		    # calculate values
		    if anz_inp == 1:
			x = float(li[0])
			v = self.work.get_calc1(x)
			li.append(str(v))
			li_result.append(str(v))
		    elif anz_inp == 2:
			x = float(li[0])
			y = float(li[1])
			v = self.work.get_calc2(x,y)
			li.append(str(v))
			li_result.append(str(v))
		    elif anz_inp == 3:
			x = float(li[0])
			y = float(li[1])
			z = float(li[2])
			v = self.work.get_calc3(x,y,z)
			v = round(float(v), 4)
			li.append(str(v))
			li_result.append(str(v))
		    else:
			print "btn_calc_fuzzy:: error"
		    rowstr = stream.readLine()	# next row
	    file_.close()
	except IOError:
	    print "calc_fuzzy:: can not open:", fname
	    self.ui.statusbar.showMessage("File Open abandoned", 2000)
	    return False
	
	# save result column ##################################
	if sameFile == False:
	    # save in separate file 
	    path, datei = os.path.split(str(fname_to_save))
	    if path == '':
		#self.value_path has path from Loaded Data File 
		s = self.value_path + '/' + datei
		fname_to_save = s
	    sfile = open(fname_to_save, 'w')
	    for v in li_result:
		s = "%f\n" % float(v)
		sfile.write(s)
	    sfile.close()
	    msg = QString("Results saved in '%1'").arg(fname_to_save) 
	    self.ui.statusbar.showMessage(msg, 4000)
	else:
	    # save in the same file, 
	    sfname = self.path_save_data +'/separate_calc_fuz.txt'
	    sfile = QFile(sfname)
	    if sfile.open(QIODevice.WriteOnly):
		stream = QTextStream(sfile)
		if anz_inp >= 1:
		    stream<<self.ui.inputCombo.itemText(0)
		if anz_inp >= 2:
		    stream<<sep<<self.ui.inputCombo.itemText(1)
		if anz_inp >= 3:
		    stream<<sep<<self.ui.inputCombo.itemText(2)
		stream<<sep<<self.ui.outputLE.text()<<'\n'
		try:
		    rfname = self.ui.includeLE.text()
		    rfile = open(rfname, 'r')
		except IOError:
		    print "can not open:", rfname
		    return False
		reader = csv.reader(rfile)
		i = 0
		for row in reader:
		    # row is a list
		    if i < numHeaderlines:
			# skip over headerlines
			i += 1
			continue
		    # list --> string
		    s = ''.join(row)
		    s += sep
		    s += li_result[i-numHeaderlines]
		    i += 1
		    stream<<s<<'\n'
		sfile.close()
		rfile.close()
		# delete orig file aus includeLE.text() 
		rfname = self.ui.includeLE.text()
		os.remove(rfname)
		# rename temp file to orig filename like includeLE  
		os.rename(sfname, rfname)
		# refresh content of calcTextEdit
		file1 = QFile(self.ui.includeLE.text())
		if file1.open(QIODevice.ReadOnly):
		    stream = QTextStream(file1)
		    txt = stream.readAll()
		    self.ui.calcTextEdit.setPlainText(txt)
		    file1.close()
		    
    #-------------------------------------------------------------------
    def btn_path_clicked(self):
	# get filename from filedialog
	curpath = os.getcwd()
	path = 	self.path_save_data+'/'
	fname = ""
	try:	
	    fname = QtGui.QFileDialog.getSaveFileName(self, 
		    self.tr("SAMT2 - Fuzzy ----- File Save As"), path, 
		    self.tr("All Files(*)"))
	except IOError:
	    self.ui.statusbar.showMessage("Error: File Save As abandoned",2000)
	
	if not fname.isEmpty(): 
	    self.ui.resultLE.setText(fname)
	    self.ui.resultLE.setEnabled(True)
 
    #-------------------------------------------------------------------
    def radio_same_check(self):
	sameFile = self.ui.radio_same.isChecked()
	if sameFile == True:
	    self.ui.resultLE.setEnabled(False)
	    self.ui.btn_path.setEnabled(False)
	else:
	    self.ui.resultLE.setEnabled(True)
	    self.ui.btn_path.setEnabled(True)
    
    #===================================================================
    #===================================================================
    #===================================================================
    #------ Training  --------------------------------------------------
    #===================================================================
    
    def btn_trainPath_clicked(self):
	# clear
	del self.trainedOutputList[:]
	self.ui.trainDataEdit.clear()
	self.clearTrainingsResults()
	self.ui.lbl_sep_train.setText('')

	#~ fname = QFileDialog.getOpenFileName(self,
		    #~ "SAMT2 - Fuzzy ----- Open Training Data File",	    
		    #~ self.path_save_data,
		    #~ "Data Files (*.txt *.csv);;All Files (*)")
	fname = ""	    
	try:
	    fname = QtGui.QFileDialog.getOpenFileName(self, 
			"SAMT2 - Fuzzy ----- Open Training Data File", 
			self.path_save_data,
			"All Files (*)")
	except IOError:
	    self.ui.statusbar.showMessage("Error: File Open abandoned",2000)
		    
	if not fname.isEmpty():
	    self.ui.trainPathEdit.setText(fname)
	    # search the separator
	    sep = self.get_separator(fname,self.ui.trainHeaderSpinBox.value()) 
	    if sep == None:
		self.ui.statusbar.showMessage("Separator missed!",5000)
		self.ui.trainDataEdit.clear()
		self.ui.lbl_sep_train.setText('')
		return
	    self.ui.lbl_sep_train.setText(sep)
	    file = QFile(fname)
	    if file.open(QIODevice.ReadOnly):
		stream = QTextStream(file)
		self.ui.trainDataEdit.setPlainText(stream.readAll())
	    self.ui.btn_startTraining.setEnabled(True)
	    self.ui.trainDataEdit.setEnabled(True)
	    self.modelTrained = False
	else:
	    self.ui.statusbar.showMessage("File Open abandoned", 2000 )
	    self.ui.btn_startTraining.setEnabled(False)
	    self.ui.trainDataEdit.setEnabled(True)
	    
	# read training data into fuzzy
	if (self.ui.outputTable.rowCount()!=0) and \
			    (self.ui.rulesTable.rowCount()!=0):
	    retu = self.work.read_train_data(str(self.ui.trainPathEdit.text()),
				    self.ui.trainHeaderSpinBox.value(),
				    str(self.ui.lbl_sep_train.text()))
	    if retu == False:
		return
	    # for the untrained model:
	    v = self.work.get_rms()
	    v = round(float(v), 4)
	    self.ui.mse1LE.setText(str(v))
	    self.ui.btn_startTraining.setFocus()
    
    #-------------------------------------------------------------------
    def btn_trainStart_clicked(self):

	if self.ui.trainPathEdit.text().isEmpty():
	    msg = QString("Data File is missing!")
	    self.ui.statusbar.showMessage(msg, 4000)
	    return
	if (self.ui.outputTable.rowCount()!=0) and \
				(self.ui.rulesTable.rowCount()!=0):
	    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
	    # Training Start
	    self.work.train_start()	# ---> new trained outputs

	    # for the trained model
	    v = self.work.get_rms()
	    v = round(float(v), 4)
	    self.ui.mse2LE.setText(str(v))

	    del self.trainedOutputList[:]
	    # save the new output objects in a list
	    self.trainedOutputList = self.work.get_outputs()
	    
	    QtGui.QApplication.restoreOverrideCursor()
	    if len(self.trainedOutputList) == 0:
		print "Error - trained Output is Empty!"
		return
	    self.modelTrained = True
	    li_title = []
	    li_trained = []
	    li_old = []
	    li_y = []   # dummy for y achse in koordsystem
	    i = 0
	    for o in self.trainedOutputList:
		name = self.work.get_outp_name_singleton(o)
		val  = self.work.get_outp_val(o)
		val = "%.3f" % val
		val_old = self.origOutputVals[i]
		# parameter for plot
		li_title.append(name)
		li_trained.append(val)
		li_old.append(val_old)
		li_y.append(0)   	# dummy
		# show: name, old outp, new trained outp
		self.ui.trainedOutputEdit.append(name + "\t"
						+ str(val_old)  + "\t"
						+ str(val))
		# refresh Reiter Output: outputTable (column: Value)   
		valItem = QTableWidgetItem(val)
		valItem.setText(str(val))
		valItem.setTextAlignment(Qt.AlignCenter)
		valItem.setFlags(valItem.flags() & ~Qt.ItemIsEditable)
		self.ui.outputTable.setItem(i,1,valItem)
		i += 1 
	    self.ui.btn_restore_orig.setEnabled(True)
	    
	    self.showTrainedOutputs(li_title,li_old,li_trained,li_y)	
	    
	    # makes it possible to load a new file and train it
	    self.fuzzy_refresh()	
	    
    #-------------------------------------------------------------------
    def showTrainedOutputs(self, li_title,li_old, li_trained, li_y):
	# called by: btn_trainStart, clearTrainingsResults
  	numOut = len(li_title)
	xname = str(self.ui.outputLE.text())
	
	# trainOutWid was mapped in GUI the file painttrain.py 
	# with class PaintTrain and class DiagrTrain
	self.ui.trainOutWid.dia.setLists(li_title,
					li_old, li_trained, li_y,
					xname, self)
	self.ui.trainOutWid.dia.plot() 
        
    #-------------------------------------------------------------------
    def btn_restore_orig_clicked(self):
	# delete the trained outputs
	self.ui.mse2LE.clear()
	self.ui.trainedOutputEdit.clear()
	del self.trainedOutputList[:]
	li = self.trainedOutputList
	# delete the plot
	self.showTrainedOutputs(li, li, li, li)    # blank lists
	
	# get the old original outputs from list 
	i = 0
	for v_old in self.origOutputVals:
  	    valItem = QTableWidgetItem(v_old)
	    valItem.setText(str(v_old))
	    valItem.setTextAlignment(Qt.AlignCenter)
	    valItem.setFlags(valItem.flags() & ~Qt.ItemIsEditable)
	    self.ui.outputTable.setItem(i,1,valItem)
	    i += 1
	self.fuzzy_refresh()		   # fuzzy with orig. Outputs
	self.ui.tabwid.setCurrentIndex(1)  # --> refresh Output page

    #-------------------------------------------------------------------
    def btn_clear_clicked(self):
	self.clear_Training_page()
    
    #-------------------------------------------------------------------
    def clear_Training_page(self):
	# called by: btn_clear_clicked, initialize (fileNew, fileOpen)
    	self.ui.mse1LE.clear()
	self.ui.lbl_sep_train.setText('')
	self.ui.trainPathEdit.clear()
	self.ui.trainDataEdit.clear()
	self.clearTrainingsResults()
	
    #-------------------------------------------------------------------
    def clearTrainingsResults(self):
	# called by: btn_trainPath, disableTrainingsWidgets
	self.ui.mse2LE.clear()
	self.ui.trainedOutputEdit.clear()
	self.ui.trainHeaderSpinBox.setValue(1)
	self.ui.btn_restore_orig.setEnabled(False)
	self.modelTrained = False
	# delete the plot
	del self.trainedOutputList[:]
	li = self.trainedOutputList
	self.showTrainedOutputs(li, li, li, li)    # 4 blank lists
	
    #-------------------------------------------------------------------
    def disableTrainingsWidgets(self):
	# called by: fileOpen()
	self.ui.trainPathEdit.clear()
	self.ui.btn_startTraining.setEnabled(False)
	self.ui.trainDataEdit.setEnabled(False)
	self.ui.trainDataEdit.clear()
	self.modelTrained = False
	self.clearTrainingsResults()


    #===================================================================
    #===================================================================
    #===================================================================
    #------ Rules Training ---------------------------------------------
    #=================================================================== 
    
    def clear_RulesTraining_page(self):
	# clear all in page
	row = self.ui.trainedRulesTbl.rowCount()
	for k in range(row):
	    self.ui.trainedRulesTbl.removeRow(0)
	self.set_trainedRulesTableLabel(2)
	
	self.ui.lbl_sep_rtrain.setText('')
	self.ui.rtrainPathEdit.clear()
	self.ui.rtrainDataEdit.clear()
	self.ui.rtrainHeaderSpinBox.setValue(1)
	self.ui.le_alpha.setText('0.75')
	
    #---------------------------------------------------------------
    def btn_rules_trainPath_clicked(self):
	self.clear_RulesTraining_page()
	fname = ""
	try:
	    fname = QFileDialog.getOpenFileName(self,
		    "SAMT2 - Fuzzy ----- Open Training Data File",	    
		    self.path_save_data,
		    "All Files (*)")
		    #"Data Files (*.txt *.csv);;All Files (*)")
	except IOError:
	    self.ui.statusbar.showMessage("Error: File Open abandoned",2000)
	    
	if not fname.isEmpty():
	    self.ui.rtrainPathEdit.setText(fname)
	    # search the separator
	    sep = self.get_separator(fname,
				    self.ui.rtrainHeaderSpinBox.value()) 
	    if sep == None:
		self.ui.statusbar.showMessage("Separator missed!",5000)
		self.ui.rtrainDataEdit.clear()
		self.ui.lbl_sep_rtrain.setText('')
		return
	    self.ui.lbl_sep_rtrain.setText(sep)
	    file = QFile(fname)
	    if file.open(QIODevice.ReadOnly):
		stream = QTextStream(file)
		self.ui.rtrainDataEdit.setPlainText(stream.readAll())
	    self.ui.btn_start_rulesTrain.setEnabled(True)
	    self.ui.rtrainDataEdit.setEnabled(True)
	else:
	    self.ui.statusbar.showMessage("File Open abandoned", 2000 )
	    self.ui.btn_start_rulesTrain.setEnabled(False)
	    self.ui.rtrainDataEdit.setEnabled(True)
	    
	# read training data into fuzzy
	if (self.ui.outputTable.rowCount()!=0) and \
			    (self.ui.rulesTable.rowCount()!=0):
	    retu = self.work.read_train_data(
				    str(self.ui.rtrainPathEdit.text()),
				    self.ui.rtrainHeaderSpinBox.value(),
				    str(self.ui.lbl_sep_rtrain.text()))
	    if retu == False:
		return
	    self.ui.btn_start_rulesTrain.setFocus()

    #-------------------------------------------------------------------
    def btn_rules_trainStart_clicked(self):
	in1 = ""
	in2 = ""
	in3 = ""
	if self.ui.rtrainPathEdit.text().isEmpty():
	    msg = QString("Data File for Rule_Training is missing!")
	    self.ui.statusbar.showMessage(msg, 4000)
	    return
	if (self.ui.outputTable.rowCount()!=0) and \
				(self.ui.rulesTable.rowCount()!=0):
	    # save current fx --> fx_old
	    # because train_rules_start overwrites rules in current fx
	    self.work.rett_fx()

	    # Training Start 
	    s = str(self.ui.le_alpha.text())
	    if self.is_number(s)==False or float(s)<=0 or float(s)>1.0:
		self.ui.le_alpha.setText('0.75') # correctur
		yesno = self.work.train_rules_start(0.75) 
	    else:
		yesno = self.work.train_rules_start(float(s))
	    if yesno == False:
		print "Error: in fx.train_rules"
		return
	    
	    # after Rule Training
	    li_outp, li_rules = self.work.get_outp_rules_list()
	    for r in li_rules:
		tupel = self.work.get_rule(r)	
		in1 = self.work.get_mf_name(0, tupel[0])
		if self.numInput >1:	
		    in2 = self.work.get_mf_name(1, tupel[1])	
		if self.numInput > 2:
		    in3 = self.work.get_mf_name(2, tupel[2])
		outidx = tupel[-2]   
		o = li_outp[outidx]
		oname = self.work.get_outp_name_singleton(o)
		cf = round(tupel[-1],3)	
		self.insert_trainedRulesTbl(in1,in2,in3,oname,cf)	
	    
	    self.upd_verticalHeaderLabel(self.ui.trainedRulesTbl, 
						len(li_rules))
    
    #-------------------------------------------------------------------
    def insert_trainedRulesTbl(self, in1,in2,in3,oname,cf):
	# called by: btn_rules_trainStart_clicked
	# put rules from current fuzzy object into trainedRulesTbl
	row = self.ui.trainedRulesTbl.rowCount()
	self.ui.trainedRulesTbl.insertRow(row)
	self.ui.trainedRulesTbl.setRowHeight(row, 24)

	if self.numInput == 1: 
	    item = QtGui.QTableWidgetItem('input1')
	    item.setText(in1)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable) # ReadOnly
	    self.ui.trainedRulesTbl.setItem(row,0,item)
	    #output
	    item = QtGui.QTableWidgetItem('o')
	    item.setText(oname)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.trainedRulesTbl.setItem(row,3,item)
	    #cf
	    item = QtGui.QTableWidgetItem('cf')
	    item.setText(str(cf))
	    item.setTextAlignment(Qt.AlignLeft)
	    item.setTextAlignment(Qt.AlignVCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.trainedRulesTbl.setItem(row,4,item)

	    self.ui.trainedRulesTbl.hideColumn(1)
	    self.ui.trainedRulesTbl.hideColumn(2)
	
	elif self.numInput == 2:
	    # input1
	    item = QtGui.QTableWidgetItem('input1')
	    item.setText(in1)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.trainedRulesTbl.setItem(row,0,item)		    
	    # input2
	    item = QtGui.QTableWidgetItem('input2')
	    item.setText(in2)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.trainedRulesTbl.setItem(row,1,item)
	    #output
	    item = QtGui.QTableWidgetItem('o')
	    item.setText(oname)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.trainedRulesTbl.setItem(row,3,item)
	    #cf
	    item = QtGui.QTableWidgetItem("cf")
	    item.setText(str(cf))      
	    item.setTextAlignment(Qt.AlignLeft)
	    item.setTextAlignment(Qt.AlignVCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.trainedRulesTbl.setItem(row,4,item)
	    
	    self.ui.trainedRulesTbl.showColumn(1)
	    self.ui.trainedRulesTbl.hideColumn(2)
	    
	elif self.numInput == 3:
	    # input1
	    item = QtGui.QTableWidgetItem('input1')
	    item.setText(in1)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.trainedRulesTbl.setItem(row,0,item)		    
	    # input2
	    item = QtGui.QTableWidgetItem('input2')
	    item.setText(in2)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.trainedRulesTbl.setItem(row,1,item)
	    #input3
	    item = QtGui.QTableWidgetItem("input3")
	    item.setText(in3)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.trainedRulesTbl.setItem(row,2,item)
	    #output
	    item = QtGui.QTableWidgetItem('o')
	    item.setText(oname)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.trainedRulesTbl.setItem(row,3,item)
	    #cf
	    item =  QTableWidgetItem("cf")
	    item.setText(str(cf))   
	    item.setTextAlignment(Qt.AlignLeft)
	    item.setTextAlignment(Qt.AlignVCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.trainedRulesTbl.setItem(row,4,item)
	    
	    self.ui.trainedRulesTbl.showColumn(1)
	    self.ui.trainedRulesTbl.showColumn(2)
	self.set_trainedRulesTableLabel(1)
    
    #-------------------------------------------------------------------
    def set_trainedRulesTableLabel(self,q):
    	# called by: insert_trainedRulesTable (q=1)
	#    "     : clear_RulesTraining_page (q=2)
	# sets the horizontal header of the trainedRulesTbl
	self.ui.trainedRulesTbl.resizeColumnToContents(2)
	self.ui.trainedRulesTbl.resizeColumnToContents(3)
	if self.numInput >= 1:
	    item = self.ui.trainedRulesTbl.horizontalHeaderItem(0)
	    if q == 1:
		item.setText(self.ui.inputCombo.itemText(0)) 
	    else:
		item.setText('Input1')
	    self.ui.trainedRulesTbl.resizeColumnToContents(0)
	    self.ui.trainedRulesTbl.resizeColumnToContents(1)
	if self.numInput >= 2:
	    item = self.ui.trainedRulesTbl.horizontalHeaderItem(1)
	    if q == 1:
		item.setText(self.ui.inputCombo.itemText(1))
	    else:
		item.setText('Input2')
	    self.ui.trainedRulesTbl.resizeColumnToContents(2)
  	if self.numInput == 3:
	    item = self.ui.trainedRulesTbl.horizontalHeaderItem(2)
	    if q == 1:
		item.setText(self.ui.inputCombo.itemText(2))
	    else:
		item.setText('Input3')
	    self.ui.trainedRulesTbl.resizeColumnToContents(3)
	outputItem = self.ui.trainedRulesTbl.horizontalHeaderItem(3)
	if q == 1:
	    outputItem.setText(self.ui.outputLE.text())
	else:
	    outputItem.setText('Output')
	cfItem = self.ui.trainedRulesTbl.horizontalHeaderItem(4)
	cfItem.setText("cf")	
	
    #-------------------------------------------------------------------
    def refresh_rulesTable(self, in1,in2,in3,oidx,cf,outList):
	# get Rules from fx obj. and fill it into table in Rules Page
	row = self.ui.rulesTable.rowCount()
	self.ui.rulesTable.insertRow(row)
	self.ui.rulesTable.setRowHeight(row,24)
	
	# create ComboTableItem for output column in the rulesTable
	cb = QtGui.QComboBox(self.ui.rulesTable)
	cb.setObjectName("cbobj")
	cb.addItems(outList)
	
	if self.numInput == 1: 
	    item = QtGui.QTableWidgetItem('input1')
	    item.setText(in1)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable) # ReadOnly
	    self.ui.rulesTable.setItem(row,0,item)
	    #output
	    cb.setCurrentIndex(oidx)
	    self.ui.rulesTable.setCellWidget(row, 3, cb)
	    #cf
	    item = QtGui.QTableWidgetItem('cf')
	    item.setText(str(cf))
	    item.setTextAlignment(Qt.AlignLeft)
	    item.setTextAlignment(Qt.AlignVCenter)
	    self.ui.rulesTable.setItem(row,4,item)
	    # set colums hidden
	    self.ui.rulesTable.hideColumn(1)
	    self.ui.rulesTable.hideColumn(2)
	elif self.numInput == 2:
	    # input1
	    item = QtGui.QTableWidgetItem('input1')
	    item.setText(in1)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.rulesTable.setItem(row,0,item)		    
	    # input2
	    item = QtGui.QTableWidgetItem('input2')
	    item.setText(in2)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.rulesTable.setItem(row,1,item)
	    #output
	    cb.setCurrentIndex(oidx)
	    self.ui.rulesTable.setCellWidget(row, 3, cb)
	    #cf
	    item = QtGui.QTableWidgetItem("cf")
	    item.setText(str(cf))      
	    item.setTextAlignment(Qt.AlignLeft)
	    item.setTextAlignment(Qt.AlignVCenter)
	    self.ui.rulesTable.setItem(row,4,item)
	    self.ui.rulesTable.showColumn(1)
	    self.ui.rulesTable.hideColumn(2)
	elif self.numInput == 3:
	    # input1
	    item = QtGui.QTableWidgetItem('input1')
	    item.setText(in1)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.rulesTable.setItem(row,0,item)		    
	    # input2
	    item = QtGui.QTableWidgetItem('input2')
	    item.setText(in2)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.rulesTable.setItem(row,1,item)
	    #input3
	    item = QtGui.QTableWidgetItem("input3")
	    item.setText(in3)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    self.ui.rulesTable.setItem(row,2,item)
	    #output
	    cb.setCurrentIndex(oidx)
	    self.ui.rulesTable.setCellWidget(row, 3, cb)
	    #cf
	    item = QTableWidgetItem("cf")
	    item.setText(str(cf))   
	    item.setTextAlignment(Qt.AlignLeft)
	    item.setTextAlignment(Qt.AlignVCenter)
	    self.ui.rulesTable.setItem(row,4,item)
	    self.ui.rulesTable.showColumn(1)
	    self.ui.rulesTable.showColumn(2)

    #-------------------------------------------------------------------
    def btn_rules_save_clicked(self):

	# delete retted fx
	self.work.delete_retted_fx()
	
	li_outp, li_rules = self.work.get_outp_rules_list()
	
	# clear rulesTable complete and refresh it with new trained Rules
	row = self.ui.rulesTable.rowCount()
	for k in range(row):
	    self.ui.rulesTable.removeRow(0)
	
	# fill outList for Output-Combobox in rulesTable
	outList = []
	for o in li_outp:
	    name = self.work.get_outp_name_singleton(o)
	    outList.append(name) 
	in1 = ""
	in2 = ""
	in3 = ""
	for r in li_rules:
	    tupel = self.work.get_rule(r)
	    outidx = tupel[-2]   
	    o = li_outp[outidx]
	    oname = self.work.get_outp_name_singleton(o)
	    in1 = self.work.get_mf_name(0, tupel[0])
	    if self.numInput >1:	
		in2 = self.work.get_mf_name(1, tupel[1])	
	    if self.numInput == 3:
		in3 = self.work.get_mf_name(2, tupel[2])
	    cf = round(tupel[-1],3)	
	    self.refresh_rulesTable(in1,in2,in3,outidx,cf, outList)
	self.upd_verticalHeaderLabel(self.ui.rulesTable,len(li_rules))
	self.clear_RulesTraining_page()
	
    #-------------------------------------------------------------------
    def btn_rules_discard_clicked(self):

	self.work.restore_fx_old()
	
	self.clear_RulesTraining_page()
	self.ui.tabwid.setCurrentIndex(2)

    #-------------------------------------------------------------------	

    #===================================================================
    #===================================================================
    #===================================================================
    #------ ALLGEMEIN --------------------------------------------------
    #===================================================================  
    
    def upd_verticalHeaderLabel(self, tableObj, lae):
	# lae: length of QTableWidget
	tableObj.setVerticalHeaderLabels(["%d" %i for i in range(lae)]) 
    
    #-------------------------------------------------------------------
    def statusbar_msg_changed(self, args):
        '''
	in:	message to show in statusbar (QString) , color BLUE
	out: 	if ERROR inside text: text color RED, 
	'''
	if not args:
            self.ui.statusbar.setStyleSheet("QStatusBar{color:blue;}") 
	else:
	    if args.left(5).toLower() == 'error':
		self.ui.statusbar.setStyleSheet("QStatusBar{color:red;}") 
    
    #-------------------------------------------------------------------
    def info(self, msg):
	QMessageBox.information(self,"SAMT-Fuzzy Info",msg)

    #-------------------------------------------------------------------
    def is_number(self, s):
	"""	in: 	s  string	"""
	try:
	    float(s)
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
    def closeEvent(self, event):
	# all PopupWindows close  
	if len(self.li_popups) > 0:
	    for win in self.li_popups:
		win.close()
	event.accept()
    
    #===================================================================
    # ----- class MyForm E N D -----------
    #===================================================================


########################################################################
class Popup_active_rules(QtGui.QWidget):
    def __init__(self, X, Y, su1,ruleList,muList,outputList,ifthenList,
		    li_col_header,n,in3const=0.0,parent=None):
	# called by: mouse on_release in analyse
	QtGui.QWidget.__init__(self,  parent=None)
	self.ui = Ui_rulesform()
	self.ui.setupUi(self)
	self.setWindowTitle('SAMT2 - Fuzzy ----- Active Rules')
	self.ui.table.setColumnWidth(0, 40)
	self.ui.table.setColumnWidth(2, 60)
	self.ui.table.setColumnWidth(6, 60)
	anz_inp = n
	
	# input names for TableColumnHeader
	self.ui.table.setHorizontalHeaderLabels(li_col_header)
	#location = "X=%.3f  Y=%.3f" % (X,Y)  # --> für winlabel

	for i in range(len(ruleList)):
	    self.ui.table.insertRow(i)
	    
	    item = QtGui.QTableWidgetItem("nr")
	    s = str(ruleList[i])
	    item.setText(s)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable) # is ReadOnly
	    self.ui.table.setItem(i,0,item) 
	    
	    item = QtGui.QTableWidgetItem("rule")
	    s = ifthenList[i]           
	    item.setText(s)
	    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    
	    # only QTextEdit has fct .setHtml()
	    qTE = QTextEdit(self.ui.table) 
	    qTE.setObjectName("QTextEdi")
	    qTE.setFrameShadow(QtGui.QFrame.Plain)
	    qTE.setLineWidth(0)
	    qTE.setReadOnly(True)
	    qTE.setHtml(s)
	    self.ui.table.setCellWidget(i,1,qTE)
	    	
	    item = QtGui.QTableWidgetItem("mu")
	    s = "%.3f" % muList[i]
	    item.setText(s)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable) # is ReadOnly
	    self.ui.table.setItem(i,2,item)
	
	    item = QtGui.QTableWidgetItem("in1")
	    s = "%.3f" % X
	    item.setText(s)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
	    self.ui.table.setItem(i,3,item)
	    
	    if anz_inp == 1:
		self.ui.table.hideColumn(4)
		self.ui.table.hideColumn(5)
		self.ui.table.resizeColumnToContents(3)
	    
	    elif anz_inp == 2:
		item = QtGui.QTableWidgetItem("in2")
		s = "%.3f" % Y
		#print Y, s
		item.setText(s)
		item.setTextAlignment(Qt.AlignCenter)
		item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
		self.ui.table.setItem(i,4,item)
		self.ui.table.hideColumn(5)
		self.ui.table.resizeColumnToContents(3)
		self.ui.table.resizeColumnToContents(4)
	    
	    elif anz_inp == 3:
		item = QtGui.QTableWidgetItem("in2")
		s = "%.3f" % Y
		item.setText(s)
		item.setTextAlignment(Qt.AlignCenter)
		item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
		self.ui.table.setItem(i,4,item)
		item = QtGui.QTableWidgetItem("in3")
		s = "%.3f" % in3const
		item.setText(s)
		item.setTextAlignment(Qt.AlignCenter)
		item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
		self.ui.table.setItem(i,5,item)
		self.ui.table.resizeColumnToContents(3)
		self.ui.table.resizeColumnToContents(4)
		self.ui.table.resizeColumnToContents(5)

	    item = QtGui.QTableWidgetItem("out")
	    s = "%.3f" % outputList[i]
	    item.setText(s)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
	    item.setForeground(QColor('darkred'))
	    self.ui.table.setItem(i,6,item)
	    
	    item = QtGui.QTableWidgetItem("ent_out")
	    s = "%.3f" % su1
	    item.setText(s)
	    item.setTextAlignment(Qt.AlignCenter)
	    item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
	    self.ui.table.setItem(i,7,item)

	    self.ui.table.setColumnWidth(1, 300)

########################################################################

class Popup_transect(QtGui.QMainWindow):
    def __init__(self,t,mx,liX, liY,oname,flag_absolut,
		max_out=0,min_out=0,
		parent=None):
	QtGui.QWidget.__init__(self,  parent=None)
	self.ui = Ui_plotwin()
	self.ui.setupUi(self)
	# Layout
	vbox = QVBoxLayout()
        vbox.addWidget(self.ui.main_frame.canvas)
	self.ui.main_frame.setLayout(vbox)
        self.setCentralWidget(self.ui.main_frame)
	self.setWindowTitle('SAMT2 - Fuzzy ----- Transect')

	pax = self.ui.main_frame.canvas.ax
	pax.clear()
	pax.set_xlabel('L')
	pax.set_ylabel(oname)
	if flag_absolut == True:
	    pax.set_ylim(min_out, max_out)
	pax.grid(True)
	
	txt = '%s: (%.3f, %.3f)  (%.3f, %.3f)' % ('Output', 
					liX[0],liY[0],liX[1],liY[1])
	pax.set_title(txt)
	 
	# thousands separator: , 
	majorFormatter = mpl.ticker.FuncFormatter \
				    (lambda x, p: format(int(x), ','))
	pax.get_xaxis().set_major_formatter(majorFormatter)
	pax.plot(t, mx, color='blue')
	self.ui.main_frame.canvas.draw()
	 
    
########################################################################
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    locale.setlocale(locale.LC_NUMERIC, "C")    # decimal_point
    window = MyForm() 
    window.show()
    sys.exit(app.exec_())
########################################################################

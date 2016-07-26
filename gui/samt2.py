#!/usr/bin/env python
# -*- coding: utf-8 -*-              

import sys
import os
import subprocess
import numpy as np
import csv
import copy
import locale

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.lines as line
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_qt4agg  \
    import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg \
    import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import pandas as pd
import pandas.io.data
from pandas import Series, DataFrame

from form1_ui import Ui_MainWindow
from plotwin_ui import Ui_plotwin
from plotwin3d_ui import Ui_plotwin3d
from tablewin_ui import Ui_tablewin
from rulesform_ui import Ui_rulesform
from expression_ui import Ui_expression

sys.path.append(os.environ['SAMT2MASTER']+"/gui")
import gisdoc 

########################################################################

class MyForm(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
	QtGui.QWidget.__init__(self,  parent)
	self.ui = Ui_MainWindow()
	self.ui.setupUi(self)
	
	self.gdoc = gisdoc.gisdoc()
	self.env = os.environ['SAMT2MASTER']+'/gui' # s. Zeile 1025
	self.daten_path = os.environ['SAMT2DATEN']
	self.openedModelPath = '' 	# writes fileOpen only
	
	env = self.env+'/pixmaps'
        self.setWindowIcon(QIcon(env+'/samt2_icon.png'))
	
	# Toolbar
	self.ui.actionZoom_in.setIcon(QIcon(env+'/viewmag+.png'))
	self.ui.actionGraph.setIcon(QIcon(env+'/log.png'))
	self.ui.actionReplot.setIcon(QIcon(env+'/reload.png'))
	self.ui.actionStart_vis.setIcon(QIcon(env+'/forward.png'))
	self.ui.actionGrid_copy.setIcon(QIcon(env+'/editcopy.png'))
	self.ui.actionGrid_rename.setIcon(QIcon(env+'/editpaste.png'))
	self.ui.actionRun_model.setIcon(QIcon(env+'/run.png'))
	self.ui.actionDelete.setIcon(QIcon(env+'/stop.png'))
	self.ui.actionClear_p.setIcon(QIcon(env+'/editdelete.png'))
	
	# mpl_widget  
	vbox = QVBoxLayout()
        vbox.addWidget(self.ui.mpl_widget.canvas)      
	self.ui.mpl_widget.setLayout(vbox)
	#       weisser statt grauer frame
	self.ui.mpl_widget.canvas.fig.set_frameon(False) 
	#       delete x, y-axis incl. ticks 
	self.ui.mpl_widget.canvas.ax.set_axis_off()   
	#        entfernt rand
	self.ui.mpl_widget.canvas.fig.subplots_adjust\
				(left=0,right=1,top=1,bottom=0)
	
	self.w_wid_orig = 646   # mpl_widget.width()
	self.h_wid_orig = 557   # mpl_widget.height()
	self.w_img_scaled = 0
	self.h_img_scaled = 0
	self.startPoint = (0,0)
	self.endPoint = (0,0)
	self.startPointC = (0,0)  # copy of startPoint for actionReplot
	self.endPointC = (0,0)	  # copy of endPoint  (only for Line)
	self.li_X = [0,0]
	self.li_Y = [0,0]
	self.pickedX = 0
	self.pickedY = 0
	self.mxzoom = None
	self.flag_mxzoom = False
	self.isLine = False
	self.isZoom = False
	self.dragging = False
	self.isNodata = False
	self.line1 = None
	self.gname = ''
	self.pname = '' 	# write in: slotTREE_Clicked
	self.mname = ''		#  "
	self.model_kind = ''	#  "
	self.parent = '' 	#  "
	self.li_popups = []
	self.li_catego = []
	self.df = None
	self.d_poi = {}
	self.expr_popup = None
	
	self.ui.ledit_p1 = QLineEdit(self.ui.toolBar)
	self.ui.ledit_p1.setObjectName(QString('P1'))
	self.ui.ledit_p1.setStyleSheet("background-color: rgb(255,255,255)")	
	#self.ui.ledit_p1.setStyleSheet("color: rgb(22,74,4)")	
	self.ui.ledit_p2 = QLineEdit(self.ui.toolBar)
	self.ui.ledit_p2.setObjectName(QString('P2'))
	self.ui.ledit_p2.setStyleSheet("background-color: rgb(255,255,255)")	
	self.ui.ledit_p3 = QLineEdit(self.ui.toolBar)
	self.ui.ledit_p3.setStyleSheet("background-color: rgb(255,255,255)")
	self.ui.ledit_p3.setObjectName(QString('P3'))
	self.ui.toolBar.addWidget(self.ui.ledit_p1)
	self.ui.toolBar.addSeparator();
	self.ui.toolBar.addWidget(self.ui.ledit_p2)
	self.ui.toolBar.addSeparator();
	self.ui.toolBar.addWidget(self.ui.ledit_p3)
	self.ui.toolBar.addSeparator();

	# treeWidget
	self.font_bold = QFont()
	self.font_bold.setBold(True)
	
	self.ui.treeWidget.clear()
	self.ui.treeWidget.setColumnCount(1)
	header = QStringList()
	header.append("data") 
	self.ui.treeWidget.setHeaderLabels(header)
	self.root_grids = QTreeWidgetItem(self.ui.treeWidget)
	self.root_grids.setText(0, "grids")
	self.root_grids.setFont(0, self.font_bold)
	self.root_models = QTreeWidgetItem(self.ui.treeWidget)
	self.root_models.setText(0, "models")
	self.root_models.setFont(0, self.font_bold)
	self.root_points = QTreeWidgetItem(self.ui.treeWidget)
	self.root_points.setText(0, "points")
	self.root_points.setFont(0, self.font_bold)

	#========== connections with GUI ===============================
	# toolbar
	self.connect(self.ui.actionZoom_in, SIGNAL('triggered()'), 
			self.slotVIS_Zoom)
	self.connect(self.ui.actionGraph, SIGNAL('triggered()'), 
			self.slotVIS_Line)
	self.connect(self.ui.actionReplot, SIGNAL('triggered()'), 
			self.slotVIS_Line_End)
	self.connect(self.ui.actionStart_vis, SIGNAL('triggered()'), 
			self.slotVIS_Start)
	self.connect(self.ui.actionGrid_copy, SIGNAL('triggered()'), 
			self.slotGRID_Copy)
			
	self.connect(self.ui.actionGrid_rename, SIGNAL('triggered()'), 
			self.slotGRID_Rename)
	self.connect(self.ui.actionRun_model, SIGNAL('triggered()'), 
			self.slotRun_Model)
	self.connect(self.ui.actionDelete, SIGNAL('triggered()'), 
			self.slotDELETE_Object)
	self.connect(self.ui.actionClear_p, SIGNAL('triggered()'), 
			self.slotClear_p123)

	# menuIO
	self.connect(self.ui.actionHDF_Open_All, SIGNAL('triggered()'), 
			self.slotHDF_Open)
	self.connect(self.ui.actionHDF_Save_Grid, SIGNAL('triggered()'), 
			self.slotHDF_File_Save)
	self.connect(self.ui.actionASCII_Open, SIGNAL('triggered()'), 
			self.slotASCII_Open)
	self.connect(self.ui.actionASCII_Save, SIGNAL('triggered()'), 
			self.slotASCII_File_Save)
	self.connect(self.ui.actionPOINT_Open_geo, SIGNAL('triggered()'), 
			self.slotPOINT_Open_geo)
	self.connect(self.ui.actionPOINT_Open_i_j, SIGNAL('triggered()'), 
			self.slotPOINT_Open_i_j)
	self.connect(self.ui.actionFUZZY_Open, SIGNAL('triggered()'), 
			self.slotFUZZY_Open)
	self.connect(self.ui.actionSVM_Open, SIGNAL('triggered()'), 
			self.slotSVM_Open)	
	
	# menuTools
	self.connect(self.ui.actionFuzzy, SIGNAL('triggered()'), 
			self.slotFuzzy)
	#~ self.connect(self.ui.actionFuzzy_Generator, SIGNAL('triggered()'), 
			#~ self.slotFuzzy_Generator)
	#~ self.connect(self.ui.actionSadato, SIGNAL('triggered()'), 
			#~ self.slotSadato)
	
	# menuAnalysis
	self.connect(self.ui.actionHistogram, SIGNAL('triggered()'), 
			self.slotHistogram)
	self.connect(self.ui.actionStatistic, SIGNAL('triggered()'), 
			self.slotStatistic)
	self.connect(self.ui.actionInfo, SIGNAL('triggered()'), 
			self.slotInfo)
	self.connect(self.ui.actionMake_Map, SIGNAL('triggered()'), 
			self.slotMake_Map)	    
	self.connect(self.ui.actionResize, SIGNAL('triggered()'), 
			self.slotResize)
	self.connect(self.ui.actionCorr, SIGNAL('triggered()'), 
			self.slotCorr)
	self.connect(self.ui.actionSample, SIGNAL('triggered()'), 
			self.slotSample)
	self.connect(self.ui.actionSample_det, SIGNAL('triggered()'), 
			self.slotSample_det)
	self.connect(self.ui.actionExport_R, SIGNAL('triggered()'), 
			self.slotExport_R)
						
	# menuSGrid
	self.connect(self.ui.actionCreate, SIGNAL('triggered()'), 
			self.slotGRID_Create)
	self.connect(self.ui.actionSet, SIGNAL('triggered()'), 
			self.slotGRID_Set)
	self.connect(self.ui.actionSet_ND, SIGNAL('triggered()'), 
			self.slotGRID_Set_ND)
	self.connect(self.ui.actionReplace, SIGNAL('triggered()'), 
			self.slotGRID_Replace)
	self.connect(self.ui.actionAdd, SIGNAL('triggered()'), 
			self.slotGRID_Add)
	self.connect(self.ui.actionMul, SIGNAL('triggered()'), 
			self.slotGRID_Mul)
	self.connect(self.ui.actionLog, SIGNAL('triggered()'), 
			self.slotGRID_Log)
	self.connect(self.ui.actionLn, SIGNAL('triggered()'), 
			self.slotGRID_Ln)
	self.connect(self.ui.actionFabs, SIGNAL('triggered()'), 
			self.slotGRID_Fabs)		
	self.connect(self.ui.actionNorm, SIGNAL('triggered()'), 
			self.slotGRID_Norm)
	self.connect(self.ui.actionZNorm, SIGNAL('triggered()'), 
			self.slotGRID_ZNorm)
	self.connect(self.ui.actionInv, SIGNAL('triggered()'), 
			self.slotGRID_Inv)
	self.connect(self.ui.actionInv_a, SIGNAL('triggered()'), 
			self.slotGRID_Inv_a)
	self.connect(self.ui.actionCond, SIGNAL('triggered()'), 
			self.slotGRID_Cond)
	self.connect(self.ui.actionCut, SIGNAL('triggered()'), 
			self.slotGRID_Cut)
	self.connect(self.ui.actionCut_Off, SIGNAL('triggered()'), 
			self.slotGRID_Cut_Off)
	self.connect(self.ui.actionClass, SIGNAL('triggered()'), 
			self.slotGRID_Class)
	self.connect(self.ui.actionRand_Int, SIGNAL('triggered()'), 
			self.slotGRID_Rand_Int)
	self.connect(self.ui.actionRand_Float, SIGNAL('triggered()'), 
			self.slotGRID_Rand_Float)
		
	# menuAGrid
	self.connect(self.ui.actionCombine_Add, SIGNAL('triggered()'), 
			self.slotGRID_Add_Grid)
	self.connect(self.ui.actionCombine_Diff, SIGNAL('triggered()'), 
			self.slotGRID_Diff_Grid)
	self.connect(self.ui.actionCombine_Mul, SIGNAL('triggered()'), 
			self.slotGRID_Mul_Grid)
	self.connect(self.ui.actionCombine_Min, SIGNAL('triggered()'), 
			self.slotGRID_Min_Grid)
	self.connect(self.ui.actionCombine_Max, SIGNAL('triggered()'), 
			self.slotGRID_Max_Grid)
	self.connect(self.ui.actionCombine_OR, SIGNAL('triggered()'), 
			self.slotGRID_OR_Grid)	
	self.connect(self.ui.actionCombine_AND, SIGNAL('triggered()'), 
			self.slotGRID_AND_Grid)		
	self.connect(self.ui.actionFlood_Fill, SIGNAL('triggered()'), 
			self.slotGRID_Flood_Fill)
	self.connect(self.ui.actionFlood_Fill_std,SIGNAL('triggered()'), 
			self.slotGRID_Flood_Fill_std)
	self.connect(self.ui.actionVarpart, SIGNAL('triggered()'), 
			self.slotGRID_Varpart)
	self.connect(self.ui.actionRemove_Trend, SIGNAL('triggered()'), 
			self.slotGRID_Remove_Trend)
	self.connect(self.ui.actionGrad_d4, SIGNAL('triggered()'), 
			self.slotGRID_Grad_d4)		
	self.connect(self.ui.actionGrad_d8, SIGNAL('triggered()'), 
			self.slotGRID_Grad_d8)
			
	# menuKernel
	self.connect(self.ui.actionKernel_sci, SIGNAL('triggered()'), 
			self.slotKERNEL_Sci)
	self.connect(self.ui.actionKernel_rect, SIGNAL('triggered()'), 
			self.slotKERNEL_Rect)
	self.connect(self.ui.actionKernel_cir, SIGNAL('triggered()'), 
			self.slotKERNEL_Cir)	
	self.connect(self.ui.actionKnn, SIGNAL('triggered()'), 
			self.slotKERNEL_Knn)
	
	# menuPoints
	self.connect(self.ui.actionPOINTS_Inter_linear, SIGNAL(
		    'triggered()'), self.slotPOINTS_Inter_linear)
	self.connect(self.ui.actionPOINTS_Inter_multiquadric, SIGNAL(
		    'triggered()'), self.slotPOINTS_Inter_multiquadric)
	self.connect(self.ui.actionPOINTS_Inter_inverse, SIGNAL(
		    'triggered()'), self.slotPOINTS_Inter_inverse)		
	self.connect(self.ui.actionPOINTS_Inter_gaussian, SIGNAL(
		    'triggered()'), self.slotPOINTS_Inter_gaussian)	
	self.connect(self.ui.actionPOINTS_Inter_cubic, SIGNAL(
		    'triggered()'), self.slotPOINTS_Inter_cubic)	
	self.connect(self.ui.actionPOINTS_Inter_quintic, SIGNAL(
		    'triggered()'), self.slotPOINTS_Inter_quintic)	
	self.connect(self.ui.actionPOINTS_Inter_thin_plate, SIGNAL(
		    'triggered()'), self.slotPOINTS_Inter_thin_plate)
	self.connect(self.ui.actionVoronoi, SIGNAL('triggered()'), 
			self.slotPOINTS_Voronoi)
	self.connect(self.ui.actionPoisson, SIGNAL('triggered()'), 
			self.slotPOINTS_Poisson)
	self.connect(self.ui.actionDistance, SIGNAL('triggered()'), 
			self.slotPOINTS_Distance)
	
	# menuView
	self.connect(self.ui.actionShow_Black_White,SIGNAL('triggered()'),
			self.slotVIS_Start)
	self.connect(self.ui.actionShow_Diff,SIGNAL('triggered()'),
			self.slotVIS_Start)
	
	# menuTable
	self.connect(self.ui.actionTABLE_Lut,SIGNAL('triggered()'),
			self.slotTABLE_Lut)
	self.connect(self.ui.actionSelect, SIGNAL('triggered()'), 
			self.slotGRID_Select)
			
	# menuHelp
	self.connect(self.ui.actionAbout,SIGNAL('triggered()'),
			self.slotAbout)
	self.connect(self.ui.actionManual,SIGNAL('triggered()'),
			self.slotManual)
			
	# allgemein
	self.connect(self.ui.statusBar,SIGNAL('messageChanged(QString)'), 
			self.statusbar_msg_changed)
	self.connect(self.ui.treeWidget, SIGNAL(
			'itemClicked(QTreeWidgetItem*,int)'),
			self.slotTREE_Clicked)
	self.connect(self.ui.treeWidget, SIGNAL(
			'itemDoubleClicked(QTreeWidgetItem*,int)'),
			self.slotTREE_DblClicked)
	
	# mouseEvents
	self.ui.mpl_widget.canvas.mpl_connect(
			     'button_press_event', self.on_press)
        self.ui.mpl_widget.canvas.mpl_connect(
			     'motion_notify_event', self.on_motion)
	self.ui.mpl_widget.canvas.mpl_connect(
			    'button_release_event', self.on_release)
	
	
	#!!!!!!!!!!!!!!!nur f. test, f. Ralf raus 
	#self.slotHDF_Open()
	#self.ui.actionColorbar.setChecked(True)
	print "*****************************************************"	

    #===================================================================
    #============ TOOLBAR actions ======================================
    #===================================================================
    #	actionZoom_in---------slotVIS_Zoom
    #	actionGraph --------- slotVIS_Line 
    #	actionReplot----------slotVIS_Line_End
    #	actionStart_vis ----- slotVIS_Start
    #	actionGrid_copy-------slotGRID_Copy
    #	actionGrid_rename-----slotGRID_Rename
    #	actionRun_model-------slotRun_Model
    #	actionDelete----------slotDELETE_Object
    #	actionClear_p123------slotClear_p123
    #===================================================================
    
    def slotVIS_Zoom(self):
	# call from: actionZoom_in,
	if self.ui.actionZoom_in.isChecked():
	    if self.flag_mxzoom == False:
		self.isZoom = True
		self.isLine = False
		self.ui.actionGraph.setChecked(False)
		self.clear_old_line()
		self.clear_old_rect()
		self.ui.mpl_widget.canvas.draw()
		self.set_default_new_rect()
	    else:
	    	print "Zoom_in is not possible 2nd time"
		self.ui.actionZoom_in.setChecked(False)
	else:
	    self.isZoom = False
	    
    #-------------------------------------------------------------------
    def clear_old_rect(self):
	# called from: slotVIS_Zoom, slotVIS_Line,vis_zoomgrid..
	lae = len(self.ui.mpl_widget.canvas.ax.patches)
	for i in range(lae):
	    self.ui.mpl_widget.canvas.ax.patches.pop(0)
	
    #-------------------------------------------------------------------
    def set_default_new_rect(self):
        # call from: slotVIS_Zoom
	self.startPoint = (0,0)
	self.endPoint = (0,0)
	w = 1
	h = 1
	self.rect = mpl.patches.Rectangle(self.startPoint, w, h,\
						    facecolor='none') 
	self.ui.mpl_widget.canvas.ax.add_patch(self.rect)
    
    #-------------------------------------------------------------------
    def slotVIS_Zoom_End(self):
	# call from: on_release,
	i0 = self.startPoint[1]
	i1 = self.endPoint[1]
	j0 = self.startPoint[0]
	j1 = self.endPoint[0]
	# i0,j0 upper left corner / i1,j1 lower right corner
	self.mxzoom,mi,ma,nrows,ncols,mea,std = self.gdoc.get_mx_zoom(
						self.gname,i0,i1,j0,j1)
	if mi == None:
	    print "Zoom_End errror"
	    return
	self.vis_zoomgrid(self.mxzoom,mi,ma,nrows,ncols)
	
	msg, mi, ma, mea = self.gdoc.zoom_statistic(self.gname,
				    i0,i1,j0,j1,mi,ma,mea,std)
 	QtGui.QMessageBox.information(self, \
		    self.tr("Zoom: Statistical output"), QString(msg)) 
	self.ui.ledit_p1.setText(QString(mi))
	self.ui.ledit_p2.setText(QString(ma))
	self.ui.ledit_p3.setText(QString(mea))
	
	# for mouse_click --> z value from self.mxzoom 
	# set = False in mouseEv on_release
	self.isZoom = True 

    #-------------------------------------------------------------------
    def vis_zoomgrid(self, mx, mi, ma, nrows, ncols):
	#print "vis_zoomgrid: nrows i, ncols j, self.startPoint: ", \
	#				nrows, ncols, self.startPoint
	# delete old line, rect if exists
	if self.line1 != None:
	    self.clear_old_line()
	    self.set_default_new_line()
	    self.ui.mpl_widget.canvas.draw()
	if self.rect != None:  
	    self.clear_old_rect()
	    #self.set_default_new_rect()    # in [0,0]
	    self.ui.mpl_widget.canvas.draw()
		
	if mx != None:
	    w_img = ncols    
	    h_img = nrows
	    w_wid = self.w_wid_orig    
	    h_wid = self.h_wid_orig
	    #print "w_wid=%d, h_wid=%d" % (self.w_wid_orig,self.h_wid_orig)    
	    fac = self.scale_coordsystem(w_wid, h_wid, w_img, h_img)
	    
	    # the top left position of mpl_widget
	    pos = QPoint   
	    pos = self.ui.mpl_widget.pos()	    
	    self.w_img_scaled = float(w_img)*fac
	    self.h_img_scaled = float(h_img)*fac
	    #print "w_img_scaled=%d, h_img_scaled=%d" % (self.w_img_scaled, self.h_img_scaled)
	    self.ui.mpl_widget.setGeometry(pos.x(), pos.y(),
					    int(self.w_img_scaled), 
					    int(self.h_img_scaled))
	    self.ui.mpl_widget.canvas.fig.set_frameon(False) 
	    self.ui.mpl_widget.canvas.ax.set_axis_off()   
	    self.ui.mpl_widget.canvas.fig.subplots_adjust\
				    (left=0,right=1,top=1,bottom=0)
	    cmap = mpl.cm.get_cmap('jet', 500)
	    cmap.set_under('white') 
	    img = self.ui.mpl_widget.canvas.ax.imshow(mx, cmap=cmap,\
				    interpolation='none',aspect='auto')
	    img.set_clim(mi, ma)
	    self.ui.mpl_widget.canvas.draw()
	    
    
    #-------------------------------------------------------------------   
    def slotVIS_Line(self):
    	if self.ui.actionGraph.isChecked():
	    self.isNodata = False
	    self.isLine = True
	    self.isZoom = False
	    self.ui.actionZoom_in.setChecked(False)
	    self.clear_old_rect()   #del point in top left (0,0)
	    self.clear_old_line()
	    self.ui.mpl_widget.canvas.draw()
	    self.set_default_new_line()
	else:
	    self.isLine = False
	
    #-------------------------------------------------------------------
    def clear_old_line(self):
	# called from: slotVIS_Start, slotVIS_Line
	lae = len(self.ui.mpl_widget.canvas.ax.lines)
	for i in range(lae):
	    self.ui.mpl_widget.canvas.ax.lines.pop(0)
		
    #-------------------------------------------------------------------
    def set_default_new_line(self):
        # call from: slotVIS_Start, slotVIS_Line
	self.startPoint = (0,0)
	self.endPoint = (0,0)
	self.li_X = [0,0]
	self.li_Y = [0,0]
	self.line1 = line.Line2D([], [], color='black', linewidth=0.5)
    
    #-------------------------------------------------------------------
    def slotVIS_Line_End(self):
	# called from: actionReplot and on_release
	if self.gdoc.get_matrix(self.gname) == False:
	    msg = self.tr("error: Line has no grid")
	    self.ui.statusBar.showMessage(msg,2000)
	    return
	if self.ui.actionReplot.isChecked():
	    #print "slotVIS_Line_End: actionReplot=T, get old line"
	    #print self.startPointC, self.endPointC
	    self.ui.actionReplot.setChecked(False)
	    li_x = [0,0]
	    li_y = [0,0]
	    li_x[0] = self.startPointC[0]    
	    li_y[0] = self.startPointC[1]
	    li_x[1] = self.endPointC[0]    
	    li_y[1] = self.endPointC[1]
	    self.line1 = line.Line2D([],[],color='black',linewidth=0.5)
	    self.line1.set_data(li_x, li_y)
	    self.ui.mpl_widget.canvas.ax.add_line(self.line1)
	    self.ui.mpl_widget.canvas.draw()
	
	#  plot transect for (y0,x0, y1,x1)
	i0 = self.startPointC[1]
	j0 = self.startPointC[0]
	i1 = self.endPointC[1]
	j1 = self.endPointC[0]
	t, mx = self.gdoc.get_mx_transect(self.gname,i0,j0,i1,j1)
	if t == None:
	    print "Line_End error"
	    return
	popup = Popup_transect(self.gname,t,mx,i0,j0,i1,j1)
	popup.show()
	self.li_popups.append(popup)
	    
    #-------------------------------------------------------------------
    def slotGRID_Rename(self):
	itemx = self.ui.treeWidget.currentItem()
	if self.parent == 'points':
	    return
	if itemx != '':
	    if self.item_is_child(itemx) == False:
		return
	    name2 = str(self.ui.ledit_p1.text())
	    gname_new = self.gdoc.grid_rename(str(itemx.text(0)),name2)  
	    print gname_new
	    # del in the tree
	    itemx.parent().removeChild(itemx)
	    # append on tree
	    it = QTreeWidgetItem(self.root_grids)
	    it.setText(0, QString(gname_new))
	    self.ui.treeWidget.addTopLevelItem(it)
	    self.ui.treeWidget.expandItem(self.root_grids)
	    self.clear_3lineEdits()
	
    #------------------------------------------------------------------
    def slotGRID_Copy(self):
	if self.parent == 'points':
	    return
	name2 = str(self.ui.ledit_p1.text())   
	copy_name = self.gdoc.grid_copy(self.gname, name2) 
	# append on tree
	it = QTreeWidgetItem(self.root_grids)
	it.setText(0, QString(copy_name))
	self.ui.treeWidget.addTopLevelItem(it)
	self.ui.treeWidget.expandItem(self.root_grids)
	self.clear_3lineEdits()
    
    #-------------------------------------------------------------------
    def slotRun_Model(self):
	#--> out: new grid --> into TREE/grids --> show HF"
	v1 = str(self.ui.ledit_p1.text())
	if v1 == '':
	    print "error run_model: P1 expected"
	    return
	v2 = str(self.ui.ledit_p2.text())
	v3 = str(self.ui.ledit_p3.text())
	if v1 != '' and v2 != '' and v3 != '':
	    anz_g = 3
	elif v2 == "":
	    anz_g = 1
	else:
	    anz_g = 2
	
	if self.parent == "grids":
	    # starts Popup with expression builder
	    self.run_popup_expr(anz_g, v1, v2, v3)
	    return
	if self.parent == "points":
	    return
	
	# -------- models -----------------
	if self.model_kind == "fuzzy":
	    anz_inp = self.gdoc.get_nr_fuz_inputs(self.mname)
	    if anz_g != anz_inp:
		print "Error: %d grids are expected, you selected %d" % \
							(anz_inp, anz_g)
		return
		
	QtGui.QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
	if anz_g == 3:
	    gx = self.gdoc.run_model(
		    self.mname,self.model_kind,anz_g,v1,v2=v2,v3=v3)
	    if gx == None:
		print "calc3 error"
	elif anz_g == 2:
	    gx = self.gdoc.run_model(
		    self.mname,self.model_kind,anz_g,v1,v2=v2)#,v3=None)
	    if gx == None:
		print "calc2 error"
	elif anz_g == 1:    
	    gx =self.gdoc.run_model(self.mname,self.model_kind,anz_g,v1)
	    if gx == None:
		print "calc1 error"
	QtGui.QApplication.restoreOverrideCursor()
	# append in TREE/grids
	if gx != None:
	    gname_new = self.gdoc.add_grid(self.mname, gx)
	    self.append_new_grid(gname_new) 
	    self.highlight_new_child(0)
	
    #-------------------------------------------------------------------
    def run_popup_expr(self, n, v1, v2, v3):
	# call from: slotRun_Model,  TREE parent='grids'
	anza = 0
	if v1 != '':
	    g1 = self.gdoc.get_d_grids_val(v1)
	    if g1 == None: 
		print "error  run_expr: g1"
		return None
	    anza = 1
	if v2 != '':
	    g2 = self.gdoc.get_d_grids_val(v2)
	    if g2 == None: 
		print "error  run_expr: g2"
		return None
	    anza = 2
	if v3 != '':
	    g3 = self.gdoc.get_d_grids_val(v3)
	    if g3 == None: 
		print "error  run_expr: g3"
		return None
	    anza = 3
	if anza != n:
	    print "not all grids found"
	    return None
		    
	if n == 2:
	    g3 = None
	elif n == 1:    
	    g2 = None
	    g3 = None
		    
	popup = Popup_expression(v1, v2,v3, g1, g2=g2, g3=g3)
	popup.show()
	self.li_popups.append(popup)
	self.expr_popup = popup   # obj. f. bridge_exr..
	# weiter in set_expr_paras	    
	
    #-------------------------------------------------------------------
    def slotDELETE_Object(self):
	itemx = self.ui.treeWidget.currentItem()
	if itemx != '':
	    if self.item_is_child(itemx) == False:
		return
	    key = str(itemx.text(0))
	    
	    # 1. del im dict   
	    if str(itemx.parent().text(0)) == 'grids':
		if self.gdoc.del_d_grids_key(str(key)) == False:
		    print "error while del_d_grids_key"
	    elif str(itemx.parent().text(0)) == 'points':
		if self.gdoc.del_d_points_key(str(key)) == False:
		    print "error while del_d_points_key"
	    elif str(itemx.parent().text(0)) == 'models':
		if self.gdoc.del_d_models_key(
				str(key),self.model_kind) == False:
		    print "error while del_d_model_key"
	    else:
		print "not deleted"
		
	    # 2. del im tree
	    itemx.parent().removeChild(itemx)	     
  
	    # 3. del self.gname   
	    if self.gname == key:
		self.gname = ''
		# clear plot 
		self.ui.mpl_widget.canvas.ax.cla()
		self.ui.mpl_widget.canvas.ax.set_axis_off() 
		self.ui.mpl_widget.canvas.ax.plot([])   #1, 2, 3
		self.ui.mpl_widget.canvas.draw()
	    if self.pname == key:
		self.gname = ''
	    if self.mname == key:
		self.mname = ''
		self.model_kind = ''
		
    #-------------------------------------------------------------------   
    def slotClear_p123(self):
	self.clear_3lineEdits()
	
    
    #===================================================================
    #========== MENU actions ===========================================
    #===================================================================
    
    #------------ menu IO ----------------------------------------------
    def slotHDF_Open(self):
	if self.openedModelPath == '':
	    path = self.daten_path +'/hdf'
	else:
	    path = self.openedModelPath
	name_hdf = QString()
	name_hdf = QtGui.QFileDialog.getOpenFileName(self, 
		    self.tr("Open File"), 
		    path, self.tr("Images (*.hdf *hdf5 *h5)"))
	
	if(name_hdf.isEmpty()):
	    #self.openedModelPath = QString("") 
	    return
	self.openedModelPath = name_hdf  
	
	li_namen_grid = self.gdoc.get_list_grids(str(name_hdf))
	if li_namen_grid == None:
	    print "HDF_Open Error"
	    return
	li_namen_grid.sort()   		
	for gname in li_namen_grid:
	    ds_new = self.gdoc.add_hdf(str(name_hdf), str(gname))
	    it = QTreeWidgetItem(self.root_grids)
	    it.setText(0, QString(ds_new))
	    self.ui.treeWidget.addTopLevelItem(it)
	self.ui.treeWidget.expandItem(self.root_grids) 
	self.highlight_new_child_only(0)
	
    #-------------------------------------------------------------------
    def highlight_new_child_only(self, idx):
	# call from slotHDF_Open, slotASCII_Open, slotSVM_Open, slotHDF_Open
	# like highlight_new_child(idx), but without slotVIS_Start
	
	topLvlItem = self.ui.treeWidget.topLevelItem(idx) 
	# first remove old selection in treeItem
	self.deselect_tree()
	if self.ui.treeWidget.isItemExpanded(topLvlItem):
	    anz = topLvlItem.childCount()
	    for i in range(0, anz):
		childItem = topLvlItem.child(i)
		if i == anz-1:
		    childItem.setSelected(True)
		    self.ui.treeWidget.setCurrentItem(childItem)
		    self.slotTREE_Clicked()
	
    #------------------------------------------------------------------
    def slotASCII_Open(self):
	if self.openedModelPath == '':
	    path = self.daten_path +'/ascii'
	else:
	    path = self.openedModelPath
	name_file = QString()
	name_file = QtGui.QFileDialog.getOpenFileName(self, 
		    self.tr("Open File"), path, 
		    self.tr("Images (*.asc *.ascii *.txt)"))
	if(name_file.isEmpty()):
	    #self.openedModelPath = QString("") 
	    return
	self.openedModelPath = name_file  
	li = name_file.split('/')
	li2 = li[-1].split('.')   # li[-1]  name.asc
	ds_new = self.gdoc.add_ascii(str(name_file), str(li2[0]))
		
	it = QTreeWidgetItem(self.root_grids)
	it.setText(0, QString(ds_new))
	self.ui.treeWidget.addTopLevelItem(it)
	self.ui.treeWidget.expandItem(self.root_grids)
	self.highlight_new_child_only(0)
	
    #-------------------------------------------------------------------
    def slotHDF_File_Save(self):
	dataset = self.ui.ledit_p1.text()
	modell = self.ui.ledit_p2.text()
	bemerk = self.ui.ledit_p3.text()
	if (modell.isEmpty() or bemerk.isEmpty() or 
			dataset.isEmpty() or self.gname==''):
	    msg = self.tr("Error: P1=dataset P2=modelname\
				  P3=remark expected")
	    self.ui.statusBar.showMessage(msg, 10000)
	    return
	path = self.openedModelPath   #self.daten_path +'/hdf'
	filename = QtGui.QFileDialog.getSaveFileName(self,
	    "Choose a filename to save under", path,
	    "Images (*.hdf *h5 *hdf5)");
	if filename.isEmpty():
	    print "error hdf_file_save: no filename"
	    return
	if self.gdoc.save_hdf(str(filename),str(dataset),
				str(modell),str(bemerk),
				str(self.gname)) == True:
	    msg = self.tr("Document saved: ") + filename
	    self.ui.statusBar.showMessage(msg, 2000)
	else:
	    msg = self.tr("error: dataset already exist: ")+dataset
	    self.ui.statusBar.showMessage(msg,2000)
	    return
    	self.clear_3lineEdits()    #self.ui.ledit_p1.clear()
    	
    #-------------------------------------------------------------------
    def slotASCII_File_Save(self):
	path = self.openedModelPath    #= self.daten_path +'/ascii'
	filename = QtGui.QFileDialog.getSaveFileName(self,
	    "Choose a filename to save under", path,
	    "Images (*.asc *.ascii *.txt)");
	if filename.isEmpty():
	    return
	self.gdoc.save_ascii(str(filename), self.gname)
	msg = self.tr('Document saved: ') + filename
	self.ui.statusBar.showMessage(msg, 2000)
	self.clear_3lineEdits()
	
    #-------------------------------------------------------------------
    def slotPOINT_Open_geo(self):
	if self.gname == '':
	    msg ="Error: No highlighted grid"
	    self.ui.statusBar.showMessage(self.tr(msg))
	    return
	art = 'yx'
	if self.openedModelPath == '':
	    path = self.daten_path +'/points'
	else:
	    path = self.openedModelPath
	name_file = QString()
	name_file = QtGui.QFileDialog.getOpenFileName(self, 
		    self.tr("Open File"), path, 
		    self.tr("Points (*.csv *.asc *.txt)"))
	if(name_file.isEmpty()):
	    #self.openedModelPath = QString("") 
	    return
	self.openedModelPath = name_file 
	name_file = str(name_file)
	li = name_file.split('/')
	li22 = li[-1].split('.')  
	pname = str(li22[0])
	li_names = ['y','x','z']
	 
	with open(name_file, 'r') as csvfile:
	    dialec = csv.Sniffer().sniff(csvfile.read())
	    csvfile.seek(0)
	    header = csv.Sniffer().has_header(csvfile.read())#True/False 
	    csvfile.seek(0)
	    if header == True:
		self.df = pd.read_csv(csvfile, dialect=dialec,
				skipinitialspace=True,
				names=li_names, sep=None, header=0) 
	    else:
		self.df = pd.read_csv(csvfile, dialect=dialec,
				skipinitialspace=True,
				names=li_names, sep=None, header=None)       
	
	li1 = self.df['y'].tolist()    	# senkrecht
	li2 = self.df['x'].tolist()	# waagerecht
	liz = self.df['z'].tolist()

	li3,li4,pname_new = self.gdoc.add_points(
				    self.gname,pname,li1,li2,liz,art) 
	if li3 == None:
	    print "POINT_geo_Open Error"
	    return
	# now d_points[pname] filled with 5 lists and
	# make a pandas:DataFrame from 5 lists
	self.d_poi.clear()
	self.d_poi['y'] = li1
	self.d_poi['x'] = li2
	self.d_poi['i'] = li3    
	self.d_poi['j'] = li4    
	self.d_poi['z'] = liz
	self.pname = pname_new
	# refresh tree	
	it = QTreeWidgetItem(self.root_points)
	it.setText(0, QString(pname_new))
	self.ui.treeWidget.addTopLevelItem(it)
	self.ui.treeWidget.expandItem(self.root_points)

    #-------------------------------------------------------------------
    def slotPOINT_Open_i_j(self):
	if self.gname == '':
	    msg ="Error: No highlighted grid"
	    self.ui.statusBar.showMessage(self.tr(msg))
	    return
	art = 'ij'
	#samtpath = window.get_samt_path()
	if self.openedModelPath == '':
	    path = self.daten_path +'/points'
	else:
	    path = self.openedModelPath

	name_file = QString()
	name_file = QtGui.QFileDialog.getOpenFileName(self, 
		    self.tr("Open File"), path, 
		    self.tr("Points (*.csv *.asc *.txt)"))
	if(name_file.isEmpty()): 
	    return
	self.openedModelPath = name_file
	name_file = str(name_file)
	li = name_file.split('/')
	li22 = li[-1].split('.')
	pname = str(li22[0]) 
	li_names = ['i','j','z']
		   
	with open(name_file, 'r') as csvfile:
	    dialec = csv.Sniffer().sniff(csvfile.read())
	    csvfile.seek(0)
	    header = csv.Sniffer().has_header(csvfile.read())
	    csvfile.seek(0)
	    if header == True:
		self.df = pd.read_csv(csvfile, dialect=dialec,
				skipinitialspace=True,
				names=li_names, sep=None, header=0) 
	    else:
		self.df = pd.read_csv(csvfile, dialect=dialec,
				skipinitialspace=True, 
				names=li_names, sep=None, header=None)       

	li1 = self.df['i'].tolist()    	# senkrecht
	li2 = self.df['j'].tolist()	# waagerecht
	liz = self.df['z'].tolist()

	li3,li4,pname_new = self.gdoc.add_points(
				    self.gname,pname,li1,li2,liz,art) 
	if li3 == None:
	    print "POINT_Open Error"
	    return
	self.d_poi.clear()
	self.d_poi['y'] = li3
	self.d_poi['x'] = li4
	self.d_poi['i'] = li1    
	self.d_poi['j'] = li2   
	self.d_poi['z'] = liz
	self.pname = pname_new
	# refresh tree	
	it = QTreeWidgetItem(self.root_points)
	it.setText(0, QString(pname_new))
	self.ui.treeWidget.addTopLevelItem(it)
	self.ui.treeWidget.expandItem(self.root_points)
    
    #-------------------------------------------------------------------
    def get_z_from_picked_YX(self, gname, Y, X):
	# call from Popup_vis_colorbar 
	z = self.gdoc.get_gx_val(gname, Y, X)
	return z
	
    #-------------------------------------------------------------------
    def get_z_from_picked_mx(self, mx, Y, X):
	# from  Popup_vis_colorbar, Show-Diff has only a mx, not gx
	z = self.gdoc.get_mx_val(mx, Y, X)
	return z

    #-------------------------------------------------------------------
    def get_dict_points(self, pname):
	li = self.gdoc.get_d_points(pname)  # list of 5 lists
	return li
	
    #-------------------------------------------------------------------
    def get_samt_path(self):
	return self.env
	
	#---------------------------------------------------------------
    def get_daten_path(self):
	return self.daten_path
	
    #-------------------------------------------------------------------
    def set_d_poi_new_z(self, liz):
	# call from Popup_points_dataframe: btn_ok
	del self.d_poi['z']
	self.d_poi['z'] = liz
	self.gdoc.set_d_points(self.pname, liz)
	
    #-------------------------------------------------------------------
    def bridge_expr_calc(self, res_name, expr, g1,g2,g3):
	# call from Popup_expression: btn_calc  (bridge!!)
	self.expr_res_name = res_name
	QtGui.QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
	gout = self.gdoc.get_expr_gout(expr, g1,g2,g3)
	if gout == None:
	    QtGui.QApplication.restoreOverrideCursor()
	    self.expr_popup.set_msg_statusbar("error in calc expression")
	else:
	    # a new grid append in TREE/grids
	    gname_new = self.gdoc.add_grid(res_name, gout)
	    self.append_new_grid(gname_new) 
	    self.highlight_new_child(0)
	    QtGui.QApplication.restoreOverrideCursor()
	    self.expr_popup.set_msg_statusbar('')
    #-------------------------------------------------------------------
    def get_edited_pandas_dataframe(self):
	dframe = pd.DataFrame(self.d_poi)
	return dframe
	
    #-------------------------------------------------------------------
    def slotFUZZY_Open(self):
	if self.openedModelPath == '':
	    path = self.daten_path +'/model/fuzzy'     #/fis'
	else:
	    path = self.openedModelPath
	name_file = QString()
	name_file = QtGui.QFileDialog.getOpenFileName(self, 
		    self.tr("Open File"), path, 
		    self.tr("Models (*.fis)"))
	if(name_file.isEmpty()): 
	    return
	self.openedModelPath = name_file
	li = name_file.split('/')
	li2 = li[-1].split('.')   
	ds_new = self.gdoc.add_model_fuz(str(name_file), str(li2[0]))
	
	# a new model append in TREE/models	
	it = QTreeWidgetItem(self.root_models)
	it.setText(0, QString(ds_new))
	self.ui.treeWidget.addTopLevelItem(it)
	self.ui.treeWidget.expandItem(self.root_models)
	self.highlight_new_child_only(1)

    #-------------------------------------------------------------------
    def slotSVM_Open(self):
	if self.openedModelPath == '':
	    path = self.daten_path +'/model/svm'
	else:
	    path = self.openedModelPath
	name_file = QString()
	name_file = QtGui.QFileDialog.getOpenFileName(self, 
		    self.tr("Open File"), path, 
		    self.tr("Models (*.svm)"))
	if(name_file.isEmpty()): 
	    return
	self.openedModelPath = name_file
	
	
	li = name_file.split('/')
	li2 = li[-1].split('.')  
	#print "slotSVM_Open::", name_file, li2[0] # 
	 
	ds_new = self.gdoc.add_model_svm(str(name_file), str(li2[0]))
	
	if ds_new != None:
	    it = QTreeWidgetItem(self.root_models)
	    it.setText(0, QString(ds_new))
	    self.ui.treeWidget.addTopLevelItem(it)
	    self.ui.treeWidget.expandItem(self.root_models)
	    self.highlight_new_child_only(1)
    
    
    #=========== menu Tools ============================================
    def slotFuzzy(self):
	# like Popup
	s = os.environ['SAMT2MASTER']+'/fuzzy/gui/samt2fuzzy.py'
	p = subprocess.Popen(s)
    
    #-------------------------------------------------------------------
    #~ def slotSadato(self):
	#~ s = os.environ['SADATO']+'/sadato'
	#~ p = subprocess.Popen(s)
 
    
    #=========== menu Analysis =========================================
    
    def slotHistogram(self):
	s = self.ui.ledit_p1.text()
	if self.is_number(s) == False or float(s) < 0:  
	    bins = 20
	else:
	    bins = int(s)
	    self.ui.ledit_p1.clear()
	mx = self.gdoc.get_mx_hist(self.gname, bins)
	if mx == None:
	    print "Hist error"
	    return
	popup = Popup_histogram(self.gname, mx, bins)
	popup.show()
	self.li_popups.append(popup)
	    
    #-------------------------------------------------------------------
    def slotStatistic(self):
	msg,mi,ma,mea = self.gdoc.grid_statistic(self.gname)  
	QtGui.QMessageBox.information(self, \
		    self.tr("Statistical output"), QString(msg)) 
	self.ui.ledit_p1.setText(QString(mi))
	self.ui.ledit_p2.setText(QString(ma))
	self.ui.ledit_p3.setText(QString(mea))
	
    #-------------------------------------------------------------------
    def slotInfo(self):
	nrows, ncols, nodata = self.gdoc.grid_info(self.gname) 
	if nrows == False:
	    print "Grid Info error"
	    return
	s = QString()
	self.ui.ledit_p1.setText(s.setNum(nrows))
	self.ui.ledit_p2.setText(s.setNum(ncols))
	self.ui.ledit_p3.setText(s.setNum(nodata))
	
    #-------------------------------------------------------------------
    def slotMake_Map(self):
	v1 = str(self.ui.ledit_p1.text())  # precis
	if self.is_number(v1) == False or v1 == '':  
	    v1 = '2399'
	
	QtGui.QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
	mx = self.gdoc.make_map_mx(self.gname, int(v1)) 
	QtGui.QApplication.restoreOverrideCursor()

	if mx == None:
	    print "Make Map error"
	else:
	    #time.sleep(1)   #sec
	    popup = Popup_map(self.gname, mx)
	    popup.show()
	    self.li_popups.append(popup)
	#threading.Timer(5, self.start_popup_map(mx)).start()

    #-------------------------------------------------------------------
    def slotResize(self):
	v1 = str(self.ui.ledit_p1.text())  # nrows
	v2 = str(self.ui.ledit_p2.text())  # ncols
	if self.is_number(v1) == False or self.is_number(v2) == False:  
	    return
	if self.gdoc.grid_resize(self.gname,int(v1),int(v2)) == False:
	    print "Grid Resize error"
	else:
	    self.slotVIS_Start()
    
    #-------------------------------------------------------------------
    def slotCorr(self):
	v1 = str(self.ui.ledit_p1.text())
	corrcoef = self.gdoc.get_corr(self.gname, v1)
	if corrcoef == False:
	    print "Corr errror"
	    return
	self.ui.ledit_p2.setText(str(corrcoef))
    
    #-------------------------------------------------------------------
    def slotSample(self):
	# v1 = nr=100  random points aus grid ---> y,x,z --> popupTable 
	# ---> save in tree/points 
	v1 = str(self.ui.ledit_p1.text())
	if self.is_number(v1) == False:  
	    v1 = 100
	a_i,a_j,a_z = self.gdoc.sample(self.gname, int(v1))
	if a_i == None:
	    print "sample error"
	    return
	lii = a_i.tolist()
	lij = a_j.tolist() 
	liz = a_z.tolist() 
	pname = self.gname
	art = 'ij'
	li3,li4,pname_new = self.gdoc.add_points(
				    self.gname,pname,lii,lij,liz,art) 
	self.d_poi.clear()
	self.d_poi['y'] = li3
	self.d_poi['x'] = li4
	self.d_poi['i'] = lii
	self.d_poi['j'] = lij
	self.d_poi['z'] = liz
	self.pname = pname_new
	self.append_new_point(pname_new)
	self.highlight_new_child(2)  # points  
	# incl. --> VIS_Start  --> points_table_show
	
    #-------------------------------------------------------------------
    def slotSample_det(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.is_number(v1) == False:  
	    v1 = '0'
	v1 = float(v1)
	a_i,a_j = self.gdoc.sample_det(self.gname, v1)
	if a_i == None:
	    print "sample error"
	    return
	lii = a_i.tolist()
	lij = a_j.tolist() 
	lae = len(lii)
	# lae mal den gleichen v1 in liste schreiben
	liz = map(lambda x: v1, range(lae))
	pname = self.gname
	art = 'ij'
	li3,li4,pname_new = self.gdoc.add_points(
				    self.gname,pname,lii,lij,liz,art) 
	self.d_poi.clear()
	self.d_poi['y'] = li3
	self.d_poi['x'] = li4
	self.d_poi['i'] = lii
	self.d_poi['j'] = lij
	self.d_poi['z'] = liz     
	self.pname = pname_new
	self.append_new_point(pname_new)
	self.highlight_new_child(2)  # points 
	
    #-------------------------------------------------------------------
    def slotExport_R(self):
	v1 = str(self.ui.ledit_p1.text())  	# grid1 (x1)
	v2 = str(self.ui.ledit_p2.text())	# grid2 (x2)
	v3 = str(self.ui.ledit_p3.text())	# grid3 (x3)
	vx = self.gname  # highlighted grid= gx (zu modellierendes y)
	
	if vx in (v1, v2, v3):
	    print "error: vx mehrfach"
	    return
	#path = self.get_samtpath() +'/data/exportR_'
	path = self.daten_path+'/data/exportR_'
	filename = QtGui.QFileDialog.getSaveFileName(self,
	    "Choose a filename to save under", path,
	    "Images (*.csv *.txt *.asc)");
	if filename.isEmpty():
	    print "A filename is necessary"
	    return
	if v3 != '':
	    res, resy = self.gdoc.sample_export_R(4,filename,vx,v1,v2=v2,v3=v3)
	elif v2 != '':
	    res, resy = self.gdoc.sample_export_R(3,filename,vx,v1,v2=v2)
	elif v1 != '':
	    res, resy = self.gdoc.sample_export_R(2,filename,vx,v1)
	self.clear_3lineEdits() 
	
    #=========== menu Simple_Grid ======================================
    
    def slotGRID_Create(self):
	v1 = str(self.ui.ledit_p1.text())	# gname
	v2 = str(self.ui.ledit_p2.text())	# nrows
	v3 = str(self.ui.ledit_p3.text())	# ncols

	if v1.strip() == "":  
	    print "v1 fehlt return"
	    self.ui.ledit_p1.clear()
	    return
	
	if self.is_number(v2) == False or v2.strip() == "":  
	    print "v2 leer oder keine Zahl - return"
	    self.ui.ledit_p2.clear()
	    return
	
	if self.is_number(v3) == False or v3.strip() == "":  
	    print "v3 leer oder keine Zahl - return"
	    self.ui.ledit_p3.clear()
	    return
	
	# make an empty new grid[rows,cols]
	# and fill it with random int values
	
	gname_new = self.gdoc.grid_create(v1, int(v2),int(v3))
	
	if gname_new == False:
	    print "create error"
	    sys.exit(0)
	else:
	    # append in TREE/grids
	    self.append_new_grid(gname_new) 
	    self.highlight_new_child(0)
	    self.slotVIS_Start(1)
	
    #-------------------------------------------------------------------
    def slotGRID_Set(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.is_number(v1) == False:
	    return
	if self.gdoc.grid_set(self.gname, v1) == False:
	    print "set error"
	else:
	    self.slotVIS_Start(1)
	    
    #-------------------------------------------------------------------
    def slotGRID_Set_ND(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.is_number(v1) == False:
	    return
	if self.gdoc.grid_set_nd(self.gname, v1) == False:
	    print "set_all_nd error"
	else:
	    self.slotVIS_Start(1)

    #-------------------------------------------------------------------
    def slotGRID_Replace(self):
	v1 = str(self.ui.ledit_p1.text())
	v2 = str(self.ui.ledit_p2.text())
	if self.is_number(v1)== False or self.is_number(v2)== False:  
	    return
	if self.gdoc.grid_replace(self.gname,v1,v2) == False:
	    print "replace error"
	else:
	    self.slotVIS_Start(1)
    
    #-------------------------------------------------------------------
    def slotGRID_Add(self):
	v1 = self.ui.ledit_p1.text()
	if self.is_number(v1) == False:  
	    return
	if self.gdoc.grid_add(self.gname,v1) == False:
	    print "add error"
	else:
	    self.slotVIS_Start(1)
	    
    #-------------------------------------------------------------------
    def slotGRID_Mul(self):
	v1 = self.ui.ledit_p1.text()
	if self.is_number(v1) == False:  
	    return
	if self.gdoc.grid_mul(self.gname,v1) == False:
	    print "mul error"
	else:
	    self.slotVIS_Start(1)
	    
    #-------------------------------------------------------------------
    def slotGRID_Log(self):
	v1 = self.ui.ledit_p1.text()
	if self.is_number(v1)== True:
	    retu = self.gdoc.grid_log(self.gname, float(v1))
	else:
	    retu = self.gdoc.grid_log(self.gname)
	if retu == False:
	    print "Log error"
	else:
	    self.slotVIS_Start(1)
	    
    #-------------------------------------------------------------------
    def slotGRID_Ln(self):
	v1 = self.ui.ledit_p1.text()
	if self.is_number(v1)== True:
	    retu = self.gdoc.grid_ln(self.gname, float(v1))
	else:
	    retu = self.gdoc.grid_ln(self.gname)
	if retu == False:
	    print "Ln error"
	else:
	    self.slotVIS_Start(1)
	    
    #-------------------------------------------------------------------
    def slotGRID_Fabs(self):
	if self.gdoc.grid_fabs(self.gname) == False:
	    print "Fabs error"
	else:
	    self.slotVIS_Start(1)
	    	    
    #-------------------------------------------------------------------
    def slotGRID_Norm(self):
	if self.gdoc.grid_norm(self.gname) == False:
	    print "Norm error"
	else:
	    self.slotVIS_Start() 
	    
    #-------------------------------------------------------------------
    def slotGRID_ZNorm(self):
	if self.gdoc.grid_znorm(self.gname) == False:
	    print "ZNorm error"
	else:
	    self.slotVIS_Start(1) 
	    
    #-------------------------------------------------------------------
    def slotGRID_Inv(self):
	if self.gdoc.grid_inv(self.gname) == False:
	    print "Inv error"
	else:
	    self.slotVIS_Start(1) 
	    
    #-------------------------------------------------------------------
    def slotGRID_Inv_a(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.is_number(v1) == False:  
	    print 'Missing P1 value'
	    return
	if self.gdoc.grid_inv_ab(self.gname, float(v1)) == False:
	    print "Inv_a error"
	else:
	    self.slotVIS_Start(1)   
	    
    #-------------------------------------------------------------------
    def slotGRID_Cond(self):
	v1 = self.ui.ledit_p1.text()	# min
	v2 = self.ui.ledit_p2.text()	# max
	v3 = self.ui.ledit_p3.text()
	if self.is_number(v1)== False or self.is_number(v2)== False: 
	    return
	if self.is_number(v3) == True:
	    retu = self.gdoc.grid_cond(self.gname,v1,v2,v3)
	else:
	    retu = self.gdoc.grid_cond(self.gname,v1,v2)
	if retu == False:
	    print "cond error"
	else:
	    self.slotVIS_Start(1)
		
    #-------------------------------------------------------------------
    def slotGRID_Cut(self):
	# replace max with v1
	v1 = self.ui.ledit_p1.text()	# new max
	v2 = self.ui.ledit_p2.text()
	if self.is_number(v1)== False : 
	    return
	if self.is_number(v2) == True:
	    retu = self.gdoc.grid_cut(self.gname,v1,v2)
	else:
	    retu = self.gdoc.grid_cut(self.gname,v1)
	if retu == False:
	    print "cut error"
	else:
	    self.slotVIS_Start(1)
    
    #-------------------------------------------------------------------
    def slotGRID_Cut_Off(self):
	v1 = self.ui.ledit_p1.text()
	v2 = self.ui.ledit_p2.text()
	v3 = self.ui.ledit_p3.text()
	if self.is_number(v1)== False or self.is_number(v2)== False: 
	    return
	if self.is_number(v3) == True:
	    retu = self.gdoc.grid_cut_off(self.gname,v1,v2,v3)
	else:
	    retu = self.gdoc.grid_cut_off(self.gname,v1,v2)
	if retu == False:
	    print "cut_off error"
	else:
	    self.slotVIS_Start(1)
    
    #-------------------------------------------------------------------
    def slotGRID_Class(self):
	v1 = self.ui.ledit_p1.text()
	if self.is_number(v1)== True:
	    retu = self.gdoc.grid_classify(self.gname, int(v1))
	else:
	    retu = self.gdoc.grid_classify(self.gname)
	if retu == False:
	    print "class error"
	else:
	    self.slotVIS_Start(1)

    #-------------------------------------------------------------------
    def slotGRID_Rand_Int(self):
	""" fills an empty grid with random int values [min, max]"""
	v1 = str(self.ui.ledit_p1.text())
	if self.is_number(v1) == False:  
	    self.ui.ledit_p1.clear()
	    v1 = 1
	v2 = str(self.ui.ledit_p2.text())
	if self.is_number(v2) == False:  
	    self.ui.ledit_p2.clear()
	    v2 = 10
	# get mx
	retu = self.gdoc.get_grid_rand_int(self.gname, int(v1), int(v2))
	if retu == None:
	    print "grid_rand_int Error"
	else:
	    self.slotVIS_Start(1)		    
	    
    #-------------------------------------------------------------------
    def slotGRID_Rand_Float(self):
	""" fills an empty grid with random values """   
	# get mx
	retu = self.gdoc.get_grid_rand_float(self.gname)
	if retu == None:
	    print "grid_rand_float Error"
	else:
	    self.slotVIS_Start(1)	
	 
    
    #=========== menu Advanced_Grid ====================================
    
    def slotGRID_Add_Grid(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.gdoc.grid_combine(self.gname, v1, 'add') == None:
	    print "add_grid error"
	else:
	    self.slotVIS_Start()
	    msg ="%s + %s" % (self.gname, v1)
	    self.ui.statusBar.showMessage(self.tr(msg))
    
    #-------------------------------------------------------------------
    def slotGRID_Diff_Grid(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.gdoc.grid_combine(self.gname, v1, 'diff') == None:
	    print "diff_grid error"
	else:
	    self.slotVIS_Start()
	    msg ="%s + %s" % (self.gname, v1)
	    self.ui.statusBar.showMessage(self.tr(msg))
    
    #-------------------------------------------------------------------
    def slotGRID_Mul_Grid(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.gdoc.grid_combine(self.gname, v1,'mul') == None:
	    print "mul_grid error"
	else:
	    self.slotVIS_Start()
	    msg ="%s * %s" % (self.gname, v1)
	    self.ui.statusBar.showMessage(self.tr(msg))
	    
    #-------------------------------------------------------------------
    def slotGRID_Min_Grid(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.gdoc.grid_combine(self.gname, v1, 'min') == None:
	    print "min_grid error"
	else:
	    self.slotVIS_Start()
	    msg ="%s, %s using minimum" % (self.gname, v1)
	    self.ui.statusBar.showMessage(self.tr(msg))
	    
    #-------------------------------------------------------------------
    def slotGRID_Max_Grid(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.gdoc.grid_combine(self.gname, v1, 'max') == None:
	    print "max_grid error"
	else:
	    self.slotVIS_Start()
	    msg ="%s, %s using maximum" % (self.gname, v1)
	    self.ui.statusBar.showMessage(self.tr(msg))
	    
    #-------------------------------------------------------------------
    def slotGRID_OR_Grid(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.gdoc.grid_combine(self.gname, v1, 'or') == None:
	    print "or_grid error"
	else:
	    self.slotVIS_Start()
	    msg ="in %s replace nodata with values from %s" %(self.gname,v1)
	    self.ui.statusBar.showMessage(self.tr(msg))
	    
    #-------------------------------------------------------------------
    def slotGRID_AND_Grid(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.gdoc.grid_combine(self.gname, v1, 'and') == None:
	    print "and_grid error"
	else:
	    self.slotVIS_Start()
	    msg ="in %s includes nodata from %s" %(self.gname,v1)
	    self.ui.statusBar.showMessage(self.tr(msg))
	    
    #-------------------------------------------------------------------
    def slotGRID_Flood_Fill(self):
    	v1 = str(self.ui.ledit_p1.text())	# picked i
	v2 = str(self.ui.ledit_p2.text())	# picked j
	v3 = str(self.ui.ledit_p3.text())	# level
	if self.is_number(v1) == False or self.is_number(v2) == False: 
	    return
	if self.is_number(v3) == False:
	    print "flood_fills error"
	    return
	count = self.gdoc.grid_flood_fill(
			    self.gname, int(v1), int(v2), float(v3))
	if count == -9999 or count == None:
	    print "flood_fill error"
	self.slotVIS_Start()
	self.ui.ledit_p1.setText(str(count))
	msg = "FloodFill:  P1: count"
	self.ui.statusBar.showMessage(self.tr(msg))
    
    #-------------------------------------------------------------------
    def slotGRID_Flood_Fill_std(self):
	v1 = str(self.ui.ledit_p1.text())	# picked i
	v2 = str(self.ui.ledit_p2.text())	# picked j
	v3 = str(self.ui.ledit_p3.text())	# level
	if self.is_number(v1) == False or self.is_number(v2) == False: 
	    return
	if self.is_number(v3) == False:
	    print "flood_fills_std error"
	    return
	std,varianz = self.gdoc.grid_flood_fill_std(
			    self.gname, int(v1), int(v2), float(v3))
	if std == -9999 or std == None:
	    print "flood_fills_std error"
	self.slotVIS_Start()
	self.ui.ledit_p1.setText(str(round(std, 4)))
	self.ui.ledit_p2.setText(str(round(varianz, 4)))
	msg ="FloodFill_std:  P1: std, P2: varianz"
	self.ui.statusBar.showMessage(self.tr(msg))
    
    #-------------------------------------------------------------------
    def slotGRID_Varpart(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.is_number(v1) == False or int(v1) == 0:
	    v1 = 5000
	else:
	    v1 = int(v1)
	print "slotGRID_Varpart: nr=%d" % v1
	copy_name = self.gdoc.grid_copy(self.gname, self.gname) 
	self.append_new_grid(copy_name) 
	
	dist = self.gdoc.grid_varpart(copy_name, v1)
	#print dist
	self.highlight_new_child(0)
	self.slotVIS_Start()
	msg ="Varpart:  with P1: nr of parts"
	self.ui.statusBar.showMessage(self.tr(msg))
	
    #-------------------------------------------------------------------
    def slotGRID_Remove_Trend(self):
	v1 = str(self.ui.ledit_p1.text())
	if self.is_number(v1) == False or int(v1) == 0:
	    v1 = 2000
	else:
	    v1 = int(v1)
	print "slotGRID_Remove_Trend: nr=%d" % v1
	if self.gdoc.grid_remove_trend(self.gname, v1) == None:
	    print "remove_trend error"
	else:
	    self.slotVIS_Start()  
	
    #-------------------------------------------------------------------
    def slotGRID_Grad_d4(self):
	if self.gdoc.grid_grad_d4(self.gname) == None:
	    print "grad_d4 error"
	else:
	    self.slotVIS_Start()  
        
    #-------------------------------------------------------------------
    def slotGRID_Grad_d8(self):
	if self.gdoc.grid_grad_d8(self.gname) == None:
	    print "grad_d8 error"
	else:
	    self.slotVIS_Start()  
    
    
    #=========== menu Kernel ===========================================
    
    def slotKERNEL_Sci(self):
	v1 = str(self.ui.ledit_p1.text())	# ai
	v2 = str(self.ui.ledit_p2.text())	# bj
	v3 = str(self.ui.ledit_p3.text())	# sigma optional
	if self.is_number(v1) == False or self.is_number(v2) == False: 
	    return
	v1 = int(v1)
	v2 = int(v2)
	if self.is_number(v3) == False:
	    v3 = 1.0
	v3 = float(v3)
	if self.gdoc.kernel_sci(self.gname,v1,v2,v3) == None:
	    print "kernel_sci error"
	else:
	    self.slotVIS_Start()
	    msg ="Kernel_Sci:  with P1: ai, P2: bj, P3: sigma"
	    self.ui.statusBar.showMessage(self.tr(msg))
	
    #-------------------------------------------------------------------
    def slotKERNEL_Rect(self):
	v1 = str(self.ui.ledit_p1.text())	# ai
	v2 = str(self.ui.ledit_p2.text())	# bj
	if self.is_number(v1) == False or self.is_number(v2) == False: 
	    return
	if self.gdoc.kernel_rect(self.gname, int(v1), int(v2)) == None:
	    print "kernel_rect error"
	else:
	    self.slotVIS_Start()
	    msg ="Kernel_Rect:  with P1: ai, P2: bj"
	    self.ui.statusBar.showMessage(self.tr(msg))
        
    #-------------------------------------------------------------------
    def slotKERNEL_Cir(self):
	v1 = str(self.ui.ledit_p1.text())	# radius
	if self.is_number(v1) == False: 
	    return
	if self.gdoc.kernel_cir(self.gname, int(v1)) == None:
	    print "kernel_cir error"
	else:
	    self.slotVIS_Start()
	    msg ="Kernel_Cir:  with P1: ai, P2: bj"
	    self.ui.statusBar.showMessage(self.tr(msg))
    
    #-------------------------------------------------------------------
    def slotKERNEL_Knn(self):
	v1 = str(self.ui.ledit_p1.text())	# k
	v2 = str(self.ui.ledit_p2.text())	# min
	v3 = str(self.ui.ledit_p3.text())	# max
	if self.is_number(v1)==False or self.is_number(v2)==False or self.is_number(v3)==False: 
	    return
	v1 = int(v1)
	v2 = float(v2)
	v3 = float(v3)
	if self.gdoc.kernel_knn(self.gname, v1, v2, v3) == None:
	    print "kernel_knn error"
	else:
	    self.slotVIS_Start()
	    msg ="Kernel_Knn:  with P1: k, P2: min, P3: max"
	    self.ui.statusBar.showMessage(self.tr(msg))
    
    
    #=========== menu Points ===========================================
    def slotPOINTS_Inter_linear(self):
	self.points_interpolate('linear')
    
    def slotPOINTS_Inter_inverse(self):
	self.points_interpolate('inverse')
	
    def slotPOINTS_Inter_multiquadric(self):
	self.points_interpolate('multiquadric')
    
    def slotPOINTS_Inter_gaussian(self):
	self.points_interpolate('gaussian')
    
    def slotPOINTS_Inter_cubic(self):
	self.points_interpolate('cubic')
    
    def slotPOINTS_Inter_quintic(self):
	self.points_interpolate('quintic')
	
    def slotPOINTS_Inter_thin_plate(self):
	self.points_interpolate('thin_plate')
    
    #-------------------------------------------------------------------
    def points_interpolate(self, method):
	v1 = str(self.ui.ledit_p1.text())
	lii = self.d_poi['i']
	lij = self.d_poi['j']
	liz = self.d_poi['z']
	copy_name = self.gdoc.grid_copy(v1, self.pname) 
	self.append_new_grid(copy_name)  
	QtGui.QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
	if self.gdoc.points_interpolate(
			    copy_name,lii,lij,liz,method) == None:    
	    print 'Points_interpolation error'
	else:
	    self.highlight_new_child(0)
	    msg ="Interpolate:  grid= %s, points= %s, method= %s" % \
					       (v1, self.pname,method)
	    self.ui.statusBar.showMessage(self.tr(msg))
	QtGui.QApplication.restoreOverrideCursor()
	    
    #-------------------------------------------------------------------
    def append_new_grid(self, copy_name):
	it = QTreeWidgetItem(self.root_grids)
	it.setText(0, QString(copy_name))
	self.ui.treeWidget.addTopLevelItem(it)
	self.ui.treeWidget.expandItem(self.root_grids)
	return
        
    #-------------------------------------------------------------------
    def append_new_point(self, pname):
	it = QTreeWidgetItem(self.root_points)
	it.setText(0, QString(pname))
	self.ui.treeWidget.addTopLevelItem(it)
	self.ui.treeWidget.expandItem(self.root_points)
	self.clear_3lineEdits()
	return    
        
    #-------------------------------------------------------------------
    def highlight_new_child(self, idx):
	# set currentItem on the last (newest) grid in tree
	# idx: 0=grids, 1=models, 2=points
	
	topLvlItem = self.ui.treeWidget.topLevelItem(idx)  # 'grids'
	# first remove old selection in treeItem
	self.deselect_tree()
	if self.ui.treeWidget.isItemExpanded(topLvlItem):
	    anz = topLvlItem.childCount()
	    for i in range(0, anz):
		childItem = topLvlItem.child(i)
		if i == anz-1:
		    childItem.setSelected(True)
		    self.ui.treeWidget.setCurrentItem(childItem)
		    self.slotTREE_Clicked()
		    self.slotVIS_Start()
		    
    #-------------------------------------------------------------------
    def deselect_tree(self):
	for x in range(0, self.ui.treeWidget.topLevelItemCount()):
	    topLvlItem = self.ui.treeWidget.topLevelItem(x)
	    if self.ui.treeWidget.isItemExpanded(topLvlItem):
		for i in range(0, topLvlItem.childCount()):
		    childItem = topLvlItem.child(i)
		    childItem.setSelected(False)  
	
    #-------------------------------------------------------------------
    def slotPOINTS_Voronoi(self):
	v1 = str(self.ui.ledit_p1.text())
	li = self.gdoc.get_d_points(self.pname)  # list of 5 lists
	lii = self.d_poi['i']
	lij = self.d_poi['j']
	liz = self.d_poi['z'] 
	copy_name = self.gdoc.grid_copy(v1, self.pname) 
	self.append_new_grid(copy_name) 
	QtGui.QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
	if self.gdoc.points_voronoi(copy_name,lii,lij,liz) == None:    
	    print 'Points_voronoi error'
	else:
	    self.highlight_new_child(0)
	    msg ="Voronoi:  grid= %s, points= %s" % (v1, self.pname)
	    self.ui.statusBar.showMessage(self.tr(msg))
	QtGui.QApplication.restoreOverrideCursor()
	
    #-------------------------------------------------------------------
    def slotPOINTS_Poisson(self):
	v1 = str(self.ui.ledit_p1.text())
	v2 = str(self.ui.ledit_p2.text())    # eps = 0.000001
	v3 = str(self.ui.ledit_p3.text())    # iter = 25
	li = self.gdoc.get_d_points(self.pname)  # list of 5 lists
	lii = self.d_poi['i']
	lij = self.d_poi['j']
	liz = self.d_poi['z']
	copy_name = self.gdoc.grid_copy(v1, self.pname) 
	self.append_new_grid(copy_name) 
	if  self.is_number(v2)== False: 
	    v2 = 0.000001
	if self.is_number(v3) == False:
	    v3 = 25
	QtGui.QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
	if self.gdoc.points_poisson(
		copy_name,lii,lij,liz,float(v2),int(v3)) == None:
	    print 'Poisson: errror'
	else:
	    self.highlight_new_child(0)
	    msg ="Poisson:  grid= %s, points= %s" % (v1, self.pname)
	    self.ui.statusBar.showMessage(self.tr(msg))
	QtGui.QApplication.restoreOverrideCursor()
		
    #-------------------------------------------------------------------
    def slotPOINTS_Distance(self):
        """ calcs the distance between all i,j points """
	v1 = str(self.ui.ledit_p1.text())
 	print "Distance grid= %s , points= %s" % (v1, self.pname)
	li = self.gdoc.get_d_points(self.pname)  # list of 5 lists
	lii = self.d_poi['i']
	lij = self.d_poi['j']   
	copy_name = self.gdoc.grid_copy(v1, self.pname) 
	self.append_new_grid(copy_name) 
	QtGui.QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
	if self.gdoc.points_distance(copy_name,lii,lij) == None:    
	    print 'Points_distance error'
	else:
	    self.highlight_new_child(0)
	    msg ="Distance:  grid= %s, points= %s" % (v1, self.pname)
	    self.ui.statusBar.showMessage(self.tr(msg))
	QtGui.QApplication.restoreOverrideCursor()
	    
    
    #=========== menu Table ============================================
    def slotTABLE_Lut(self):
	# get dictionary with unique categories
	d_unic = self.gdoc.grid_unique(self.gname)
	if d_unic == None:
	    print "unique error"
	    return
	# in table ist rechte col editierbar mit integer
	popup = Popup_table(d_unic, self.gname, "Lut")
	popup.show()
	self.li_popups.append(popup)
	
    #-------------------------------------------------------------------
    def slotGRID_Select(self):
	""" set all values in vals to val1 else to val2 """
	
	# get dictionary with unique categories
	d_unic = self.gdoc.grid_unique(self.gname)
	if d_unic == None:
	    print "unique error"
	    return
	popup = Popup_table(d_unic, self.gname, "Select")
	popup.show()
	self.li_popups.append(popup)
	return
	# go on with btn_ok_clicked: show_img_from_list
		
    
    #=========== menu Help =============================================
    def slotManual(self):
	path = 'python '+self.env + '/helpwin.py &'
	os.system(path)
    
    #-------------------------------------------------------------------
    def slotAbout(self):
	# QMessageBox.about uses an icon       
	QMessageBox.information(self, "About...",
		"SAMT2:\t\t"
		"28.05.2015 by:\n\n"
		"Dr. Ralf Wieland:\tscientific leader\n"
		"\t\tsamt2.py, Pyfuzzy.py, mlpy_mod.py\n"
		"Dipl.-Ing. Karin Groth:	Design and GUI\n\n"
		"download:\n"
		"https:github.com/Ralf3/samt2\n\n"
		"This Software is distributed under GPL v3\n" 
		"http://www.gnu.org/licenses/gpl-3.0.en.html")
	
    
    #=========== Allgemeines ===========================================
    
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
    def item_is_child(self, itemx):
	if itemx.text(0) in ('grids', 'models', 'points'):
	    msg =self.tr("Error: root was selected, not a child")
	    self.ui.statusBar.showMessage(msg, 2000)
	    return False
	return True
 
    #-------------------------------------------------------------------
    def clear_3lineEdits(self):
	self.ui.ledit_p1.clear()
	self.ui.ledit_p2.clear()
	self.ui.ledit_p3.clear()
	
    #-------------------------------------------------------------------
    def slotTREE_Clicked(self):
	itemx = self.ui.treeWidget.currentItem()
	#print "slotTREEclicked: %s" %  str(itemx.text(0))
	if itemx != '':
	    if self.item_is_child(itemx) == False:
		return
	    # only saving here : 
	    # self.parent, self.gname, self.pname, self.mname, 
	    # self.model_kind 
	    self.parent = str(itemx.parent().text(0)) 
	    
	    if self.parent == 'grids':
		self.gname = str(itemx.text(0))
		self.ui.statusBar.clearMessage()
	    elif self.parent == 'points':
		self.pname = str(itemx.text(0))
		self.ui.statusBar.clearMessage()
	    elif self.parent == 'models':
		self.mname = str(itemx.text(0))
		
		# search mname in d_models_fuzzy und d_models_svm
		kind = ''
		if self.gdoc.get_d_models_fuz(self.mname) != None:
		    anz = self.gdoc.get_nr_fuz_inputs(self.mname)
		    li =  self.gdoc.get_name_fuz_input(self.mname, anz)
		    if li == None:
			print "error get_inputname"
			return
		    kind = 'fuzzy'
		elif self.gdoc.get_d_models_svm(self.mname) != None:
		    li =  self.gdoc.get_svm_name(self.mname)
		    if li == None:
			print "error get inputname"
		    anz = len(li)
		    kind = 'svm'
		else:
		    print "error, %s not found in both dict"
		    return
		self.model_kind = kind
		
		if anz == 3:
		    if li[2] == None: # --> P3: None raus
			s = "P1: %s,  P2: %s" % (li[0], li[1])
		    elif li[1] == None:
			s = "P1: %s" % (li[0])
		    else:
			s = "P1: %s,  P2: %s,  P3: %s" % (li[0], li[1],li[2])
		elif anz == 2:
		    s = "P1: %s,  P2: %s" % (li[0], li[1])
		elif anz == 1:
		    s = "P1: %s" % (li[0])
		msg = "%s:  usage  %s  with  %s " % (self.model_kind.upper(),self.mname,s)
		self.ui.statusBar.showMessage(msg) #, 2000)
		
		if kind == 'fuzzy':
		    self.li_all_outp, self.li_all_rules = self.gdoc.get_outp_rules_list(self.mname)
		
		    #for r in self.li_all_rules:
			#tupel = self.gdoc.get_rule(r) 	# (0, 0, 6, 1.0)
			#print "TREE: li_all_rules: get_rule: tupel=", tupel

		# reset actionFuzzy_Analysis
		if self.ui.actionFuzzy_Analysis.isChecked():
		    # Fyzzy_Analysis ( opens Popup_active_rules with table)
		    # can work, if gridname = modelname
		    if self.mname != self.gname:
			self.ui.actionFuzzy_Analysis.setChecked(False)
	  
    #-------------------------------------------------------------------
    def slotTREE_DblClicked(self):
	itemx = self.ui.treeWidget.currentItem()
	if itemx != '':
	    if self.item_is_child(itemx) == False:
		return
	    if self.parent == 'grids':      
		gname = str(itemx.text(0)) 
		gname = QString()
		gname = itemx.text(0)
		if self.ui.ledit_p1.text().isEmpty():
		    self.ui.ledit_p1.setText(gname)
		    return
		if self.ui.ledit_p2.text().isEmpty():
		    self.ui.ledit_p2.setText(gname)
		    return
		if self.ui.ledit_p3.text().isEmpty():
		    self.ui.ledit_p3.setText(gname)
		    return
		
    #-------------------------------------------------------------------	
    def statusbar_msg_changed(self, args):
        '''
	in:	message to show in statusbar (QString) , color BLUE
	out: 	if ERROR inside text: text color RED, 
	'''
	if not args:					
            self.ui.statusBar.setStyleSheet("QStatusBar{color:blue;}") 
	else:
	    if args.left(5).toLower() == 'error':
		self.ui.statusBar.setStyleSheet("QStatusBar{color:red;}") 
    
    #-------------------------------------------------------------------
    def closeEvent(self, event):
	# all PopupWindows close  
	if len(self.li_popups) > 0:
	    for win in self.li_popups:
		win.close()
	event.accept()
	
    #-------------------------------------------------------------------
    #~ def resizeEvent(self, event):
	#~ print "resizeEv"
	
	
    
    
    ####################################################################
    #####   VISUALISATION    ###########################################
    ####################################################################
    
    def slotVIS_Start(self, clear=None):
	itemx = self.ui.treeWidget.currentItem()
	if itemx != '':
	    if self.item_is_child(itemx) == False:  
		return
	    if self.parent == 'points':
		self.points_table_show(itemx) 
		return
	self.delete_old_line_or_rect()
	self.flag_mxzoom = False
	
	# self.gname only was saved in slotTREE_Clicked
	# Sonderfall: self.gname='' wenn nach DELETE_Object kein 
	# neues treeItem geKlickt, aber focus exist.
	if self.gname == '':
	    itemx = self.ui.treeWidget.currentItem()
	    if itemx != '':
		if self.item_is_child(itemx) == False: 
		    return
		if self.parent == 'grids':
		    self.gname = str(itemx.text(0))
		    
	# menu_View auswerten 
	#--- Show_Range -->  Vis im Haupt-Fenster
	if self.ui.actionShow_Range.isChecked():
	    v1 = str(self.ui.ledit_p1.text())   # min
	    v2 = str(self.ui.ledit_p2.text())	# max
	    if self.is_number(v1)== False or self.is_number(v2)== False: 
		return
	    mx,nr,nc = self.gdoc.get_mx_range(self.gname, v1, v2)
	    if nr == False:
		print "show_Range error"
		return
	    mi, ma = self.gdoc.get_min_max(self.gname)  # gx gesamt
	    if mi == None:
		print "VIS_Start error"
		return
	    w_img = nc   #ncols    
	    h_img = nr   #nrows
	else:
	    #--- Show_List --> Vis im Popup Window
	    if self.ui.actionShow_List.isChecked():		
		# get dictionary with unique categories
		d_unic = self.gdoc.grid_unique(self.gname)
		if d_unic == None:
		    print "Show_List: unique error"
		    return
		popup = Popup_table(d_unic, self.gname, "Show_List")
		popup.show()
		self.li_popups.append(popup)
		self.ui.actionShow_List.setChecked(False)
		return
		# go on with btn_ok_clicked: show_img_from_list
	    else:
		# ********* Vis Normalfall  im Haupt-Fenster *******
		mx, mi, ma = self.gdoc.get_matrix(self.gname)
		if mx == None:
		    return
		tup = self.gdoc.get_gx_size(self.gname)
		h_img = tup[0]  
		w_img = tup[1]   
		#print "Vis Normal: mi=%s, ma=%s" %  (mi, ma)
	
	w_wid = self.w_wid_orig    
	h_wid = self.h_wid_orig    
	fac = self.scale_coordsystem(w_wid, h_wid, w_img, h_img)
	# the top left position of mpl_widget
	pos = QPoint()   
	pos = self.ui.mpl_widget.pos()  
	self.w_img_scaled = float(w_img)*fac
	self.h_img_scaled = float(h_img)*fac
	
	self.ui.mpl_widget.setGeometry(pos.x(), pos.y(),
					int(self.w_img_scaled), 
					int(self.h_img_scaled))
	# weisser statt grauer frame
	self.ui.mpl_widget.canvas.fig.set_frameon(False) 
	# del x,y-achses incl. ticks 
	self.ui.mpl_widget.canvas.ax.set_axis_off()   
	# ohne rand 
	self.ui.mpl_widget.canvas.fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
	# colormap 
	if self.ui.actionShow_Black_White.isChecked():
	    cmap = mpl.cm.get_cmap('Greys', 500)
	else:
	    cmap = mpl.cm.get_cmap('jet', 500)
	cmap.set_under('white') 
	img = self.ui.mpl_widget.canvas.ax.imshow(mx, cmap=cmap,aspect='auto')
	if mi == ma:
	    img.set_clim(-9999, ma)    
	else:
	    img.set_clim(mi, ma)
	self.clear_old_rect()		# black rect in 0,0
	self.ui.mpl_widget.canvas.draw() 
	
	#--- menu_View auswerten 
	#--- Colorbar --> show in new PopupWindow
	if self.ui.actionColorbar.isChecked():
	    v1 = str(self.ui.ledit_p1.text())
	    v2 = str(self.ui.ledit_p2.text())
	    if v1 != "" and v2 != "":
	    	if self.is_number(v1)==False or self.is_number(v2)==False:  
		    print "error: P1 or P2 is not a number"
		else:
		    if float(v1) < float(v2):
			mi = float(v1)
			ma = float(v2)
			#print "Colorbar neu: mi=%s, ma=%s" %  (mi,ma)
		    else:
			print "error Show_Colorbar: P1:min > P2:max"
	    popup = Popup_vis_colorbar(self.gname, mx, mi, ma)
	    popup.show()
	    self.li_popups.append(popup)
	    self.ui.actionColorbar.setChecked(False)
	
	#--- Show_Diff --> show in new PopupWindow
	if self.ui.actionShow_Diff.isChecked():
	    v1 = str(self.ui.ledit_p1.text())
	    if v1 == '':
		print "error Show_Diff: P1 expected"
		return 
	    mx = self.gdoc.get_mx_diff(self.gname, v1)
	    if mx == None:
		print "Error Show_Diff"
		return
	    mx2 = mx[mx > -9999.0] 
	    mi = np.min(mx2) 
	    ma = np.max(mx)
	    popup = Popup_vis_colorbar(self.gname, mx, mi, ma, v1)
	    popup.show()
	    self.li_popups.append(popup)
	
	#--- Show_3d --> show in new PopupWindow
	if self.ui.actionShow_3d.isChecked(): 
	    s = str(self.ui.ledit_p1.text())
	    if self.is_number(s) == False or float(s) < 0:  
		strid = -1
	    else:
		strid = int(s)
	    mx, nrows, ncols = self.gdoc.get_mx_3d(self.gname, strid)
	    if nrows == False:
		print "show_3d error"
		return
	    if strid == -1:
		strid = int(max(nrows,ncols)/60.0)
	    if strid < 1:
		strid = 1
	    popup = Popup_show_3d(self.gname,mx,nrows,ncols,mi,ma,strid)
	    popup.show()
	    self.li_popups.append(popup)
	    self.ui.actionShow_3d.setChecked(False)

	self.ui.actionShow_List.setChecked(False)
	self.ui.actionShow_Range.setChecked(False)
	self.ui.actionShow_Diff.setChecked(False) 
	
	# clear P1, P2, P3
	if clear == 1:
	    # all fct from Simple_Grid set 1 
	    self.clear_3lineEdits()  

    #-------------------------------------------------------------------
    def points_table_show(self, itemx):
	# call from slotVIS_Start after TREE_Clicked into points
	pname = str(itemx.text(0))
	li = self.get_dict_points(pname)
	self.d_poi.clear()			
	self.d_poi['y'] = li[0]
	self.d_poi['x'] = li[1]
	self.d_poi['i'] = li[2]
	self.d_poi['j'] = li[3]   
	self.d_poi['z'] = li[4]
	art = 'yx'
	popup = Popup_points_dataframe(self.d_poi, art, pname)   
	popup.show()
	self.li_popups.append(popup)

    #-------------------------------------------------------------------
    def show_img_from_list(self, li, caller):
	# call from Popup_table: btn_ok -->  Vis im Haupt-Fenster
	# get the selected list from Popup_table()
	if caller == "Show_List":
	    mx,nr,nc = self.gdoc.get_mx_list(self.gname, li)
	    if nr == False:
		print "show_List error"
		return
	elif caller == "Select":
	    v1 = str(self.ui.ledit_p1.text())
	    if self.is_number(v1) == False:  
		v1 = 1
		self.ui.ledit_p1.clear()
	    else:
		v1 = float(v1)
	    v2 = str(self.ui.ledit_p2.text())
	    if self.is_number(v2) == False:  
		v2 = 0
		self.ui.ledit_p2.clear()
	    else:
		v2 = float(v2)
	    mx,nr,nc = self.gdoc.get_mx_select(self.gname,li,v1,v2)
	    if nr == False:
		print "Select error"
		return
	else:
	    # caller= Lut --> li has 2 lists  --> fill into dict
	    d_lut = {}
	    d_lut = dict(zip(li[0], li[1])) 
	    mx,nr,nc = self.gdoc.get_mx_lut(self.gname, d_lut)
	    if nr == None:
		print "Lut error"
		return  
	    
	mi, ma = self.gdoc.get_min_max(self.gname) 
	if mi == None:
	    print "show_img_from_list Error"
	    return
	w_img = nc   
	h_img = nr
	w_wid = self.w_wid_orig    
	h_wid = self.h_wid_orig    
	fac = self.scale_coordsystem(w_wid, h_wid, w_img, h_img)

	# the top left position of mpl_widget
	pos = QPoint()   
	pos = self.ui.mpl_widget.pos()  # (165,9)
	
	self.w_img_scaled = float(w_img)*fac
	self.h_img_scaled = float(h_img)*fac
	#print "scaled:w=%d h=%d" %(self.w_img_scaled,self.h_img_scaled)
	self.ui.mpl_widget.setGeometry(pos.x(), pos.y(),
					int(self.w_img_scaled), 
					int(self.h_img_scaled))
	self.ui.mpl_widget.canvas.fig.set_frameon(False) 
	self.ui.mpl_widget.canvas.ax.set_axis_off()   
	self.ui.mpl_widget.canvas.fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
	# colormap 
	cmap = mpl.cm.get_cmap('jet', 500)
	cmap.set_under('white') 
	img = self.ui.mpl_widget.canvas.ax.imshow(mx,cmap=cmap,aspect='auto')
	img.set_clim(mi, ma)
	self.ui.mpl_widget.canvas.draw() 

    #-------------------------------------------------------------------
    def scale_coordsystem(self, w_wid, h_wid, w_img, h_img):
	"""
	    in:	    w_wid	width of the mpl_widget
		    h_wid	height    "
		    w_img	width of the img to plot
		    h_wid	height    "
	    out:    fac		scale factor
	    scale mpl_widget to original img proportions
	    called from slotVIS_Start
	"""
	fac = 0.0
	if h_img < w_img:
	    #print "Rechteck horizontal: fac= %d/%d" % (h_wid,h_img) 
	    fac = float(w_wid)/float(w_img)
	else:
	    if h_img > w_img:
		#print "Rechteck vertical: fac= %d/%d" % (h_wid,h_img)
		fac = float(h_wid)/float(h_img)
	    else:
		#ralf raus: print "Quadrat: fac= %d/%d" % (h_wid,h_img)
		fac = float(h_wid)/float(h_img)
	return fac
    
    #-------------------------------------------------------------------
    def delete_old_line_or_rect(self):
	# call from slotVIS_Start
	if self.line1 != None:
	    self.clear_old_line()
	    self.set_default_new_line()
	    self.ui.mpl_widget.canvas.draw()
	    self.ui.actionGraph.setChecked(False)
	if self.rect != None:       
	    self.clear_old_rect()
	    self.set_default_new_rect()
	    self.ui.mpl_widget.canvas.draw()
	    self.ui.actionZoom_in.setChecked(False)
	    
    #-------------------------------------------------------------------
    def check_nodata(self, Y, X):
    	val = self.gdoc.get_gx_val(self.gname,Y,X)
	if val == -9999:
	    self.isLine = False  
	    self.isNodata = True
	    self.ui.statusBar.clearMessage()
	    self.ui.actionGraph.setChecked(False)
	    # msg
	    print "nodata in row: %d, col: %d" % (Y,X)
	    msg = self.tr("Error: outside the range (nodata)")
	    self.ui.statusBar.showMessage(msg,5000)
	    return True
	return False
    
    #-------------------------------------------------------------------
    def fill_ifthenList(self, ruleList, anz_inp):
	li = []
	for nr in ruleList:
	    ifthen = QString("IF ")
	    ru = self.li_all_rules[nr]
	    tupel = self.gdoc.get_rule(ru)  #  (0, 0, 6, 1.0)

	    in1 = self.gdoc.get_mf_name(self.mname, 0, tupel[0])
	    ss = "<strong>x1=<font color='mediumblue'>%s</font></strong>" % in1
	    ifthen.append(ss)   
	    if anz_inp >= 2:
		ifthen.append(" AND ")
		in2 = self.gdoc.get_mf_name(self.mname, 1, tupel[1])
		ss = "<strong>x2=<font color='mediumblue'>%s</font></strong>" % in2
		ifthen.append(ss)
		if anz_inp == 3:
		    ifthen.append(" AND ")
		    in3 = self.gdoc.get_mf_name(self.mname, 2, tupel[2])
		    ss = "<strong>x3=<font color='mediumblue'>%s</font></strong>" % in3
		    ifthen.append(ss)
	    ifthen.append(" THEN ")
	    outidx = tupel[-2]	# 2. from right site
	    o = self.li_all_outp[outidx]
	    oname = self.gdoc.get_outp_name_singleton(o)
	    ss = "<font color='darkred'><strong>%s</strong></font>" % oname				
	    ifthen.append(ss)
	    cf = tupel[-1]	# last in tupel
	    ifthen.append(" (")
	    ifthen.append(str(cf))
	    ifthen.append(")")
	    li.append(ifthen)
	return li

    #-------------------------------------------------------------------
    def prepare_Fuzzy_Analysis_popup(self, X, Y, z):
	# called by: mouse on_press 
	# Fyzzy_Analysis (opens  with table)
	# can work, if gridname = modelname
	if self.mname != self.gname:
	    self.ui.actionFuzzy_Analysis.setChecked(False)
	    print "Error in Fuzzy_Analysis: false grid was selected - Abort"
	    return

	# prepaire Popup_active_rules window only
	anz_inp = 0
	li_input_names = []
	v1 = str(self.ui.ledit_p1.text())
	if v1 == '':
	    print "error Fuzzy_Analysis: P1 expected"
	    return
	li_input_names.append(v1)
	
	v2 = str(self.ui.ledit_p2.text())
	v3 = str(self.ui.ledit_p3.text())
	if v1 != '' and v2 != '' and v3 != '':
	    # anzahl input grids = 3
	    li_input_names.append(v2)
	    li_input_names.append(v3)
	elif v2 == "":
	    anz_g = 1
	else:
	    li_input_names.append(v2)
	#print "li_input_names=", li_input_names
	anz_inp = len(li_input_names)
	anz = self.gdoc.get_nr_fuz_inputs(self.mname)
	if anz_inp != anz:
	    print "Error: P1, P2, P3 not equal with model inputs"
	    return
	#print "Fuzzy_Analysis:: z EntireOutp= ", z
	li_col_header = ['Nr.','Rule','Mu']
	li_outval = []
	in1 = 0.0
	in2 = 0.0
	in3 = 0.0
	if anz_inp == 1:
	    s = "x1=%s" % v1
	    li_col_header.append(s)
	    li_col_header.append("inp2 dummy")
	    li_col_header.append("inp3 dummy")
	    in1 = self.gdoc.get_gx_val(v1, Y, X)
	    su1,ruleList,muList,outputList=self.gdoc.get_calct1(
					self.mname,in1)
	    ifthenList = self.fill_ifthenList(ruleList,1)
	elif anz_inp == 2:
	    s = "x1=%s" % v1
	    li_col_header.append(s)
	    s = "x2=%s" % v2
	    li_col_header.append(s)
	    li_col_header.append("inp3 dummy")
	    in1 = self.gdoc.get_gx_val(v1, Y, X)
	    in2 = self.gdoc.get_gx_val(v2, Y, X)
	    #print "Fuzzy_Analysis: in1= %.3f, in2= %.3f" % (in1,in2)
	    su1,ruleList,muList,outputList=self.gdoc.get_calct2(
				    self.mname,in1,in2)
	    #~ print "su1/tmu=", su1
	    #~ print "muList=", muList
	    #~ print "outputList=", outputList
	    #~ print "ruleList=", ruleList
	    ifthenList = self.fill_ifthenList(ruleList,2)
	elif anz_inp == 3:
	    s = "x1=%s" % v1
	    li_col_header.append(s)
	    s = "x2=%s" % v2
	    li_col_header.append(s)
	    s = "x3=%s" % v3
	    li_col_header.append(s)
	    in1 = self.gdoc.get_gx_val(v1, Y, X)
	    in2 = self.gdoc.get_gx_val(v2, Y, X)
	    in3 = self.gdoc.get_gx_val(v3, Y, X)
	    su1, ruleList,muList,outputList=self.gdoc.get_calct3(
				self.mname,in1,in2,in3)
	    ifthenList = self.fill_ifthenList(ruleList,3)
    
	# important: modelname has to be equal current gridname
	oname = self.gdoc.get_name_fuz_output(self.gname)
	li_col_header.append(oname) 
	li_col_header.append('Entire Output')
	
	# opens window with active_rules
	popup = Popup_active_rules(in1, in2, in3,
				su1, ruleList, 
				muList, outputList, 
				ifthenList,
				li_col_header, anz_inp)
	popup.show()
	self.li_popups.append(popup)
    
    #-------------------------------------------------------------------
    
    
    
    ####################################################################
    ###             Mouse-Events 
    ####################################################################
    
    def on_press(self, event):
	# leftButton only
	if event.button == 1:
	    in3const = 0.0
	    X = int(event.xdata)   # col or j
	    Y = int(event.ydata)   # row or i
	    #print "on press: Y=%d, X=%d, isZoom=%s" % (Y,X,self.isZoom) 
	    if self.isZoom==True and self.ui.actionZoom_in.isChecked()==False:  
		z = self.gdoc.get_mx_val(self.mxzoom, Y, X)
		self.flag_mxzoom = True
		self.isZoom = False
	    else:
		if self.flag_mxzoom == False:
		    z = self.gdoc.get_gx_val(self.gname, Y, X)
		    
		    if self.ui.actionFuzzy_Analysis.isChecked():
			self.prepare_Fuzzy_Analysis_popup(X,Y,z)
		else:
		    # up 2. click in zoomed img
		    z = self.gdoc.get_mx_val(self.mxzoom, Y, X)
		    # self.flag_mxzoom set False in slotVIS_Start only
	    s = "i0, j0:  [%d, %d]   z= %0.4f" % (Y,X,z)
	    msg =self.tr(s)
	    self.ui.statusBar.showMessage(msg)   #, 1000)
	    self.pickedX = X
	    self.pickedY = Y
	    #print "picked:  i0=%d  j0=%d  z=%f" % (Y,X,z)
	
	if self.isZoom or self.isLine: 
	    self.dragging = True
	    if self.isLine:
		if self.check_nodata(Y,X):
		    return
		self.li_X[0] = X    
		self.li_Y[0] = Y    
		self.line1.set_data(self.li_X, self.li_Y)
	    self.startPoint = [X, Y]
	    return 
	else:
	    self.dragging = False
   
    #-------------------------------------------------------------------
    def on_motion(self, event):
	# motion_notify_event
	if self.isNodata == False or self.isZoom:
	    if self.dragging:   
		X = int(event.xdata)    	
		Y = int(event.ydata)  	
		#print "moved: X: %d, Y: %d" % (X,Y)
		if self.isLine:
		    # validation
		    if self.check_nodata(Y,X):
			return
		    self.endPoint = [X,Y]
		    self.clear_old_line()
		    self.ui.mpl_widget.canvas.draw()
		    # new line
		    self.li_X[1] = X        
		    self.li_Y[1] = Y        
		    self.line1.set_data(self.li_X, self.li_Y)
		    self.ui.mpl_widget.canvas.ax.add_line(self.line1)
		else:
		    self.endPoint = [X,Y]
		    self.clear_old_rect()
		    y0 = self.startPoint[1]	
		    y1 = self.endPoint[1]
		    x0 = self.startPoint[0]   
		    x1 = self.endPoint[0]	
		    self.rect.set_width(x1 - x0)
		    self.rect.set_height(y1 - y0) 
		    self.rect.set_xy((x0, y0))
		    self.ui.mpl_widget.canvas.ax.add_patch(self.rect)
		self.ui.mpl_widget.canvas.draw()  
			
    #-------------------------------------------------------------------
    def on_release(self, event):
	# leftButton only
	if event.button==1 and (self.isLine or self.isZoom):    	
	    self.dragging = True
	    X = int(event.xdata)    
	    Y = int(event.ydata) 	  
	    # validation only for line
	    if self.isLine:
		if self.check_nodata(Y,X)==True:
		    return
	    self.endPoint = [X,Y]
	    if self.startPoint[0] == self.endPoint[0] and \
		    self.startPoint[1] == self.endPoint[1]:
		print "startPoint = endPoint --> abort"
		return
	    if self.isLine:
		self.li_X[1] = X        
		self.li_Y[1] = Y        
		self.line1.set_data(self.li_X, self.li_Y)
		self.ui.mpl_widget.canvas.ax.add_line(self.line1)
		# save copy for slotVIS_Line_End (actionReplot)
		self.startPointC = self.startPoint
		self.endPointC = self.endPoint
	    else:
		#print "isZoom: rect", self.startPoint, self.endPoint
		y0 = self.startPoint[1]	
		y1 = self.endPoint[1]
		x0 = self.startPoint[0]   
		x1 = self.endPoint[0]	
		self.rect.set_width(x1-x0)
		self.rect.set_height(y1-y0) 
		self.rect.set_xy((x0,y0))  
	    self.ui.mpl_widget.canvas.draw()
			
	    s = "i0, j0, i1, j1:  [%d, %d, %d, %d]" %\
		(self.startPoint[1],self.startPoint[0], Y, X)
	    msg =self.tr(s)
	    self.ui.statusBar.showMessage(msg)   #, 1000)
	    
	    if self.ui.actionGraph.isChecked():
		self.dragging = False   
		if self.isLine:     
		    self.isLine = False 
		    self.slotVIS_Line_End() 
		self.ui.actionGraph.setChecked(False)
	    if self.ui.actionZoom_in.isChecked():
		self.dragging = False   
		self.isZoom = False 
		self.slotVIS_Zoom_End()  
		self.ui.actionZoom_in.setChecked(False) 
	else:
	    self.dragging = False
			
    # --------- ende mouse events---------------------------------------



########################################################################
########################################################################
########################################################################

class Popup_vis_colorbar(QtGui.QMainWindow):
    def __init__(self,gridname,mx,mi,ma,diff_grid=None, parent=None):
	QtGui.QWidget.__init__(self,  parent=None)
	self.ui = Ui_plotwin()
	self.ui.setupUi(self)
	env = os.environ['SAMT2MASTER']+'/gui'
        self.setWindowIcon(QIcon(env+'/pixmaps/samt2_icon.png'))
	
	self.gridname = gridname
	self.mx = mx
	self.show_diff = False
	# Layout
	vbox = QVBoxLayout()
        vbox.addWidget(self.ui.main_frame.canvas)
	self.mpl_toolbar=NavigationToolbar(self.ui.main_frame.canvas,\
						    self.ui.main_frame)
	self.lbl_z = QtGui.QLabel()
	self.lbl_z.setObjectName('lbl_z')
	self.lbl_z.setText('picked z value')
	self.mpl_toolbar.addWidget(self.lbl_z)						    
	self.chbox_grid = QtGui.QCheckBox()
	self.chbox_grid.setObjectName('chbox_gridlines')
	self.chbox_grid.setText('Gridlines')
	self.mpl_toolbar.addWidget(self.chbox_grid)
	vbox.addWidget(self.mpl_toolbar)
	self.ui.main_frame.setLayout(vbox)
        self.setCentralWidget(self.ui.main_frame)
	
	self.chbox_grid.stateChanged.connect(self.chbox_changed)  
	self.ui.main_frame.canvas.mpl_connect(
			     'motion_notify_event', self.on_motion)
	self.setWindowTitle('SAMT 2')
	#self.ui.main_frame.canvas.ax.clear()
	self.ui.main_frame.canvas.ax.set_xlabel('x')
	self.ui.main_frame.canvas.ax.set_ylabel('y')
	self.ui.main_frame.canvas.ax.set_axis_on()
	
	# plot matrix as image with colorbar
	self.ui.main_frame.canvas.fig.subplots_adjust\
				(left=0.1,right=0.9,top=0.9,bottom=0.1)

	self.ui.main_frame.canvas.ax.clear()    # only img
	if diff_grid == None:
	    self.ui.main_frame.canvas.ax.set_title(gridname)
	else:
	    s = "%s - %s" % (gridname, diff_grid)
	    self.ui.main_frame.canvas.ax.set_title(s)
	    self.show_diff = True
			  
	cmap = mpl.cm.get_cmap('jet', 500)
	cmap.set_under('white') 
	img = self.ui.main_frame.canvas.ax.imshow(mx,cmap=cmap,aspect='equal')
	# scale img-data and colorbar
	img.set_clim(mi, ma)   
	self.ui.main_frame.canvas.fig.colorbar(img,aspect=20,pad=0.05, \
				    shrink=1.0, orientation='vertical') 
	self.ui.main_frame.canvas.draw() 
    
    #-------------------------------------------------------------------
    def on_motion(self, event):
	if event.xdata == None:
	    return
	X = int(event.xdata)   # col
	Y = int(event.ydata)   # row
	if self.show_diff == True:
	    z = window.get_z_from_picked_mx(self.mx,Y,X)
	else:
	    z = window.get_z_from_picked_YX(self.gridname,Y,X)
	s = "z= %0.4f" % z
	msg =self.tr(s)
	self.lbl_z.setText(msg)
	    		
    #-------------------------------------------------------------------
    def chbox_changed(self, state):
	# set / unset gridlines in canvas
	if state == 2:   #checked
	   self.ui.main_frame.canvas.ax.grid(True) 
	else:
	   self.ui.main_frame.canvas.ax.grid(False)  
	self.ui.main_frame.canvas.draw() 
	
########################################################################

class  Popup_show_3d(QtGui.QMainWindow):
    """shows a grid using 3D: stride (Schritt) should be so that the
				grid size is approx 25..50  """
    def __init__(self,gridname,mx, nrows, ncols, mi, ma, stride, parent=None):
	QtGui.QWidget.__init__(self,  parent=None)
	self.ui = Ui_plotwin3d()
	self.ui.setupUi(self)
	env = os.environ['SAMT2MASTER']+'/gui'
        self.setWindowIcon(QIcon(env+'/pixmaps/samt2_icon.png'))
	
	# Layout
	vbox = QVBoxLayout()
        vbox.addWidget(self.ui.main_frame.canvas)
	self.mpl_toolbar=NavigationToolbar(self.ui.main_frame.canvas,\
						self.ui.main_frame)
	vbox.addWidget(self.mpl_toolbar)
	self.ui.main_frame.setLayout(vbox)
        self.setCentralWidget(self.ui.main_frame)
	self.ui.main_frame.canvas.ax.mouse_init() 
	
	self.setWindowTitle('SAMT 2')
	txt = '%s,  stride=%d' % (gridname, stride)
	self.ui.main_frame.canvas.ax.set_title(txt)
		
	mx = mx.transpose()
        Xt = np.arange(0, nrows)
        Yt = np.arange(0, ncols)
        X1, Y1 = np.meshgrid(Xt, Yt)
        print np.shape(mx)
        #self.ui.main_frame.canvas.ax.set_zlim(-1.01, 50) 
	
	cmap = mpl.cm.get_cmap('jet', 500)
	print "Popup_show_3d: stride=%s" % stride
	surf = self.ui.main_frame.canvas.ax.plot_surface(X1, Y1, mx, 
                        rstride = stride, cstride = stride,
			vmin = mi, vmax = ma, 
                        cmap = cmap, 
                        linewidth = 0, antialiased = True)   
	#vmin, vmax enfernt blauen nodata-teppich
			
	cmap.set_under('white') 		
	self.ui.main_frame.canvas.fig.colorbar(surf,aspect=20,pad=0.05,\
				    shrink=1.0, orientation='vertical')
	self.ui.main_frame.canvas.draw()
    
########################################################################

class Popup_transect(QtGui.QMainWindow):
    def __init__(self,gridname,t,mx,i0,j0,i1,j1, parent=None):
	QtGui.QWidget.__init__(self,  parent=None)
	self.ui = Ui_plotwin()
	self.ui.setupUi(self)
	env = os.environ['SAMT2MASTER']+'/gui'
        self.setWindowIcon(QIcon(env+'/pixmaps/samt2_icon.png'))
	
	# Layout
	vbox = QVBoxLayout()
        vbox.addWidget(self.ui.main_frame.canvas)
	self.ui.main_frame.setLayout(vbox)
        self.setCentralWidget(self.ui.main_frame)
	
	self.setWindowTitle('SAMT 2')
	self.ui.main_frame.canvas.ax.clear()
	self.ui.main_frame.canvas.ax.set_xlabel('distance  [m]')
	self.ui.main_frame.canvas.ax.set_ylabel(gridname)
	self.ui.main_frame.canvas.ax.grid(True)
	txt = '%s:  (i0,j0) (i1,j1):  (%d, %d) (%d, %d)' % \
					    (gridname,i0,j0,i1,j1)
	self.ui.main_frame.canvas.ax.set_title(txt) 
	# thousands separator: , 
	majorFormatter = mpl.ticker.FuncFormatter \
				    (lambda x, p: format(int(x), ','))
	self.ui.main_frame.canvas.ax.get_xaxis(). \
				    set_major_formatter(majorFormatter)
	self.ui.main_frame.canvas.ax.plot(t, mx, color='blue')
	self.ui.main_frame.canvas.draw()
	 
########################################################################

class Popup_histogram(QtGui.QMainWindow):
    def __init__(self, gridname, mx, bins, parent=None):
	QtGui.QWidget.__init__(self,  parent=None)
	self.ui = Ui_plotwin()
	self.ui.setupUi(self)
	env = os.environ['SAMT2MASTER']+'/gui'
        self.setWindowIcon(QIcon(env+'/pixmaps/samt2_icon.png'))
	
	# Layout
	vbox = QVBoxLayout()
        vbox.addWidget(self.ui.main_frame.canvas)
	self.ui.main_frame.setLayout(vbox)
        self.setCentralWidget(self.ui.main_frame)
	
	self.setWindowTitle('SAMT 2')
	self.ui.main_frame.canvas.ax.clear()
	self.ui.main_frame.canvas.ax.set_xlabel('data')
	self.ui.main_frame.canvas.ax.set_ylabel('frequency')
	
	txt = 'Histogram: %s' % gridname 
	self.ui.main_frame.canvas.ax.set_title(txt)
	self.ui.main_frame.canvas.ax.grid(True) 
        self.ui.main_frame.canvas.ax.hist(mx,bins,normed=False,color='r')
	
########################################################################

class Popup_table(QtGui.QMainWindow):
    def __init__(self, d_unic, gridname, caller, parent=None):
	QtGui.QWidget.__init__(self,  parent=None)
	self.ui = Ui_tablewin()
	self.ui.setupUi(self)
	env = os.environ['SAMT2MASTER']+'/gui'
        self.setWindowIcon(QIcon(env+'/pixmaps/samt2_icon.png'))

	self.ui.btn_save_ijz.setVisible(False)
	self.ui.btn_save_yxz.setVisible(False)
	self.connect(self.ui.btn_ok, SIGNAL('clicked()'), 
						self.btn_ok_clicked) 
	self.caller = caller
	self.title = caller   # Show_List, Select, Lut					    
	s = "%s: %s" % (caller, gridname)
	self.setWindowTitle(s)
	self.ui.tblwid.horizontalHeader().setVisible(True)
	if self.caller == "Lut":
	    cn = "categories, put an int value"
	else:
	    cn = "categories,."
	self.ui.tblwid.setHorizontalHeaderLabels(QString(cn).split(","))  
	self.ui.tblwid.setColumnWidth(1,25)
	i = 0
	for key,value in sorted(d_unic.iteritems(),key=lambda(k,v):(k,v)):
	    self.ui.tblwid.insertRow(i)
	    self.ui.tblwid.setRowHeight(i,22)
	    newItem = QtGui.QTableWidgetItem(str(key))
	    self.ui.tblwid.setItem(i, 0, newItem) 
	    if self.caller == "Lut":
		le = QtGui.QLineEdit()
		le.setText(str(key))
		self.ui.tblwid.setCellWidget(i, 1, le)
	    else:
		cb = QtGui.QCheckBox()
		self.ui.tblwid.setCellWidget(i, 1, cb)
	    i += 1
	    
    #-------------------------------------------------
    def btn_ok_clicked(self):
	ctr = 0
	rows = self.ui.tblwid.rowCount()
	if self.caller == 'Lut':
	    li_c = []
	    li_v = []
	    for i in range(0, rows):
		c = int(self.ui.tblwid.item(i,0).text())
		v = int(self.ui.tblwid.cellWidget(i,1).text())
		if c != v:
		    li_c.append(c)
		    li_v.append(v)
		ctr += 1 
	    li = [li_c, li_v]
	else: 
	    li = []
	    for i in range(0, rows):
		cb = QtGui.QCheckBox()
		cb = self.ui.tblwid.cellWidget(i,1)  
		if cb.isChecked():     
		    c = self.ui.tblwid.item(i,0).text()  # 18
		    li.append(int(c))
		    ctr += 1 
	if ctr == 0:
	    QtGui.QMessageBox.information(self,  self.tr("Error"), 
				self.tr(u" Not category selected")) 
	    return False
	window.show_img_from_list(li, self.caller)

########################################################################

# call from : points_table_show()
class Popup_points_dataframe(QtGui.QMainWindow):
    def __init__(self, d_poin, art, pname, parent=None):
	QtGui.QWidget.__init__(self,  parent=None)
	self.ui = Ui_tablewin()
	self.ui.setupUi(self)
	self.resize(570,520)
	env = os.environ['SAMT2MASTER']+'/gui'
        self.setWindowIcon(QIcon(env+'/pixmaps/samt2_icon.png'))
	
	self.d_poin = d_poin
	self.df = None
	
	# all tablecells are editable and rows deletable
	self.ui.lbl_tipp.setText(
			    'After  z  values  were  edited, click  Refresh')
	self.ui.btn_ok.setText('Refresh')
	self.connect(self.ui.btn_ok, SIGNAL('clicked()'), 
				    self.btn_ok_clicked)
	self.connect(self.ui.btn_save_ijz, SIGNAL('clicked()'), 
				    self.btn_save_clicked)
	self.connect(self.ui.btn_save_yxz, SIGNAL('clicked()'), 
				    self.btn_save_clicked)
	self.ui.tblwid.verticalHeader().setVisible(True)
	
	if art == 'yx':
	    s = 'y,x,i,j,z'
	    s2 = '%s :   yx  TO  ij: ' % pname
	elif art == 'ij':
	    s = 'y,x,i,j,z'
	    s2 = '%s :  ij  TO  yx: ' % pname
	else:
	    # call from slotVIS_Start, art: yx or ij
	    s = ' , '     # problem !
	    s2 = pname
	self.setWindowTitle(s2)
	self.tbl_show()  # has header only for col0, col1
	self.ui.tblwid.setHorizontalHeaderLabels(QString(s).split(","))
    
    #-------------------------------------------------------------------
    def tbl_show(self):
    	self.df = pd.DataFrame(self.d_poin,
				columns=['y','x','i','j','z']) 
	#print "tbl_show df from d_poin"
	#print self.df
	ncols = len(self.df.columns)
	nrows = len(self.df.index)
	if self.ui.tblwid.rowCount() == 0:
	    self.ui.tblwid.setRowCount(nrows)
	if self.ui.tblwid.columnCount() < 5:
	    self.ui.tblwid.setColumnCount(ncols)
	for r in range(nrows):
	    for c in range(ncols):
		self.ui.tblwid.setItem(r,c,QtGui.QTableWidgetItem(
					str(self.df.iget_value(r,c))))
					
    #-------------------------------------------------------------------
    def tbl_clear(self):
	rowctr = 0
	if self.ui.tblwid.rowCount() > 0:
	    rowctr = self.ui.tblwid.rowCount()
	    print "tbl.rowctr = %d" % rowctr
	    for i in range(rowctr-2, -1, -1):
		print "del row=%d" % i
		self.ui.tblwid.removeRow(i)
   
    #-------------------------------------------------------------------
    def btn_ok_clicked(self):
	print "refresh col z in dict"
	# edited z-column save in dataframe (liz)
	nrows = self.ui.tblwid.rowCount()
	liz = []
	for i in range (nrows):
	    it = self.ui.tblwid.item(i,4)
	    z = it.text()
	    #print i, z, float(z)
	    liz.append(float(z))
	del self.d_poin['z']
	self.d_poin['z'] = liz
	window.set_d_poi_new_z(liz)
    
    #-------------------------------------------------------------------
    def btn_save_clicked(self):
	#print "sender = %s" % self.sender().objectName()
	li = self.sender().objectName().split('_')
	q = li[-1]   # yxz  or  ijz
	#path = window.get_samtpath() +'/points/'+q+'_'
	path = window.get_daten_path() +'/points/'+q+'_'
	filename = QtGui.QFileDialog.getSaveFileName(self,
	    "Choose a filename to save under", path,
	    "Images (*.csv *.txt *.asc)");
	if filename.isEmpty():
	    return
	dframe = window.get_edited_pandas_dataframe() 
	if q == 'yxz':
	    c = ['y', 'x', 'z']
	else:
	    c = ['i', 'j', 'z'] 
	dframe.to_csv(filename, sep=' ', index=False, cols=c) 
	print "save is ready"

	
########################################################################

# call from: slotRun_Model:  if self.parent == "grids"

class Popup_expression(QtGui.QMainWindow):
    def __init__(self, v1,v2,v3, g1,g2=None,g3=None, parent=None):
	QtGui.QWidget.__init__(self, parent=None)
	self.ui = Ui_expression()
	self.ui.setupUi(self)
	self.title = "Expression Builder"				    
	self.setWindowTitle("Expression Builder")
	env = os.environ['SAMT2MASTER']+'/gui'
        self.setWindowIcon(QIcon(env+'/pixmaps/samt2_icon.png'))
	self.ui.statusBar.setStyleSheet("QStatusBar{color:red;}") 
	
	# connects
	self.connect(self.ui.btn_calc, SIGNAL('clicked()'), 
						self.btn_calc_clicked) 
	self.connect(self.ui.btn_clear, SIGNAL('clicked()'), 
						self.btn_clear_clicked)
	self.connect(self.ui.tblwid,SIGNAL(
	    'cellDoubleClicked(int,int)'),self.tblcell_DblClicked)
	
	self.connect(self.ui.ledit_exp, SIGNAL(
	    'cursorPositionChanged(int,int)'), self.set_cursor_pos)
	
	self.cursorpos = 0	
	self.g1 = g1
	self.g2 = g2
	self.g3 = g3
	self.ui.label_3.setStyleSheet("QLabel{color:'#0000FF';}")
	self.ui.label_4.setStyleSheet("QLabel{color:'#0000FF';}")
	self.ui.label_5.setStyleSheet("QLabel{color:'#0000FF';}")
	self.ui.lbl_a.setText(v1)
	self.ui.lbl_b.setText(v2)
	self.ui.lbl_c.setText(v3)
	self.ui.ledit_res.setText('exec')
	
	# fill tbl
	fpath = window.get_samt_path() +'/expr_fct_semik.csv'
	with open(fpath, 'r') as csvfile:
	    self.df = pd.read_csv(csvfile, sep=';', header=None) 

	ncols = len(self.df.columns)
	nrows = len(self.df.index)
	self.ui.tblwid.setColumnWidth(0,80)
	self.ui.tblwid.setColumnWidth(1,90)
	self.ui.tblwid.setColumnWidth(5,65)
	self.ui.tblwid.setColumnWidth(6,70)
	self.ui.tblwid.setColumnWidth(7,70)
	for r in range(nrows):
	    for c in range(ncols):
		self.ui.tblwid.setItem(r,c,QtGui.QTableWidgetItem(
					str(self.df.iget_value(r,c))))
	self.ui.ledit_exp.setFocus()
	#print "grids for expression: : %s,  %s,  %s" % (v1, v2, v3)
	    
    #-------------------------------------------------------------------
    def set_cursor_pos(self, old, new):
	#print "slot: old_pos= %d  new=%d" % (old, new)
	self.cursorpos = new
		    
    #-------------------------------------------------------------------
    def tblcell_DblClicked(self, row,column):
	s = str(self.ui.tblwid.item(row, column).text())
	if s == ' ':
	    return
	pos = self.cursorpos
	if pos == 0:
	    txt_neu = 'np.%s ' % s
	else:
	    txt_neu = ' np.%s ' % s
	txt_old = str(self.ui.ledit_exp.text())
	li = list(txt_old)
	li.insert(pos, txt_neu) 
	self.ui.ledit_exp.setText(''.join(li))
	
    #-------------------------------------------------------------------
    def btn_calc_clicked(self):
	expr = str(self.ui.ledit_exp.text())
	gname = str(self.ui.ledit_res.text())
	# validation expr clicked in empty cell
	c = str(self.ui.lbl_c.text()) 
	if c == '':
	    if expr.find('c_') > -1:
		print "error in expr: c_ not exists"
		return
	b = str(self.ui.lbl_b.text())  
	if b == '':
	    if expr.find('b_') > -1:
		print "error in expr: b_ not exists"
		return
	window.bridge_expr_calc(gname, expr, self.g1, self.g2, self.g3)

    #-------------------------------------------------------------------
    def btn_clear_clicked(self):
	self.ui.ledit_exp.clear()
	self.ui.statusBar.clearMessage()
	
    #-------------------------------------------------------------------
    def set_msg_statusbar(self, msg):
	# called from MyForm.bridge_expr_calc
	self.ui.statusBar.showMessage(msg, 5000)   #.clearMessage()
    
    #-------------------------------------------------------------------
    # wenn connected:   ralf raus
    #~ self.connect(self.ui.tblwid,SIGNAL(
	    #~ 'itemClicked(QTableWidgetItem*)'),self.tblitem_clicked)
    
    #~ def tblitem_clicked(self, item):
	#~ rownr = self.ui.tblwid.selectedItems()[0].row()
	#~ colnr = self.ui.tblwid.selectedItems()[0].column()
	#~ txt = 'np.%s' % self.ui.tblwid.item(rownr, colnr).text()
	#~ txt_old = ...

########################################################################

class Popup_map(QtGui.QMainWindow):
    def __init__(self, gridname, mx, parent=None):
	QtGui.QWidget.__init__(self, parent=None)
	self.ui = Ui_plotwin()
	self.ui.setupUi(self)
	self.gridname = gridname
	# Layout
	vbox = QVBoxLayout()
        vbox.addWidget(self.ui.main_frame.canvas)
	self.mpl_toolbar=NavigationToolbar(self.ui.main_frame.canvas,\
						self.ui.main_frame)
	vbox.addWidget(self.mpl_toolbar)
	self.ui.main_frame.setLayout(vbox)
        self.setCentralWidget(self.ui.main_frame)
	env = os.environ['SAMT2MASTER']+'/gui'
        self.setWindowIcon(QIcon(env+'/pixmaps/samt2_icon.png'))
	
	s = 'Map for grid:  %s' % gridname
	self.setWindowTitle(s)
	self.ui.main_frame.canvas.ax.set_axis_on()
	self.ui.main_frame.canvas.ax.set_xlabel('x')
	self.ui.main_frame.canvas.ax.set_ylabel('y')
	self.ui.main_frame.canvas.ax.set_title(gridname)
	
	cmap = mpl.cm.get_cmap('jet', 500)
	cmap.set_under('white') 
	img = self.ui.main_frame.canvas.ax.imshow(mx, \
					    cmap=cmap,aspect='equal')
	self.ui.main_frame.canvas.draw() 
   
########################################################################

class Popup_active_rules(QtGui.QWidget):
    def __init__(self, in1, in2, in3, 
		su1, ruleList, muList, outputList, ifthenList,
		li_col_header, anz_inp, parent=None):
	# called by: mouse on_release
	QtGui.QWidget.__init__(self,  parent=None)
	self.ui = Ui_rulesform()
	self.ui.setupUi(self)
	self.setWindowTitle('SAMT2 ----- Fuzzy_Analysis')
	#print "Popup_active_rules:: X=%.3f  Y=%.3f" % (X,Y)
	#self.ui.table.verticalHeader().setVisible(False)
	self.ui.table.setColumnWidth(0, 40)
	self.ui.table.setColumnWidth(2, 60)
	self.ui.table.setColumnWidth(6, 60)
	
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
	    s = "%.3f" % in1
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
		s = "%.3f" % in2
		item.setText(s)
		item.setTextAlignment(Qt.AlignCenter)
		item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
		self.ui.table.setItem(i,4,item)
		self.ui.table.hideColumn(5)
		self.ui.table.resizeColumnToContents(3)
		self.ui.table.resizeColumnToContents(4)
	    
	    elif anz_inp == 3:
		item = QtGui.QTableWidgetItem("in2")
		s = "%.3f" % in2
		item.setText(s)
		item.setTextAlignment(Qt.AlignCenter)
		item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
		self.ui.table.setItem(i,4,item)
		item = QtGui.QTableWidgetItem("in3")
		s = "%.3f" % in3
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
	    
	    #self.ui.table.resizeColumnToContents(1) # QTextEdit not ok
	    self.ui.table.setColumnWidth(1, 300)

########################################################################    
	
########################################################################
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    locale.setlocale(locale.LC_NUMERIC, "C") # decimal_point
    window = MyForm() 
    window.show()
    sys.exit(app.exec_())
########################################################################

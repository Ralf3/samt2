#!/usr/bin/env python
# -*- coding: utf-8 -*-  

### Aufbau siehe matplotlibwidgetFile.py   
  
import sys
import os
import math
import timeit
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class Diagr(QtGui.QWidget):
    def __init__(self, u, v, parent=None ):      
	super(Diagr,self).__init__()   
	#print "in super (Diagr __init__, parent=", self.parent
	# called by class PaintWidget, nur nach Neustart der GUI 
	
	self.dix = u  		# Diagrammgröße int
	self.diy = v
	self.setMinimumSize(u,v)
	
	self.ax = 0		# "Koordinatenursprung" int
	self.ay = 0
	self.dx = 0.0		# Verschiebungsfaktor
	self.dy = 0.0
	self.xmin = 0		# Achsenanfangs- und endpunkte int
	self.xmax = 0
	self.ymin = 0
	self.ymax = 0
	self.xfactor = 0.0	# Skalierungsfaktor float
	self.yfactor = 0.0
	self.xname = ""
	self.yname = ""
	self.mausx = 0
	self.mausy = 0        	# int current cursor-position
	self.xsteps = 0
	self.ysteps = 0   	# int Anzahl steps einer Achse, schreibt getSteps()
        self.vxstep = 0.0
	self.vystep = 0.0       # float Wert am ersten Strich,  schreibt getSteps()
        self.minX = 0.0
	self.minY = 0.0
	self.maxX = 0.0
	self.maxY = 0.0    	# float Min-und Max-Werte der Inputdaten
        
	self.xpoints = []	# list of floats,  parameter !!!!!
	self.ypoints = []	
        self.titleList = []    	# list of strings
	self.typeList = []	#   "
        self.numCurves = 0      # len(self.typeList)
	self.numPoints = 0	# len(self.xpoints)
	
	#~ QMainWindow *mainwindow;
	self.timer = QTimer()
	self.cursor = QCursor()
	self.startPoint = QPoint()  
	self.cursPoint = QPoint()
	
	self.time_start = 0
	self.leftdown = False
	self.dragging = False
	self.hit_index = -1	# nr. der Curve wo HandCursor ist
	self.hit = False
	self.grid = True
	self.parent_mainwin = None
	
	# actualizeMfTable ist in form1
	# not ok self.connect(self, SIGNAL('plotChanged'), self.bin_slot)   #window.actualizeMfTable
	
	# defaults:
	self.ANGLE = 0.999848
	self.MIN_X = 0.01
	self.MIN_DISTANCE = 5
	
	self.minX =  999  #FLT_MAX
	self.maxX = -999  #FLT_MIN
	self.minY =  999  # min. Wert auf neg. Y-Achse
	self.maxY = -999  # max. Wert auf pos. Y-Achse
	
	self.setMouseTracking(True)	
	self.setAttribute(QtCore.Qt.WA_StaticContents)
	#self.mainwindow = window 		# mainwin
	
	self.color_back = QtCore.Qt.white	# backgroundcolor weiß 
	self.color_rot = QtCore.Qt.red		# hilfsline
	self.color_schwarz = QtCore.Qt.black
	self.color_grau = QtCore.Qt.gray	# Gitternetzlinien
	#self.grau.setNamedColor('grey')     	#(150,150,150)   
	
	self.skalaFont = QtGui.QFont()
	self.skalaFont.setFamily("Arial")
	self.skalaFont.setPointSize(8)
	self.skalaFont.setWeight(25)
	self.skalaFont.setItalic(False)
	
	self.normFont = QtGui.QFont()
	self.normFont.setFamily("Arial")
	self.normFont.setPointSize(10)
	self.normFont.setWeight(50)
	self.normFont.setItalic(False)
	
	self.penDefault = QtGui.QPen()
	self.penDefault.setColor(self.color_schwarz) 
	self.penDefault.setStyle(Qt.SolidLine)
	self.penDefault.setWidth(2)
	
	self.penGrid = QtGui.QPen()
	self.penGrid.setColor(self.color_grau)
	self.penGrid.setStyle(Qt.DotLine)
	self.penGrid.setWidth(0)
	
	self.penMem = QtGui.QPen()
	self.penMem.setColor(self.color_schwarz)
	self.penMem.setStyle(Qt.SolidLine)
	self.penMem.setWidth(1)
	
	self.penRedLine = QtGui.QPen()
	self.penRedLine.setColor(self.color_rot)
	self.penRedLine.setStyle(Qt.SolidLine)
	self.penRedLine.setWidth(1)	

        self.count = 0
	
    #-------------------------------------------------------------------
    def clear_plot(self):
	# called by: parent.showMembership
	self.dia = None
	
    #-------------------------------------------------------------------
    def setLists(self, li1, li2, li3, li4, anzCurves, anzPoints, xname, grid_yesno, mainwin):
	# called by: MyForm.btn
	self.titleList = li1
	self.typeList  = li2
	self.xpoints   = li3   	# = xMf ,filled in getMfVector
	self.ypoints   = li4	# = yMf ,	   "
	#self.memb      = li5
	self.numCurves = anzCurves
	self.numPoints = anzPoints
	self.xname = xname
	self.grid_yesno = grid_yesno
	self.parent_mainwin = mainwin
	
    #-------------------------------------------------------------------
    def plot(self):
	# called by init, mouseMove, mouseRelease , MyForm 
	if len(self.ypoints) == 0:  
	    self.maxY = 1   	
	    self.minY = 0
	if self.numPoints == 1:    
	    self.minX = self.xpoints[0]
	    self.maxX = self.minX + 1
	    self.minY = 0
	    self.maxY = 1
	else:
	    if len(self.xpoints) > 0:		
		self.minX = min(self.xpoints)
		self.minY = min(self.ypoints)
		self.maxX = max(self.xpoints)
		self.maxY = max(self.ypoints)
	#print "plot:: Min Max der Inputs: minX, maxX, minY, maxY",self.minX,self.maxX,self.minY,self.maxY

	self.testValues()  #Diagrammgrenzen festlegen, so dass immer beide Achsen zu sehen sind
	
	self.getSteps(self.minX, self.maxX, self.minY, self.maxY)   #call nur von hier !!!!
	
	self.update()    # calls paintEvent
	
    #-------------------------------------------------------------------
    def paintEvent(self, event):
	# called by: plot() and  PaintWidget.__init__
	#print "paintEv"
	xmin = 0
	xmax = 0
	ymin = 0
	ymax = 0
	self.count += 1
	
	# get current (if stretched) geometry of paintwid
	self.dix = self.width()     # Width of mf diagramm (paintwid)
	self.diy = self.height()    # Height    "
	#print "paintwid.width=%d height=%d" % (self.dix,self.diy)
	
	p = QtGui.QPainter()
	p.begin(self) 
	# all painter settings (setPen(), setBrush()..) 
	# are reset to default values when begin() is called.
	p.setPen(self.penDefault)
	p.setFont(self.skalaFont)
	
	#Hintergrund des Diagramms
	p.fillRect(0,0, self.dix, self.diy, QBrush(self.color_back))

	# Skalierungsfaktor   dix, diy Size of Diagramm 
	#print "start paintEv -----------------------------------------"
	#print "paintEv:: dix=%d, diy=%d,  %d" % (
	#			    self.dix, self.diy, self.count)
	#print "paintEv:: minX=%d, maxX=%d, minY=%d, maxY=%d" % (
	#		    self.minX, self.maxX,self.minY, self.maxY)
	if (self.maxX == 0.0) and (self.minX == 0.0):
	    return
	self.xfactor = self.dix / (self.maxX-self.minX)
	self.yfactor = self.diy / (self.minY-self.maxY)
	#print "paintEv:: xfactor, yfactor", self.xfactor, self.yfactor
	
	# (0,0) im globalen Sytem
	self.ax = int(self.minX* self.xfactor)
	self.ay = int(self.maxY* self.yfactor)
	#print "paintEv:: KoordUrsprung: ax, ay, self.ax, self.ay
	
	#Grenzen des Diagramms bestimmen
	xmin = int(self.minX* self.xfactor)
	xmax = int(self.maxX* self.xfactor)
	ymax = int(self.maxY* self.yfactor)
	ymin = int(self.minY* self.yfactor)

	#neues Koordinatensystem
	p.setWindow(xmin, ymax, self.dix, self.diy)
	
	# neue min. und max. Werte (Achsenanfangs- und endpunkte).
	# damit nicht bis an die Grenzen des Diagramms gezeichnet wird.
	xmin = int(xmin*0.95)
	xmax = int(xmax*0.95)
	ymin = int(ymin*0.95)
	ymax = int(ymax*0.95)
	
	#x-Achse
	p.drawLine(xmin,0,xmax,0)
	#y-Achse
	p.drawLine(0, ymin, 0, ymax)
	
	#Pfeilspitzen --------------
	pfeilBrush = QBrush(self.color_schwarz, Qt.SolidPattern)
	p.setBrush(pfeilBrush)
	xpoints = [QPoint(xmax,-3), QPoint(xmax,3), QPoint(xmax+8,0)]
	xpfeil = QPolygon(xpoints)
	p.drawPolygon(xpfeil)
	ypoints = [QPoint(-3,ymax), QPoint(3,ymax), QPoint(0,ymax-8)]
	ypfeil = QPolygon(ypoints)
	p.drawPolygon(ypfeil)
	#--------------- end pfeil 
	
	ymax = int(ymax*0.97)
	#print self.vxstep	# 100
	if self.numCurves <= 0:
	    p.end()
	    return
	
	#######if self.numCurves > 0:
	   
	# x-Skala
	if (abs(xmax) > abs(xmin)):
	    step = int(abs(xmax) / self.xsteps)  #Abstand der Striche
	else:
	    step = int(abs(xmin) / self.xsteps)
	    #print "paintEv:: xsteps=%d, step=%d" % (self.xsteps, step)
	xskala = 0  #int 
	num = 0.0	#float 
	while (xskala+step) <= xmax:
	    xskala += step
	    num    += self.vxstep
	    #print "paintEv:: xskala=%d,  num=%f" % (xskala, num)
    
	while xskala >= xmin:
	    #print "Senkrechte Gitternetzlinien xskala =", xskala
	    if self.grid_yesno== True:
		p.setPen(self.penGrid)
		if (not abs(xskala) < 3):
		    p.drawLine(xskala, ymax, xskala, ymin)
	    p.setPen(self.penDefault)

	    # X-AchsenNumerierung
	    zahl = str(num)   # QString ?
	    if  (not num==0) and (not abs(xskala)==0):
		p.drawText(int(xskala-step/2),0 ,step,25, Qt.AlignCenter, zahl) 
	    num -= self.vxstep
	    # X-Achsenskala
	    p.drawLine(xskala,-2,xskala,+2)
	    xskala -= step

	# y-Skala
	if (abs(ymax)>abs(ymin)):
	    step = int(abs(ymax) / self.ysteps)
	else:
	    step = int(abs(ymin) / self.ysteps)
	num = 0.0
	yskala = 0	
	while (yskala+step) > ymax:
	    yskala -= step
	    num    += self.vystep
	
	#print "paintEv::yskala=%d, ymin=%d, ymax=%d"%(yskala,ymin,ymax)
	while yskala <= ymin:
	    #Waagerechte Gitternetzlinien
	    if self.grid_yesno == True:
		p.setPen(self.penGrid)
		if (not (abs(yskala)<7) and (yskala>(ymax-3))):
		    p.drawLine(xmin,yskala,xmax,yskala)
	    p.setPen(self.penDefault)
	    #Y-AchsenSkala
	    p.drawLine(-2,yskala,2,yskala)
	    yskala += step
	
	#Beschriftung der x-Achse
	if self.xname == '':
	    self.xname = "X-Achse"
	p.drawText(0, 25, xmax, 25, Qt.AlignRight, self.xname)

	#Beginn der Darstellung der einzelnen Graphen
	if (abs(xmax) > abs(xmin)):
	    self.dx= (abs(xmax) / self.xsteps) / self.vxstep
	else:
	    self.dx= (abs(xmin) / self.xsteps) / self.vxstep
	if (abs(ymax) > abs(ymin)):
	    self.dy= (abs(ymax) / self.ysteps) / self.vystep
	else:
	    self.dy= (abs(ymin) / self.ysteps) / self.vystep
	
	# umspeichern
	self.xmin = xmin
	self.xmax = xmax
	self.ymin = ymin
	self.ymax = ymax
	
	#**************************
	#**** start plot the graph
	#**************************
	p.setPen(self.penMem)
	for i in range(self.numPoints-1):		
	    x1= int(self.xpoints[i] * self.dx)
	    y1= int(self.ypoints[i] * (-1) * self.dy)
	    x2= int(self.xpoints[i+1] *  self.dx)
	    y2= int(self.ypoints[i+1] * (-1) * self.dy)
	    
	    #print "paintEv start plot:: i=%d: x1=%d, y1=%d, x2=%d, y2=%d" % (i,x1, y1, x2, y2)
    
	    if not(self.ypoints[i]==0 and self.ypoints[i+1]==0):
		if self.typeList[0] == "left":
		    if i > 0:
			#print "Gerade links außen nicht plotten"
			if i < 4:
			    #print "i ist kleiner 4"
			    p.drawLine(x1,y1,x2,y2)
			else:
			    if self.typeList[-1] == "right":
				if i < self.numPoints-2:	
				     p.drawLine(x1,y1,x2,y2)
				#else:
				     #print "Gerade rechts aussen not plot"
			    else:
				#print "triangle or trapeze"
				p.drawLine(x1,y1,x2,y2)
		else:
		    if self.typeList[-1] == "right":
			if i < self.numPoints-2:     
			     p.drawLine(x1,y1,x2,y2)
			#else:
			     #print "Gerade rechts außen nicht plotten"
		    else:
			#print "triangle (x1=x2) or trapeze"
			p.drawLine(x1,y1,x2,y2)

	# member-title at the top of each curve
	curvCtr = -1
	for i in range(self.numPoints-1):  
	    if self.ypoints[i]==0 and self.ypoints[i+1]==1:
		curvCtr += 1
		name = self.titleList[curvCtr]
		qname = QString(name)	# rein 18.12.
		if qname.length() >= 10:
		    qname = qname.left(10)
		    name = str(qname)
		y1 = int(self.maxY*self.yfactor)
		y2 = int(ymax-y1)
		if self.typeList[curvCtr] == "triangular":
		    x1 = int(self.xpoints[i+1] * self.dx-25)
		    x2= 50
		    p.drawText(x1,y1,x2,y2,Qt.AlignCenter,name)
		else:
		    # trapeze, left and right
		    x1 = int((((self.xpoints[i+2]-self.xpoints[i+1]) /2) +self.xpoints[i+1])*self.dx)
		    x2 = 60
		    p.drawText(x1-30,y1,x2,y2,Qt.AlignCenter,name)
	
	# paint vertical redLine
	p.setPen(self.penRedLine)   
	if self.hit == True:
	    # set TRUE only in mouseMove
	    x1 = int(self.xpoints[self.hit_index]*self.dx)
	    p.drawLine(x1,ymax,x1,10)
	p.end()
    
    #-------------------------------------------------------------------
    def setCorrectValues(self, maus1x, index):
	# called by: mouseMoveEv,  
	# args: self.mausx, self.hit_index (index of clicked Points)
	# nutzt self.ax, self.dx, self.startPoint (wrote in mousePressEv)
	
	#--------- 1. Fall ---------------------------------------------
	# bei index==0 aufpassen, dass nicht zu weit nach rechts geschoben wird
	if index==0:
	    if maus1x > self.startPoint.x():
		#nach rechts
		if maus1x < (self.xpoints[index+1]*self.dx-self.MIN_X*self.dx-self.ax):
		    self.xpoints[index] = round((maus1x+self.ax) / self.dx, 2)
		else:
		    self.xpoints[index]= round(self.xpoints[index+1]-self.MIN_X, 2)

	    if maus1x < self.startPoint.x():
		# nach links
		if maus1x > (self.xmin+20-self.ax):
		    v = (maus1x+self.ax) / self.dx
		    self.xpoints[index] = round(v,2)  
		else:
		    self.xpoints[index] = round((self.xmin+20) / self.dx, 2)
	
	#--------- 2. Fall ---------------------------------------------
	# Beim letzten Punkt aufpassen, wenn man ihn nach links schiebt
	if index==self.numPoints-1:    # zB. rechts außen v. trapez
	    if maus1x < self.startPoint.x():
		# nach links
		if maus1x > (self.xpoints[index-1]*self.dx+self.MIN_X*self.dx-self.ax):
		    self.xpoints[index]= (maus1x+self.ax) / self.dx
		else:
		    self.xpoints[index]= self.xpoints[index-1] + self.MIN_X

	    if maus1x > self.startPoint.x():
		# nach rechts
		if maus1x < (self.xmax-20-self.ax):
		    self.xpoints[index]=(maus1x+self.ax) / self.dx
		else:
		    self.xpoints[index]=(self.xmax-20) / self.dx	
	
	
	#--------- 3. Fall ---------------------------------------------
	# Aufpassen, dass nicht zu weit nach links 
	# (keine weitere Mf verschieben) oder nach rechts 
	# (aufpassen wegen nächster Mf, falls vorhanden)
	if index==1:
	    if maus1x < self.startPoint.x():
		# nach links
		if self.numPoints > 4: 
		    # mehr als eine Mf 
		    if (self.ypoints[index+1]==0):
			#Dreieck
			if maus1x > (self.xpoints[index-1]*self.dx+self.MIN_X*self.dx-self.ax):
			    self.xpoints[index]= (maus1x+self.ax) / self.dx
			    self.xpoints[index+2]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index-1] + self.MIN_X
			    self.xpoints[index+2]=self.xpoints[index-1] + self.MIN_X
		    else:
			if maus1x > (self.xpoints[index-1]*self.dx+self.MIN_X*self.dx-self.ax):
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index-1] + self.MIN_X
		else:
		    #nur eine Mf
		    if maus1x > (self.xpoints[index-1]*self.dx+self.MIN_X*self.dx-self.ax):
			self.xpoints[index]=(maus1x+self.ax) / self.dx
		    else:
			self.xpoints[index]=self.xpoints[index-1] + self.MIN_X

	    if maus1x > self.startPoint.x():
		# nach rechts
		if self.numPoints > 4:
		    #mehr als eine Mf
		    if self.ypoints[index+1]==0:
			#Dreieck
			if maus1x < (self.xpoints[index+1]*self.dx-self.MIN_X*self.dx-self.ax):
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			    self.xpoints[index+2]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index+1] - self.MIN_X
			    self.xpoints[index+2]=self.xpoints[index+1] - self.MIN_X
		    else:
			if self.ypoints[index+1]==1:
			    #Trapez
			    if (self.xpoints[index+1]-self.xpoints[index])*self.dx > 10:
				self.xpoints[index]=(maus1x+self.ax)/self.dx
			    else:
				self.xpoints[index]=self.xpoints[index+1]-10/self.dx
		else:
		    #eine Mf
		    if self.ypoints[index+1]==0:
			#Dreieck
			if maus1x < (self.xpoints[index+1]*self.dx-self.MIN_X*self.dx-self.ax):
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index+1] - self.MIN_X
		    elif self.ypoints[index+1]==1:
			#Trapez
			if (self.xpoints[index+1]-self.xpoints[index])*self.dx > 10:
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index+1]-10/self.dx
	
	#------ 4. Fall ------------------------------------------------
	if index==self.numPoints-2 and index!=1:     #numCurves-2 and index!=1:
	    if maus1x < self.startPoint.x():
		# nach links
		if self.numPoints > 4:  
		    #mehr als eine Mf
		    if self.ypoints[index-1]==0:
			#Dreieck
			if maus1x > (self.xpoints[index-1]*self.dx+self.MIN_X*self.dx-self.ax):
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			    self.xpoints[index-2]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index-1] + self.MIN_X
			    self.xpoints[index-2]=self.xpoints[index-1] + self.MIN_X
		    else:
			#Trapez
			if (self.xpoints[index]-self.xpoints[index-1])*self.dx > 10:
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index-1] + 10/self.dx
		else:
			#eine Mf
		    if (self.xpoints[index]-self.xpoints[index-1])*self.dx > 10:
			self.xpoints[index]=(maus1x+self.ax) / self.dx
		    else:
			v = self.xpoints[index-1] + 10/self.dx 
			self.xpoints[index]= round(v,2)  			
	    
	    if maus1x > self.startPoint.x():
		# nach rechts
		if self.numPoints > 4:   
		    if self.ypoints[index-1] == 0:
			#Dreieck
			if maus1x < (self.xpoints[index+1]*self.dx-self.MIN_X*self.dx-self.ax):
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			    self.xpoints[index-2]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index+1] - self.MIN_X
			    self.xpoints[index-2]=self.xpoints[index+1] - self.MIN_X
		    else:
			#Trapez
			if maus1x < (self.xpoints[index+1]*self.dx-self.MIN_X*self.dx-self.ax):
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index+1] - self.MIN_X
		else:
		    #eine Mf
		    if maus1x < (self.xpoints[index+1]*self.dx-self.MIN_X*self.dx-self.ax):
			self.xpoints[index]=(maus1x+self.ax) / self.dx
		    else:
			self.xpoints[index]=self.xpoints[index+1] - self.MIN_X
	
	#--------- 5. Fall -----------------------------------------
	if index>1 and index<self.numPoints-2 and self.numPoints>4:

	    #print "5. Fall set self.xpoints"

	    #eine der Spitzen gegriffen
	    if self.ypoints[index]==1:
		if maus1x < self.startPoint.x():
		    # nach links
		    if self.ypoints[index-1]==0 and self.ypoints[index+1]==0:
			#Dreieck
			if maus1x > (self.xpoints[index-1]*self.dx+self.MIN_X*self.dx-self.ax):
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			    self.xpoints[index-2]=(maus1x+self.ax) / self.dx
			    self.xpoints[index+2]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index-1] + self.MIN_X
			    self.xpoints[index-2]=self.xpoints[index-1] + self.MIN_X
			    self.xpoints[index+2]=self.xpoints[index-1] + self.MIN_X

		    if self.ypoints[index-1]==0 and self.ypoints[index+1]==1:
			#links oben vom Trapez
			if maus1x > (self.xpoints[index-1]*self.dx+self.MIN_X*self.dx-self.ax):
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			    self.xpoints[index-2]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index-1] + self.MIN_X
			    self.xpoints[index-2]=self.xpoints[index-1] + self.MIN_X

		    if self.ypoints[index-1]==1 and self.ypoints[index+1]==0:
			#rechts oben vom Trapez
			if (self.xpoints[index]-self.xpoints[index-1])*self.dx > 10:
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			    self.xpoints[index+2]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index-1] + 10/self.dx
			    self.xpoints[index+2]=self.xpoints[index-1] + 10/self.dx

		if maus1x > self.startPoint.x():
		    # nach rechts
		    if self.ypoints[index-1]==0 and self.ypoints[index+1]==0:
			#Dreieck
			if maus1x < (self.xpoints[index+1]*self.dx-self.MIN_X*self.dx-self.ax):
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			    self.xpoints[index-2]=(maus1x+self.ax) / self.dx
			    self.xpoints[index+2]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index+1] - self.MIN_X
			    self.xpoints[index-2]=self.xpoints[index+1] - self.MIN_X
			    self.xpoints[index+2]=self.xpoints[index+1] - self.MIN_X

		    if self.ypoints[index-1]==0 and self.ypoints[index+1]==1:
			# links oben vom Trapez
			if (self.xpoints[index+1]-self.xpoints[index])*self.dx > 10:
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			    self.xpoints[index-2]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index+1] - 10/self.dx
			    self.xpoints[index-2]=self.xpoints[index+1] - 10/self.dx

		    if self.ypoints[index-1]==1 and self.ypoints[index+1]==0:
			#rechts oben vom Trapez
			if maus1x < (self.xpoints[index+1]*self.dx-self.MIN_X*self.dx-self.ax):
			    self.xpoints[index]=(maus1x+self.ax) / self.dx
			    self.xpoints[index+2]=(maus1x+self.ax) / self.dx
			else:
			    self.xpoints[index]=self.xpoints[index+1] - self.MIN_X
			    self.xpoints[index+2]=self.xpoints[index+1] - self.MIN_X
	
	    #----------- 6. letzter Fall -----------------------------------
	    # auf dem Boden gegriffen
	    #~ if self.ypoints[index]==0:
	    
		#~ if maus1x < self.startPoint.x():
		    #~ # nach links
		    #~ #print "666666_nach links ,  startPoint.x() = ", self.startPoint.x()
		    #~ #Stelle, wo zwei Geraden sich auf der x-Achse treffen ???
		    
		    #~ if index+4 > len(self.xpoints):
			#~ print "idx ist ausserhalb"
		    #~ if ((self.xpoints[index]==self.xpoints[index+4-1] or self.xpoints[index]==self.xpoints[index-4+1]) and (index!=2 or index!=self.numPoints-3)):
			#~ if self.xpoints[index]==self.xpoints[index+4-1]:
			    #~ #linker Punkt erfasst
			    #~ if maus1x > (self.xpoints[index-1]*self.dx+self.MIN_X*self.dx-self.ax):
				#~ self.xpoints[index]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index+2]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index+4]=(maus1x+self.ax) / self.dx
			    #~ else:	
				#~ self.xpoints[index]=self.xpoints[index-1] + self.MIN_X
				#~ self.xpoints[index+2]=self.xpoints[index-1] + self.MIN_X
				#~ self.xpoints[index+4]=self.xpoints[index-1] + self.MIN_X

			#~ if self.xpoints[index]==self.xpoints[index-4+1]:
			    #~ #rechter Punkt erfasst
			    #~ if maus1x > (self.xpoints[index-5]*self.dx+self.MIN_X*self.dx-self.ax):
				#~ self.xpoints[index]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index-2]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index-4]=(maus1x+self.ax) / self.dx
			    #~ else:
				#~ self.xpoints[index]=self.xpoints[index-5] + self.MIN_X
				#~ self.xpoints[index+2]=self.xpoints[index-5] + self.MIN_X
				#~ self.xpoints[index+4]=self.xpoints[index-5] + self.MIN_X
		    #~ else:
			#~ #Normalfall
			#~ if self.ypoints[index-3]==1:
			    #~ #Links unten --- Mf-1 ist ein Trapez
			    #~ if (self.xpoints[index]-self.xpoints[index-3])*self.dx > 10:
				#~ v = (maus1x+self.ax) / self.dx
				#~ self.xpoints[index] = round(v,2)
				#~ self.xpoints[index-2] = round(v,2)  
			    #~ else:
				#~ self.xpoints[index]=self.xpoints[index-3] + 10/self.dx
				#~ self.xpoints[index-2]=self.xpoints[index-3] + 10/self.dx
				
			#~ if self.ypoints[index-1]==1:
			    #~ #rechts unten vom Trapez oder links vom Dreieck
			    #~ if maus1x > (self.xpoints[index-1]*self.dx+self.MIN_X*self.dx-self.ax):
				#~ self.xpoints[index]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index+2]=(maus1x+self.ax) / self.dx
			    #~ else:
				#~ self.xpoints[index]=self.xpoints[index-1] + self.MIN_X
				#~ self.xpoints[index+2]=self.xpoints[index-1] + self.MIN_X
			#~ if self.ypoints[index-1]==0 and self.ypoints[index-3]==0:
			    #~ if maus1x > (self.xpoints[index-3]*self.dx+self.MIN_X*self.dx-self.ax):
				#~ self.xpoints[index]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index-2]=(maus1x+self.ax) / self.dx
			    #~ else:
				#~ self.xpoints[index]=self.xpoints[index-3] + self.MIN_X
				#~ self.xpoints[index-2]=self.xpoints[index-3] + self.MIN_X

		#~ if maus1x > self.startPoint.x():
		    #~ # nach rechts
		    #~ if (self.xpoints[index]==self.xpoints[index-4+1]) and (index!=2 or index!=self.numPoints-3):
			#~ if self.xpoints[index]==self.xpoints[index+4]:
			    #~ #linker Punkt erfasst
			    #~ if maus1x < (self.xpoints[index+5]*self.dx-self.MIN_X*self.dx-self.ax):
				#~ self.xpoints[index]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index+2]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index+4]=(maus1x+self.ax) / self.dx
			    #~ else:
				#~ self.xpoints[index]=self.xpoints[index+5] - self.MIN_X
				#~ self.xpoints[index+2]=self.xpoints[index+5] - self.MIN_X
				#~ self.xpoints[index+4]=self.xpoints[index+5] - self.MIN_X

			#~ if self.xpoints[index]==self.xpoints[index-4]:
			    #~ #rechter Punkt erfasst
			    #~ if maus1x < (self.xpoints[index+1]*self.dx-self.MIN_X*self.dx-self.ax):
				#~ self.xpoints[index]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index-2]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index-4]=(maus1x+self.ax) / self.dx
			    #~ else:
				#~ self.xpoints[index]=self.xpoints[index+1] - self.MIN_X
				#~ self.xpoints[index-2]=self.xpoints[index+1] - self.MIN_X
				#~ self.xpoints[index-4]=self.xpoints[index+1] - self.MIN_X
		    #~ else:
			#~ #Normalfall
			#~ if self.ypoints[index+3]==1:
			    #~ #rechts unten nächste Mf ist ein Trapez
			    #~ if (self.xpoints[index+3]-self.xpoints[index+2])*self.dx > 10:
				#~ self.xpoints[index]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index+2]=(maus1x+self.ax) / self.dx
			    #~ else:
				#~ self.xpoints[index]=self.xpoints[index+3] - 10/self.dx
				#~ self.xpoints[index+2]=self.xpoints[index+3] - 10/self.dx
			#~ if self.ypoints[index+1]:
			    #~ #links unten vom Dreieck oder Trapez
			    #~ if maus1x < (self.xpoints[index+1]*self.dx-self.MIN_X*self.dx-self.ax):
				#~ self.xpoints[index]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index-2]=(maus1x+self.ax) / self.dx
			    #~ else:
				#~ self.xpoints[index]=self.xpoints[index+1] - self.MIN_X
				#~ self.xpoints[index-2]=self.xpoints[index+1] - self.MIN_X
			#~ if self.xpoints[index]==self.xpoints[self.numPoints-1]:
			    #~ if maus1x < (self.xpoints[self.numPoints-1]*self.dx-self.MIN_X*self.dx-self.ax):
				#~ self.xpoints[index]=(maus1x+self.ax) / self.dx
				#~ self.xpoints[index+2]=(maus1x+self.ax) / self.dx
			    #~ else:
				#~ self.xpoints[index]=self.xpoints[self.numPoints-1] - self.MIN_X
				#~ self.xpoints[index+2]=self.xpoints[self.numPoints-1] - self.MIN_X
		
	if self.parent_mainwin != None:
	    msg = "%1.3f" % (float(self.xpoints[index]))
	    self.parent_mainwin.ui.statusbar.showMessage(msg)
	
    #-------------------------------------------------------------------
    def testValues(self):
	# print "testValues start mit: minX, maxX, minY, \
	#	    maxY", self.minX, self.maxX, self.minY, self.maxY
	# called by: plot
	# testet max. und min. x(y), verändert diese so, 
	# dass Achsen immer sichtbar bleiben

	#minX<0
	if (self.minX>=0 ):
	    h=float((-0.2)* self.maxX)
	    self.minX=h
	
	#maxX>0
	if (self.maxX<=0):
	    h= float((-0.2)* self.minX)
	    self.maxX=h
	
	#maxX=> 20% von |minX|
	if (self.maxX>0):
	    h= float((-0.2)*self.minX)
	    if (self.maxX<h):
		self.maxX=h
	
	#minX<=20% von |maxX|
	if (self.minX<0):
	    h= float((-0.2)* self.maxX)
	    if (self.minX>h):
		self.minX=h
	
	#minY<0
	if (self.minY>=0 ):
	    h= float((-0.2)* self.maxY)
	    self.minY=h
	
	#maxY>0
	if (self.maxY<=0):
	    h= float((-0.2)* self.minY)
	    self.maxY=h
	
	#maxY=> 20% von |minY|
	if (self.maxY>0):
	    h= float((-0.2)* self.minY)
	    if (self.maxY<h):
		self.maxY=h
	
	#minX<=20% von |maxX|
	if (self.minY<0):
	    h= float((-0.2)* self.maxY)
	    if (self.minY>h):
		self.minY=h
	
    #-------------------------------------------------------------------
    def getSteps(self, minx, maxx, miny, maxy):
	# all is float 
	#print "getSteps called by: plot"
	if math.fabs(minx) <= math.fabs(maxx):
	    minx=0
	else:
	    maxx=0
	if math.fabs(miny) <= math.fabs(maxy):
	    miny=0
	else:
	    maxy=0
	
	# --- x-Achse
	xline = 1.0;
	xscale = 0
	ix1 = 0
	iy1 = 0
	#~ int hxsteps, hysteps   #Hilfsvariablen für %steps
	step = math.fabs(maxx - minx)   # float
	if step > 1.0:
	    while step > 10.0:
		xscale += 1
		step /= 10.0
	else:
	    while step < 1.0:
		xscale -= 1
		step *= 10
	while step < 5:
	    step += step
	    xline /= 2
	if (int(step))%2 :  
	    step += 1
	xline = xline*pow(10,xscale)
	hxsteps = int(step)   	# x Schrittbreite

	# --- y-Achse
	yline = 1.0
	yscale = 0
	step = math.fabs(maxy - miny)  #float
	if step > 1.0:
	    while step > 10.0:
		yscale += 1
		step /= 10.0
	else:
	    while step<1.0:
		yscale -= 1
		step *= 10
	while step<5:
	    step += step
	    yline /= 2
	if int(step)%2:
	    step += 1
	yline = yline*pow(10,yscale)
	hysteps = int(step)	# y #Schrittbreite
	
	
	while math.fabs(maxx) > math.fabs(2*ix1*xline):
	    if (minx < 0 or maxx > 0):
		ix1 -= 1
	    else:
		ix1 += 1
	while math.fabs(miny) > math.fabs(2*iy1*yline):
	    if(miny < 0 or maxy > 0):
		iy1 -= 1
	    else:
		iy1 += 1
	if minx >= 0 and minx < xline:
	    ix1 = 0
	if miny >= 0 and miny < yline:
	    iy1 = 0
	while (hysteps+iy1)*yline < math.fabs(maxy - miny):
	    hysteps += 1
	while (hxsteps+ix1)*xline < math.fabs(maxx - minx):
	    hxsteps += 1
	
	self.xsteps = hxsteps
	self.ysteps = hysteps
	self.vxstep = xline
	self.vystep = yline
    
    
    #==== MOUSE  ====================================
    
    def mousePressEvent(self, ev):
	#~ if self.leftdown == True: return  
	if ev.button() == Qt.LeftButton:
	    # Linke Maustaste gedrückt: Zuerst klicken annehmen, 
	    # dragging=false, Zeitpunkt und Position merken
	    self.leftdown = True
	    self.dragging = False
	    
	    # start stoppuhr, end in MouseMove
	    #self.time_start = timeit.default_timer()  
	    #print "self.time_start=", self.time_start
	    
	    self.startPoint = ev.pos()     
	    self.mausx = self.startPoint.x() #aktuelle Maus-Position
	    self.mausy = self.startPoint.y()
	    #print "mausX=%d, mausY = %d" % (self.mausx, self.mausy) 
	    
	    for i in range(self.numPoints):     
		a = math.fabs(self.mausx-(self.xpoints[i]*self.dx-self.ax))
		b = math.fabs(self.mausy-(self.ypoints[i]*(-1)*self.dy-self.ay))
		if (a<5) and (b<5):
		    self.hit = True	# set True only here!
		    self.hit_index = i	# idx of xpoints, write only here!
		    msg = "%1.3f" % (float(self.xpoints[self.hit_index]))
		    self.parent_mainwin.ui.statusbar.showMessage(msg)
		    return
		else:
		    self.hit = False
		    self.hit_index = -1

    #-------------------------------------------------------------------
    def mouseMoveEvent(self, ev):
	self.mausx = ev.pos().x()
	self.mausy = ev.pos().y()
	#print "mouseMoveEv: mausx=%d, mausy=%d, dx=%s, ax=%s" % 
	#		(self.mausx, self.mausy, self.dx, self.ax)
	if self.leftdown == False: 
	    #nur bei gedrückter li. Taste, releaseEv set leftdown=False
	    for i in range(self.numPoints): 
		
		a = math.fabs(self.mausx-(self.xpoints[i]*self.dx-self.ax))
		b = math.fabs(self.mausy-(self.ypoints[i]*(-1)*self.dy-self.ay)) # Hand am Boden
		
		#print "x[%d]=%s  y=%s a=%s, b=%s" % (i, self.xpoints[i], self.ypoints[i], a, b)
		
		if (a<5) and self.mausy>23 and self.mausy<30 :        #(b<5):        		
		    # handcursor nur am oberen Rand, nicht am Boden
		    self.cursor.setShape(Qt.PointingHandCursor)	
		    self.setCursor(self.cursor)
		    return
		else:
		    self.cursor.setShape(Qt.ArrowCursor)
		    self.setCursor(self.cursor)
	if self.dragging == False:
	    # MousePress started the timer 
	    #time_stop = timeit.default_timer()-self.time_start
	    #print "time_stop=", time_stop	# welche einheit?
	    #if time_stop >= 300:   #or    msec?           
		#~ if ((self.startPoint.x() - self.mausx > 10) or 
			#~ (self.mausx - self.startPoint.x() >10)  or
			#~ (self.startPoint.y() - self.mausy > 10) or 
			#~ (self.mausy - self.startPoint.y() > 10)):
			#self.dragging = True
	    self.dragging = True
		
	if self.dragging == True and self.hit == True:
	    #print "mouseMove...dragging=True and hit = True"
	    # hit_index set in MousePress = CurvePointNr, wo HandCursor 
	    self.setCorrectValues(self.mausx, self.hit_index)
	    self.plot() 
	
    #-------------------------------------------------------------------
    def mouseReleaseEvent(self, ev):
	if self.leftdown == False or ev.button() != Qt.LeftButton:
	    return
	# Falls die Maus nicht bewegt worden ist, aber mehr als 300ms 
	# vergangen sind, muss dragging= True gesetzt werden
	ev.accept()
	self.leftdown = False
	self.hit = False
	self.hit_index = -1
	self.cursor.setShape(Qt.ArrowCursor)
	self.setCursor(self.cursor)
	self.plot()   
	self.parent_mainwin.ui.statusbar.clearMessage()	# in gui
	self.parent_mainwin.actualizeMfTable()     
	

########################################################################
## class wird im QtDesigner in QWidget promotet
## calls the class Diagr, einmalig nach start
class PaintWidget(QtGui.QWidget):
    def __init__(self, parent = None):
	QtGui.QWidget.__init__(self, parent)  # init der Basisklasse
	self.dia = Diagr(806,300)  # weißer Background 
	#print "PaintWidget__ init__"
	self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.dia)      
	self.setLayout(self.vbox)   
	
########################################################################


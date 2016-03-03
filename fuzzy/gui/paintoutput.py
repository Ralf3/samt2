#!/usr/bin/env python
# -*- coding: utf-8 -*-  
     
import sys
import os
import math
import timeit
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DiagrOut(QtGui.QWidget):
    def __init__(self, u, v, parent=None ):     
	super(DiagrOut,self).__init__()   
	#print "in super (DiagrOut __init__, parent=", self.parent
	# called by class PaintOutput, nur nach Neustart der GUI 

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
	
	self.cursor = QCursor()
	self.startPoint = QPoint()  
	self.cursPoint = QPoint()
	
	self.leftdown = False
	self.dragging = False
	self.hit_index = -1	# nr. of curve with HandCursor 
	self.hit = False
	self.grid = True
	self.parent_mainwin = None
	
	self.ANGLE = 0.999848
	self.MIN_X = 0.01
	self.MIN_DISTANCE = 5
	
	self.minX =  999  #FLT_MAX
	self.maxX = -999  #FLT_MIN
	self.minY =  999  # min. Wert auf neg. Y-Achse
	self.maxY = -999  # max. Wert auf pos. Y-Achse
	
	self.setMouseTracking(True)	
	self.setAttribute(QtCore.Qt.WA_StaticContents)
	
	self.color_back = QtCore.Qt.white	# backgroundcolor weiß 
	self.color_rot = QtCore.Qt.red	# hilfsline
	self.color_schwarz = QtCore.Qt.black
	self.color_grau = QtCore.Qt.gray	# Gitternetzlinien
	
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
	self.penDefault.setColor(self.color_schwarz) # alt: standard
	self.penDefault.setStyle(Qt.SolidLine)
	self.penDefault.setWidth(2)
	#self.penDefaultWidth = 2
	
	self.penGrid = QtGui.QPen()
	self.penGrid.setColor(self.color_grau)
	self.penGrid.setStyle(Qt.DotLine)
	self.penGrid.setWidth(0)
	
	self.penOut = QtGui.QPen()
	self.penOut.setColor(self.color_schwarz)
	self.penOut.setStyle(Qt.SolidLine)
	self.penOut.setWidth(2)

	self.hitPenOut = QtGui.QPen()
	self.hitPenOut.setColor(self.color_rot)
	self.hitPenOut.setStyle(Qt.SolidLine)
	self.hitPenOut.setWidth(2)
	
	self.penRedLine = QtGui.QPen()
	self.penRedLine.setColor(self.color_rot)
	self.penRedLine.setStyle(Qt.SolidLine)
	self.penRedLine.setWidth(1)	

        self.count = 0
	
    #-------------------------------------------------------------------
    def clear_plot(self):
	# called by: parent.showOutput
	self.dia = None
	
    #-------------------------------------------------------------------
    def setLists(self, li1, li2, li3, anzCurves, xname, grid_yesno, mainwin):
	# called by: MyForm.btn
	self.titleList = li1
	#print "paintOut: setLists:: titleList=", self.titleList
	self.xpoints   = li2   	# = xOut ,filled in getOutputVector
	self.ypoints   = li3   	# = xOut 
	self.numCurves = anzCurves
	#self.numPoints = anzPoints
	self.xname = xname
	self.grid_yesno = grid_yesno
	self.parent_mainwin = mainwin
	
    #-------------------------------------------------------------------
    def plot(self):
	# called by init, mouseMove, mouseRelease , MyForm 
	if len(self.ypoints) == 0:
	    self.minY = 0 
	    self.maxY = 1 
	if len(self.xpoints) > 0:		
	    self.minX = min(self.xpoints)
	    self.maxX = max(self.xpoints)  
	    self.minY = 0
	    self.maxY = 1
	if self.numCurves == 1:    
	    self.minX = self.xpoints[0]
	    self.maxX = self.minX + 1

	#print "plot out:: Min Max der Inputs: minX, maxX: ",self.minX, self.maxX
	#Diagrgrenzen setzen, so dass immer beide Achsen zu sehen sind
	self.testValues()  
	
	self.getSteps(self.minX, self.maxX, self.minY, self.maxY)   
	
	self.update()    # calls paintEvent
	
    #-------------------------------------------------------------------
    def paintEvent(self, event):
	# called by: plot() and  PaintWidget.__init__
	xmin = 0
	xmax = 0
	ymin = 0
	ymax = 0
	self.count += 1
	
	# get current (if stretched) geometry of outputwid
	self.dix = self.width()     # Width of mf diagramm (outputwid)
	self.diy = self.height()    # Height    "
	
	p = QtGui.QPainter()
	p.begin(self) 
	#all painter settings (setPen(), setBrush()..) 
	#are reset to default values when begin() is called.
	p.setPen(self.penDefault)
	p.setFont(self.skalaFont)
	#Hintergrund des Diagramms
	p.fillRect(0,0, self.dix, self.diy, QBrush(self.color_back))

	# Skalierungsfaktor   dix, diy Size of Diagramm 
	#print "paintEv:: dix=%d,  diy=%d ,   %d" % (
	#				self.dix, self.diy, self.count)
	#print "paintEv:: minX=%d, maxX=%d, minY=%d, maxY=%d" % (
	#			self.minX,self.maxX,self.minY,self.maxY)
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
	
	#Pfeilspitzen
	pfeilBrush = QBrush(self.color_schwarz, Qt.SolidPattern)
	p.setBrush(pfeilBrush)
	xpoints = [QPoint(xmax,-3), QPoint(xmax,3), QPoint(xmax+8,0)]
	xpfeil = QPolygon(xpoints)
	p.drawPolygon(xpfeil)
	ypoints = [QPoint(-3,ymax), QPoint(3,ymax), QPoint(0,ymax-8)]
	ypfeil = QPolygon(ypoints)
	p.drawPolygon(ypfeil)
	#----- end pfeil 
	
	ymax = int(ymax*0.97)
	#print self.vxstep	# 100
	if self.numCurves > 0:   
	    # --- x-Skala -------
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
		    #print "paintEv:: draw xAchsenScala "
		    p.drawText(int(xskala-step/2),0 ,step,25, Qt.AlignCenter, zahl) 
		num -= self.vxstep
		# X-Achsenskala
		p.drawLine(xskala,-2,xskala,+2)
		xskala -= step

	    # --- y-Skala -------
	    if (abs(ymax)>abs(ymin)):
		step = int(abs(ymax) / self.ysteps)
	    else:
		step = int(abs(ymin) / self.ysteps)
	    num = 0.0
	    yskala = 0	
	    while (yskala+step) > ymax:
		yskala -= step
		num    += self.vystep
	    #print "paintEv:: yskala=%d,  ymin=%d,  ymax=%d" % (yskala, ymin, ymax)
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
	    p.drawText(0, 20, xmax, 20, Qt.AlignRight, self.xname)

	    #Start der Darstellung der einzelnen Graphen
	    if (abs(xmax) > abs(xmin)):
		self.dx= (abs(xmax) / self.xsteps) / self.vxstep
	    else:
		self.dx= (abs(xmin) / self.xsteps) / self.vxstep
	    if (abs(ymax) > abs(ymin)):
		self.dy= (abs(ymax) / self.ysteps) / self.vystep
	    else:
		self.dy= (abs(ymin) / self.ysteps) / self.vystep

	    self.xmin = xmin
	    self.xmax = xmax
	    self.ymin = ymin
	    self.ymax = ymax
	    
	    #**************************
	    #**** start plot the graph
	    #**************************
	    p.setPen(self.penOut)
	    outn = QString()
	    for i in range(self.numCurves):
		if i == self.hit_index:
		    p.setPen(self.hitPenOut)
		else:
		    p.setPen(self.penOut)
		    
		x1 = int(self.xpoints[i] * self.dx)
		x2 = int(self.xpoints[i] *  self.dx)
		y1 = 0
		y2 = int(-0.8 * self.dy)
		p.drawLine(x1,y1,x2,y2)
		
		# draw titel on top of the line
		x1 = int(x1-(step/2.0))
		outn = QString(self.titleList[i])
		outn.truncate(8)		# only first 8 chars
		p.drawText(x1-10,y2-30,step+20,30,Qt.AlignCenter, outn)
	p.end()	

    #-------------------------------------------------------------------
    def setCorrectValues(self, maus1x, index):
	# called by: mouseMoveEv,  
	if index==0:
	    #erster Singleton
	    if maus1x > self.startPoint.x():
		#nach rechts
		if (maus1x<self.xpoints[index+1]*self.dx-5-self.ax):
		    self.xpoints[index]=(maus1x+self.ax) / self.dx
		else:
		    self.xpoints[index]=self.xpoints[index+1] - 5/self.dx
	    if maus1x < self.startPoint.x():
		#nach links
	       if (maus1x>(self.xmin-self.ax+20)):
		    self.xpoints[index]=(maus1x+self.ax) / self.dx
	       else:
		    self.xpoints[index]=(self.xmin+20) / self.dx

	if index>0 and index<(self.numCurves-1):
	    if maus1x < self.startPoint.x():
		#nach links
		if (maus1x>self.xpoints[index-1]*self.dx+5-self.ax):
		    self.xpoints[index]=(maus1x+self.ax) / self.dx
		else:
		    self.xpoints[index]=self.xpoints[index-1] + 5/self.dx
	    if maus1x > self.startPoint.x():
		#nach rechts
		if (maus1x<self.xpoints[index+1]*self.dx-5-self.ax):
		    self.xpoints[index]=(maus1x+self.ax) / self.dx
		else:
		    self.xpoints[index]=self.xpoints[index+1] - 5/self.dx

	if index == self.numCurves-1:
	    #letzter Singleton
	    if (maus1x<self.startPoint.x()):
		#nach links
		if (maus1x>self.xpoints[index-1]*self.dx+5-self.ax):
		    self.xpoints[index]=(maus1x+self.ax) / self.dx
		else:
		    self.xpoints[index]=self.xpoints[numCurves-2] + 5/self.dx

	    if (maus1x>self.startPoint.x()):
		#nach rechts
		if (maus1x < (self.xmax-20-self.ax)):
		    self.xpoints[index]=(maus1x+self.ax) / self.dx
		else:
		    self.xpoints[index]=(self.xmax-20) / self.dx
	
	if self.parent_mainwin != None:
	    msg = "%1.3f" % (float(self.xpoints[index]))
	    self.parent_mainwin.ui.statusbar.showMessage(msg)
	
    #-------------------------------------------------------------------
    def testValues(self):
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
	# called by: plot
	# alles float 

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
	    
    
    #==== MOUSE ========================================================
    
    def mousePressEvent(self, ev):
	if ev.button() == Qt.LeftButton:
	    # Linke Maustaste gedrückt: Zuerst klicken annehmen, 
	    # dragging=false, Zeitpunkt und Position merken
	    self.leftdown = True
	    self.dragging = False
	    self.startPoint = ev.pos()     
	    self.mausx = self.startPoint.x() #akt. Maus-Position
	    self.mausy = self.startPoint.y()
	    #print "mausX=%d, mausY = %d" % (self.mausx, self.mausy) 
	    for i in range(self.numCurves):     
		a = math.fabs(self.mausx-(self.xpoints[i]*self.dx-self.ax))
		if a < 5:
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
	#print "mouseMoveEv:", self.mausx, self.mausy, self.dx, self.ax, self.leftdown
	if self.leftdown == False: 
	    #nur bei gedrückter li. Taste, releaseEv set leftdown=False
	    for i in range(self.numCurves): 
		v1 = self.mausx-(self.xpoints[i]*self.dx-self.ax)
		if math.fabs(self.mausx-(self.xpoints[i]*self.dx-self.ax)) < 5:
		    self.cursor.setShape(Qt.PointingHandCursor)	# Hand Cursor
		    self.setCursor(self.cursor)
		    return
		else:
		    self.cursor.setShape(Qt.ArrowCursor)
		    self.setCursor(self.cursor)
	
	if self.dragging == False:
	    self.dragging = True
	if self.dragging == True and self.hit == True:
	    # hit_index is nr. of Curve, where HandCursor is, 
	    # set in MousePress
	    self.setCorrectValues(self.mausx, self.hit_index)
	    self.plot() 
	
    #-------------------------------------------------------------------
    def mouseReleaseEvent(self, ev):
	#print "MouseRelease xpoints=" , self.xpoints
	if self.leftdown == False or ev.button() != Qt.LeftButton:
	    return
	ev.accept()
	self.leftdown = False
	self.hit = False
	self.hit_index = -1
	self.cursor.setShape(Qt.ArrowCursor)
	self.setCursor(self.cursor)
	self.plot()   
	self.parent_mainwin.ui.statusbar.clearMessage()	
	self.parent_mainwin.actualizeOutputTable() 
	    

########################################################################
## class wird im QtDesigner in QWidget promotet
## calls the class DiagrOut
class PaintOutput(QtGui.QWidget):
    def __init__(self, parent = None):
	QtGui.QWidget.__init__(self, parent)  # init of BasicClass
	self.dia = DiagrOut(806,300)  # white DiagramBackground
	#print "PaintOutput__ init__"
	self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.dia)      
	self.setLayout(self.vbox)   
	
########################################################################


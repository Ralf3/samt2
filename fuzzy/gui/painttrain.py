#!/usr/bin/env python
# -*- coding: utf-8 -*-  
import sys
import os
import math
import timeit
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

	
class DiagrTrain(QtGui.QWidget):
    def __init__(self, u, v, parent=None ):      
	super(DiagrTrain,self).__init__()   
	#print "in super (DiagrTrain __init__, parent=", self.parent
	# called by class PaintTrain, nur nach Neustart der GUI 
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
        
	self.titleList = []    	# list of strings
        self.numOut = 0     
	self.parent_mainwin = None
	
	self.xsteps = 0
	self.ysteps = 0   	# int Anzahl steps einer Achse, schreibt getSteps()
        self.vxstep = 0.0
	self.vystep = 0.0       # float Wert am ersten Strich,  schreibt getSteps()
        self.minX = 0.0
	self.minY = 0.0
	self.maxX = 0.0
	self.maxY = 0.0    	# float Min-und Max-Werte der Inputdaten
        
	self.MIN_X = 0.01
	self.MIN_DISTANCE = 5
	
	self.minX =  999.0  #FLT_MAX
	self.maxX = -999.0  #FLT_MIN
	self.minY =  999.0  # min. Wert auf neg. Y-Achse
	self.maxY = -999.0  # max. Wert auf pos. Y-Achse
	
	self.setAttribute(QtCore.Qt.WA_StaticContents)
	
	self.color_back = QtCore.Qt.white	# backgroundcolor weiß 
	self.color_rot = QtCore.Qt.red		# hilfsline
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
	self.normFont.setWeight(25)
	self.normFont.setItalic(False)
	
	self.penDefault = QtGui.QPen()
	self.penDefault.setColor(self.color_schwarz) # alt: standard
	self.penDefault.setStyle(Qt.SolidLine)
	self.penDefault.setWidth(0)
	
	self.penOut = QtGui.QPen()
	self.penOut.setColor(self.color_schwarz)
	self.penOut.setStyle(Qt.SolidLine)
	self.penOut.setWidth(1)

	self.penTrainedOut = QtGui.QPen()
	self.penTrainedOut.setColor(self.color_rot)
	self.penTrainedOut.setStyle(Qt.SolidLine)
	self.penTrainedOut.setWidth(1)
 
        self.count = 0
	
    #-------------------------------------------------------------------
    def setLists(self, li1, li2, li3, li4, xname, mainwin):
	# called by: MyForm.btn
	self.titleList = li1
	#print "painttrain: setLists:: titleList=", self.titleList
	self.oldList = li2   		# list of strings
	self.trainedList = li3
	self.yList = li4   
	self.numOut = len(self.oldList)
	self.xname = xname
	self.parent_mainwin = mainwin
	#print "setLists:: oldList : " , self.oldList
	#print "setLists:: trainedList : " , self.trainedList
    #-------------------------------------------------------------------
    def plot(self):
	# called by init, MyForm 
	#print "painttrain:: plot()"
	if self.numOut > 0:
	    if self.oldList[self.numOut-1] < self.trainedList[self.numOut-1]:
		self.maxX = float(self.trainedList[self.numOut-1])
	    else:
		self.maxX = float(self.oldList[self.numOut-1])
	    if self.oldList[0] < self.trainedList[0]:
		self.minX = float(self.oldList[0])
	    else:
		self.minX = float(self.trainedList[0])
	else:
	    self.maxX = 10.0
	    self.minX = -1.0
	self.minY = -0.1 
	self.maxY = 1.1
	self.xname = "output"
	#Diagrenzen festlegen, so dass immer beide Achsen zu sehen sind
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
	p = QtGui.QPainter()
	p.begin(self) 	#all painter settings are default
	p.setPen(self.penDefault)
	p.setFont(self.skalaFont)
	
	# get current (if stretched) geometry of trainoutwid
	self.dix = self.width()     # Width of mf diagramm (trainoutwid)
	self.diy = self.height()    # Height    "
	
	# Hintergrund des Diagramms
	p.fillRect(0,0, self.dix, self.diy, QBrush(self.color_back))
	
	# Skalierungsfaktor   dix, diy Size of Diagramm 
	if (self.maxX == 0.0) and (self.minX == 0.0):
	    print "return:  maxX=minX"
	    return
	self.xfactor = self.dix / (self.maxX-self.minX)
	self.yfactor = self.diy / (self.minY-self.maxY)
	
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
	# neue Diagrammgrenzen
	xmin = int(xmin*0.95)
	xmax = int(xmax*0.95)
	ymin = int(ymin*0.95)
	ymax = int(ymax*0.95)
	#x-Achse
	p.drawLine(xmin,0,xmax,0)
	#y-Achse
	p.drawLine(0, ymin, 0, ymax)
	
	#--Pfeilspitzen
	pfeilBrush = QBrush(self.color_schwarz, Qt.SolidPattern)
	p.setBrush(pfeilBrush)
	xpoints = [QPoint(xmax,-3), QPoint(xmax,3), QPoint(xmax+8,0)]
	xpfeil = QPolygon(xpoints)
	p.drawPolygon(xpfeil)
	ypoints = [QPoint(-3,ymax), QPoint(3,ymax), QPoint(0,ymax-8)]
	ypfeil = QPolygon(ypoints)
	p.drawPolygon(ypfeil)
	#----end pfeil 
	
	ymax = int(ymax*0.97)
	#print self.vxstep	# 100
	if self.numOut > 0:   
	    # --- x-Skala -------
	    if (abs(xmax) > abs(xmin)):
		step = int(abs(xmax) / self.xsteps)  #Abstand der Striche
	    else:
		step = int(abs(xmin) / self.xsteps)
		#print "paintEv:: xsteps=%d, step=%d" % (self.xsteps, step)
	    xskala = 0  #int 
	    num = 0.0	
	    while (xskala+step) <= xmax:
		xskala += step
		num    += self.vxstep
		#print "paintEv:: xskala=%d,  num=%f" % (xskala, num)
	    while xskala >= xmin:
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
	    while yskala <= ymin:
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
	    outn = QString()
	    # lines for old Outputs
	    for i in range(self.numOut):
		x1 = int(float(self.oldList[i]) * self.dx)
		x2 = x1
		y1 = 0
		y2 = int(-0.9 * self.dy)
		p.setPen(self.penOut)
		p.drawLine(x1,y1,x2,y2)
		# draw titel on top of the line
		x1 = int(x1-(step/2.0))
		outn = QString(self.titleList[i])
		outn.truncate(8)		# only first 8 chars
		p.drawText(x1-10,y2-30,step+20,30,Qt.AlignCenter, outn)
	    # lines for trained Outputs
	    for i in range(self.numOut):
		x1 = int(float(self.trainedList[i]) * self.dx)
		x2 = x1
		y1 = 0
		y2 = int(-0.7 * self.dy)
		p.setPen(self.penTrainedOut)
		p.drawLine(x1,y1,x2,y2)
	p.end()	
   	
    #-------------------------------------------------------------------
    def testValues(self):
	# called by: plot
	# testet max. und min. x(y), verändert diese so, 
	# dass Achsen immer sichtbar bleiben
	
	#minX<0
	if (self.minX>=0 ):
	    h=(-0.2)* self.maxX
	    h = float(h)
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
	# called by: plot      float overall
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
	hxsteps = int(step)   		# x Schrittbreite

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
	hysteps = int(step)		# y Schrittbreite
	
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
	#print "getSteps: xsteps=%d, ysteps=%d, vxstep=%f, vystep=%f" % 
		#(self.xsteps,self.ysteps,self.vxstep,self.vystep)
    

######################################################################
## class wird im QtDesigner in QWidget promotet
## calls the class DiagrTrain
class PaintTrain(QtGui.QWidget):
    def __init__(self, parent = None):
	QtGui.QWidget.__init__(self, parent)  # init der Basisklasse
	self.dia = DiagrTrain(420,211)        # white DiagramBG
	self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.dia)      
	self.setLayout(self.vbox)   
	
########################################################################

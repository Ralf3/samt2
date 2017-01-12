#! /usr/bin/env python
# -*- coding: utf-8 -*- 
import sys
import os
import subprocess
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from helpwin_ui import Ui_helpwin


class MyHelp(QtGui.QMainWindow, Ui_helpwin):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,  parent)
        self.ui = Ui_helpwin()
        self.ui.setupUi(self)
	
	env = os.environ['SAMT2MASTER']+'/gui'
	env1 = env+'/pixmaps'
	self.setWindowIcon(QIcon(env1+'/area.png'))
	
	global fac
	if fac > 1:
	    self.resize(800*fac, 600*fac)
	    self.ui.menubar.setGeometry(QtCore.QRect(0,0,800*fac,21*fac))
	
	
	# toolbar icons
	self.ui.actionHome.setIcon(QIcon(env1+'/home.png'))
	self.ui.actionSpacer.setIcon(QIcon(env1+'/spacer.png'))
	self.ui.actionBack.setIcon(QIcon(env1+'/back.png'))
	self.ui.actionForward.setIcon(QIcon(env1+'/rechts.png'))
	self.ui.actionTop.setIcon(QIcon(env1+'/top.png'))
	
	# connections
	self.connect(self.ui.actionHome, SIGNAL('triggered()'), 
			self.slotGo_Home)
	self.connect(self.ui.actionBack, SIGNAL('triggered()'), 
			self.slotGo_Back)
	self.connect(self.ui.actionForward, SIGNAL('triggered()'), 
			self.slotGo_Forward)
	self.connect(self.ui.actionTop, SIGNAL('triggered()'), 
			self.slotGo_Top)
	
	# open the first html site
	path = env+'/html/index.html'
	self.ui.textBrowser.setSource(QUrl(path))     
	
	# make external links possible
	self.ui.textBrowser.setOpenExternalLinks(True)
	# like:  <a href='http://www.zalf.de'> www.zalf.de</a>
    

    #-------------------------------------------------------------------
    def slotGo_Home(self):
	self.ui.textBrowser.home()
	
    def slotGo_Back(self):
	self.ui.textBrowser.backward()
	
    def slotGo_Forward(self):
	self.ui.textBrowser.forward()
	
    def slotGo_Top(self):
	self.ui.textBrowser.reload()


#######################################################
	
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    
    # scale factor for current monitor resolution (QDesktopWidget)
    screen_resolution = app.desktop().screenGeometry()
    w, h = screen_resolution.width(), screen_resolution.height()
    if w <= 1920 and h <= 1200:  # monitor 24'' hat 1920x1200
		fac = 1.0
    else:
		fac = float(h/1200.0)     # w/1920.0
    print "Monitor width, height, fac", w, h, fac
    
    window = MyHelp()      
    window.show()
    sys.exit(app.exec_())

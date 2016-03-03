#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import sys
import os
sys.path.append(os.environ['SAMT2MASTER']+"/src")       
import grid
sys.path.append(os.environ['SAMT2MASTER']+"/fuzzy/src")
import Pyfuzzy
from Pyfuzzy import read_model 
from Pyfuzzy import start_training

import numpy as np
import pylab as plt
import scipy.ndimage
import re
import string
import copy
import timeit
import math

class worker:
    def __init__(self):
	self.fx = None		# used by add_model_fuz()
	self.mx = None
	self.d_fuzz = {}	# dictionary {modelname: fx}
	self.d_fuzz_type = {0: 'triangular', 1: 'trapeze', 2: 'left', 3: 'right'}
	self.d_fuzz_flag = {'triangular': 0, 'trapeze':1, 'left':2, 'right':3}
	
	self.fx_neu = None	# used by Pages Analysis, Calc, Training 
	self.ip_neu = None
	self.memb_neu = None
	self.out_neu = None
	self.rule_neu = None
	
	self.fx_old = None
    
    #-------------------------------------------------------------------
    def create_fx_neu(self, modelname):
	# called by: fill_input_lists_for_new_fuz()
	self.fx_neu = Pyfuzzy.fuzzy()
	self.fx_neu.set_name(str(modelname))
	
    #-------------------------------------------------------------------
    def refresh_fx(self):
	# called by: switchTab idx=3 Analyse
	if self.fx_neu == None:
	    print "fx_neu is None - Abort"
	    return
	# new fuzzy model with edited inp, outp, rules
	self.fx = self.fx_neu 

	self.ip_neu = None
	self.memb_neu = None
	self.out_neu = None
	self.rule_neu = None
	
    #-------------------------------------------------------------------
    def get_outputval(self, outp_idx):
	val = self.fx.get_output(outp_idx)
	return val
	
    #-------------------------------------------------------------------
    def get_mx_inp1(self,xgrids,ygrids,xmi,xma):
	# called by: showAnalyse: anz_inp == 1
	x = np.linspace(xmi, xma, xgrids) 
	li_y = []
	for j in range(xgrids):
	    y = self.fx.calc1(x[j]) 
	    li_y.append(y)
	    #self.mx[0,j] = y	# ??????????????
	    
	#self.fx.store_model("file_kontrol_get_mx.fis")  
	mi = min(li_y)   
	ma = max(li_y)   
	li_retu = []
	li_retu.append(li_y)  
	li_retu.append(mi)
	li_retu.append(ma)
	li_retu.append(x)	
	return li_retu

    #-------------------------------------------------------------------
    def get_mx(self,anz_inp, xgrids,ygrids,index0,index1,index2,
		in3const,xmi,xma,ymi,yma):
	# called by: showAnalyse:  anz_inp > 1
	#start = timeit.default_timer()  # Timer Start
	
	li_retu = []
	self.mx = np.zeros((ygrids, xgrids))
	if self.fx == None:
	    return li_retu
	x = np.linspace(xmi, xma, xgrids) 
	y = np.linspace(yma, ymi, ygrids)
	if anz_inp == 1:
	    for j in xrange(xgrids):
		self.mx[0,j] = self.fx.calc1(x[j])  #, y[i]) 
	    
	elif anz_inp == 2:
	    #print "work:get_mx:: index0=%d, index1=%d" % (index0, index1)
	    if index0==0 and index1==1:
		for i in xrange(ygrids):
		    for j in xrange(xgrids):
			self.mx[i,j] = self.fx.calc2(x[j], y[i]) 
	    elif index0==1 and index1==0:
		for i in xrange(ygrids):
		    for j in xrange(xgrids):
			self.mx[i,j] = self.fx.calc2(y[i], x[j])  
	    
	elif anz_inp == 3:
	    #print "work:get_mx:: index0=%d, index1=%d, index2=%d" % (index0,index1,index2)
	    for i in xrange(ygrids):
		for j in xrange(xgrids):
		    if index0 == 0:
			if index1 == 1:
			    self.mx[i,j] = self.fx.calc3(x[j],y[i],in3const)
			    continue
			elif index1 == 2:
			    self.mx[i,j] = self.fx.calc3(x[j],in3const,y[i])
			    continue
		    elif index0 == 1:
			if index1 == 0:
			    self.mx[i,j] = self.fx.calc3(y[i],x[j],in3const)
			elif  index1 == 2:
			    self.mx[i,j] = self.fx.calc3(in3const,x[j],y[i])
		    elif index0 == 2:
			if index1 == 0:
			     self.mx[i,j] = self.fx.calc3(y[i],in3const,x[j])
			elif index1 == 1:
			    self.mx[i,j] = self.fx.calc3(in3const,y[i],x[j])

	#dauer = timeit.default_timer() - start    # TimerEnd
	#print "work::get_mx: fx.calc dauer [sec]: ", dauer 

	mxmi = np.min(self.mx)
	mxma = np.max(self.mx)
	a = 0.2 * mxma
	b = 0.8 * mxma
	if mxma == 0.0:
	    a = 0.2 * mxmi
	    b = 0.8 * mxmi
	li_contour = np.linspace(a, b, 4)
	
	li_retu.append(self.mx)
	li_retu.append(mxmi)
	li_retu.append(mxma)
	li_retu.append(li_contour)
	return li_retu

    #-------------------------------------------------------------------
    def get_name_of_input(self, modelname, idx):
	# idx: 0, 1, 2
	fx = self.d_fuzz[modelname]		
	name = fx.get_input_name(idx)
	return name
	
    #-------------------------------------------------------------------
    def get_mx_transect(self,i0,j0,i1,j1):
	# called by: draw_line_end
	# nur linie abarbeiten und alle z-vals holen
	# von startPoint bis endPoint
	# oberer linker Eckpunkt einer matrix ist immer [col=0,row=0] 
	nrows = self.mx.shape[0]	# = ygrids	
	ncols = self.mx.shape[1]	# = xgrids
	if i0<0 or j0<0 or i1>=nrows or j1>= ncols:
	    print "get_mx_transect- Abort"
            return None,None
	linelaenge = int(np.sqrt(((i1-i0)*(i1-i0)) + ((j1-j0)*(j1-j0))))
	
	x = np.linspace(j0, j1, linelaenge) 
	y = np.linspace(i0, i1, linelaenge)
	
	z = scipy.ndimage.map_coordinates(np.transpose(self.mx), 
					np.vstack((x,y)),order=1)
	t = np.arange(len(z))
        return z, t    

    #-------------------------------------------------------------------
    def get_mx_val(self, y, x):
	# called by: all mouseEvents 
	return self.mx[y,x]
    
    #-------------------------------------------------------------------
    def set_flag_inter(self, v):
	# call by: btn_calc_fuzzy
	self.fx.set_flag(int(v))
 
    #-------------------------------------------------------------------
    def get_calc1(self, x1):
	# called by: btn_calc_fuzzy, 1 input
	retu = self.fx.calc1(x1)
	return retu
	
    #-------------------------------------------------------------------
    def get_calc2(self, x1, x2):
	# called by: btn_calc_fuzzy, 2 inputs
	retu = self.fx.calc2(x1,x2)
	return retu
    
    #-------------------------------------------------------------------
    def get_calc3(self, x1, x2, x3):
	# called by: btn_calc_fuzzy, 3 inputs
	retu = self.fx.calc3(x1,x2,x3)
	return retu
	
    #-------------------------------------------------------------------
    def get_calct1(self, X):
	# called by: on_release mouse
	retu= self.fx.calct1(X)
	return retu,self.fx.ruleList,self.fx.muList, self.fx.outputList

    #-------------------------------------------------------------------
    def get_calct2(self, X,Y):
	# called by: on_release mouse
	retu= self.fx.calct2(X,Y)
	return retu, self.fx.ruleList,self.fx.muList, self.fx.outputList
    
    #-------------------------------------------------------------------
    def get_calct3(self,X,Y,in3const):
	# called by: on_release mouse
	retu= self.fx.calct3(X,Y,in3const)
	return retu, self.fx.ruleList,self.fx.muList, self.fx.outputList
    
    #-------------------------------------------------------------------
    def get_min_inp(self, i):
	# called by: combinate_input_combos
	# i: idx of input (0 or 1 or 2)
	# lo: left oben value
	lo = self.fx.get_min_input(i)  # fx_neu
	return lo    
    
    #-------------------------------------------------------------------
    def get_max_inp(self, i):
	# called by: combinate_input_combos
	# i: idx of input (0 or 1 or 2)
	# ro: right oben value
	ro = self.fx.get_max_input(i)  # fx_neu
	return ro 
    
    #-------------------------------------------------------------------
    def model_file_store(self, filename):
	# called by: fileSave
	if self.fx == None:
	    print "work.model_file_save:: self.fx not exists"
	    return False
   
	if self.fx.store_model(filename) == True:
	    return True
	else:
	    return False
	    
    #-------------------------------------------------------------------
    def fill_new_fuz_with_inputs(self, mfRangeList, mfTitleList, 
					mfTypeList, inputname, anz1): 
	# called by: switchTab=3,4,5,6 --> fill_input_lists, 
	# only for ONE input with inputname 
	li_range = mfRangeList		
	li_title = mfTitleList
	li_type = mfTypeList
	anz_inp = anz1
	inam = inputname     
	
	self.ip_neu = Pyfuzzy.input(inam)  # new input
	
	for j in range(len(li_range)):
	    li_xval = []
	    mname = li_title[j]
	    mtyp = li_type[j]	# 'left',...
	    typflag = self.d_fuzz_flag[mtyp]
	    for v in li_range[j]:
		li_xval.append(round(float(v), 3)) 
	    
	    # Sonderfall:  if mtyp = "left" 
	    # dann li_xval[0] u. li_xval[1] löschen
	    # damit in member.init: 0.Wert=self.ro und 1.Wert=self.ru 
	    if mtyp=="left":
		del li_xval[0:2]
	    
	    # muss self.memb_neu geleert werden???
	    self.memb_neu = Pyfuzzy.member(mname,typflag,li_xval) # new member
	    
	    # dem input-obj hinzufügen
	    self.ip_neu.set_member(mname,mtyp,li_xval)
	
	self.fx_neu.add_input(self.ip_neu)	
	anz = self.ip_neu.get_len()
	n = self.ip_neu.get_n()

    #-------------------------------------------------------------------
    def fill_new_fuz_with_outputs(self, oname, outputTitleList, xOut):
	# called by: switchTabs 3=Analysis, 4=Calc, 5=Training, 6
	anz_out = len(outputTitleList)
	for j in range(anz_out):
	    onamj = outputTitleList[j]
	    oval = round(xOut[j], 3)
	    self.out_neu = Pyfuzzy.output(onamj,oval)
	    self.fx_neu.add_output(self.out_neu)
	self.fx_neu.set_oname(oname)
		
    #-------------------------------------------------------------------
    def fill_new_fuz_with_rules(self, rulesList):
	# called by: switchTabs 3=Analysis, 4=Calc, 5=Training, 6
	for li_one_rule in rulesList:
	    self.rule_neu = Pyfuzzy.rule(li_one_rule)  # new rule
	    self.fx_neu.add_rule(self.rule_neu)
    
    #-------------------------------------------------------------------
    def add_model_fuz(self, filename, modelname):
	"""	called from: fileOpen
		adds a new model from filesystem  (.fis) with:
	in:	filename incl. path     str
		modelname		str 
	out:	name of the new model or None
		model_new		str
	if model_name is already in dict self.d_fuz then:
	add a 1 to the name to make it unique """
	modelname_new = modelname
        while(modelname_new in self.d_fuzz):
            modelname_new += "1"
	    
	self.fx =  Pyfuzzy.read_model(filename, DEBUG=1)

	#~ for i in range(len(self.fx.inputs)):
	    #~ for li in self.fx.inputs[i]:
		#~ for j in range(len(li)):
		    #~ print "self.fx.inputs:: ", self.fx.inputs[i][j]	
	
	li_inp = self.fx.get_inputs()
	for i in range(len(li_inp)):
	    li_memb = self.get_members_of_input(li_inp[i])
	
	self.d_fuzz[modelname_new] = self.fx
	return modelname_new   # fx only for inside of class worker 
        
    #-------------------------------------------------------------------
    def get_members_of_input(self, one_input):
	# called by: fileOpen
    	inp = one_input
	anz_memb = inp.get_len()
	li_memb = []
	for j in range(anz_memb):
	    li = []
	    m = inp.get_member(j)    # one member-object
	    flag = m.get_flag()
	    flagg = self.flag2type(flag)
	    lu = "%.3f" % m.get_lu()
	    li.append(lu)
	    lo = "%.3f" % m.get_lo()
	    li.append(lo)

	    # if trianular: dummy ro = lo  
	    ro = "%.3f" % m.get_ro()
	    li.append(ro)
	    ru = "%.3f" % m.get_ru()
	    li.append(ru)
	    li.append(flagg)
	    name = m.get_name()
	    li.append(name)
	    li_memb.append(li)
	return li_memb	
    
    #-------------------------------------------------------------------
    def get_lists_in_out_rule(self, modelname):
	# called by: fileOpen
	fx = self.d_fuzz[modelname]
	li_inp = fx.get_inputs()
	li_outp = fx.get_outputs()
	li_rule = fx.get_rules()
	return li_inp, li_outp, li_rule
    
    #-------------------------------------------------------------------
    def get_inpu(self):
	# called by: isModelComplete()
	return self.fx.get_inputs() 	# list of input_objects
    
    #-------------------------------------------------------------------
    def get_name_of_output(self):
	return self.fx.get_output_name()	
    
    #-------------------------------------------------------------------
    def get_outp_name_singleton(self, o):
	return o.get_name()
    
    #-------------------------------------------------------------------
    def get_outp_val(self, o):
	return o.getv()
	
    #-------------------------------------------------------------------
    def get_rule(self, r):
	# called by: fileOpen
	return r.get_rule()  # tupel: (in1,in2,in3,outp,cf)
    
    #-------------------------------------------------------------------
    def get_outputs(self):
	return self.fx.get_outputs()	# list of output_objects
    
    #-------------------------------------------------------------------
    def get_len_outp(self):
	# called by: isModelComplete()
	return self.fx.get_len_output()
	
    #-------------------------------------------------------------------
    def flag2type(self, flag):
	return self.d_fuzz_type[flag]
	
    #-------------------------------------------------------------------
    def read_train_data(self, fname, anz, separator):
	# called by: btn_trainStart
	# retu: X_list, Y_list or False
	return self.fx.read_training_data(fname,header=anz,sep=separator)
    
    #-------------------------------------------------------------------
    def get_rms(self):
	return self.fx.get_rmse()
	
    #-------------------------------------------------------------------
    def train_start(self):
	# called by: btn_trainStart
	Pyfuzzy.start_training(self.fx)

    #-------------------------------------------------------------------
    def train_rules_start(self, alpha):
	# called by: btn_start_rulesTrain
	yesno = self.fx.train_rules(alpha=alpha)
	return yesno
	
    #-------------------------------------------------------------------
    def get_outp_rules_list(self):
	# called by: btn_start_rulesTrain, refresh_rulesTable
	li_outp = self.fx.get_outputs()
	li_rules = self.fx.get_rules()
	return li_outp, li_rules
    
    #-------------------------------------------------------------------
    def get_mf_name(self, inpidx, mfidx):
	# called by: fill_ifthenList
	return self.fx.inputs[inpidx].member[mfidx].get_name()
   
    #-------------------------------------------------------------------
    def rett_fx(self):
	self.fx_old = copy.copy(self.fx)
    
    #-------------------------------------------------------------------
    def restore_fx_old(self):
	# fx has trained rules inside, discard this rules
	# overwrite fx with fx_old
	self.fx = self.fx_old

    #-------------------------------------------------------------------
    def delete_retted_fx(self):
	# called by: btn_rules_save
	self.fx_old = None	

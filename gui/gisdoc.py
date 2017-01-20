#!/usr/bin/env python
# -*- coding: utf-8 -*- 
  
import sys
import os
sys.path.append(os.environ['SAMT2MASTER']+'/src')
import grid
sys.path.append(os.environ['SAMT2MASTER']+'/fuzzy/src')
import Pyfuzzy 
sys.path.append(os.environ['SAMT2MASTER']+'/svm')
import svm_mod as sx
import numpy as np
import pylab as plt
import re
import string

from grid import copy_grid
from grid import create_zoom
from grid import sample
from Pyfuzzy import read_model
from osm_object import create_map


class gisdoc:
    def __init__(self):
        self.d_grids = {}
	self.d_points = {}  # write in: add_points, set_d_points, 
	self.d_models_fuz = {}
	self.d_models_svm = {}

    #-------------------------------------------------------------------
    def get_list_grids(self, hdf_name):
	"""
	   in:	hdf  str
	   out: list of all grids in hdf
	   call from slotHDF_Open_All
	"""
	gx = grid.grid()
	return gx.list_hdf(hdf_name)   

    #-------------------------------------------------------------------
    def get_d_grids(self):
	return self.d_grids
    
    #-------------------------------------------------------------------
    def get_d_grids_val(self, key):
	return self.d_grids[key]
	
    #-------------------------------------------------------------------
    def get_d_points(self, key):
	return self.d_points[key]
    
    #-------------------------------------------------------------------
    def get_d_models_fuz(self, key):
	if key in self.d_models_fuz:
	    return self.d_models_fuz[key]
	else:
	    return None
    
    #-------------------------------------------------------------------
    def get_d_models_svm(self, key):
	if key in self.d_models_svm:
	    return self.d_models_svm[key]
	else:
	    return None
    
    #-------------------------------------------------------------------
    def set_d_points(self, key, liz):
	# call from start.py:set_d_poi_new_z(liz)
	print "set_d_points"
	#del self.d_points[key][4]   # later in tuple delete no possible
	li = self.d_points[key]
	li1 = li[0]
	li2 = li[1]
	li3 = li[2]
	li4 = li[3]
	li_neu = []
	li_neu.append(li1)
	li_neu.append(li2)
	li_neu.append(li3)
	li_neu.append(li4)
	li_neu.append(liz)
	
	del self.d_points[str(key)]
	
	self.d_points[key] = li_neu
	print "----- gisdoc.d_points:"
	print self.d_points[key]    # ok
	
    #-------------------------------------------------------------------
    def del_d_grids_key(self, key):
	""" delete key-value pair from dict """
	#print "del_d_grids: vorm loeschen:", self.d_grids.keys()
	if key in self.d_grids:
	    del self.d_grids[key]
	    return True
	else:
	    print "g key not found"
	    return False
	    
    #-------------------------------------------------------------------
    def del_d_points_key(self, key):
	""" delete key-value pair from dict """
	if key in self.d_points:
	    del self.d_points[key]
	    return True
	else:
	    print "p key not found"
	    return False
    
    #-------------------------------------------------------------------
    def del_d_models_key(self, key, kind):
	""" delete key-value pair from dict """
	#print "del_d_models: vorm loeschen:", self.d_models.keys()
	
	if kind == "fuzzy":
	    if key in self.d_models_fuz:
		del self.d_models_fuz[key]
		return True
	    else:
		print "model for delete was not found"
		return False
	else:
	    if key in self.d_models_svm:
		del self.d_models_svm[key]
		return True
	    else:
		print "model for delete was not found"
		return False
    
    #-------------------------------------------------------------------
    def grid_copy(self, gname1, gname2):
	"""
	    in:		gname1	str
			gname2	str
	    out:	name of the copied grid
			gname_new	str
	"""
	gx = self.d_grids[gname1]
	if gx is None:
	    return False
	ga = copy_grid(gx)
	gname_new = self.add_grid(gname2, ga)
	return gname_new   
	
    #-------------------------------------------------------------------
    #~ def grid_copy_model_out(self, gx, modelname):
	#~ """
	    #~ in:		gx  output grid from run_model()
			#~ modelname	str
	    #~ out:	name of the copied grid  str
	#~ """
	#~ #ga = copy_grid(gx)
	#~ gname_new = self.add_grid(modelname, gx)
	#~ return gname_new  
    
    #-------------------------------------------------------------------
    def grid_rename(self, gname1, gname2):
	"""
	    in:		gname1		str
			gname2		str
	    out:	new grid name
			gname_new	str
	""" 
	gx = self.d_grids[gname1]
	if gx is None:
	    return False
	del self.d_grids[gname1]      
	gname_new = self.add_grid(gname2, gx)   
	#print self.d_grids.keys()
	return gname_new      

    #-------------------------------------------------------------------
    def add_grid(self, grid_name, grid):
	"""
	    adds a new grid from a hdf filesystem with:
	    in:		grid_name  	str
			grid	      	grid
	    out:	name of the new grid
			gname_new	str
	    if grid_name is already in the dict self.d_grids then:
	    add a 1 to the gname_new to make it unique
	    result: add the grid in self.d_grids
        """
	gname_new = grid_name
        while(gname_new in self.d_grids):
            gname_new += "1"
	self.d_grids[gname_new] = grid
	return gname_new	
    
    #-------------------------------------------------------------------
    def add_hdf(self, hdf_name, dataset_name):
        """a
	    adds a new grid from a hdf filesystem with:
	    in:		hdf_name
			dataset_name
	    out:	name of the new grid  or False
			dataset_new	str
	    if dataset_name is already in the dict self.d_grids then:
	    add a 1 to the name to make it unique
	    result: add the grid in self.d_grids
        """
        dataset_new = dataset_name
        while(dataset_new in self.d_grids):
            dataset_new += "1"
        gx = grid.grid()
        if gx.read_hdf(hdf_name, dataset_name) == True:
            self.d_grids[dataset_new] = gx
	    return dataset_new
	else:
	    return None
	    
    #-------------------------------------------------------------------
    def add_ascii(self, filename, ascii_name):
	"""
	    adds a new grid from filesystem  (.asc) with:
	    in:		filename incl. path     str
			ascii_name		str 
	    out:	name of the new grid or None
			dataset_new		str
	    if dataset_name is already in the dict self.d_grids then:
	    add a 1 to the name to make it unique
	    result: add the grid in self.d_grids
        """
	dataset_new = ascii_name
        while(dataset_new in self.d_grids):
            dataset_new += "1"
        gx = grid.grid()
        if gx.read_ascii(filename) == True:
            self.d_grids[dataset_new] = gx
	    return dataset_new
	else:
	    print "error: ascii-filename not found"
	    return None
	    
    #-------------------------------------------------------------------
    def save_hdf(self, filename,dataset,modell,bemerk,gridname):    
	"""
	    save a grid into hdf file 
	    in:		filename incl. path     str
			dataset	(Input P1)	str 
			modell (Input P2)	str
			bemerk (Input P3)	str
			gridname 		str
	    out:	saved file

        """
	gx = self.d_grids[gridname]
	if gx is None: 
	    return False
	return gx.write_hdf(filename, dataset, modell, bemerk)
	
    #-------------------------------------------------------------------
    def save_ascii(self, filename, gridname):
	"""
	    stores a ascii file and the header as export to the GIS 
	    in:		filename incl. path     str
			gridname 		str
	    out:	ascii file 
        """
	gx = self.d_grids[gridname]
	if gx is None: 
	    return False
	return gx.write_ascii(filename)
	
    #-------------------------------------------------------------------
    def add_points(self,gridname,pname,li1,li2,liz,art):
	"""
	    call from start.py: slotHDF_Open, ..ASCII_Open, slotSample
	    adds new points from filesystem  (.csv) with:
	    in:		gridname		str
			pname			str
			li1, li2, liz		lists
			art (ij or yx)		str
	    out:	name of the new dataset or None
			dataset_new		str
	    if dataset_name is already in the dict self.d_points then:
	    add a '1' to the name to make it unique
	    result: add pointsthema to self.d_points
        """
	print "add_points gname=%s  pname=%s" %(gridname,pname)
	
	gx = self.d_grids[gridname]
	if gx is None: 
	    print "error gx"
	    return None
	pname_new = pname
        while(pname_new in self.d_points):
            pname_new += "1"
	if art == 'yx':
	    a_3, a_4 = gx.transform_to_ij(li1, li2)  # y,x
	    # np.array ohne comma --> py_list, comma separated
	    if a_3 is None:
		print "err a_3"
		return None, None, None
	    else:
		li3 = a_3.tolist()  # i
		li4 = a_4.tolist()  # j
		self.d_points[pname_new] = li1, li2, li3, li4, liz # y,x,i,j,z
	else:
	    a_3, a_4 = gx.transform_from_ij(li1, li2)  #y,x
	    if a_3 is None:
		print "err a_3"
		return None, None, None
	    else:
		li3 = a_3.tolist()
		li4 = a_4.tolist() 
		self.d_points[pname_new] = li3, li4, li1, li2, liz  # y,x,i,j,z
	#print "add_points: d_points:"
	#print self.d_points[pname_new]
	return li3, li4, pname_new
	
    
    ####################################################################
    #######   MODEL 
    ####################################################################
    
    #-------------------------------------------------------------------
    def add_model_svm(self, filename, svmname):
	"""
	# called by: slotSVM_Open
	"""
	fname = filename.strip()
	ds_new = svmname
        while((ds_new in self.d_models_svm) or (ds_new in self.d_models_fuz)):
            ds_new += "1"

	#~ self.test()
	#~ return
 
	model = sx.svm()
	if model.read_model(fname) == True:
	    self.d_models_svm[ds_new] = model
	    print self.d_models_svm.items()
	    return ds_new   
	else:
	    return None
	    
    #-------------------------------------------------------------------
    def get_svm_name(self, modelname):
	# called by: slotTREE_Clicked : model
	sx = self.d_models_svm[modelname]
	if sx is None: 
	    return False
	li = sx.names   	# list of max 3 names   
	return li
	
    #-------------------------------------------------------------------
    #~ def test(self):	# unused
	#~ bd=grid.grid()
	#~ struktur=grid.grid()
	#~ nahr=grid.grid()
	#~ # load the grids
	#~ bd.read_hdf('schreiadler_all.h5','bd_all')
	#~ struktur.read_hdf('schreiadler_all.h5','struktur')
	#~ nahr.read_hdf('schreiadler_all.h5','nahr_schreiadler')
	# draw a sample of a size of 2000
	#~ X,Y=grid.sample(g1=bd,g2=struktur,g4=nahr,n=2000,filename='s_nahr.csv')
	#~ X=np.array(X)
	#~ Y=np.array(Y)
	#~ print X.shape, Y.shape
	#~ model= sx.svm('bd','struktur')
	#~ model.def_model()
	#~ model.train(X,Y)
#~ 
	#~ bias,rsme,r2=model.test(X,Y)
	#~ print 'Bias=', bias, 'RSME=', rsme, 'R^2=', r2
#~ 
	#~ model.write_model('/media/karing/work/samt2/model/svm/xxx.svm')
	#~ del model
	#~ model=sx.svm()
	#~ model.read_model('/media/karing/work/samt2/model/svm/xxx.svm')
	#~ print 'after read:', model.get_names()

    #-------------------------------------------------------------------    
    def add_model_fuz(self, filename, modelname):
	"""
	    adds a new model from filesystem  (.fis) with:
	    in:		filename incl. path     str
			modelname		str 
	    out:	name of the new model or None
			dataset_new		str
	    if dataset_name is already in dict self.d_models_fuz then:
	    add a 1 to the name to make it unique
	    result: add the model in self.d_models_fuz an in TREE
        """
	ds_new = modelname
        #while(ds_new in self.d_models_fuz):
	while((ds_new in self.d_models_svm) or (ds_new in self.d_models_fuz)):
            ds_new += "1"
	fx =  Pyfuzzy.read_model(filename)
	self.d_models_fuz[ds_new] = fx
	#print self.d_models_fuz.items()
	return ds_new

    #-------------------------------------------------------------------
    def get_nr_fuz_inputs(self, modelname):
	f1 = self.d_models_fuz[modelname]
	if f1 is None: 
	    return False
	nr = f1.get_number_of_inputs()
	return nr
    
    #------------------------------------------------------------------- 
    def get_name_fuz_input(self, modelname, anz_inp):
	f1 = self.d_models_fuz[modelname]
	if f1 is None: 
	    return None
	li = []	
	for i in range(anz_inp):
	    name = f1.get_input_name(i) 
	    if name is None:
		print "error get_input_name"
		return None
	    li.append(name)
	return li
    
    #------------------------------------------------------------------- 
    def get_name_fuz_output(self, modelname):
	# called by: Fuzzy_Analysis
	f1 = self.d_models_fuz[modelname]
	if f1 is None: 
	    return None
	return f1.get_output_name()
	  
    #-------------------------------------------------------------------
    def run_model(self, modelname, model_kind, n, v1, v2=None, v3=None):
	# called by: slotRun_Model()
	#print "gdoc.run_model : %s / anz inputs= %d" % (modelname,n)
	anza = 0
	if v1 is not None:
	    g1 = self.d_grids[v1]
	    if g1 is None: 
		print "error  run_model: g1"
		return None
	    anza = 1
	if v2 is not None:
	    g2 = self.d_grids[v2]
	    if g2 is None: 
		print "error  run_model: g2"
		return None
	    anza = 2
	if v3 is not None:
	    g3 = self.d_grids[v3]
	    if g3 is None: 
		print "error  run_model: g3"
		return None
	    anza = 3
	if anza != n:
	    print "not all grids found"
	    return None
	
	# start calc  
	if model_kind == "fuzzy":
	    fx = self.d_models_fuz[modelname]
	    if n == 1:
	       return fx.grid_calc1(g1) 
	    elif n == 2:
		return fx.grid_calc2(g1, g2)
	    elif n == 3:
		retu = fx.grid_calc3(g1, g2, g3)
		return retu  # gx
	    return None         
	
	elif model_kind =="svm":
	    sx = self.d_models_svm[modelname]
	    if n == 1:
	       return sx.calc(g1)
	    elif n == 2:
		return sx.calc(g1, g2)
	    elif n == 3:
		print "gisdoc:: run_model : calc 3 grids"
		retu = sx.calc(g1, g2, g3)
		return retu  # gx or None
	    return None   
	    
    #-------------------------------------------------------------------
    def get_expr_gout(self, expr, g1, g2=None, g3=None):
	ctr = 0
	if g1 is not None:
	    g1.set_nan()
	    a = 'g1'+'.get_matp()'
	    ctr += 1
	    if g2 is not None:
		g2.set_nan()
		b = 'g2'+'.get_matp()'
		ctr += 1
		if g3 is not None:
		    g3.set_nan()
		    c = 'g3'+'.get_matp()'
		    ctr += 1
	if ctr == 0:
	    print "gdoc.get_expr_gout error"
	    return None
	# Formel, die ausgefuehrt werden soll
	s = expr
	# Sample: 
	# s = 'a_+50*b_*np.sin(c_+2.0)' 
	# --> g1.get_matp()+50*g2.get_matp()*np.sin(g3.get_matp()+2.0)
	
	s = re.sub('a_',a,s)
	if ctr == 2:
	    s = re.sub('b_',b,s)
	if ctr == 3:
	    s = re.sub('b_',b,s)
	    s = re.sub('c_',c,s)
	print "m = eval(%s) " % s
	try:
	    m = eval(s)
	except:
	    print "error in eval(expr)" 
	    g1.reset_nan()
	    if ctr == 2:
		g2.reset_nan()
		if ctr == 3:
		    g3.reset_nan()
	    return None
	g1.reset_nan()
	if ctr == 2:
	    g2.reset_nan()
	    if ctr == 3:
		g3.reset_nan()
	gout = copy_grid(g1)
	gout.set_mat(m)
	gout.reset_nan()	
	return gout   
    
	
    
    ####################################################################
    #####   Analysis
    ####################################################################
    
    def get_corr(self, gridname, g1):
	"""
	    in:	        g1  gridname  str
	    out:	corrcoef
	    calculates the correlation between two grids
	"""
	gx = self.d_grids[gridname]
	if gx is None: 
	    return False
	g2 = self.d_grids[g1]
	if g2 is None: 
	    return False
	return gx.corr(g2) 
    
    #-------------------------------------------------------------------  
    def get_entropy(self, gridname):
	# the shannon entropy
	gx = self.d_grids[gridname]
	if gx is None: 
	    return False
	return gx.shannon()
    
    #-------------------------------------------------------------------  
    def get_entropy_s(self, gridname, nr=30):
	""" nr: integer, number of bins in histogram	"""
	gx = self.d_grids[gridname]
	if gx is None: 
	    return False
	return gx.shannons(nr=nr)
    
    #-------------------------------------------------------------------  
    def get_complexity(self, gridname, nr=30, dis=0):
	""" nr: int, number of bins in histogram
	   dis: int, distribution=0, Histogramm=1 unique()	"""
	gx = self.d_grids[gridname]
	if gx is None: 
	    return False
	return gx.complexity(nr=int(nr), dis=int(dis))
    
    #-------------------------------------------------------------------  
    def get_majorization(self, gridname, grid1_name, nr=10, dis=0):
	gx = self.d_grids[gridname]
	if gx is None: 
	    return False
	g1 = self.d_grids[grid1_name]
	if g1 is None: 
	    return False
	return gx.majorization(g1, nr=nr, dis=0)
    
    #-------------------------------------------------------------------
    def sample(self, gridname, nr):
        """ 
	    in:		nr  int
	    out:	3 arrays  i,j,z  
	    very fast version now, uses: np.random.shuffle
        """
	gx = self.d_grids[gridname]
	if gx is None: 
	    return None, None, None
	return gx.sample(nr)   # y,x,z
    
    #-------------------------------------------------------------------
    def sample_p(self, gridname, v1, v2):
	# suche points in map, wo z > v
	# in:	v1: Anzahl Koordinaten int
	
	# 	v2: z-Schwellwert float	
	gx = self.d_grids[gridname]
	if gx is None: 
	    return None, None, None
	return gx.sample_p(v1, v2)   # y,x,z
		
    #-------------------------------------------------------------------
    def sample_det(self, gridname, val):
        """ 
	    in:		val  float
	    out:	2 arrays  i,j 
        """
	gx = self.d_grids[gridname]
	if gx is None: 
	    return None, None
	return gx.sample_det(val)   # y,x
	
    #-------------------------------------------------------------------
    def sample_export_R (self,anzgrids,fname,vx,v1,v2=None,v3=None):
	#print "sample_export_R: anzgrids=%d, vx=%s,v1=%s,v2=%s,v3=%s"
					    #% (anzgrids,vx,v1,v2,v3)
	g2 = None
	g3 = None
	gx = self.d_grids[vx]	# Pflicht
	if gx is None: 
	    return None, None
	g1 = self.d_grids[v1]	# Pflicht
	if g1 is None: 
	    return None, None
	n = 2000
	anz = int(anzgrids)
	if anz == 2:
	    res, resy = sample(g1,g4=gx,n=n,filename=fname,x1=v1,x4=vx) 
	elif anz == 3:
	    if v2 is not None:		
		g2 = self.d_grids[v2]
		if g2 is not None: 
		    return None, None
		res, resy = sample(g1,g4=gx,g2=g2,n=n,
				    filename=fname,x1=v1,x2=v2,x4=vx) 
	elif anz == 4:
	    if v2 is not None:		
		g2 = self.d_grids[v2]
		if g2 is None: 
		    return None, None
	    if v3 is not None:		
		g3 = self.d_grids[v3]
		if g3 is None: 
		    return None, None
		res, resy = sample(g1,g4=gx,g2=g2,g3=g3,n=n,
			    filename=fname,x1=v1,x2=v2,x3=v3,x4=vx) 
	return res, resy
    #-------------------------------------------------------------------
    
    
    ####################################################################
    #####   Simple_Grid
    ####################################################################
    
    #------ 12.5.2016 --------------------------------------------------
    def grid_create(self, gname, nrows, ncols):
	gx = grid.grid(nrows,ncols)
	# add grid
	gname_new = self.add_grid(gname, gx)
	# fill with random 
	retu = self.get_grid_rand_float(gname_new)
	if retu is None:
	    return False
	return gname_new    
	
    #-------------------------------------------------------------------
    def grid_set(self, gridname, val1):
	"""
	    in:	val1	value to set	
	    out:	True / False
	    set all values to a const
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	gx.set_all(float(val1))
	
	#-------------------------------------------------------------------
    def grid_set_nd(self, gridname, val1):
	"""
	    in:	val1	value to set	
	    out:	True / False
	    set all value exept nodata
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	gx.set_all_nd(float(val1))
	
    #-------------------------------------------------------------------
    def grid_replace(self, gridname, val1, val2):
	"""
	    in:	val1:	value to replace str 
		val2:	replace value	 str 
	    out:	True / False
	    replace the val1 with val2
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.replace(float(val1), float(val2))
	
    #-------------------------------------------------------------------
    def grid_add(self, gridname, val1):
	"""
	    in:	val1:	value to add  	
	    out:	True / False
	    add the grid with an float
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.add(float(val1))
	
    #-------------------------------------------------------------------
    def grid_mul(self, gridname, val1):
	"""
	    in:	val1:	value to mul  	
	    out:	True / False
	    multiply the grid with a float 
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.mul(float(val1))
	
    #-------------------------------------------------------------------
    def grid_log(self, gridname, d=1.0):
	"""
	    in: d	float
	    calc: mat[mat<0]=0.0; lg(mat+d)
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.log(d)   

    #-------------------------------------------------------------------
    def grid_ln(self, gridname, d=1.0):
	"""
	    in:	d	float
	    calc: mat[mat<0]=0.0; ln(mat+d)
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.ln(d)
	
    #-------------------------------------------------------------------
    def grid_fabs(self, gridname):
	"""
	    calc: mat[mat!=nodata]=fabs(mat[mat!=nodata])
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.fabs()
	
    #-------------------------------------------------------------------
    def grid_norm(self, gridname):
	"""
	    out:	True / False
	    normalizes the mat in [0.0,1.0] according to: 
	    (x-min)/(max-min). Remove the nodata before 
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.norm()
	
#-------------------------------------------------------------------
    def grid_znorm(self, gridname):
	"""
	    out:	True / False
	    normalizes the mat:=(mat-mean(mat))/std(mat)
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.znorm()
    
    #-------------------------------------------------------------------
    def grid_inv(self, gridname):
	"""
	    invert a grid between min and max
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.inv()
	    
    #-------------------------------------------------------------------
    def grid_inv_ab(self, gridname, a):
	"""
	    in: 	a   float   upper limit of interval
	    out: 	True / False
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.inv_ab(a)
	    
    #-------------------------------------------------------------------
    def grid_cond(self, gridname, mi, ma, val3=-9999):
	"""
	    in:		min,  max,  val3 
	    out:	True / False
	    retrict all values in the range from [min,max]
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	if val3 == -9999:
	    return gx.cond(float(mi), float(ma))
	else:
	    return gx.cond(float(mi), float(ma), val=float(val3))

    #-------------------------------------------------------------------
    def grid_cut(self, gridname, ma, val2=-9999):
	"""
	    in:		new max,  val2 
	    out:	True / False
	    clamps the max with v1
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	if val2 == -9999:
	    return gx.cut(float(ma))
	else:
	    return gx.cut(float(ma), val=float(val2))

    #-------------------------------------------------------------------
    def grid_cut_off(self, gridname, val1, val2, val3=-9999):
	"""
	    in:		str val1 , str val2 , str val3 
	    out:	True / False
	    removes all values in the range from [min,max)
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.cut_off(float(val1), float(val2), val=float(val3))
	
    #-------------------------------------------------------------------
    def grid_classify(self, gridname, val1=10):
	""" 
	    in:		val1   int
	    out:	True / False
	    classify a continous range [min,max] in a 
	    set {c1,c2,c3,...cnr},  default=10
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	gx.classify(nr=val1)    #int(val1))
	
    #-------------------------------------------------------------------
    def grid_unique(self, gridname):
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	dic = gx.unique()
	#print dic.keys()
	return dic
    #-------------------------------------------------------------------
    def get_mx_select(self, gridname, li_categories, v1, v2):
	""" 
	    in:		v1, v2  int
	    out:	True / False
	    set all values in grid to val1 else to val2
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return False, False, False
	nr, nc = gx.size()
	vals_arr = li_categories
	if vals_arr is None:
	    print "grid_select error"
	    return None,None,None
	    
	print "P1=%f , P2=%f" % (v1, v2)	
        if gx.select(vals_arr, val1=v1, val2=v2) == False:
	    return None,None,None
	else:
	    mx = gx.get_matc()
	    return mx, nr, nc    
	    
    #-------------------------------------------------------------------
    def get_grid_rand_int(self, gridname, v1, v2):
	""" 
	    in:		v1, v2  int
	    out:	None or mx
	    generate a random mat using int numbers
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	if gx.randint(v1, v2) == True:
	    return gx.get_matc()

	
    #-------------------------------------------------------------------
    def get_grid_rand_float(self, gridname):
	""" 
	    in:		gridname
	    out:	None or mx
	    generate a random mat using float
	"""
	gx = self.d_grids[gridname]
	print gx
	if gx is None:
	    return None
	if gx.randfloat() == True:
	    return gx.get_matc()
	
	
    ####################################################################
    #####   Advanced_Grid
    ####################################################################
    
    def grid_combine(self, gridname, v1, kind):
	""" 
	    in:		gridname (of the highlighted grid)  str
			v1  (P1:gridname)  str
			kind ('add','diff','mul','min','max','or','and')  str
	    out:	None or mx
	    combine highlighted grid (gx) with P1:grid (g1)
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	g1 = self.d_grids[v1]
	if g1 is None:
	    return None
	print "grid_combine: gx=%s ,  g1=%s" % (gridname, v1)
	if kind == 'add':
	    """ add on grid to an other """
	    retu = gx.add_grid(g1)
	elif kind == 'diff':
	    """ diff of two grids """
	    retu = gx.diff_grid(g1)
	elif kind == 'mul':
	    """ multiply two grids """
	    retu = gx.mul_grid(g1)
	elif kind == 'min':
	    """ combine two grids using minimum """
	    retu = gx.min_grid(g1)
	elif kind == 'max':
	    """ combine two grids using maximum """
	    retu = gx.max_grid(g1)
	elif kind == 'or':
	    """replace nodata with values from grid g1"""
	    retu = gx.or_grid(g1)
	elif kind == 'and':
	    """includes nodata from g1"""
	    retu = gx.and_grid(g1)
	else: 
	    return None
	if retu == True:
	    return gx.get_matc()
	    
    #-------------------------------------------------------------------
    def grid_flood_fill(self, gridname,i,j,level1):
        """ 
	    in:		gridname str
			i,j    int
			level1  float  
	    out:	count
	    flood fill algorithm based on a stack implementation 
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	count = gx.floodFill(i,j,level1,mark=-1) 
	return count
	
    #-------------------------------------------------------------------
    def grid_flood_fill_std(self, gridname,i,j,level1):
        """ 
	    in:		gridname str
			i,j    int  
			level1  float  
	    out:	std, varianz bzw. count1, count
	    flood fill algorithm based on a stack implementation 
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	std, varianz = gx.floodFills(i,j,level1,mark=-1)
	return std, varianz  # bzw. count1,count or 0,0 or -9999,-9999 
	    
    #-------------------------------------------------------------------
    def grid_varpart(self, gridname, nr):
	""" 
	    in:		gridname str
			nr   	int
	    out:	dist   	list
	    part a grid in nr=5000 rectangular region 
	    with min var criterion
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	dist = gx.varpart(nr)
	return dist
    
    #-------------------------------------------------------------------
    def grid_remove_trend(self, gridname, nr):
	""" 
	    in:		gridname str
			nr   	int
	    out:	True/False or mx
	    remove the trend from a map using a linear regression
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	retu = gx.remove_trend(nr)     
	if retu == True:
	    return gx.get_matc()

    #-------------------------------------------------------------------
    def grid_grad_d4(self, gridname):
	""" 
	    in: 	
	    out: 	True/False, mx	
	    generates a map with gradient values from d4 
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	if gx.grad_d4() == True:
	    return gx.get_matc()
	return None
    #-------------------------------------------------------------------
    def grid_grad_d8(self, gridname):
	""" 
	    in: 	
	    out: 	True/False, mx	
	    generates a map with gradient values from d8
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	if gx.grad_d8() == True:
	    return gx.get_matc()
	return None

	
    ####################################################################
    #####   Kernel
    ####################################################################
    
    def kernel_sci(self, gridname, ai, bj, sigma):
	""" 
	    in: 	ai 	int
			bj	int
			sigma	float
	    out: 	True/False, mx	
	    convolves a gaussian kernel to mat
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	retu = gx.kernel_sci(ai, bj, sigma) 
	if retu == True:
	    return gx.get_matc()
	else:
	    return None
	
    #-------------------------------------------------------------------
    def kernel_rect(self, gridname, ai, bj):
	""" 
	    in: 	ai 	int
			bj	int
	    out: 	True/False, mx	
	    convolves a rectangular kernel to mat
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	retu = gx.kernel_squ(ai, bj) 
	if retu == True:
	    return gx.get_matc()
	else:
	    return None
	
    #-------------------------------------------------------------------
    def kernel_cir(self, gridname, r):
	""" 
	    in: 	r   radius	int
	    out: 	True/False, mx	
	    convolves a circle kernel to mat
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	retu = gx.kernel_cir(r) 
	if retu == True:
	    return gx.get_matc()
	else:
	    return None
    
    #-------------------------------------------------------------------
    def kernel_knn(self, gridname, k, mi, ma):
	""" 
	    in: 	k	int
			mi	float
			ma	float
	    out: 	True/None, mx
	    selects all k neighbors of the cell(i,j) and
            classifies all k neighbors into:
            1 : if min1<=cell(k)<=max1
            0 : else
            the result is the majority of the k neighbors	
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	retu = gx.knn(k, mi, ma) 
	if retu == True:
	    return gx.get_matc()
	else:
	    return None
	
	
    ####################################################################
    ####  Points
    ####################################################################
    
    def points_interpolate(self, gridname, lii, lij, liz, method):
	"""
	    in: x,y,z coordinates and values 
		range from: 0<=x<=1 and 0<=y<=1
		method= ...... s. grid.py
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	if gx.interpolate(lii,lij,liz,method=method) is None:
	    return None
	else:
	    return gx.get_matc()
	    
    #-------------------------------------------------------------------
    def points_voronoi(self, gridname, lii, lij, liz):
	"""
	    in: coordinates and values 
	"""
	#print "point_voronoi: %s" % gridname
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	if gx.voronoi(lii,lij,liz) is None:
	    return None
	else:
	    return gx.get_matc()
	    
    #-------------------------------------------------------------------
    def points_distance(self, gridname, lii, lij):
	"""
	    in: coordinates
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	if gx.distance(lii,lij) is None:
	    return None
	else:
	    return gx.get_matc()

    #-------------------------------------------------------------------
    def points_poisson(self, gridname, lii, lij, liz, eps, itnr):
	""" in:     x,y,z: coordinates and values 
		    eps:   double  (default = 0.000001)
		    itnr: int number of iterations (default = 25)
	    out:    True
	    uses a iterative method to solve the poisson equation:
            d^2V(x,y)/dx^2+d^2V(x,y)/dy^2=-const(x,y)
            uses number of iterations=25
        """
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	if gx.poisson(lii,lij,liz,eps, iter=itnr) == True:
	    return gx.get_matc()
	else:
	    return None
	
 
	
    ####################################################################
    #####   VISUALISATION    ###########################################
    ####################################################################
    
    def get_gx_size(self, gridname):
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.size()  # (nrows,ncols)
    
    #-------------------------------------------------------------------
    def get_gx_val(self, gridname, i, j):
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.get(i,j)
    
    #-------------------------------------------------------------------    
    def get_matrix(self, gridname):
	gx = self.d_grids[gridname]
	if gx is None:
	    return None, None, None      
	mx = gx.get_matc()  # with nodata
	(mi,ma) = gx.get_minmax()   
	return mx, mi, ma
    
    #-------------------------------------------------------------------    
    def get_min_max(self, gridname):
	gx = self.d_grids[gridname]
	if gx is None:
	    return None, None       
	(mi,ma) = gx.get_minmax()  
	return mi, ma
	
    #-------------------------------------------------------------------
    def grid_statistic(self, gridname):
	gx = self.d_grids[gridname]
	if gx is None:
	    return False, False, False, False
	tup = gx.size()
	ncols = tup[1]      
	nrows = tup[0]
	count_cells = ncols*nrows
	count_datacells = gx.get_datacells()
	count_nodatacells = count_cells - count_datacells
	(mi,ma) = gx.get_minmax()  
	mea, std = gx.mean_std()
	total = str(round(mea * count_datacells, 2))
	mi = str(round(mi, 4)) 
	ma = str(round(ma, 4))	
	mea = str(round(mea, 4))
	li= []
	#ss = "<strong><font color='mediumblue'>%s</font></strong>" % gridname
	li.append(gridname)
	li.append(str(count_cells))
	li.append(str(count_nodatacells))
	li.append(str(count_datacells))
	li.append(str(int(gx.get_csize())))
	li.append(mi)
	li.append(ma)
	li.append(total)	
	li.append(mea)
	li.append(str(round(std,4)))
	return li, mi, ma, mea

    #-------------------------------------------------------------------
    def zoom_statistic(self, gridname,i0,i1,j0,j1,mi,ma,mea,std):
	gx = self.d_grids[gridname]
	if gx is None:
	    return False, False, False, False
	
	mx = gx.get_matc(i0, i1, j0, j1)  # incl. nodata
	ncols = mx.shape[1]
	nrows = mx.shape[0]    
	count_cells = ncols*nrows
	count_nodatacells = len(mx[mx==-9999])
	count_datacells = count_cells-count_nodatacells
	
	mi = str(round(mi, 4))   
	ma = str(round(ma, 4))
	total = str(round(mea*count_datacells, 2))
	mea = str(round(mea, 4))
	std = str(round(std, 4))
	li= []
	li.append(gridname)
	li.append(str(count_cells))
	li.append(str(count_nodatacells))
	li.append(str(count_datacells))
	li.append(mi)
	li.append(ma)
	li.append(total)	
	li.append(mea)
	li.append(std)
	return li, mi, ma, mea
	
    #-------------------------------------------------------------------
    def get_mx_zoom(self,gridname, i0,i1, j0,j1):
	"""
	    in:	i0,j0 	upper left corner
		i1,j1 	lower right corner
	    out: a new grid of the zoom , min, max, nrows, ncols, ...	
	"""
	gx = self.d_grids[gridname]
	if gx is None:
	    return None, None, None, None, None, None, None
	gz = create_zoom(gx,i0,i1,j0,j1)
	(mi,ma) = gz.get_minmax()
	nr, nc = gz.size()
	mea, std = gz.mean_std()
	#~ print "gdoc: gz: mi=%f, ma=%f, nrow=%d, ncol=%d, mea=%f,std=%f"\
					    #~ % (mi,ma,nr,nc,mea,std)
	mx = gz.get_matc() 
	return mx, mi, ma, nr, nc, mea, std
        
    #-------------------------------------------------------------------
    def grid_info(self, gridname):
	gx = self.d_grids[gridname]
	if gx is None:
	    return False, False, False
	tup = gx.size()
	nrows = tup[0]
	ncols = tup[1]     
	nodata = gx.get_nodata()
	return nrows, ncols, nodata
     
    #-------------------------------------------------------------------
    def make_map_mx(self, gridname, proj=None):
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	try:
	    map_mx = create_map(gx, proj) 
	except:
	    print "error while create_map"
	    return None
	return map_mx

    #-------------------------------------------------------------------
    def grid_resize(self, gridname, nrows, ncols):
	gx = self.d_grids[gridname]
	if gx is None:
	    return False
	return gx.resize(nrows, ncols)
	
    #-------------------------------------------------------------------
    def get_mx_hist(self, gridname, bins):
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	mx = gx.show_hist(b1=bins,flag=1) 
	return mx
    
    #-------------------------------------------------------------------
    def get_mx_show_p(self,gname,color,size,pname,x,y):
	gx = self.d_grids[gname] 
	if gx is None:
	    return False
	  
	#title = "Points aus %s" % pname
	#mx,gridmin,gridmax = gx.show_p(x,y,color='w',size=size,t=title,X='xaxis',Y='yaxis',flag=1) 
	mx,gridmin,gridmax = gx.show_p(x,y,flag=1) 
	
	return mx,gridmin,gridmax
	
    #-------------------------------------------------------------------
    def get_mx_transect(self,gridname,i0,j0,i1,j1):
	gx = self.d_grids[gridname]
	if gx is None:
	    return None, None
	#gx.show_transect(i0,j0,i1,j1)
	t,mx = gx.show_transect(i0,j0,i1,j1, flag=1)  
	return t, mx
    
    #-------------------------------------------------------------------
    def get_mx_3d(self, gridname, strid):
	gx = self.d_grids[gridname]
	if gx is None:
	    return False, False, False
	nr, nc = gx.size()
	mx=gx.show_3d(stride=strid,sub1=False,title='',X='',Y='',flag=1)    
	return mx,nr,nc
    
    #-------------------------------------------------------------------
    def get_mx_range(self, gridname, mi, ma):
	gx = self.d_grids[gridname]
	if gx is None:
	    return False, False, False
	nr, nc = gx.size()
	mx = gx.showr(float(mi), float(ma), flag=1)    
	return mx,nr,nc
	
    #-------------------------------------------------------------------
    def get_mx_list(self, gridname, li_categories):
	gx = self.d_grids[gridname]
	if gx is None:
	    return False, False, False
	nr, nc = gx.size()
	mx = gx.shows(li_categories, flag=1)    
	return mx,nr,nc
    
    #-------------------------------------------------------------------
    def get_mx_lut(self, gridname, d_lut):
	gx = self.d_grids[gridname]
	if gx is None:
	    return None, None, None
	nr, nc = gx.size()
	if gx.lut(d_lut) == False:
	    return None, None, None
	else:
	    mx = gx.get_matc()
	    return mx,nr,nc
    
    #-------------------------------------------------------------------
    def get_mx_diff(self, gridname, v1):
	gx = self.d_grids[gridname]
	if gx is None:
	    return None
	g1 = self.d_grids[v1]
	if g1 is None:
	    return None
	mx = gx.show_diff(g1, flag=1)
	return mx
	
    #-------------------------------------------------------------------
    def get_mx_val(self, mx, i, j):
	# call from Popup_vis_colorbar --> Show_Diff has a mx only
	# call from mouse_clicked in self.mxzoom
	return mx[i,j]
    
	
    
    #-------------------------------------------------------------------
    #------ 11.2.2016 --------------------------------------------------
    def get_outp_rules_list(self, modelname):
	# called by: slotTREE_clicked in root models
	fx = self.d_models_fuz[modelname]

	li_outp = fx.get_outputs()
	li_rules = fx.get_rules()
	
	#~ for r in li_rules:
	    #~ tupel = self.get_rule(r)	# (0, 0, 6, 1.0)
	    #~ print "gdoc.get_rules_list::li_rules: get_rule: tupel=",tupel
	return li_outp, li_rules
    
    #-------------------------------------------------------------------
    def get_rule(self, r):
	return r.get_rule()   # tupel: (in1,in2,in3,outp,cf)
    
    #-------------------------------------------------------------------
    def get_mf_name(self, modelname, inpidx, mfidx):
	# called by: fill_ifthenList
	fx = self.d_models_fuz[modelname]
	return fx.inputs[inpidx].member[mfidx].get_name()
    
    #-------------------------------------------------------------------
    def get_outp_name_singleton(self, o):
	return o.get_name()
    
    #-------------------------------------------------------------------
    def get_name_of_output(self, modelname):
	fx = self.d_models_fuz[modelname]
	return fx.get_output_name()
    
    #-------------------------------------------------------------------
    def get_calct1(self,modelname,in1):
	# called by: on_release mouse
	print "in gdoc.get_calct1"
	fx = self.d_models_fuz[modelname]
	retu = fx.calct1(in1)
	return retu,fx.ruleList,fx.muList, fx.outputList

    #-------------------------------------------------------------------
    def get_calct2(self,modelname,in1,in2):
	# called by: on_release mouse
	fx = self.d_models_fuz[modelname]
	retu = fx.calct2(in1,in2)
	return retu, fx.ruleList, fx.muList, fx.outputList
    
    #-------------------------------------------------------------------
    def get_calct3(self,modelname,in1,in2,in3):
	# called by: on_release mouse
	#print "gdoc.get_calct3:: paras=", modelname, in1, in2, in3
	fx = self.d_models_fuz[modelname]
	retu = fx.calct3(in1,in2,in3)
	return retu, fx.ruleList, fx.muList, fx.outputList
    
    #-------------------------------------------------------------------
    def get_min_inp(self, modelname, i):
	# called by: on_press: -> Fyzzy_Analyse
	# i: idx of input (0 or 1 or 2)
	# lo: left oben value
	fx = self.d_models_fuz[modelname]
	lo = fx.get_min_input(i)  
	return lo    
    
    #-------------------------------------------------------------------
    def get_max_inp(self, modelname, i):
	# called by: on_press: -> Fyzzy_Analyse
	# i: idx of input (0 or 1 or 2)
	# ro: right oben value
	fx = self.d_models_fuz[modelname]
	ro = fx.get_max_input(i)  
	return ro 

    ####### end ########################################################
    


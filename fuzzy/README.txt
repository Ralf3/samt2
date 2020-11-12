#Define ===================================================================
fx=read_model(name,DEBUG=0)   # reads an fuzzy model, DEBUG=1  
			      # prints the model
fx.store_model(name)          # stores a model with the extension .fis

# Fuzzy help functions ====================================================
fx.get_number_of_inputs()     # returns the number of inputs [1..3]
fx.get_input_name(i)          # returns the name of the selected input [0..2]
fx.get_min_input(i)           # returns of the minimum supp val of input i
fx.get_max_input(i)           # returns of the maximum supp val of input i
fx.get_output_name()          # returns the name of the output
fx.get_len_output()           # returns the number of outputs
fx.get_output(i)              # returs the value of the output i
fx.set_output(i,val)          # set the output to a new val
fx.get_inputs()               # returns the list of inputs
fx.get_outputs()              # returns the list of outputs
fx.get_rules()                # returns the list of rules

# Fuzzy calculation =======================================================
fx.calc1(x)         # returns a double from fuzzy(double x)  
fx.calc2(x,y)       # returns a double from fuzzy(double x,double y)
fx.calc3(x,y,z)     # returns a double from fuzzy(x,y,z)  
# Fuzzy calculation debug mode ============================================
fx.calct1(x)        # returns a double from fuzzy(double x)  
fx.calct2(x,y)      # returns a double from fuzzy(double x,double y)
fx.calct3(x,y,z)    # returns a double from fuzzy(x,y,z)  
fx.get_ruleList()   # returns a List of rules which were used in calctX
fx.get_muList()	    # returns the List of mu-vals of the ruleList
fx.get_outputList() # returns the List of outputs 
# Fuzzy calculation returns the membership of the rules ==================
fx.calc1_r(x)       # returns a list with [mu(output1), mu(output2),...]
fx.calc2_r(x,y)     # returns a list with [mu(output1), mu(output2),...]
fx.calc3_r(x,y,z)   # returns a list with [mu(output1), mu(output2),...]
# Fuzzy calculation over a numpy array: return a numpy array
fx.array_calc1(g1)      # g1 is a numpy array
fx.array_calc2(g1,g2)   # g1,g2 are numpy arrays
fx.array_calc2(g1,g2,g3)# g1,g2,g3 are numpy arrays
# Fuzzy grid calculation ==================================================
fx.grid_calc1(g1)       # g1 is a SAMT2 grid,       returns a grid 
fx.grid_calc2(g1,g2)    # g1,g2 are SAMT2 grids,    returns a grid 
fx.grid_calc3(g1,g2,g3) # g1,g2,g3 are SAMT2 grids, returns a grid

# Fuzzy show model ========================================================
fx.show_model(tag1=2,default1=-9999)  # shows a fuzzy model for one, two or 
# three inputs. If more then two inputs are defined tag1=[0,1,2] selects
# the default input. I default1!=-9999 then it will be used otherwise
# mean of the range is used as default value for the input==tag1 
# Fuzzy show membership of a selected input
fx.show_input(i)
# FUZZY rule training =====================================================
fx.read_training_data(filename, header=0,sep=' ') # read a table x1,x2,x3,y
				                  # and returns pat, tar 
fx.set_trainX(X)  # set the numpy array X[0:n,0:n_inputs] as training data 
fx.set_trainY(Y)  # set the numpy array Y[n] training as data directly
fx.train_rules(alpha): # uses X and Y for trainig,
                       # alpha=0.75 cuts the rules 

fx.set_zero_cf(val)    # sets all zero cf values to val=1.0, returns the
		       # number of replacements
# Fuzzy training: apdat the outputs========================================
fx.read_training_data(filename, header=0,sep=' ') # read a table x1,x2,x3,y
fx.get_rmse()           # returns the rmse based on the training data  
fx.get_mae()            # returns the mae based on the training data  
start_training(fx)      # starts the training using GN_DIRECT_L 
		
Remark: the notebook  Fuzzy_Output_Training.ipynb contains an example
for fuzzy training. It can be started with:
ipython notebook 
in the fuzzy directory. It is a little tutorial for the fuzzy training. 
An example for dynamic fuzzy models can be found there: Daphnie

# some help functions =====================================================
o.get_name()	      # the name of the output
o.get_v()	      # the value of the output
o.get_m()	      # the mu of the output

i.get_member_list()   # the list of membership funtions
i.get_n()	      # the name of the input
i.get_mu()	      # the mu of the input

m.get_lo()	      # upper left
m.get_lu()            # lower left
m.get_ru()	      # lower right
m.get_ro()	      # upper right 
m.get_flag()	      # DREIECK=0 TRAPEZ=1 LEFT=2 RIGHT=3

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

# Fuzzy calculation =======================================================
fx.calc1(x)         # returns a double from fuzzy(double x)  
fx.calc2(x,y)       # returns a double from fuzzy(double x,double y)
fx.calc3(x,y,)      # returns a double from fuzzy(x,y,z)  
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

# Fuzzy grid calculation ==================================================
fx.grid_calc1(g1)       # returns a grid 
fx.grid_calc2(g1,g2)    # returns a grid 
fx.grid_calc3(g1,g2,g3) # returns a grid

# Fuzzy show model ========================================================
fx.show_model(tag1=2,default1=-9999)  # shows a fuzzy model for one, two or 
# three inputs. If more then two inputs are defined tag1=[0,1,2] selects
# the default input. I default1!=-9999 then it will be used otherwise
# mean of the range is used as default value for the input==tag1 

# FUZZY rule training =====================================================
fx.read_training_data(filename, header=0,sep=' ') # read a table x1,x2,x3,y
				                  # and returns pat, tar 
fx.train_rules(pat, tar, alpha): # uses pat and tar for trainig,
                                 # alpha=0.75 cuts the rules 

# Fuzzy training: apdat the outputs========================================
fx.read_training_data(filename, header=0,sep=' ') # read a table x1,x2,x3,y
start_training(fx)      # starts the training using GN_DIRECT_L from nlopt

Remark: the notebook  Fuzzy_Output_Training.ipynb contains an example
for fuzzy training. It can be started with:
ipython notebook 
in the fuzzy directory. It is a little tutorial for the fuzzy training. 

#Define ===================================================================
fx=read_model(name,DEBUG=0)   # reads an fuzzy model, DEBUG=1  
			      # prints the model

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
fx.calc3(x,y,z)     # returns a double from fuzzy(x,y,z)  
# Fuzzy calculation debug mode ============================================
fx.calc1(x)         # returns a double from fuzzy(double x)  
fx.calc2(x,y)       # returns a double from fuzzy(double x,double y)
fx.calc3(x,y,z)     # returns a double from fuzzy(x,y,z)  
fx.get_ruleList()   # returns a List of rules which were used in calctX
fx.get_muList()	    # returns the List of mu-vals of the ruleList
fx.get_outputList() # returns the List of outputs 

# Fuzzy grid calculation ==================================================
fx.grid_calc1(g1)       # returns a grid 
fx.grid_calc2(g1,g2)    # returns a grid 
fx.grid_calc3(g1,g2,g3) # returns a grid

# Fuzzy training: apdat the outputs========================================
fx.read_training_data(filename, header=0,sep=' ') # read a table x1,x2,x3,y
start_training(fx)      # starts the training using GN_DIRECT_L from nlopt
 

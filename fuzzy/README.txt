#Define ===================================================================
fx=read_model(name,DEBUG=0)   # reads an fuzzy model, DEBUG=1  
			      # prints the model

# Fuzzy calculation =======================================================
fx.calc1(x)         # returns a double from fuzzy(double x)  
fx.calc2(x,y)       # returns a double from fuzzy(double x,double y)
fx.calc3(x,y,z)     # returns a double from fuzzy(x,y,z)  

# Fuzzy grid calculation ==================================================
fx.grid_calc1(g1)       # returns a grid 
fx.grid_calc2(g1,g2)    # returns a grid 
fx.grid_calc3(g1,g2,g3) # returns a grid

 

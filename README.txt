# Define =====================================================================
gx=samt2.grid()        # defines a new grid object 
gx=samt2.grid(500,500) # defines a new grid object with a zero mat

# In-Out =====================================================================
gx.read_ascii(name,f)  # reads an ASCII-file   f=1 ===> DEBUG
gx.write_ascii(name)   # writes an ASCII-file
gx.read_csv(name)      # reads from a csv file and converts it to a grid
gx.list_hdf(name)      # lists all data sets in the h5 file
gx.read_hdf(name,set,f # loads the dataset (set) from h5 f=1 ===> DEBUG
gx.write_hdf(name,set,model,author) # writes a new hdf or appends an existing

# Create random grids ========================================================
gx.randfloat()         # fills an empty grid with random values
gx.randint(min,max)    # fills an empty grid with random int values [min,max)

# Access to the grid =========================================================
gx.print_mat(i0,i1,j0,j1)# print the region mat[i0:i1,j0:j1]
gx.get_matc(i0,i1,j0,j1) # returns a copy of the mat[i0:i1,j0:j1] 
		         # if i0==0, i1==0, j0==0, j1==0 returns a copy of mat
gx.get_matp()            # returns a pointer to mat
gx.set_mat(mat)          # set the np.ndarray with the same size to self.mat
gx.get(i,j)              # retruns the mat[i,j]
gx.set(i,j,val)          # mat[i,j]=val
gx.set_all(val)		 # mat[:,:]=val
gx.size()                # returns nrows and ncols
gx.get_nodata()          # returns the nodata
gx.get_csize()           # returns the cell size
gx.set_header(nrows,ncols,x,y,csize,nodata)
gx.get_header()          # returns nrows, ncols, x, y, csize, nodata

# Show data =================================================================
gx.show_hist(bins=20)  # shows a hist with bins 
gx.show(sub=False)     # shows a color picture of mat or sub (subarray)
gx.show_contour(sub=False,title='',X='',Y='',clines=6,flag=0) 
gx.showbw(sub=False)   # shows a bw picture of mat or sub (subarray)
                       # options: title, X, Y label
gx.show3d(stride=10, sub=False)   
		       # shows a 3D view of a grid with stride=10
gx.showi()             # draws a plot interactive using ion() no nodata!
gx.shows(array)        # selects, shows all int in grid which are in array
gx.showr(val1,val2,bw=0) # selects, shows all cells between val1 and val2 bw=1
			 # gets a grey image
gx.save_color(name)    # save a png
gx.save_bw(name)       # save a bw png
gx.show_transect(i0,j0,i1,j1,flag=0) # shows a transect from i0,j0 to i1,j1
gx.show_cwt(i0,j0,i1,j1,l=0,flag=0)  # shows a ricker cwt from i0,j0 to i1,j1
				     # with a lenght l (default: s/2)
# Statistics ================================================================
gx.info()              # describes the grid
gx.mean_std()          # returns the mean and the std
gx.get_min(minval=inv,mark=-1) # returns the position and minval>mark: x,y,min 
gx.get_max()           # returns the position and maxval: x,y,max 
gx.unique()            # returns a dict with index:count of an int value mat
gx.corr(gx)            # calculates the corrcoef between two arrays 
gx.sample(nr=100,ix=10)# generates x,y,z as sample from gx without
  		       # nodata and without duplication in x,y
gx.sample_det(val)     # returns the coord. with mat==val
gx.sample_neg(i,j,dist,n) # samples random [i,j] with a dist from
			  # the list i,j, returns an nd.array 
gx.statr(a,b)          # returns the total,mean,std of cells>=a and cells<=b

# Simple destructive operations (overwrites the mat) ========================
gx.norm()              # normalizes the mat in [0.0,1.0]
gx.znorm()	       # normalizes the mat: mat=(mat-mean(mat))/std(mat)
gx.fabs()	       # mat=np.fabs(mat)
gx.sign()	       # if mat<0 : 0 else: mat=1
gx.classify(nr=10)     # classifies the continious grid into nr classes
gx.reclass(m,k)        # -inf,m1 ==> k1, (m1,m2] ==> k2, ... m=[], k=[]
gx.replace(v1,v2)      # replaces v1 with v2
gx.add(v)              # adds the value v to all elements of mat
gx.mul(v)              # multiplies all elements of math with v
gx.mul_add(mu,add)     # mat=mat*mu+add
gx.log(d=1.0)          # calc: mat[mat<0]=0.0; lg(1+x)
gx.ln(d=1.0)           # calc: mat[mat<0]=0.0; ln(1+x)
gx.set_nan()	       # replaces the nodata with numpy.nan
gx.reset_nan()	       # replaces numpy.nan with nodata

# Complex destructive operations ============================================
gx.inv()               # mat:=gridmax-mat+gridmin for all cells
gx.inv_ab(a)           # mat:=a-mat for all cells
gx.lut(table)          # mat:=table[mat] for all cells (table=dict)
gx.select(vals,val1=1,val2=0) # set all values in vals (np.array) with val1
			      # otherwise with val2
gx.border(val)         # returns a lut with {id,freq} from neighbor of mat==val
gx.cut(max,val=-9999)  # clamps the max or set it nodata
g.cond(min,max,min1=-9999,max1=-9999) # if(mat<min): mat=min1
			  	      # if(mat>=max): mat=max1
gx.cut_off(min,max,val=-9999) # removes the [min,max] from mat

# Maximum subarray ==========================================================
gx.varpart(nr=5000):   # part a grid in nr part using min variance criterion
gx.max_subarray_list(thresh=0.0, iter=1) # calculates iter max. subarrays

# Trend and kernel techniques ===============================================
gx.remove_trend(nr=2000) # removes the trend estimated from nr samples
gx.kernel(w)             # uses convolve with the kernel w
gx.kernel_sci(ai,bj,s)   # convolves a gaussian kernel to mat
gx.kernel_squ(ai,bj)     # convolves a rectangular kernel to mat
gx.kernel_cir(r)         # convolves a circle kernel to mat
gx.knn(k,min1,max1) 	 # knn with +1/0 as majority measure

# Flood fill algorithm ======================================================
gx.floodFill(x,y,l,mark=-1)  # floods an area (x,y) with level l mark it
gx.floodFill_size(x,y,l,s=5,mark=-1) 
			# floods an area (x,y) with level l rem reg<s, mark it

# Add and Mul other grids ===================================================
gx.add_grid(g1)          # gx.mat+=g1.mat
gx.diff_grid(g1)	 # gx.mat-=g1.mat
gx.mul_grid(g1)          # gx.mat*=g1.mat
gx.set_all(val)          # gx.mat=val
gx.min_grid(g1)          # gx.mat=min(gx.mat,g1.mat)
gx.max_grid(g1)          # gx.mat=max(gx.mat,g1.mat)
gx.and_grid(g1)		 # includes nodata from both grids
gx.or_grid(g1)           # replaces nodata in gx.mat with gx.mat1

# Point algorithms  x=int y=int z=float =====================================
gx.transform_to_ij(y,x)  # takes a list [np.ndarray] in geo to ij
gx.inside_geo(y,x)       # takes a geo. coord and returns the value of the grid
gx.set_geo(y,x,z)	 # set mat=z at pos y,x
gx.interpolate(y,x,z,m)  # interpolates x,y,z to a grid using m= 
# multiquadratic, inverse, gaussian, linear, cubic, quintic, thin_plate
gx.voronoi(y,x,z)        # voronoi
gx.distance(y,x)         # distance to all grid cells from pos x,y
gx.poisson(y,x,z,eps,iter) # x,y: np.ndarray(dtype=np.int)
			   # z=np.ndarray(dtype=np.double), eps,iter=25
			   # poisson equation solver

# Flow algorithms ===========================================================
gx.d4()                  # calc the D4 and store it in self.d4_mat
gx.d8()                  # calc the D8 and store it in self.d8_mat
gx.grad_g4()             # apply the u=1 r=3 d=5 l=7 sink=-1 from d4_mat
gx.grad_g8()             # apply the u=1 ur=2 r=3 dr=4 d=5 dl=6 l=7 ul=8 
			 # sink=-1 from d8_mat to mat
# ==================== Functions outside the object =========================
samt2.copy_grid(gx)      # returns a 1:1 copy of a grid

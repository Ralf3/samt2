The last update of "Machine Learning Python" (mlpy) is from 2012. SAMT2 uses 
the SVMLIB and now the LIBLINEAR for modeling. Both libraries are part of mlpy 
but are alternatively available from:   https://www.csie.ntu.edu.tw/~cjlin/. 
SAMT2 will use both SVM libraries directly from the developer web page and 
will remove the mlpy. This change allows a code review and a clearer 
object-oriented design and faster training.

Ralf Wieland
2.12.2015

====================================svm===================================

svm()  # init svm with inputs
m=svm()       # define a svm
m.set_names('gwd','rise','ufc') # names are important for training
m.type=0              # 0:C-SVC,nu-SVC,one-class,epsilon-SVR,nu-SVR
m.kernel=0            # 0:linear,polynomial,radial basis,sigmoid,precomputed
m.degree=3	      # degree	    
m.gamma=1/len(names)  #
m.coef0=0     # coef0 in kerne function
m.c=1         # cost factor
m.nu=0.5      # nu of nu-SVC, one-class SVM, and nu-SVR
m.eps=0.001   # tolerance of termination criterion
m.p=0.1       # epsilon in loss function of epsilon-SVR
m.prob=0      # whether to train a SVC or SVR model for prob. est.
m.weight=1    # weight*C, for C-SVC
m.q=0         # quiet mode (no outputs) default no
m.v=0         # -v n: n-fold cross validation mode

methods ==================================================================

read_model(filename)          # read a model 'name.svm'
write_model(filename)	      # write a trained model 'name.svm'
train(x,y)		      # x must be a list of lists, y can be a numpy 
evaluation(ty,tv)	      # ty: list of true; tp list of predicted
			      # return: ACC, MSE, SCC
predict(x,y=None)		      # x list of inputs, y list of true values
			      # return  p_labels, p_acc, p_vals
calc(g1,g2,...)		      # uses a list of grids as inputs
			      # return a grid 

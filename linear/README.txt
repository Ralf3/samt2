The last update of "Machine Learning Python" (mlpy) is from 2012. SAMT2 uses 
the SVMLIB and now the LIBLINEAR for modeling. Both libraries are part of mlpy 
but are alternatively available from:   https://www.csie.ntu.edu.tw/~cjlin/. 
SAMT2 will use both SVM libraries directly from the developer web page and 
will remove the mlpy. This change allows a code review and a clearer 
object-oriented design and faster training.

Ralf Wieland
2.12.2015

==================================linsvm==================================

m=linsvm('inp1','inp2',...)   # define the input names
m.bias			      # read/write the bias<0 no bias is used
m.c			      # read/write the c (cost)
m.eps			      # read write tolerance of termination criterion
m.p			      # read/write epsilon in loss function
m.v			      # read/write n-fold cross validation (def=0)
m.q			      # read/write quiet mode
m.L			      # read/write method [0,1,2,3,4,5,6,7] for
			      # classification or [11,12,13] for regression

methods ==================================================================

read_model(filename)          # read a model
write_model(filename)	      # write a trained model
train(x,y)		      # x must be a list of lists, y can be a numpy 
best_C(x,y)		      # estimates the best c
evaluation(ty,tv)	      # ty: list of true; tp list of predicted
			      # return: ACC, MSE, SCC
predict(x,y=[])		      # x list of inputs, y list of true values
			      # return  p_labels, p_acc, p_vals
calc(g1,g2,...)		      # uses a list of grids as inputs
			      # return a grid with x*w values

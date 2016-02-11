Sugar Beet Model
================

The model consists of three notebooks:
	Analysis : 		used to analysis the training data set
	Fuzzy Model :	used to explain the model, start the training
	Simulation :	used to analyze the training results

The model needs the following python modules:

	numpy
	pylab (matplotlib)
	pandas
	statsmodels
	nlopt (could be installed under Ubuntu 14.04 (Debian) or from the source
	http://ab-initio.mit.edu/wiki/index.php/NLopt

please install this if you haven't

The model reads an Excel file with the data (ZR_Daten_DDR_1976_1990.xlsx) and
used the following fuzzy models:
	zr_simple.fis
	zr_simple334.fis
	zr_simple344.fis
	zr_simple_t.fis  (trained model as result of the "Fuzzy Model")
All files are included.


Start the model: ipython notebook  

remark: ipython and the notebook should be installed

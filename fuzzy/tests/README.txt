This directory contains some examples to test the rule training of SAMTFUZZY

Three fuzzy models are used to produce a training data set.

The models:
	data1.fis  		# one dimensional example
	nahr_schreiadler.fis  	# two dimensional example
	hab_schreiadler.fis	# three dimensional example

The Python scripts to produce the training data are:
	gen_from_fuzzy1.py
	gen_from_fuzzy2.py
	gen_from_fuzzy3.py 

They are hard coded but can be used as template for own models too.

This scripts produce the training data:
	data1.csv
	nahr_data.csv
	hab_data.csv

The test procedures take the models and the data to produce new trained models:
	data1.fis
	nahr.fis
	hab.fis

The test scripts can be easily modified to test your own models/data

-------------------------------------------------------------------------

Some files for testing have been added: 
     	  alge_daphnie.fis 
	  alge_phosphor.fis
	  daphnie_alge.fis
	  cyano_phosphor.fis

They are use in a dynamic fuzzy approach, published in:
http://www.rroij.com/open-access/the-use-of-the-dynamic-fuzzy-method-in-ecosystemmodeling.pdf



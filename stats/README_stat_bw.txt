STAT_BW
=======

stat_bw is a collection of often used definitions which are available in the 
net. The aim of this collection is to have a set of such function handy to
use in Python. This collection will be extended from time to time and 
can be with and without SAMT2.

Authors: Ralf Wieland and Rainer Bruggemann

hasse.py
========

is a simple analysis tool to implement Hasse diagrams. It uses the graph
toolbox networkX (https://networkx.github.io/) which should be installed.
For reading Excel-files it uses pandas which should be installed too.

It includes two example to check:

hasse_excel.py: read the hasse values from the Excel-file: 5models_stat.xlsx

hasse_csv.py:   read the hasse values from the CSV-file:   data2.txt
hasse_csv.py includes now a parser for the arguments (using argparse).
This parser allows to adapt the use of hasse.py:

-f     : to select a file.scv
-m     : choices between hasse, majorization, m2, majo
-d     : switches between hasse and simple visualization
-dir   : switches between succ or pred oriented HD generation (default=succ)
-delta : allows to specify a delta in % to make similar nodes EQ

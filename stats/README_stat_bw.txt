STAT_BW
=======

stat_bw2/3 (Python2/3) is a suite of statistical methods written for us, but hopefully also interesting for others.
It includes simple statistical functions that are used in many everyday problems of ecological modeling
are useful. This library is constantly being expanded and supplemented. Surely there are all these functions as part of
statistical software, but often hidden and not explicit. We use this library in our research and development
They often found it helpful. The library can be used together with SAMT2 or separately.

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
-m     : choices between hasse, majorization, m2, majo, majo1, ms
-d     : switches between hasse and simple visualization
-dir   : switches between succ or pred oriented HD generation (default=succ)
-delta : allows to specify a delta in % to make similar nodes EQ

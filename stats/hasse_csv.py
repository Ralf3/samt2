#!/usr/bin/env python

import hasse as hd
import argparse

""" new user friendly version based on argparse """

def main():
    parser = argparse.ArgumentParser(description='HASSE')
    parser.add_argument('-f', help='csv-data filename',required=True)
    parser.add_argument('-m', default='hasse',
                        choices=['hasse', 'majorization',
                                 'm2', 'majo', 'majo1'],
                        help='select a comparison method')
    parser.add_argument('-d', default='hasse',
                        choices=['hasse','simple'],
                        help='select a visualisation method: hasse/simple'
                        )
    parser.add_argument('-dir', default='succ', choices=['succ','pred'],
                        help='uses succ or pred to build the DH'
                        )
    parser.add_argument('-delta', default=0.0, type=float,
                        help='set the delta in % for the EQ'
                        )
    args = parser.parse_args()
    #read data from file
    
    #mw,z_namen=hd.read_data('test.csv')
    #mw,z_namen=hd.read_data('data2.txt')
    #mw,z_namen=hd.read_data('Bawue1.txt')
    #mw,z_namen=hd.read_data('BawueRheinks.txt')
    filename=args.f       # the filename of the structure
    hd.DELTA=args.delta/100.0   # the delta for EQ fabs(i,j)<delta
     
    mw,z_namen=hd.read_data(filename)
    for i in range(len(mw)):
	print z_namen[i],
        for j in range(len(mw[i])):
	    print mw[i,j],
        print
    
    
    for i in range(len(mw)):
	print z_namen[i],
        for j in range(len(mw[i])):
	    print mw[i,j],
        print
    # define a hassetree
    if(args.m=='hasse'):
        hasse1=hd.hassetree(hd.hasse_comp)
    if(args.m=='majorization'):
        hasse1=hd.hassetree(hd.majorization_comp)
    if(args.m=='majo'):
        hasse1=hd.hassetree(hd.majo_comp)
    if(args.m=='majo1'):
        hasse1=hd.hassetree(hd.majo1_comp)  
    if(args.m=='m2'):
        hasse1=hd.hassetree(hd.m2_comp)
    # fill it from mw
    for i in range(len(mw)):
        sitp=hd.sit(z_namen[i],mw[i])
        hasse1.insert(sitp)
    #hasse1.col_norm()
    if(args.d=='hasse'):
        if(args.dir=='succ'):
            gx,level=hasse1.make_graphs()
            hd.print_hd(gx,level,args.m,'succ')
        else:
            gx,level=hasse1.make_graph()
            hd.print_hd(gx,level,args.m,'pred')
    if(args.d=='simple'):
       hasse1.draw_simple(args.m)
       
if __name__ == "__main__":
    main()

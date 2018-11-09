#!/usr/bin/env python3

import hasse3 as hd
import argparse

""" new user friendly version based on argparse """

def main():
    parser = argparse.ArgumentParser(description='HASSE')
    parser.add_argument('-f', help='csv-data filename',required=True)
    parser.add_argument('-m', default='hasse',
                        choices=['hasse', 'majorization',
                                 'm2', 'majo', 'majo1', 'ms'],
                        help='select a comparison method')
    parser.add_argument('-d', default='hasse',
                        choices=['hasse','simple'],
                        help='select a visualisation method: hasse/simple'
                        )
    parser.add_argument('-delta', default=0.0, type=float,
                        help='set the delta in % for the EQ'
                        )
    parser.add_argument('-color', default='True', choices=['True','False'],
                        help='select color or black and white graph'
                        )
    parser.add_argument('-shift', default='False', choices=['True','False'],
                        help='if shift is True: the draw is shifted about 0.8 for better view'
                        )
    args = parser.parse_args()
    print(args)
    #read data from file
    
    filename=args.f       # the filename of the structure
    hd.DELTA=args.delta/100.0   # the delta for EQ fabs(i,j)<delta
     
    mw,z_namen=hd.read_data(filename)
    for i in range(len(mw)):
        print(z_namen[i],end=' ')
        for j in range(len(mw[i])):
            print(mw[i,j],end=' ')
        print()
    
    
    for i in range(len(mw)):
        print(z_namen[i],end=' ')
        for j in range(len(mw[i])):
            print(mw[i,j],end=' ')
        print()
        
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
    if(args.m=='ms'):
        hasse1=hd.hassetree(hd.ms_comp)
    # fill it from mw
    for i in range(len(mw)):
        sitp=hd.sit(z_namen[i],mw[i])
        hasse1.insert(sitp)
    #hasse1.col_norm()
    if(args.d=='hasse'):
        gx,level=hasse1.make_graphs()
        hd.print_hd(gx,level,args.m,'succ',eval(args.color),eval(args.shift))
    if(args.d=='simple'):
        hasse1.draw_simple(args.m,eval(args.color))
       
if __name__ == "__main__":
    main()

#!/usr/bin/env python

import hasse as hd

def main():
    #read data from file
    # mw,z_namen=hd.read_data('test.csv')
    mw,z_namen=hd.read_data('data2.txt')
    for i in range(len(mw)):
	print z_namen[i],
        for j in range(len(mw[i])):
	    print mw[i,j],
        print
    # define a hassetree
    hasse1=hd.hassetree()
    # fill it from mw
    for i in range(len(mw)):
        sitp=hd.sit(z_namen[i],mw[i])
        hasse1.insert(sitp)
    hasse1.print_eq()
    gx,level=hasse1.make_graph()
    # print HD
    hd.print_hd(gx,level,'test')

if __name__ == "__main__":
    main()

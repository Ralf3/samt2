#!/usr/bin/env python3

import hasse3 as hd
import numpy as np

def main():
    # read from execl
    mw=hd.read_from_excel('test1.xlsx',
                          'test1',
                          ['A','B','C','D'])
    z_namen=np.arange(mw.shape[0])
    hd.pprint(mw,z_namen)
    hasse1=hd.hassetree()
    for i in range(len(mw)):
        sitp=hd.sit(z_namen[i],mw[i])
        hasse1.insert(sitp)
    hasse1.print_eq()
    gx,level=hasse1.make_graphs()
    # print HD
    hd.print_hd(gx,level,'test1.xlsx')
    
if __name__ == "__main__":
    main()

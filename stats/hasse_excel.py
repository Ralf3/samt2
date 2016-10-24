#!/usr/bin/env python

import hasse as hd

def main():
    # read from execl
    mw,z_namen=hd.read_from_excel('5models_stat.xlsx',
                                  'model',
                                  ['spezifitaet','mean'])
    hd.pprint(mw,z_namen)
    hasse1=hd.hassetree()
    for i in range(len(mw)):
        sitp=hd.sit(z_namen[i],mw[i])
        hasse1.insert(sitp)
    hasse1.print_eq()
    gx,level=hasse1.make_graph()
    # print HD
    hd.print_hd(gx,level,'5models_stat.xlsx')
    
if __name__ == "__main__":
    main()

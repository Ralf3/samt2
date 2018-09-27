#!/usr/bin/env python

import hasse2 as hd

def main():
    # read from execl
    mw,z_namen=hd.read_from_excel('Hasse_Selectivity_Exactness.xlsx',
                                  'Tabelle2','Modell',
                                  ['Selectivity','Exactness'])
    hd.pprint(mw,z_namen)
    hasse1=hd.hassetree()
    for i in range(len(mw)):
        sitp=hd.sit(z_namen[i],mw[i])
        hasse1.insert(sitp)
    hasse1.print_eq()
    gx,level=hasse1.make_graph()
    # print HD
    hd.print_hd(gx,level,'Hasse_Selectivity_Exactness.xlsx')
    
if __name__ == "__main__":
    main()

import sys


sharps = ['c','cis','d','dis','e','f','fis','g','gis','a','ais','b']
flats =  ['c','des','d','ess','e','f','ges','g','ass','a','bes','b']

strings = ['e','a','d','g','b','e']

filename = sys.argv[1]
ntablines = 0
firsttabread = False
ntabset = 0


with open(filename) as tabfile:
    tab = tabfile.readlines()
    
for idx,line in enumerate(tab):
    if line.startswith('|'):
        if not firsttabread:
            ntablines += 1
    else:
        firsttabread = ntablines > 0
        if tab[idx-1].startswith('|'):
            ntabset += 1
            print(ntabset)
            tabset = tab[idx-ntablines:idx]
            print(tabset)
            print('---')

print(ntablines)

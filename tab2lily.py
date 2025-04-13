#!/usr/bin/python3

import sys


sharps = ['c','cis','d','dis','e','f','fis','g','gis','a','ais','b']
flats =  ['c','des','d','ees','e','f','ges','g','aes','a','bes','b']
durations = {'W':1, 'H':2, 'Q':4, 'E':8, 'S':16, 'T':32, 'X':64}

"""
W - whole; H - half; Q - quarter; E - 8th; S - 16th; T - 32nd; X - 64th; a - acciaccatura
+ - note tied to previous; . - note dotted; .. - note double dotted
Uncapitalized letters represent notes that are staccato (1/2 duration)
Irregular groupings are notated above the duration line
Duration letters will always appear directly above the note/fret number it represents the
duration for.  Duration letters with no fret number below them represent rests.  Multi-
bar rests are notated in the form Wxn, where n is the number of bars to rest for.  Low
melody durations appear below the staff
"""

durationlineidx = 1 # 1st line before the tab
strings = ['e','a','d','g','b','e']
time = 'C'
clef = 'bass'
sharpkey = False


if len(sys.argv) >1:
    filename = sys.argv[1]
    outfile = filename + '.lil'
else:
    print('No file',file=sys.stderr)
    sys.exit(2)
ntablines = 0
firsttabread = False
ntabset = 0
stringidx = []
if sharpkey:
    notes = sharps
else:
    notes = flats
for string in strings:
    stringidx.append(notes.index(string))

with open(filename) as tabfile:
    tab = tabfile.readlines()

def checkstart(line):
    return line.startswith('|')

tabset = []
print(f'{{\n \\time {time}\n \\clef {clef}')
for idx,line in enumerate(tab):
    line=line.strip()
    if checkstart(line):
        if not firsttabread:
            ntablines += 1
        continue
    else:
        firsttabread = ntablines > 0
        if tab[idx-1].startswith('|'):
            ntabset += 1
            print(ntabset,file = sys.stderr)
            tabset = tab[idx-ntablines:idx]
            print(f'tabset:{tabset} {len(tabset)}',file = sys.stderr)
            print('---',file = sys.stderr)
            if durationlineidx:
                durationline = tab[idx-ntablines-durationlineidx]
        else:
            continue
    equallen = True
    tablen = len(tabset[0])
    for tabline in tabset:
        equallen = equallen and len(tabline) == tablen
    if not equallen:
        print(f'Fault tab {idx}, {tabset}',file = sys.stderr)
        continue

    for charidx in range(tablen):
        note = None
        for tabidx,tabline in enumerate(tabset):
            linenote = None
            if durationlineidx:
                duration = ''
                try:
                    if durationline[charidx] in durations:
                        duration = durations[durationline[charidx]]
                        if durationline[charidx+1] == '.':
                            duration = f'{duration}.'
                except IndexError:
                    # May try to read a dot out of line
                    pass

            else:
                duration=''
            char = tabline[charidx]
            try:
                fret = int(char)
                noteidx = stringidx[tabidx]+fret
                note = notes[noteidx]
                linenote = note
                print(f'fret {char} on string {tabidx} is {note}, {duration}',file = sys.stderr)
                print(f'{note}{duration}', end=' ')
            except:
                pass
        if duration != '' and linenote is None:
            print(f'r{duration}', end = ' ')
            duration = ''
    print(' ')
    tabset = []

print('}')
# print(ntablines)

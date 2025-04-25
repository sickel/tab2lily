#!/usr/bin/python3

import sys
import re
import argparse

sharps = ['c','cis','d','dis','e','f','fis','g','gis','a','ais','b']
flats =  ['c','des','d','ees','e','f','ges','g','aes','a','bes','b']
durations = {'W':'1', 'H':'2', 'Q':'4', 'E':'8', 'S':'16', 'T':'32', 'X':'64'}

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

parser = argparse.ArgumentParser(
                    prog='tab2lily',
                    description='Converts asciitab to lilypond notation. Reads <filename.ext>, outputs <filename.lil>',
                    epilog='(c) Morten Sickel 2025')

parser.add_argument('filename')
parser.add_argument('--time', default='4/4', help='Time signatur, default: 4/4', type=str)
parser.add_argument('--composer', default='', type =str)
parser.add_argument('--title', default = '',type =str)
parser.add_argument('--lilypondversion', help='default: 2.24.1', default='2.24.1')
parser.add_argument('--strings',help='Strings, default: eadgbe', default='eadgbe')
args =parser.parse_args()
filename = args.filename
filenameparts = filename.split('.')
outfilename = filenameparts[0]+'.lil'
composer = args.composer
time = args.time
versionstring = f'\\version "{args.lilypondversion}"'
title = args.title
durationlineidx = 1 # 1st line before the tab
commentlineidx = 2
strings = list(args.strings)
clef = 'bass'

sharpkey = False


if not filename:
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
outfile = open(outfilename,'w')
with open(filename,'r') as tabfile:
    tab = tabfile.readlines()

def checkstart(line):
    return line.startswith('|')

tabset = []
print(f"""{versionstring}
      \\header{{
    title = "{title}"
    composer ="{composer}"}}
""", file = outfile)
print(f"""{{
    \\time {time}
    \\clef {clef}
""", file = outfile)


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
            tabset = tab[idx-ntablines:idx]
            if durationlineidx:
                durationline = tab[idx-ntablines-durationlineidx]
            comments = {}
            if commentlineidx:
                commentline = tab[idx-ntablines-commentlineidx]
                commentlist = re.split(r'\s{2,}', commentline)
                for comment in commentlist:
                    comment = comment.strip()
                    comments[commentline.find(comment)] = comment
                #print(comments,file = sys.stderr)
        else:
            continue
    equallen = True
    tablen = len(tabset[0])
    for tabline in tabset:
        equallen = equallen and len(tabline) == tablen
    if not equallen:
        print(f'Warning: Invalid tabset {idx}: {tabset}',file = sys.stderr)
        continue

    for charidx in range(tablen):
        note = None
        frets = []
        if commentlineidx:
            pass
        for tabidx,tabline in enumerate(tabset):
            frets.append(tabline[charidx])
            duration = ''
            linenote = None
            if durationlineidx:
                try:
                    if durationline[charidx] in durations:
                        duration = durations[durationline[charidx]]
                        if len(durationline) > charidx+1:
                            if durationline[charidx+1] == '.':
                                duration += '.'
                            tie = durationline[charidx+1:].strip().startswith('+')
                            if tie:
                                duration += '~'
                except IndexError:
                    # May try to read a dot after eol
                    pass
                    # print('idxerr',file=sys.stderr)
            char = tabline[charidx]
            try:
                fret = int(char)
                noteidx = stringidx[tabidx]+fret
                note = notes[noteidx]
                linenote = note
                print(f'{note}{duration}', end=' ', file=outfile)
            except:
                pass
        if char == '|' and tabline[charidx-1] == '|':
            print('\\bar "||"', file = outfile)
        if duration != '' and len(set(frets))==1 and frets[0] == '-' :
            print(f'r{duration}', end = ' ' ,file=outfile)
            duration = ''
        if charidx in comments and comments[charidx] > "":
            print(f'^"{comments[charidx]}"', file= outfile)
    print(' ', file = outfile)
    tabset = []

print('}', file = outfile)
print(f"\n   Written to {outfilename}")

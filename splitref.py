#!/usr/bin/python

import os
import sys
import math
from glob import glob

# chunk size in MB
#CHUNKSIZE = 100
LINEPERMEGA = 20 * 1000
OVERLAP = 100
BPPERLINE = 50
HG38SIZEMB = 32400

# TESTING
#CHUNKSIZE = 10
#LINEPERMEGA = 1
#OVERLAP = 20
#BPPERLINE = 10

def splitDida(refgfname, nSplit, overlap=OVERLAP):
    nlines = 0
    nchunk = 1
    chromeSplitIdx = 0
    chunksize = round(math.ceil(HG38SIZEMB/nSplit)/10,1)
    readnlines = chunksize * LINEPERMEGA
    overlaplines = int(math.ceil(overlap/BPPERLINE))
    #print ("overlap lines: ", overlaplines)
    lines = []
    mychr = None
    with open(refgfname) as f:
        aline = f.readline()
        if aline.startswith(">chr"):
            mychr = aline.strip()
        nlines += 1
        lines.append(aline)
        while aline:
            while nlines < readnlines + overlaplines:
                aline = f.readline()
                if aline.startswith(">chr"):
                    mychr = aline.strip()
                    chromeSplitIdx = 0
                lines.append(aline)
                nlines += 1
            #curfname = f"{fname}_{nchunk}_OL{overlap}.{fsuffix}"
            curfname = "mref-%s.fa" % nchunk
            with open(curfname, "w") as fw:
                #fw.writelines(f"{line}" for line in lines)
                fw.writelines("%s" % line for line in lines)
                fw.close()
            #print (f"finished writing chunk: {nchunk}")
            print ("finished writing chunk: %s" % nchunk)
            chromeSplitIdx += 1
            tlines = lines[-overlaplines:]
            nlines = 0
            nchunk += 1
            lines = ["%s_splitP%s\n" % (mychr, chromeSplitIdx)]
            lines.extend(tlines)

def main():
    fname = "hg38_reference.fa"
    nSplit = 80
    if len(sys.argv) > 1:
        nSplit = int(sys.argv[1])
    splitDida(fname, nSplit, 100)

if __name__ == "__main__":
    main()


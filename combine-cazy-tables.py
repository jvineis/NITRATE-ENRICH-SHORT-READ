#!/usr/env/python

import sys

sample_list = open(sys.argv[1], 'r')

# This sample_list is a list of the sample names.  Names should be separated by a new line and the corresponding
# functional table for the sample must end in "-cazy-stringent-hits.txt".
outfile = open("ALL-CAZY-HITS.txt", 'w')
all_funcs = {}
all_samples = []
for line in sample_list:
    x = line.strip()
    all_samples.append(x)
    file = ('s_'+x+'-cazy-stringent-hits.txt')
    open_file = open(file, 'r')
    for func in open_file:
        f = func.strip().split('\t')
        k = x+':'+f[0]
        all_funcs[k] = f[0:len(f)]

all_mag_funcs = []
for key in all_funcs.keys():
    all_mag_funcs.append(key)

all_cogs = []
for line in all_mag_funcs:
    all_cogs.append(line.split(":")[1])

all_cogs_uniq = set(all_cogs)
outfile.write("MAG"+'\t'+'\t'.join(all_cogs_uniq)+'\n')

def func_finder(sample):
    hits = []
    for cog in all_cogs_uniq:
        bin_cog = sample+":"+cog
        if bin_cog in all_funcs.keys():
            hits.append("1")
        else:
            hits.append("0")
    return(hits)

for sample in all_samples:
    x = func_finder(sample)
    outfile.write(sample+'\t'+'\t'.join(x)+'\n')

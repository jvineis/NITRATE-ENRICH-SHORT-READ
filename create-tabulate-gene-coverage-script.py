#!/usr/bin/env python

import sys

name = sys.argv[1]
outfile = open(name+"_"+"tabulate"+"-"+"gene"+"coverage"+".shx", 'w')

outfile.write("#!/bin/bash"+'\n'+
              "#SBATCH --nodes=1"+'\n'+
              "#SBATCH --tasks-per-node=20"+'\n'+
              "#SBATCH --mem=250Gb"+'\n'+
              "#SBATCH --time=00:20:30"+'\n'+
              "#SBATCH --partition=express"+'\n'+
              "#SBATCH --array=1-62"+'\n'+
              "SAMPLE=$(sed -n "+'"'+"$SLURM_ARRAY_TASK_ID"+'"'+"p sample_names.txt)"+'\n'+
              "target="+name+'\n'+
              "coverage_file=MAPPING/${target}-vs-${SAMPLE}-covstats.txt"+'\n'+
              "output=MAPPING/${target}-vs-${SAMPLE}-narG.txt"+'\n'+
              "python ~/scripts/estimate-gene-coverage-from-hmms-and-covstats.py --cov ${coverage_file} --fa x_ANVIO-assembly-dbs/x_narG-sequences.faa --out ${output}")

# Use this script to launch all the other scripts

import os
import subprocess
from props import *
from numpy import *
from sympy import *
import pickle as pk

print ('The analysis has just begun...')

# Temperature of analysis
tems=[293,300,325,350,375,400,425,450,475,500,525,550,575,600,605,610,615,616,617,618,619,620,625,630,635,640,645,650,660,665,670,680,690,700]
#tems=[625,630,645,665,675,700]
#tems=[293,300,325,350,400,425,450,475,500]
#tems=[300,325,350,400,425]
#tems=[500,525,550,620,625,650]

for tt in tems:

    #Run the volume fraction analysis and get results back from it
    from vol import vol
    mat_vol,pore_vol= vol(tt)

    print ('pore volume is', pore_vol)

    from pack import pack
    pack(pore_vol,tt)

    # Use temp to run temp dependent properties module
    from temp_variation import temp_variation
    temp_variation(tt)

    f=open('axis%d'%tt,'rb')
    flip=pk.load(f)
    f.close()

    if flip<=0.001:


    	f=open('run_p.job', 'w')
    	f.write("#!/bin/bash")
    	f.write("\n")
    	f.write("#PBS -N P%d"%tt)
    	f.write("\n")
    	f.write("#PBS -W group_list=oiz")
    	f.write("\n")
    	f.write("#PBS -q standard")
    	f.write("\n")
    	f.write("#PBS -l select=1:ncpus=1:mem=6gb:pcmem=6gb")
    	f.write("\n")
    	f.write("#PBS -l place=free:shared")
    	f.write("\n")
    	f.write("#PBS -l walltime=00:30:00")
    	f.write("\n")
    	f.write("#PBS -l cput=00:30:00")
    	f.write("\n")
    	f.write("cd /home/u23/tejakondury/SAPHYR3")
    	f.write("\n")
    	f.write("abaqus cae noGUI=no_pore.py ")
    	f.close()

    	os.environ['tt']=str(tt)
        os.environ['pr_vol']=str(pore_vol)
        os.environ['mat_vol']=str(mat_vol)

    	subprocess.call('qsub -v tt=$tt,mat_vol=$mat_vol,pr_vol=$pr_vol run_p.job',shell=True)

        print('analysis is submitted for temp',tt)

    else:


    	f=open('run_p.job', 'w')
    	f.write("#!/bin/bash")
    	f.write("\n")
    	f.write("#PBS -N P%d"%tt)
    	f.write("\n")
    	f.write("#PBS -W group_list=oiz")
    	f.write("\n")
    	f.write("#PBS -q standard")
    	f.write("\n")
    	f.write("#PBS -l select=1:ncpus=1:mem=6gb:pcmem=6gb")
    	f.write("\n")
    	f.write("#PBS -l place=free:shared")
    	f.write("\n")
    	f.write("#PBS -l walltime=00:30:00")
    	f.write("\n")
    	f.write("#PBS -l cput=00:30:00")
    	f.write("\n")
    	f.write("cd /home/u23/tejakondury/SAPHYR3")
    	f.write("\n")
       	f.write("abaqus cae noGUI=pore_cond.py")

	f.close()

	os.environ['tt']= str(tt)
    	os.environ['pr_vol']=str(pore_vol)
    	os.environ['mat_vol']=str(mat_vol)

	subprocess.call('qsub -v tt=$tt,mat_vol=$mat_vol,pr_vol=$pr_vol run_p.job',shell=True)

        print('analysis is submitted for temp',tt)

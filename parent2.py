import os
import subprocess
import numpy as np

data1=np.loadtxt('results_therm_cond_5')
len=len(data1)

tt=np.zeros(len)
k=np.zeros(len)
pore_vol=np.zeros(len)
mat_vol=np.zeros(len)

for i in xrange(len):
    tt[i]=data1[i][0]
    k[i]=data1[i][1]
    pore_vol[i]=data1[i][2]
    mat_vol[i]=data1[i][3]

for i in xrange(len):
    tk=tt[i]
    ratio=k[i]/mat_vol[i]
   #norm=ratio*(0.5-pore_vol[i])
    norm=k[i]	
    f=open('norm%d'%tk,'w')
    f.write(str(norm))
    f.close()

    f=open('fib-cond%d'%tk,'w')
    dummy=1.8
    #dummy=np.sqrt((tk/theta_0))*6.83
    f.write(str(dummy))
    f.close()

    f=open('norm_matrix_cond','a')
    f.write(str(tk)+' '+str(norm)+"\n")
    f.close()

    f=open('run_p.job', 'w')
    f.write("#!/bin/bash")
    f.write("\n")
    f.write("#PBS -N P%d"%tk)
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
    f.write("abaqus cae noGUI=no_pore_2step.py ")
    f.close()

    os.environ['tt']=str(tk)

    subprocess.call('qsub -v tt=$tt run_p.job',shell=True)

    print('analysis is submitted for temp',tk)

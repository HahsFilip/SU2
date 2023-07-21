import sys
from optparse import OptionParser	# use a parser for configuration
import pysu2			            # imports the SU2 wrapped module
from math import *
import os
import pysu2ad
from mpi4py import MPI
import numpy as np
import shutil
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
ad_com = MPI.COMM_WORLD
rank_ad = ad_com.Get_rank() 

rotation_velocity = 20
perturb = 1
substeps = 10
derivatives = np.zeros(substeps)
SU2Driver = pysu2.CSinglezoneDriver("spinning_cylinder.cfg",1, comm)
SU2Driver.SetMarkerRotationRate(0,0,0,rotation_velocity)

SU2Driver.Preprocess(0)
SU2Driver.Run()
SU2Driver.Postprocess()

SU2Driver.Output(0)
SU2Driver.Finalize()
result = np.genfromtxt("history.csv", dtype=float, delimiter=',', names=True)
data = result['CL']
first_value = data[-1]
result_file = open("results.txt", "w+")
result_file.write("first_value: \n")
result_file.write(str(first_value) + "\n")
result_file.write("\n\n\n\n")
del data
del result
shutil.copy("history.csv", "history_"+str(0)+".csv")

for i in range(substeps):
    SU2Driver = pysu2.CSinglezoneDriver("spinning_cylinder.cfg",1, comm)
    SU2Driver.SetMarkerRotationRate(0,0,0,rotation_velocity+perturb)
    SU2Driver.Preprocess(0)
    SU2Driver.Run()
    SU2Driver.Postprocess()
    SU2Driver.Output(0)
    SU2Driver.Finalize()
    shutil.copy("history.csv", "history_"+str(i+1)+".csv")
  
    result = np.genfromtxt("history.csv", dtype=float, delimiter=',', names=True)
    data = result['CL'] 
    derivatives[i] = (data[-1]-first_value)/perturb
    result_file.write(str(data[-1])+" "+str(perturb)+"\n")

    perturb = perturb/2
    del data
    del result
print(derivatives)

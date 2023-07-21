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
n_of_steps = 1 
rotation_vector = np.zeros(n_of_steps)+20
eps = 10
os.system('rm *.csv')
# print(iVertex)
    # CoordX[iVertex], CoordY[iVertex] = SU2Driver.MarkerInitialCoordinates(MovingMarkerID).Get(iVertex)
# print(MovingMarkerID)
# print(SU2Driver.GetMarkerMeshVelocity(MovingMarkerID, 1))
for j in range(10):
    SU2Driver = pysu2.CSinglezoneDriver("spinning_cylinder.cfg",1, comm)

    for i in range(n_of_steps):
        
        SU2Driver.SetMarkerRotationRate(0,0,0,rotation_vector[n_of_steps-i-1])

    
        SU2Driver.Preprocess(i)
        SU2Driver.Run()
        SU2Driver.Postprocess()
        
        SU2Driver.Output(i)
        SU2Driver.Update()
    shutil.copy("history.csv", "history_"+str(j)+".csv")
    SU2Driver.Finalize()
    SU2DriverAD = pysu2ad.CDiscAdjSinglezoneDriver("spinning_cylinder_ad.cfg",1, ad_com)

    for i in range(n_of_steps):
        SU2DriverAD.SetMarkerRotationRate(0,0,0,rotation_vector[i])

    
        SU2DriverAD.Preprocess(i)
        SU2DriverAD.Run()
        SU2DriverAD.Postprocess()
        
        SU2DriverAD.Output(i)
        SU2DriverAD.Update()
    SU2DriverAD.Finalize()
    data = np.genfromtxt("history_ad.csv", dtype=float, delimiter=',', names=True)
    result = np.genfromtxt("history.csv", dtype=float, delimiter=',', names=True)
    sens = data["Sens_Rot"]
    rotation_vector = rotation_vector - eps*sens[-1]
    print(rotation_vector)
    shutil.copy("history_ad.csv", "history_ad_"+str(j)+".csv")
    

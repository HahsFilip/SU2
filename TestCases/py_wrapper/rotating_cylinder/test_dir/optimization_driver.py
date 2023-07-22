import sys
from optparse import OptionParser	# use a parser for configuration
import pysu2			            # imports the SU2 wrapped module
from math import *
import os
import pysu2ad
from mpi4py import MPI
import numpy as np
import shutil
import scipy
import time
import copy
import SU2
class OptimizationDriver:
    
    
    def __init__(self, direct_path, adjoint_path, time_steps, period_of_optimization, initial_rotation) -> None:
        self.tmp_direct_name = "tmp.cfg"
        self.tmp_ad_name = "tmp_ad.cfg"
        self.direct_path = direct_path
        self.direct_config = SU2.io.Config(self.direct_path)
 
        self.adjoint_path = adjoint_path
        self.adjoint_config =SU2.io.Config(self.adjoint_path)
        self.control_array = np.ones(time_steps)*initial_rotation
        self.time_steps = time_steps

    def primary_calc(self):
        timing_file = open("times.txt", "w+")
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        SU2Driver = pysu2.CSinglezoneDriver(self.tmp_direct_name,1, comm)
        start_time = time.time()

        for i in range(self.time_steps):
            SU2Driver.SetMarkerRotationRate(0,0,0,self.control_array[i])

            SU2Driver.Preprocess(i)
            SU2Driver.Run()
            SU2Driver.Postprocess()
            SU2Driver.Output(i)
            SU2Driver.Update()
            time_step_time = time.time()-start_time
            timing_file.write(str(time_step_time) + " \n")
            start_time = time.time()
        SU2Driver.Finalize()
        timing_file.close()

    def adjoint_calc(self):
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        SU2DriverAD = pysu2ad.CDiscAdjSinglezoneDriver(self.tmp_ad_name,1, comm)

        for i in range(self.time_steps):
            SU2DriverAD.SetMarkerRotationRate(0,0,0,self.control_array[i])
            SU2DriverAD.Preprocess(i)
            SU2DriverAD.Run()
            SU2DriverAD.Postprocess()
            SU2DriverAD.Output(i)
            SU2DriverAD.Update()
            # sensitivity = SU2DriverAD.GetOutputValue("Sens_Rot")
            print(SU2DriverAD.GetOutputValue('SENS_ROT'))
            sensitivity = SU2DriverAD.GetOutputValue('SENS_ROT')

            print("\n\n\n SENSITYVITY:\n" + str(sensitivity))
    def change_dir(self, name):
        try:
            os.mkdir(name)
        except:
            try:
                shutil.rmtree(name)
                os.mkdir(name)
            except:
                pass
        shutil.copy(self.direct_config["MESH_FILENAME"], name+"/"+self.direct_config["MESH_FILENAME"])
        os.chdir(name)
        self.direct_config.dump(self.tmp_direct_name)
        self.adjoint_config.dump(self.tmp_ad_name)

main_driver = OptimizationDriver("tmp.cfg", "tmp_ad.cfg", 1000,1000, 20)

# main_driver.change_dir("test_dir")
main_driver.primary_calc()
main_driver.adjoint_calc()



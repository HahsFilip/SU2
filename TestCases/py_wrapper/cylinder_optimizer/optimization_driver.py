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
    
    
    def __init__(self, direct_path, adjoint_path, time_steps,  path_to_control_array) -> None:
        self.tmp_direct_name = direct_path
        self.tmp_ad_name = adjoint_path
        
        # self.direct_path = h
       
 
        # self.adjoint_path = 
        
        self.control_array = np.loadtxt(path_to_control_array)
        self.time_steps = time_steps

    def primary_calc(self):
        timing_file = open("times.txt", "w+")
        comm = MPI.COMM_WORLD
        print(comm)
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
            SU2DriverAD.SetMarkerRotationRate(0,0,0,self.control_array[self.time_steps-1-i])
            SU2DriverAD.Preprocess(i)
            SU2DriverAD.Run()
            SU2DriverAD.Postprocess()
            SU2DriverAD.Output(i)
            SU2DriverAD.Update()
            # sensitivity = SU2DriverAD.GetOutputValue("Sens_Rot")
        SU2DriverAD.Finalize()


# main_driver.change_dir("test_dir")

def main():
    parser = OptionParser()
    parser.add_option(
        "-f", "--file",dest="filename", help="read config from FILE", metavar="FILE"
    )
    parser.add_option(
        "-d", "--dir",dest="dir_config", help="read config from FILE", metavar="FILE"
    )
    parser.add_option(
        "-a", "--ad",dest="ad_config", help="read config from FILE", metavar="FILE"
    )
    parser.add_option(
        "-n", "--nn", dest="n_steps", help="read config from FILE", metavar="FILE"
    )
    (options, args) = parser.parse_args()
    
    n_steps = int(options.n_steps)
    print(options.dir_config)
    main_driver = OptimizationDriver(options.dir_config, options.ad_config,n_steps, options.filename )
    main_driver.primary_calc()
    main_driver.adjoint_calc()
    
if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()


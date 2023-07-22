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
import subprocess
class MpiDriver:

    def __init__(self, direct_path, adjoint_path, file_to_run) -> None:
            self.tmp_direct_name = "tmp.cfg"
            self.tmp_ad_name = "tmp_ad.cfg"
            self.direct_path = direct_path
            self.direct_config = SU2.io.Config(self.direct_path)
    
            self.adjoint_path = adjoint_path
            self.adjoint_config =SU2.io.Config(self.adjoint_path)
            self.file_to_run = file_to_run
    def change_dir(self, name):
        try:
            os.mkdir(name)
        except:           
            shutil.rmtree(name)
            os.mkdir(name)

        shutil.copy(self.direct_config["MESH_FILENAME"], name+"/"+self.direct_config["MESH_FILENAME"])
        shutil.copy(self.file_to_run, name)

        os.chdir(name)
        self.direct_config.dump(self.tmp_direct_name)
        self.adjoint_config.dump(self.tmp_ad_name)

    def run(self):
        print("mpirun --use-hwthread-cpus python "+ self.file_to_run)
        subprocess.run(["mpirun", "--use-hwthread-cpus"," python "+ self.file_to_run], check=True)


driver = MpiDriver("spinning_cylinder.cfg", "spinning_cylinder_ad.cfg", "optimization_driver.py")

driver.change_dir("test_dir")

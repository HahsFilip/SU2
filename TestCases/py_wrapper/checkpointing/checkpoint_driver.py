import sys
from optparse import OptionParser	# use a parser for configuration
import pysu2			            # imports the SU2 wrapped module
from math import *
import os
import pysu2ad
from mpi4py import MPI
class Checkpoints:
    def __init__(self, i, l) -> None:
        self.i = i
        self.level = l
        self.dispensable = False
        pass
class CheckpointDriver:
    checkpoints  = []
    
    delta = 0
    n_of_points = 0
    number_of_timesteps = 0
    direct_cfg = ""
    adjoint_cfg = ""
    def __init__(self, d, direct_conf, adjoint_conf) -> None:
        self.delta = d
        self.checkpoints.append(Checkpoints(0,1000000))
        self.direct_cfg = direct_conf
        self.adjoint_cfg = adjoint_conf
        self.ad_comm = MPI.COMM_WORLD
        self.ad_rank = self.ad_comm.Get_rank()
        self.SU2DriverAD = pysu2ad.CDiscAdjSinglezoneDriver(self.adjoint_cfg, 1, self.ad_comm)     

        pass
    def advance_solution(self, i):
        # i: iteration from which to restart
        self.n_of_points = len(self.checkpoints)
        assert i in self.get_checkpoint_locations() or i == 0

        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        
        os.system("cp " + self.direct_cfg + " " + "tmp.cfg")
        with open("tmp.cfg", "a") as conf:
            if i == 0:
                conf.write("RESTART_SOL= NO\n")
                
            else:
                conf.write("RESTART_SOL= YES\n")
                conf.write("RESTART_ITER= " + str(i+1) + "\n")
            conf.write("MATH_PROBLEM= DIRECT\n")
            conf.close()

        SU2Driver = pysu2.CSinglezoneDriver("tmp.cfg", 1, comm)
        SU2Driver.Preprocess(i+1)
        SU2Driver.Run()
        SU2Driver.Postprocess()
        SU2Driver.Output(i+1)
        # print("n of points" + str(self.n_of_points))
        is_dispensable = False
        ind_of_max_disp = 0
        max_disp_i = 0
        for j in range(len(self.checkpoints)):
            if self.checkpoints[j].dispensable:
                is_dispensable = True
                if self.checkpoints[j].i > max_disp_i:
                    ind_of_max_disp = j
                
        if self.n_of_points < self.delta:
            
            new_checkpoint = Checkpoints(i+1, 0)
            
            self.checkpoints.append(new_checkpoint)
            self.n_of_points +=1

        else:
            if is_dispensable:
                # print("removed cp: " + str(ind_of_max_disp))
                os.remove("restart_flow_"+str(self.checkpoints[ind_of_max_disp].i).zfill(5)+".dat")

                self.checkpoints.pop(ind_of_max_disp)

                new_checkpoint = Checkpoints(i+1, 0)
                self.checkpoints.append(new_checkpoint)
            else:
                
                level = self.checkpoints[-1].level
                index_to_remove = self.checkpoints[-1].i

                self.checkpoints.pop(-1)
                os.remove("restart_flow_"+str(index_to_remove).zfill(5)+".dat")
                new_checkpoint = Checkpoints(i+1, level+1)
                self.checkpoints.append(new_checkpoint)
        for j in range(len(self.checkpoints)):
            for k in range(len(self.checkpoints)):
                if j != k:
                    if self.checkpoints[j].i <= self.checkpoints[k].i and self.checkpoints[j].level < self.checkpoints[k].level:
                        self.checkpoints[j].dispensable = True   

    def advance_adjoint(self, i):
        # calcualte from i to i - 1
        assert i > 0
        current_checkpoints = self.get_checkpoint_locations()
        
        if i-1 in current_checkpoints:
            self.number_of_timesteps -= 1
            self.checkpoints.pop(current_checkpoints.index(i-1))
           
        else:
            closest_checkpoint = max([j for j in current_checkpoints if  i-1 > j])
            restart_checkpoint = self.checkpoints[current_checkpoints.index(closest_checkpoint)]
            for j in range(i-restart_checkpoint.i-1):
                # print(self.n_of_points)
                # print(self.get_checkpoint_locations())
                self.advance_solution(restart_checkpoint.i+j)
            new_checkpoints = self.get_checkpoint_locations()
            self.number_of_timesteps -=1
            os.remove("restart_flow_"+str(self.checkpoints[new_checkpoints.index(i-1)].i).zfill(5)+".dat")

            self.checkpoints.pop(new_checkpoints.index(i-1))


        print(i-1)

    
            
         
    def get_checkpoint_locations(self):
        check_pts = []
        for point in self.checkpoints:
            check_pts.append(point.i)
        return check_pts
    def print_checkpoints(self):
        for point in self.checkpoints:
            print(str(point.i) + "  " + str(point.level) + "  " + str(point.dispensable))

def main():
    test = os.listdir("/home/filip/SU2/SU2/TestCases/py_wrapper/checkpointing")

    for item in test:
        if item.endswith(".dat") or item.endswith(".vtu") :
            os.remove(os.path.join("/home/filip/SU2/SU2/TestCases/py_wrapper/checkpointing", item))
    driver = CheckpointDriver(6, "common.cfg", "unsteady_naca0012_opt_ad.cfg")
    for i in range(30):
        driver.advance_solution(i)
        # driver.print_checkpoints()
    print("begining adjoint run")
    for i in range(31,1, -1):
        # driver.print_checkpoints()
        print(driver.get_checkpoint_locations())

        # print(driver.n_of_points)
        driver.advance_adjoint(i)
        # driver.print_checkpoints()

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
            

import sys
from optparse import OptionParser	# use a parser for configuration
import pysu2			            # imports the SU2 wrapped module
from math import *
import os
import pysu2ad
from mpi4py import MPI
import numpy as np

from matplotlib import pyplot as plt
plt.ioff()
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
    adjoint_position =  -1
    def __init__(self, d, direct_conf, adjoint_conf, run=True) -> None:
        self.delta = d
        self.checkpoints.append(Checkpoints(0,1000000))
        self.direct_cfg = direct_conf
        self.adjoint_cfg = adjoint_conf

        if run:
            self.ad_comm = MPI.COMM_WORLD
            self.ad_rank = self.ad_comm.Get_rank()
            self.run = True
            self.SU2DriverAD = pysu2ad.CDiscAdjSinglezoneDriver(self.adjoint_cfg, 1,1)     
        else:
            self.run = False
        self.direct_computation_number = 0
        pass
    def advance_solution(self, i):
        # i: iteration from which to restart
        # save computation number for analysis

        self.direct_computation_number += 1
        self.n_of_points = len(self.checkpoints)
        assert i in self.get_checkpoint_locations() or i == 0
        if self.run:
            comm = MPI.COMM_WORLD
            rank = comm.Get_rank()
        
            os.system("cp " + self.direct_cfg + " " + "tmp.cfg")
            with open("tmp.cfg", "a") as conf:
                if i == 0:
                    conf.write("RESTART_SOL= NO\n")
                    
                else:
                    conf.write("RESTART_SOL= YES\n")
                    conf.write("RESTART_ITER= " + str(i+1) + "\n")
                # conf.write("MATH_PROBLEM= DIRECT\n")
                conf.close()
        
            SU2Driver = pysu2.CSinglezoneDriver("tmp.cfg", 1, 1)
            SU2Driver.Preprocess(i+1)
            SU2Driver.Run()
            SU2Driver.Postprocess()
            SU2Driver.Output(i+1)
            SU2Driver.Finalize()
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
                if self.run:
                    os.remove("restart_flow_"+str(self.checkpoints[ind_of_max_disp].i).zfill(5)+".dat")
             
                self.checkpoints.pop(ind_of_max_disp)

                new_checkpoint = Checkpoints(i+1, 0)
                self.checkpoints.append(new_checkpoint)
            else:
                
                level = self.checkpoints[-1].level
                index_to_remove = self.checkpoints[-1].i
                
                self.checkpoints.pop(-1)
                if self.run:
                    os.remove("restart_flow_"+str(index_to_remove).zfill(5)+".dat")
                new_checkpoint = Checkpoints(i+1, level+1)
                self.checkpoints.append(new_checkpoint)
        for j in range(len(self.checkpoints)):
            for k in range(len(self.checkpoints)):
                if j != k:
                    if self.checkpoints[j].i <= self.checkpoints[k].i and self.checkpoints[j].level < self.checkpoints[k].level:
                        self.checkpoints[j].dispensable = True   
        if not self.run:
            self.print_checkpoints()
    def advance_adjoint(self, i):
        # calcualte from i to i - 1
        assert i > 0
        current_checkpoints = self.get_checkpoint_locations()
        if not self.run:
            self.print_checkpoints()
        if i-1 in current_checkpoints:
            
            self.number_of_timesteps -= 1
            if self.run:
                self.SU2DriverAD.Preprocess(i)
                self.SU2DriverAD.Run()
                self.SU2DriverAD.Postprocess()
                self.SU2DriverAD.Output(i)
                self.SU2DriverAD.Update()
     
            self.checkpoints.pop(current_checkpoints.index(i-1))

        else:
            closest_checkpoint = max([j for j in current_checkpoints if  i-1 > j])
            restart_checkpoint = self.checkpoints[current_checkpoints.index(closest_checkpoint)]
            for j in range(i-restart_checkpoint.i-1):
                self.advance_solution(restart_checkpoint.i+j)

            new_checkpoints = self.get_checkpoint_locations()
            self.number_of_timesteps -=1
            if self.run:
                self.SU2DriverAD.Preprocess(i)
                self.SU2DriverAD.Run()
                self.SU2DriverAD.Postprocess()
                self.SU2DriverAD.Output(i)
                self.SU2DriverAD.Update()
                
                os.remove("restart_flow_"+str(self.checkpoints[new_checkpoints.index(i-1)].i).zfill(5)+".dat")
            self.checkpoints.pop(new_checkpoints.index(i-1))
        # print(i-1)
    def garbage_collector(self):
        if self.run:
            for i in range(self.SU2DriverAD.GetNumberTimeIter()):
            
                if i not in self.get_checkpoint_locations():
                    try:
                        os.remove("restart_flow_"+str(i).zfill(5)+".dat")
                    except:
                        pass
                
        
    def get_checkpoint_locations(self):
        check_pts = []
        for point in self.checkpoints:
            check_pts.append(point.i)
        return check_pts
    def print_checkpoints(self):
        with open("check_point_log.txt", "a+") as f:
            for point in self.checkpoints:
                # print(str(point.i) + "  " + str(point.level) + "  " + str(point.dispensable))
                f.write(str(point.i) + " ")
            f.write("\n")
            
        with open("adjoint_log.txt", "a+") as f:
            f.write(str(self.adjoint_position)+" "+str(self.number_of_timesteps) + "\n")
            
    def run_calculation(self, n_of_timesteps):
        self.number_of_timesteps = n_of_timesteps
        for i in range(n_of_timesteps):
            self.advance_solution(i)
            # print("Begining adjoint run")
        for i in range(n_of_timesteps+1,0, -1):
            self.adjoint_position = i
            self.garbage_collector()        
            self.advance_adjoint(i)
        if self.run:
            for i in range(n_of_timesteps+1):
                os.rename("restart_adj_cd_"+str(i+1).zfill(5)+".dat","restart_adj_cd_"+str(i).zfill(5)+".dat")

    def __del__(self):
        if self.run:
            self.SU2DriverAD.Finalize()
def main():
    # test = os.listdir("/home/filip/SU2/SU2/TestCases/py_wrapper/checkpointing")
    # fig, axs = plt.subplots(1)
    # axs = axs.reshape(-1)
    i = 0
    plt.figure(figsize=(10,4.5))
    for n_of_points in [15]:
        try:
            os.remove("check_point_log.txt")
            os.remove("adjoint_log.txt")
        except:
            pass

        # for item in test:
        # #     if item.endswith(".dat") or item.endswith(".vtu"):
        # #         os.remove(os.path.join("/home/filip/SU2/SU2/TestCases/py_wrapper/checkpointing", item))
        
        # # os.system("cp unsteady_naca0012_FFD.su2 mesh_in.su2")
        # # test = os.listdir("/home/filip/SU2/SU2/TestCases/py_wrapper/checkpointing")
        
        # n_of_calculations = []
        # timestep_array = [25]
        # print(timestep_array)
        # # timestep_array = timestep_array.astype(int)
        
        driver = CheckpointDriver(n_of_points, "common.cfg", "unsteady_naca0012_opt_ad.cfg", run=False)

        # # print(i)
        # # print(n_timesteps)
        driver.run_calculation(20)
        # # i = 0
        # ad_steps = []
        # ad_inds = []
        # max_step = 40
        # old_points = [0]
        # flag_start_adjoint = False
        i = 0
        
        with open("check_point_log.txt", 'r') as log:
            # print(log)
            for line in log.readlines():
                points = np.fromstring(line, sep=" ")
                if i == 0:
                    plt.scatter(np.ones(points.shape[0])*i, points, color = "black", marker='.', label="Checkpoints")
                else:
                    plt.scatter(np.ones(points.shape[0])*i, points, color = "black", marker='.')

                i+=1
        plt.vlines(20, 0, 22, color = 'red', label="Start of adjoint calculation")
        plt.xlabel("Evolution of the algorithm", fontsize=12)
        plt.ylabel("Timestep", fontsize=12)
        plt.title("Checkpointing schedule", fontsize=15)
        plt.legend()
        plt.show()
        #         difference = list(set(points)-set(old_points))
        #         difference_2 = list(set(old_points)-set(points))

        #         if not len(difference) == 0 and not len(old_points) == 0:
        #             print( difference_2)

        #             axs.plot( [max(old_points), difference[0]], np.ones(2),  c="r")

        #         if i == 0:
        #             axs.scatter(  points,np.ones(points.size), c="b", marker=",", s=15, label="Checkpoint")
        #         else:
        #             axs.scatter(  points, np.ones(points.size),c="b", marker=",", s=15,label="Checkpoint")
        #             print("here")
        #         if max(points) == max_step:
        #             flag_start_adjoint = True
        #         if flag_start_adjoint:
        #             axs.scatter( max_step,1, c="g",marker=",",  s=15, label="Adjoint")
        #         if max(points) == max_step -1 and flag_start_adjoint:    
        #             axs.plot( [max(points), max_step],  np.ones(2),c="g")

        #             max_step = max(points)
        #         i += 1
        #         # plt.title(str(i))
        #         axs.set_xlabel("Timestep")
        #         axs.legend()
        #         axs.set_title("6 checkpoints, 40 timesteps")
        #         # axs.spines['left'].set_visible(False)
        #         axs.get_yaxis().set_visible(False)
        #         fig.savefig("test/cpoints{}.png".format(i))
                
        #         axs.clear()
                
        #         print(difference)
        #         old_points = points
                # plt.show()
    #         del driver
    #     axs[i].plot(timestep_array, n_of_calculations)
    #     axs[i].set_xlabel("Timesteps")
    #     axs[i].set_ylabel("Recalculations")
    #     axs[i].set_title("{} checkpoints".format(n_of_points))
        # i += 1
    # fig.savefig("recalculations.png")
    # fig.show()
    # fig.suptitle("Average number of recalculations")

    # with open("results.txt", "w+") as result:
    #     for j in [10, 25, 50, 100]:
    #         n_for_plot = []
    #         result.write("Number of checkpoints: " + str(j)+"\n")
    #         lengths_to_eval = np.logspace(3, 5, 9, dtype=int)
    #         print(lengths_to_eval)
    #         for number_of_calcs in lengths_to_eval:
                
    #             # number_of_calcs = 2**i
    #             print(number_of_calcs)
    #             # for item in test:
    #                 # if item.endswith(".dat"):
    #                     # os.remove(os.path.join("/home/filip/SU2/SU2/TestCases/py_wrapper/checkpointing", item))

    #             driver = CheckpointDriver(j+2 , "common.cfg", "unsteady_naca0012_opt_ad.cfg", run=False)
    #             print("here")
    #             driver.run_calculation(number_of_calcs)
    #             result.write(str(number_of_calcs) + " " + str(driver.direct_computation_number/number_of_calcs)+ "\n")
    #             n_for_plot.append(driver.direct_computation_number/number_of_calcs)
    #             del driver
    #         plt.figure(figsize=(10,4.5))
    #         ax = plt.gca()

    #         ax.scatter(lengths_to_eval, n_for_plot)
    #         ax.set_yscale('log')
    #         ax.set_xscale('log')
    #         plt.title("Average number of recalculations, {} checkpoints".format(j), fontsize =15)
    #         plt.xlabel("Number of timesteps", fontsize= 12)
    #         plt.ylabel("Number of recalculations", fontsize= 12)
    #         # plt.show()
    #         plt.savefig("{}-pts.png".format(j))
    #         plt.clf()
            # os.rename("surface_deformed_00000.vtu", "surface_deformed_"+str(i).zfill(5)+".vtu")
        # os.rename("mesh_out.su2", "mesh_in.su2")
if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
            

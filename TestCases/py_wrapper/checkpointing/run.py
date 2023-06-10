import sys
from optparse import OptionParser	# use a parser for configuration
import pysu2			            # imports the SU2 wrapped module
from math import *
import os
import pysu2ad
from mpi4py import MPI
def calc_direct(start_iter, n_steps, checkpoints, cfg_file):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    
    os.system("cp " + cfg_file + " " + "tmp.cfg")
    with open("tmp.cfg", "a") as conf:
        if start_iter == 0:
            conf.write("RESTART_SOL= NO\n")
            
        else:
            conf.write("RESTART_SOL= YES\n")
            conf.write("RESTART_ITER= " + str(start_iter+1) + "\n")
        conf.write("MATH_PROBLEM= DIRECT\n")
        conf.close()
    SU2Driver = pysu2.CSinglezoneDriver("tmp.cfg", 1, comm)
    number_of_timesteps = n_steps
    
    for time_iter in range( number_of_timesteps):
        SU2Driver.Preprocess(time_iter+start_iter)
        SU2Driver.Run()
        # Postprocess the solver and exit cleanly
        SU2Driver.Postprocess()
        if time_iter in checkpoints:
            SU2Driver.Output(time_iter+start_iter)
        # Update the solver for the next time iteration
        SU2Driver.Update()
    SU2Driver.Output(time_iter+start_iter)
    SU2Driver.Finalize()
    os.remove("tmp.cfg")


def main():
    test = os.listdir("/home/filip/SU2/SU2/TestCases/py_wrapper/checkpointing")

    for item in test:
        if item.endswith(".dat") or item.endswith(".vtu") :
            os.remove(os.path.join("/home/filip/SU2/SU2/TestCases/py_wrapper/checkpointing", item))
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    interval_between_checkpoints = 10

    number_of_steps = 100
    checkpoints = range(0, number_of_steps, interval_between_checkpoints)
    calc_direct( 0,number_of_steps, checkpoints,"common.cfg")
    SU2DriverAD = pysu2ad.CDiscAdjSinglezoneDriver("/home/filip/SU2/SU2/TestCases/py_wrapper/checkpointing/unsteady_naca0012_opt_ad.cfg", 1, comm)     

    for i in range(SU2DriverAD.GetNumberTimeIter()):
        closest_checkpoint = max([j for j in checkpoints if number_of_steps - i > j])
        print("Closest checkpoint")
        print(closest_checkpoint)
        print(number_of_steps - closest_checkpoint-i)
        calc_direct(closest_checkpoint, number_of_steps - closest_checkpoint-i-1, checkpoints, "common.cfg")
        print("got here")
        SU2DriverAD.Preprocess(i)
        SU2DriverAD.Run()
        SU2DriverAD.Postprocess()
        SU2DriverAD.Update()
        SU2DriverAD.Monitor(i)

        SU2DriverAD.Output(i)
        os.remove("restart_flow_"+str(number_of_steps - i).zfill(5)+".dat")
    SU2DriverAD.Finalize()
        
        
    # try:
    #     SU2Driver = pysu2.CSinglezoneDriver("/home/filip/SU2/SU2/TestCases/py_wrapper/checkpointing/unsteady_naca0012_opt.cfg", 1, comm)
    # except TypeError as exception:
    #     print('A TypeError occured in pysu2.CDriver : ',exception)
    

    # number_of_timesteps = SU2Driver.GetNumberTimeIter()
    # checkpoints = range(0, number_of_timesteps+1, interval_between_checkpoints)

    # for time_iter in range(number_of_timesteps):
    #     SU2Driver.Preprocess(time_iter)
    #     SU2Driver.Run()
    #     # Postprocess the solver and exit cleanly
    #     SU2Driver.Postprocess()
    #     if time_iter in checkpoints:
    #         SU2Driver.Output(time_iter)
    #     # Update the solver for the next time iteration
    #     SU2Driver.Update()
    # SU2Driver.Finalize()

    # SU2DriverAD.Preprocess(0)
    # SU2DriverAD.Run()
    # SU2DriverAD.Postprocess()
    # SU2DriverAD.Output(0)

if __name__ == '__main__':
    main()

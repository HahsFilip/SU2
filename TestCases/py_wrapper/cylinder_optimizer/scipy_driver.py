import sys
	# use a parser for configuration
			            # imports the SU2 wrapped module
from math import *
import os


import numpy as np
import shutil

import SU2
import subprocess
import scipy
def compute_gradients(control_array, configs):
    tmp_dir_name = "tmp_dir_for_grad"
    c_array = "control_array.txt"
    bash_name = "bash_file.sh"
    dir_cfg_name = "tmp_dir.cfg"
    ad_cfg_name = "tmp_ad.cfg"
    n_steps = control_array.size
    configs[0]["TIME_ITER"] = n_steps
    configs[1]["TIME_ITER"] = n_steps
    configs[1]["UNST_ADJOINT_ITER"] = n_steps
    try:
        os.mkdir("tmp_dir_for_grad")
    except:
        shutil.rmtree(tmp_dir_name)
        os.mkdir(tmp_dir_name)

    shutil.copy(configs[0]["MESH_FILENAME"],tmp_dir_name )
    shutil.copy("optimization_driver.py",tmp_dir_name )

    os.chdir(tmp_dir_name)
    np.savetxt(c_array, control_array)
    configs[0].dump(dir_cfg_name)
    configs[1].dump(ad_cfg_name)
    with open(bash_name,"w+") as f:
        f.write("#!/bin/bash\n")
        f.write("mpirun --use-hwthread-cpus python optimization_driver.py -f "+ c_array + " -d " + dir_cfg_name + " -a " + ad_cfg_name + " -n "+ str(n_steps))
    os.system("chmod +rwx "+ bash_name)
    result = subprocess.run("./"+bash_name, shell=True)
    direct_history = np.genfromtxt(configs[0]["CONV_FILENAME"]+".csv", dtype=float, delimiter=',', names=True)
    ad_history = np.genfromtxt(configs[1]["CONV_FILENAME"]+".csv", dtype=float, delimiter=',', names=True)
    goal_function =np.mean(np.abs(direct_history['CL']-np.sin(np.arange(n_steps)*6.28/20)))
    os.chdir("..")
    with open("main_history.txt", 'a+') as f:
        f.write(str(goal_function)+"\n")
    gradient = ad_history["Sens_Rot"]
    gradient = gradient[::-1]
    # print(result.stdout.decode('utf-8'))
    return (goal_function, -1*gradient)
def main():
    direct_config = SU2.io.Config("cylinder.cfg")
    adjoint_config = SU2.io.Config("cylinder_adjoint.cfg")
    start_vector = np.ones(50)*0
    compute_gradients(np.zeros(10), (direct_config, adjoint_config))
    eps = 1000
    # for i in range(100):
    #     (goal, grad) = compute_gradients(start_vector, [direct_config, adjoint_config])
    #     if  i == 0:
    #         old_goal = goal
    #     else:
    #         if goal > old_goal:
    #             eps =  eps/2
    #         old_goal = goal
    #     start_vector = start_vector+eps*grad
    #     shutil.copytree("tmp_dir_for_grad", "tmp_dir_for_grad_"+str(i))
    opt = {'maxiter': 3}
    # res  = scipy.optimize.minimize(compute_gradients, start_vector,method='BFGS',args=([direct_config, adjoint_config]), jac=True,  options=opt)
    # print(res.x)
    # print(res.message)
    # print(res.success)
if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
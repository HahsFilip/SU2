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
def compute_gradients(control_array, configs, n_steps):
    global iter
    tmp_dir_name = "tmp_dir_for_grad"
    c_array = "control_array.txt"
    bash_name = "bash_file.sh"
    dir_cfg_name = "tmp_dir.cfg"
    ad_cfg_name = "tmp_ad.cfg"
    ad_steps = control_array.size
    configs[0]["TIME_ITER"] = n_steps
    configs[1]["TIME_ITER"] = n_steps
    # configs[1]["UNST_ADJOINT_ITER"] = ad_steps
    

    try:
        os.mkdir("tmp_dir_for_grad")
    except:
        shutil.rmtree(tmp_dir_name)
        os.mkdir(tmp_dir_name)

    shutil.copy(configs[0]["MESH_FILENAME"],tmp_dir_name )
    shutil.copy("optimization_driver.py",tmp_dir_name )
    offset = 0
    if iter != 0:
        configs[0]["RESTART_SOL"] = "YES"
        configs[0]["RESTART_ITER"] = n_steps-ad_steps
        configs[1]["UNST_ADJOINT_ITER"]= n_steps
        # configs[1]["RESTART_SOL"] = "YES"
        # configs[1]["RESTART_ITER"] = n_steps-ad_steps
        shutil.copy(configs[0]["RESTART_FILENAME"][0:-4]+"_"+str(n_steps-ad_steps-1).zfill(5)+".dat",tmp_dir_name)
        shutil.copy(configs[0]["RESTART_FILENAME"][0:-4]+"_"+str(n_steps-ad_steps-2).zfill(5)+".dat", tmp_dir_name)
        shutil.copy(configs[0]["RESTART_FILENAME"][0:-4]+"_"+str(n_steps-ad_steps-1).zfill(5)+".csv",tmp_dir_name)
        shutil.copy(configs[0]["RESTART_FILENAME"][0:-4]+"_"+str(n_steps-ad_steps-2).zfill(5)+".csv", tmp_dir_name)
        offset = n_steps- ad_steps
        n_steps = ad_steps

    os.chdir(tmp_dir_name)
    control_array_to_write = np.zeros(n_steps)

    control_array_to_write[n_steps-ad_steps:n_steps] = control_array
    np.savetxt(c_array, control_array_to_write)
    configs[0].dump(dir_cfg_name)
    configs[1].dump(ad_cfg_name)
    with open(bash_name,"w+") as f:
        f.write("#!/bin/bash\n")
        f.write("mpirun --use-hwthread-cpus python3 optimization_driver.py -f "+ c_array + " -d " + dir_cfg_name + " -a " + ad_cfg_name + " -n "+ str(n_steps)+" -t " + str(ad_steps) + " -o "+ str(offset))
    os.system("chmod +rwx "+ bash_name)
    result = subprocess.run("./"+bash_name, shell=True)
    if iter == 0:
        direct_history = np.genfromtxt(configs[0]["CONV_FILENAME"]+".csv", dtype=float, delimiter=',', names=True)
    else:
        direct_history = np.genfromtxt(configs[0]["CONV_FILENAME"]+"_"+str(offset).zfill(5)+".csv", dtype=float, delimiter=',', names=True)
    ad_history = np.genfromtxt(configs[1]["CONV_FILENAME"]+".csv", dtype=float, delimiter=',', names=True)
    goal_function =np.mean(direct_history['ComboObj'][n_steps-ad_steps:n_steps])
    os.chdir("..")
    if iter == 0:
        shutil.copy(tmp_dir_name + "/"+ configs[0]["RESTART_FILENAME"][0:-4]+"_"+str(n_steps-ad_steps-1).zfill(5)+".dat", ".")
        shutil.copy(tmp_dir_name + "/"+ configs[0]["RESTART_FILENAME"][0:-4]+"_"+str(n_steps-ad_steps-2).zfill(5)+".dat", ".")
        shutil.copy(tmp_dir_name + "/"+ configs[0]["RESTART_FILENAME"][0:-4]+"_"+str(n_steps-ad_steps-1).zfill(5)+".csv", ".")
        shutil.copy(tmp_dir_name + "/"+ configs[0]["RESTART_FILENAME"][0:-4]+"_"+str(n_steps-ad_steps-2).zfill(5)+".csv", ".")
    with open("main_history.txt", 'a+') as f:
        f.write(str(goal_function)+"\n")
    gradient = ad_history["Sens_Rot"]
    gradient = 1*gradient[::-1]
    # print(result.stdout.decode('utf-8'))
    shutil.copytree(tmp_dir_name, tmp_dir_name+"_"+str(iter))
    iter += 1
    return (goal_function, gradient)
def main():
    global iter
    iter = 100
    direct_config = SU2.io.Config("cylinder.cfg")
    adjoint_config = SU2.io.Config("cylinder_adjoint.cfg")
    start_vector = np.loadtxt("control_array.txt")
    # start_vector = np.zeros(200)
    eps_values = open("eps.txt", "w+")
    # compute_gradients(start_vector, (direct_config, adjoint_config))
    eps = 25
    old_grad = 1000
    old_goal = 1000
    for i in range(200):
        (goal, grad) = compute_gradients(start_vector, [direct_config, adjoint_config],600)
        start_vector = start_vector+eps*grad
        if  old_goal < goal:
            eps = eps/1.1
        elif old_goal > goal:
            eps = eps*1
        old_grad = np.mean(np.abs(grad))
        old_goal = goal
        eps_values.write(str(eps)+"\n")
        # shutil.copytree("tmp_dir_for_grad", "tmp_dir_for_grad_"+str(i))
    opt = {'maxiter': 3}
    # res  = scipy.optimize.minimize(compute_gradients, start_vector,method='BFGS',args=([direct_config, adjoint_config], 100), jac=True,  options=opt)
    # print(res.x)
    # print(res.message)
    # print(res.success)
if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()

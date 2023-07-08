import numpy as np
from sklearn.decomposition import IncrementalPCA
import time
import sys
from optparse import OptionParser	# use a parser for configuration
import pysu2			            # imports the SU2 wrapped module
from math import *
import os
import pysu2ad
from mpi4py import MPI
import SU2
import shutil
from matplotlib import pyplot as plt
import copy
class PodDriver:
    def __init__(self, config_path, n_of_modes, n_of_fields, n_of_points):
        self.header = ["\"Pressure\"","\"Velocity_x\"","\"Velocity_y\"","\"Nu_Tilde\"","\"Pressure_Coefficient\"","\"Density\"","\"Laminar_Viscosity\"","\"Heat_Capacity\"","\"Thermal_Conductivity\"","\"Skin_Friction_Coefficient_x\"","\"Skin_Friction_Coefficient_y\"","\"Heat_Flux\"","\"Y_Plus\"","\"Eddy_Viscosity\""]
        self.front_header = "\"PointID\", \"x\", \"y\", "
        self.n_of_fields = n_of_fields
        self.n_of_points = n_of_points
        self.config_path = config_path
        self.n_of_modes = n_of_modes
        self.main_config = SU2.io.Config(self.config_path)
        self.n_of_timesteps = self.main_config['TIME_ITER']
        self.column_hash_map = [0,1,2,3,7,8]
        self.x = np.empty([n_of_points])
        self.y = np.empty([n_of_points])
        self.ids  = np.empty([n_of_points])
        assert (self.n_of_timesteps-1)%self.n_of_modes == 0
        self.batch_number = int((self.n_of_timesteps-1)/self.n_of_modes)
        batch_array = np.empty([self.n_of_points, self.n_of_fields, self.n_of_modes])
        self.solution_filename = self.main_config['SOLUTION_FILENAME']
        self.ipca = []
        for i in range(n_of_fields):
            self.ipca.append(IncrementalPCA(n_components=self.n_of_modes, batch_size=self.n_of_modes, whiten=False))
        self.reduced_model = np.empty([self.n_of_timesteps, self.n_of_fields, self.n_of_modes])
    def reduce_flow(self):

        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        shutil.rmtree(str(self.n_of_modes))
        os.mkdir(str(self.n_of_modes))

        shutil.copy(self.main_config["MESH_FILENAME"], str(self.n_of_modes))
        os.chdir(str(self.n_of_modes))
        self.main_config.dump("tmp.cfg")
        SU2Driver = pysu2.CSinglezoneDriver("tmp.cfg", 1,comm)
        SU2Driver.Preprocess(0)
        SU2Driver.Run()
        SU2Driver.Postprocess()
        SU2Driver.Output(0)
        
        current_time_step = 1
        offset = 1
        for i in range(self.batch_number):
            batch_array = np.empty([self.n_of_points, self.n_of_fields, self.n_of_modes])

            for j in range(self.n_of_modes):
                SU2Driver.Preprocess(current_time_step)
                SU2Driver.Run()
                SU2Driver.Postprocess()
                SU2Driver.Output(current_time_step)
                
                current_time_step += 1
            for j in range(self.n_of_modes):
                file = self.solution_filename[0:-4]+"_"+str(i*self.n_of_modes+j+offset).zfill(5)+".csv"
                data = np.loadtxt(file, comments="\"", delimiter=",", dtype=float)
                if i == 0 and j == 0:
                    self.ids = data[0:self.n_of_points,0]
                    self.x = data[0:self.n_of_points,1]
                    self.y = data[0:self.n_of_points,2]
                    print(max(self.ids))
                    # exit()
                for k in range(self.n_of_fields):
                    batch_array[:, k, j] = data[0:self.n_of_points, self.column_hash_map[k]].reshape(1,-1)
            for j in range(self.n_of_fields):
                self.ipca[j].partial_fit(batch_array[:,k,:].transpose())
            for j in range(self.n_of_modes):
                file = self.solution_filename[0:-4]+"_"+str(i*self.n_of_modes+j+offset-1).zfill(5)+".csv"
                os.remove(file)
        
        
        SU2Driver.Finalize()
        SU2Reducer = pysu2.CSinglezoneDriver("tmp.cfg", 1,comm)
        SU2Reducer.Preprocess(0)
        SU2Reducer.Run()
        SU2Reducer.Postprocess()
        SU2Reducer.Output(0)
        
        for i in range(1,self.batch_number*self.n_of_modes):
            SU2Reducer.Preprocess(i)
            SU2Reducer.Run()
            SU2Reducer.Postprocess()
            SU2Reducer.Output(i)
            file = self.solution_filename[0:-4]+"_"+str(i).zfill(5)+".csv"
            data = np.loadtxt(file, comments="\"", delimiter=",", dtype=float)

            for j in range(self.n_of_fields):

                self.reduced_model[i,j,:] = self.ipca[j].transform(data[0:self.n_of_points, self.column_hash_map[j]].reshape(1,-1))
            os.remove(self.solution_filename[0:-4]+"_"+str(i-1).zfill(5)+".csv")
        

    def get_timestep(self, j):
        file_name = self.solution_filename[0:-4]+"_"+str(j).zfill(5)+".csv"
        file = open(file_name, "w+")
        data_to_write = np.empty([self.n_of_fields+3, self.n_of_points])
        data_to_write[0,:] = self.ids
   
        data_to_write[1,:] = self.x
        data_to_write[2,:] = self.y
        first_line = self.front_header
        for i in range(self.n_of_fields):
            first_line = first_line + self.header[self.column_hash_map[i]] + ", "
            data_to_write[i+3, :] = self.ipca[i].inverse_transform(self.reduced_model[j, i, :])
        first_line = first_line[0:-2]
        first_line = first_line + "\n"
        file.write(first_line)
        np.savetxt(file, data_to_write.transpose(), delimiter=", ")
        file.close()
    def drive_adjoint(self):
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        ad_config = copy.deepcopy(self.main_config)
        ad_config['MATH_PROBLEM'] = "DISCRETE_ADJOINT"
        ad_config.dump("tmp_ad.cfg")
        AD_driver = pysu2ad.CDiscAdjSinglezoneDriver("tmp_ad.cfg", 1,comm)
        current_ad_step = 0  
        for i in range(self.n_of_timesteps,0, -1):
            
            self.get_timestep(i-1)
            AD_driver.Preprocess(current_ad_step)
            AD_driver.Run()
            AD_driver.Postprocess()
            AD_driver.Output(current_ad_step)
            AD_driver.Update()
            current_ad_step += 1
def main():
    for i in range(5):
        driver = PodDriver("cylinder.cfg", 10*(i+1),5, 4791)
        driver.reduce_flow()
        driver.drive_adjoint()
        os.chdir("..")
    # fig, ax = plt.subplots()
    
    # # print(driver.ids)
    # # print(driver.x)
    # # print(driver.y)
    # # ax.tripcolor(driver.x, driver.y,modes[5,:])
    # plt.show()
if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
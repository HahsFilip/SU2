from checkpoint_driver import CheckpointDriver
import SU2
import copy
import os
class CheckpointOptimizer:
    dir_conf_path = "base.cfg"
    ad_conf_path = "base_ad.cfg"
    checkpoint_number = 10

    def __init__(self, conf_file):
        
        self.main_config = SU2.io.Config(conf_file)
        assert self.main_config["MATH_PROBLEM"] == "DISCRETE_ADJOINT"
        self.main_config["NUMBER_PART"] = 1
        self.ad_config = copy.deepcopy(self.main_config)
        self.dir_config = copy.deepcopy(self.main_config)
        self.dir_config.pop("RESTART_SOL")
        self.dir_config["MATH_PROBLEM"] = "DIRECT"
       
        
        self.iter_number = self.main_config["TIME_ITER"]
        
        self.ad_config.dump(self.ad_conf_path)
        self.dir_config.dump(self.dir_conf_path)
    def run_calculation(self):
        for j in range(10):
            self.driver = CheckpointDriver(self.checkpoint_number, self.dir_conf_path, self.ad_conf_path)
            self.driver.run_calculation(self.iter_number-1)
            
            state = SU2.run.projection(self.ad_config)
            gradients = state['GRADIENTS']['DRAG']
            for i in range(len(gradients)):
                gradients[i] = gradients[i]*10000
            
            self.ad_config.unpack_dvs(gradients)
            SU2.run.DEF(self.ad_config)
            os.rename("mesh_out.su2", "mesh_in.su2")
            os.rename("surface_deformed_00000.vtu", "surface_deformed_"+str(j).zfill(5)+".vtu")
            
def main():
    os.system("cp unsteady_naca0012_FFD.su2 mesh_in.su2")
    optimizer = CheckpointOptimizer("unsteady_naca0012_opt_ad.cfg")
    optimizer.run_calculation()
    

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
            

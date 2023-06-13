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
    def __init__(self, d) -> None:
        self.delta = d
        self.checkpoints.append(Checkpoints(0,1000000))
        pass
    def advance_solution(self, i):
        # i: iteration from which to restart
        self.n_of_points = len(self.checkpoints)
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
                self.checkpoints.pop(ind_of_max_disp)
                new_checkpoint = Checkpoints(i+1, 0)
                self.checkpoints.append(new_checkpoint)
            else:
                
                level = self.checkpoints[-1].level
                self.checkpoints.pop(-1)
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
    driver = CheckpointDriver(6)
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
            

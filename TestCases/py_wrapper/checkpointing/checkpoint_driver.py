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
        else:
            if is_dispensable:
                print("removed cp: " + str(ind_of_max_disp))
                self.checkpoints.pop(ind_of_max_disp)
                new_checkpoint = Checkpoints(i+1, 0)
                self.checkpoints.append(new_checkpoint)
            else:
                print("here")
                level = self.checkpoints[-1].level
                self.checkpoints.pop(-1)
                new_checkpoint = Checkpoints(i+1, level+1)
                self.checkpoints.append(new_checkpoint)
        self.n_of_points +=1
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
            
         
    def get_checkpoint_locations(self):
        check_pts = []
        for point in self.checkpoints:
            check_pts.append(point.i)
        return check_pts
    def print_checkpoints(self):
        for point in self.checkpoints:
            print(str(point.i) + "  " + str(point.level) + "  " + str(point.dispensable))

def main():
    driver = CheckpointDriver(3)
    for i in range(25):
        driver.advance_solution(i)
        driver.print_checkpoints()
        print("\n ")


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
            

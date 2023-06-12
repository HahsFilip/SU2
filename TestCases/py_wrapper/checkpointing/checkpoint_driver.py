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
    def __init__(self, d) -> None:
        self.delta = d
        pass
    def advance_solution(self, i):
        # i: iteration from which to restart
        assert i in self.checkpoints
        if self.n_of_points <= self.delta:
            new_checkpoint = Checkpoints(i+1, 0)
            self.checkpoints.append(new_checkpoint)
        
            

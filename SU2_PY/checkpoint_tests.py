#!/usr/bin/env python

## \file shape_optimization.py
#  \brief Python script for performing the shape optimization.
#  \author T. Economon, T. Lukaczyk, F. Palacios
#  \version 7.5.1 "Blackbird"
#
# SU2 Project Website: https://su2code.github.io
#
# The SU2 Project is maintained by the SU2 Foundation
# (http://su2foundation.org)
#
# Copyright 2012-2023, SU2 Contributors (cf. AUTHORS.md)
#
# SU2 is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# SU2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with SU2. If not, see <http://www.gnu.org/licenses/>.

import os, sys, shutil
from optparse import OptionParser
sys.path.append(os.environ['SU2_RUN'])
import SU2
from SU2 import eval
from SU2 import run

import copy

#  Main
# -------------------------------------------------------------------

def main():

    parser=OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="read config from FILE", metavar="FILE")
    parser.add_option("-n", "--partitions", dest="partitions", default=1,
                    help="number of PARTITIONS", metavar="PARTITIONS")


    (options, args)=parser.parse_args()

    options.partitions  = int( options.partitions )

    sys.stdout.write('\n-------------------------------------------------------------------------\n')
    sys.stdout.write('|    ___ _   _ ___                                                      |\n')
    sys.stdout.write('|   / __| | | |_  )   Release 7.5.1 \"Blackbird\"                         |\n')
    sys.stdout.write('|   \\__ \\ |_| |/ /                                                      |\n')
    sys.stdout.write('|   |___/\\___//___|   Aerodynamic Shape Optimization Script             |\n')
    sys.stdout.write('|                                                                       |\n')
    sys.stdout.write('-------------------------------------------------------------------------\n')
    sys.stdout.write('| SU2 Project Website: https://su2code.github.io                        |\n')
    sys.stdout.write('|                                                                       |\n')
    sys.stdout.write('| The SU2 Project is maintained by the SU2 Foundation                   |\n')
    sys.stdout.write('| (http://su2foundation.org)                                            |\n')
    sys.stdout.write('-------------------------------------------------------------------------\n')
    sys.stdout.write('| Copyright 2012-2023, SU2 Contributors (cf. AUTHORS.md)                |\n')
    sys.stdout.write('|                                                                       |\n')
    sys.stdout.write('| SU2 is free software; you can redistribute it and/or                  |\n')
    sys.stdout.write('| modify it under the terms of the GNU Lesser General Public            |\n')
    sys.stdout.write('| License as published by the Free Software Foundation; either          |\n')
    sys.stdout.write('| version 2.1 of the License, or (at your option) any later version.    |\n')
    sys.stdout.write('|                                                                       |\n')
    sys.stdout.write('| SU2 is distributed in the hope that it will be useful,                |\n')
    sys.stdout.write('| but WITHOUT ANY WARRANTY; without even the implied warranty of        |\n')
    sys.stdout.write('| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU      |\n')
    sys.stdout.write('| Lesser General Public License for more details.                       |\n')
    sys.stdout.write('|                                                                       |\n')
    sys.stdout.write('| You should have received a copy of the GNU Lesser General Public      |\n')
    sys.stdout.write('| License along with SU2. If not, see <http://www.gnu.org/licenses/>.   |\n')
    sys.stdout.write('-------------------------------------------------------------------------\n')

    checkpoints( options.filename)

#: main()
def start_from_checkpoint(needed_step, checkpoint_array, conf):
    konfig = copy.deepcopy(conf)
    restart_point = min(checkpoint_array, key=lambda x:abs(x-needed_step));
    time_step = 1
    current_iter = restart_point
    for i in range(needed_step-restart_point):
        sys.stdout.write(str(i))

        konfig['TIME_ITER'] = current_iter + time_step+1
        konfig['RESTART_ITER'] = current_iter+1
        SU2.run.direct(konfig)

        current_iter += time_step
        if current_iter-3 not in checkpoint_array and current_iter-2 not in checkpoint_array:
            if current_iter-2 < 10:
                os.remove("restart_flow_0000"+str(current_iter-2)+".dat")
            else:
                os.remove("restart_flow_000"+str(current_iter-2)+".dat")

def checkpoints( filename, partitions  = 0):
    # Config
    config = SU2.io.Config(filename)
    config.NUMBER_PART = partitions
    sys.stdout.write(str(filename))
    tmp_file_name = "/home/filip/SU2/SU2Tutorials/design/Unsteady_Shape_Opt_NACA0012/unsteady_naca0012_opt_dump.cfg"
    # State
    state = SU2.io.State()
    
    state.find_files(config)
    current_iter = 1
    time_step = 1
    config['TIME_ITER'] = time_step+1
    config['NZONES'] = 1
    SU2.run.direct(config)
    config['RESTART_SOL'] = 'YES'
    current_iter += 1
    check_pts = range(0,25,10)

    for i in range(25):
        sys.stdout.write(str(i))
        
        config['TIME_ITER'] = current_iter + time_step
        config['RESTART_ITER'] = current_iter
        current_iter += time_step
        SU2.run.direct(config)
        if current_iter-3 not in check_pts and current_iter-2 not in check_pts:
            if current_iter-3 < 10:
                os.remove("restart_flow_0000"+str(current_iter-3)+".dat")
            else:
                os.remove("restart_flow_000"+str(current_iter-3)+".dat")

    start_from_checkpoint(13, check_pts, config)

    config['MATH_PROBLEM'] = 'DISCRETE_ADJOINT'
    config['UNST_ADJOINT_ITER'] = current_iter-1
    config['TIME_ITER'] = 1
    config['RESTART_SOL'] = 'NO'
    config['GRADIENT_METHOD'] = 'DISCRETE_ADJOINT'
    # SU2.run.adjoint(config)

    


#: shape_optimization()


# -------------------------------------------------------------------
#  Run Main Program
# -------------------------------------------------------------------

# this is only accessed if running from command prompt
if __name__ == '__main__':
    main()


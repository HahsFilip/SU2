#!/bin/bash
python mpi_driver.py
cd test_dir
mpirun --use-hwthread-cpus python optimization_driver.py
#!/bin/bash
mpirun --use-hwthread-cpus python optimization_driver.py -f control_array.txt -d tmp_dir.cfg -a tmp_ad.cfg -n 10
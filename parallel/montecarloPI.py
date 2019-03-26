from mpi4py import MPI
import sys
import numpy as np
import random

# Montecarlo PI can be used to find pi over random samples.
"""
    Let a square with a centrif circle with radius R.
    Area of the square is   AS = (2r)^2
    Area of the circle is   AC = pi*r^2
    
    Note then that -> AS / AC = pi/4



"""
SAMPLES_TO_COMPUTE = 100000000

circle_pts = 0
radius = 1

# Compute all random samples
for i in range(SAMPLES_TO_COMPUTE):
    x = np.random.uniform(-radius,radius,1)
    y = np.random.uniform(-radius,radius,1)

    if(x**2 + y**2 < radius**2):
        circle_pts = circle_pts + 1

print circle_pts
pi_estim = float(circle_pts)/SAMPLES_TO_COMPUTE*4

print pi_estim

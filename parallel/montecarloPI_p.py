from mpi4py import MPI
import sys
import numpy as np

TOTAL_SAMPLES = int( sys.argv[1])

TaskMaster = 0
comm = MPI.COMM_WORLD
worldSize = comm.Get_size()
rank = comm.Get_rank()
processorName = MPI.Get_processor_name()

radius = 1

def samplerInsideCircle(numSamples):

    circle_pts = 0
    
    for i in range(numSamples):
        x = np.random.uniform(-radius,radius,1)
        y = np.random.uniform(-radius,radius,1)

        if(x**2 + y**2 < radius**2):
            circle_pts = circle_pts + 1

    # return circle points
    return circle_pts

if (rank == TaskMaster):

    samplesPerProcesor = TOTAL_SAMPLES / (worldSize-1)

    for proID in range(1, worldSize):
         comm.send(samplesPerProcesor, dest=proID, tag=proID)


if (rank != TaskMaster):
    # Get number of samples to compute
    temp_Samples = comm.recv(source=TaskMaster, tag=rank)
    points_in_circle = samplerInsideCircle(temp_Samples)
    comm.send(points_in_circle, dest=TaskMaster, tag=rank)

comm.Barrier()

if (rank == TaskMaster):
    # get total points inside circle
    tp_circle = 0
    for proID in range(1, worldSize):
        tp = comm.recv(source=proID, tag=proID)
        tp_circle = tp_circle + tp
    
    # print calculated pi
    COMPUTED_SAMPLES = int(TOTAL_SAMPLES / (worldSize-1)) * (worldSize-1)
    pi_estim = float(tp_circle)/COMPUTED_SAMPLES*4
    print "Estimated PI: ", pi_estim
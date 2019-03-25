# Author: Sebastian Rivera
# Date: 24 March. 2019

from mpi4py import MPI
import numpy as np
import sys

# ===== GLOBAL VARIABLES =====
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
worldSize = comm.Get_size()
TASK_MASTER = 0
# ============================

def printBuckets(buckets):
    for bucket in buckets:
        print("\n ===================== ")
        print(bucket)
        print(" ===================== \n")

def parallelBucketSort(dSize, lowBound, upperBound):
    global comm
    global rank
    global worldSize
    global TASK_MASTER
    
    if rank == TASK_MASTER:
        rawData = np.random.uniform(low=lowBound, high=upperBound, size=dSize)
        buckets = []
        rangeOfData = upperBound - lowBound
        rangePerRank = rangeOfData / worldSize
        limits = []

        # Compute the limits of each bucket & Create one bucket for each rank in worldSize
        for thisRank in range(worldSize):
            thisLimit = lowBound + ((thisRank + 1) * rangePerRank)
            limits.append(thisLimit)
            buckets.append([])

        # Iterate through rawData to split it into the buckets
        for num in rawData:
            if num < limits[0]:
                buckets[0].append(num)
            elif num < limits[1]:
                buckets[1].append(num)
            elif num < limits[2]:
                buckets[2].append(num)
            else:
                buckets[3].append(num)

        # Print buckets before ordering them
        print("== BUCKETS BEFORE ORDERING ==")
        # printBuckets(buckets)

        # Send the corresponding bucket to each rank
        for thisRank in range(1,worldSize):
            comm.send(buckets[thisRank], dest=thisRank, tag=thisRank)

        # Order the data assigned to TASK MASTER
        buckets[TASK_MASTER].sort()

        # Receive ordered data from other processors & append
        for thisRank in range(1,worldSize):
            buckets[thisRank] = comm.recv(source=thisRank, tag=thisRank)

        # Display the ordered data
        print("== BUCKETS AFTER ORDERING ==")
        # printBuckets(buckets)


    if rank != TASK_MASTER:
        # Reveive data to be ordered from TASK MASTER
        data = comm.recv(source=TASK_MASTER, tag=rank)

        # Order the data
        data.sort()

        # Send it back to TASK MASTER
        comm.send(data, dest=TASK_MASTER, tag=rank)



if __name__ == "__main__":
    dataSize = int(sys.argv[-1])
    # lowDataBound = float(sys.argv[-2])
    lowDataBound = -100.0
    # highDataBound = float(sys.argv[-1])
    highDataBound = 100.0

    parallelBucketSort(dataSize, lowDataBound, highDataBound)
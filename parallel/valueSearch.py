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

def lookForValue(targetValue, nums):
    assert(type(nums) == list)
    try:
        ans = nums.index(targetValue)
    except ValueError:
        ans = -1
    
    return ans

def parallelBucketSort(dSize, lowBound, upperBound, targetValue):
    global comm
    global rank
    global worldSize
    global TASK_MASTER
    
    if rank == TASK_MASTER:
        rawData = np.random.uniform(low=lowBound, high=upperBound, size=dSize)
        roundedData = np.round(rawData, decimals=2)
        listOfData = list(roundedData)
        rangePerRank = int(dSize / worldSize)
        limits = []

        # Compute the limits to divide the array
        # for thisRank in range(worldSize):
        #     thisLimit = lowBound + ((thisRank + 1) * rangePerRank)
        #     limits.append(thisLimit)

        print(" == BEGIN THE SEARCH FOR {}... == ".format(targetValue))
        # print(listOfData)
        taskMasterData = listOfData[0:rangePerRank]

        # Send the corresponding range to each rank
        for thisRank in range(1,worldSize):
            thisLow = thisRank * rangePerRank
            thisHigh = (thisRank+1) * rangePerRank
            thisData = {"nums" : listOfData[thisLow:thisHigh],
                        "targetVal" : targetValue}
            # print(thisData)
            comm.send(thisData, dest=thisRank, tag=thisRank)

        # Look for target value on the batch
        indexAns = lookForValue(targetValue, taskMasterData)

        # Receive results from other processors
        for thisRank in range(1,worldSize):
            thisIndex = comm.recv(source=thisRank, tag=thisRank)
            realIndex = thisIndex + (thisRank * rangePerRank)
            if thisIndex != -1:
                indexAns = realIndex

        # Display the ordered data
        if indexAns != -1:
            print("\n == Element {} found at index position {} ==".format(listOfData[indexAns], indexAns))
        else:
            print("\n == Element not found. ==")


    if rank != TASK_MASTER:
        # Reveive data to be ordered from TASK MASTER
        data = comm.recv(source=TASK_MASTER, tag=rank)

        # Order the data
        ans = lookForValue(data["targetVal"], data["nums"])

        # Send it back to TASK MASTER
        comm.send(ans, dest=TASK_MASTER, tag=rank)



if __name__ == "__main__":
    dataSize = int(sys.argv[-2])
    lowBound = 0.0
    highBound = 100.0
    targetValue = float(sys.argv[-1])

    parallelBucketSort(dataSize, lowBound, highBound, targetValue)
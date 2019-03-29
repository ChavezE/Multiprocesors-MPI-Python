# Author: Sebastian Rivera
# Date: 20 March. 2019

from mpi4py import MPI
import numpy as np
from math import sqrt
import sys

# ===== GLOBAL VARIABLES =====
COMM = MPI.COMM_WORLD
RANK = COMM.Get_rank()
WORLD_SIZE = COMM.Get_size()
TASK_MASTER = 0
# ============================



def Create_Matrix(N):
    rawMat = np.random.uniform(1, 100, (N,N))
    roundedMat = np.round(rawMat, decimals=2)

    # Create 0's on the main diagonal
    for i in range(N):
        roundedMat[i,i] = 0

    print("\n Initial Mat is: ")
    print(roundedMat)
    return roundedMat

def Distribute_Sub_Matrices(rowsPerProcessor, remainingRows, Mat):
    lowerBound = 0
    returnSubMat = None
    limitsPerProcessor = np.zeros(Mat.shape[0])

    for thisRank in range(WORLD_SIZE):
        if thisRank == TASK_MASTER:
            upperBound = lowerBound + rowsPerProcessor + remainingRows
            returnSubMat = Mat[lowerBound:upperBound]
        else:
            upperBound = lowerBound + rowsPerProcessor
            sendSubMat = Mat[lowerBound:upperBound]
            data = {
                "subMat" : sendSubMat,
                "lowerBound" : lowerBound
            }
            COMM.send(data, dest=thisRank, tag=thisRank)

        lowerBound = upperBound
        limitsPerProcessor[thisRank] = lowerBound

    return returnSubMat, limitsPerProcessor

def Kth_Row_Is_Mine(bcastRoot):
    return RANK == bcastRoot

def Kth_Floyd_Optimization(k, thisKthRow, subMat):
    # M is a matrix with the costs of going through each road
    rows, cols = subMat.shape

    for i in range(rows):
        for j in range(cols):
            subMat[i,j] = min(subMat[i,j], subMat[i,k] + thisKthRow[j])
    
    return subMat

def floyds_shortest_paths(graph):
    N = graph.shape[0]
    for k in range(N):
        for i in range(N):
            for j in range(N):
                graph[i,j] = min(graph[i,j],graph[i,k] + graph[k,j])

    return graph

def Parallel_Floyd_Warshall(sizeOfMat):
    # The matrix used on the Floyd Washall algorithm is always square

    # (I.a) == Create & Distribute Matrix within ALL processors ==
    if RANK == TASK_MASTER:
        Mat = Create_Matrix(sizeOfMat)
        rowsPerProcessor = int(sizeOfMat / WORLD_SIZE)
        remainingRows = sizeOfMat % WORLD_SIZE

        # Distribute the matrix
        subMat, limitsPerProcessor = Distribute_Sub_Matrices(rowsPerProcessor, remainingRows, Mat)
        lowerBound = 0
        upperBound = subMat.shape[0]
        

    # (I.b) == Receive my submatrix, if RANK != TASK_MASTER
    if RANK != TASK_MASTER:
        data = COMM.recv(source=TASK_MASTER, tag=RANK)
        subMat = data["subMat"]
        lowerBound = data["lowerBound"]
        upperBound = lowerBound + subMat.shape[0]
        limitsPerProcessor = None

    limitsPerProcessor = COMM.bcast(limitsPerProcessor, root=0)
    # print("\n == From rank {}, the subMat BEFORE is: {}".format(RANK, subMat))

    # (II) == Iterate from k --> {0,N} to optimize subMat ==
    bcastRoot = 0 # Pointer to limitsPProcessor to define the bcast root
    for k in range(sizeOfMat):

        # Check if its time for the (bcastRoot+1) processor to bcast
        if k >= limitsPerProcessor[bcastRoot]:
            bcastRoot += 1

        # Check if KthRow is within my limits
        if Kth_Row_Is_Mine(bcastRoot):
            thisKthRow = subMat[k-lowerBound]
        else: 
            thisKthRow = None

        thisKthRow = COMM.bcast(thisKthRow, root=bcastRoot)
        subMat = Kth_Floyd_Optimization(k, thisKthRow, subMat)

        COMM.Barrier()
        

    # (III) == Send subMats back to TASK_MASTER to create the finalMat
    if RANK != TASK_MASTER:
        COMM.send(subMat, dest=TASK_MASTER, tag=RANK)
    if RANK == TASK_MASTER:
        finalMat = subMat
        for thisRank in range(1, WORLD_SIZE):
            thisSubMat = COMM.recv(source=thisRank, tag=thisRank)
            finalMat = np.concatenate((finalMat, thisSubMat))

        print("\n Final Mat is: ")
        print(finalMat)
        
        

if __name__ == "__main__":
    N = int(sys.argv[-1])
    Parallel_Floyd_Warshall(N)
    
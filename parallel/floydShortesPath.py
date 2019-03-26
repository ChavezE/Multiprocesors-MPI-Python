# Author: Sebastian Rivera
# Date: 20 March. 2019

from mpi4py import MPI
import numpy as np
from math import sqrt
import sys

# ===== GLOBAL VARIABLES =====
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
worldSize = comm.Get_size()
TASK_MASTER = 0
# ============================


def floydWarshallOptimization(M, kRow, kCol):
    # M is a matrix with the costs of going through each road
    N = M.shape[0]
    for i in range(N):
        for j in range(N):
            M[i][j] = min(M[i][j], kCol[i] + kRow[j])
    
    # print(M) 

def createMatrix(N):
    rawMat = np.random.uniform(0, 100, (N,N))
    roundedMat = np.round(rawMat, decimals=2)
    return roundedMat

def distributeMat(Mat):
    sizeOfMat = Mat.shape
    sizeOfSubMatrix = int(sizeOfMat[0] / sqrt(worldSize))
    rankOfProcessor = 0
    TMData = {}

    for xOffset in range(0, sizeOfMat[0], sizeOfSubMatrix):
        for yOffset in range(0, sizeOfMat[1], sizeOfSubMatrix):
            # Compute the submatrix using offsets
            thisMat = Mat[xOffset:xOffset+sizeOfSubMatrix, yOffset:yOffset+sizeOfSubMatrix]
            initX = xOffset
            initY = yOffset
            data = {
                'mat': thisMat,
                'x', initX,
                'y', initY
            }
            if rankOfProcessor == TASK_MASTER:
                TMData = data
            else:
                comm.send(data, dest=rankOfProcessor, tag=rankOfProcessor)
            rankOfProcessor += 1
    
    # Return the submatrix to Task Master
    return TMData

def computeSlicesOfK(M, initX, initY, k):
    lengthOfM = M.shape[0]
    kthRowSlice = None
    kthColSlice = None

    if k >= initX and k < initX + lengthOfM:
        kthRowSlice = M[k,:]
    if k >= initY and k < initY + lengthOfM:
        kthColSlice = M[:,k]
    
    return kthRowSlice, kthColSlice


def floydAlgorithm(sizeOfMat):
    # The matrix used on the Floyd Washall algorithm is always square

    # (I) == Distribute the Matrix from the Task Master to the remaining processors ==
    if rank == TASK_MASTER:
        weightsMatrix = createMatrix(sizeOfMat)
        # print("== Original Weights Matrix ==")
        # print(weightsMatrix)
        
        # Distribute the Matrix in N/sqrt(worldSize) x N/sqrt(worldSize) matrices
        data = distributeMat(weightsMatrix)
        initX = data['x']
        initY = data['y']
        thisMat = data['mat']
        # print("From rank {} ==> {}".format(rank, thisMat))
    
    # (II) == Each Processor that isn't the task master receives its own subMatrix ==
    if rank != TASK_MASTER:
        # Receive its corresponding submatrix, e.g. if sizeOfMat = 4 ==> submatrix is of 2x2
        data = comm.recv(source=TASK_MASTER, tag=rank)
        initX = data['x']
        initY = data['y']
        thisMat = data['mat']

        # print("From rank {} ==> {}".format(rank, thisMat))

    comm.Barrier()
    # (III) == Loop for each value of k to compute the shortest paths ==

    # ==> Iterate range(0 to k); bcast kRow and/or kCol slices
    # TODO create a function, bcause this will be called from either ...
    # ... TASK MASTER and the other processors
    for k in range(0, sizeOfMat):
        # These two arrays are placeholders to be used in future steps
        kRow = None
        kColumn = None
        # a. If I have some slice of kthRow or kthColumn, broadcast it to all other processors
        kRowSlice, kColSlice = computeSlicesOfK(thisMat, initX, initY, k)

        # a.1 Arrange the data to be sent
        # TODO move this section into a function
        rowData2 = None
        colData2 = None

        if kRowSlice != None:
            rowData1 = {
                "row_slice": kRowSlice,
                "x": initX
            }
        else:
            rowData1 = None

        if kColSlice != None:
            colData1 = {
                "col_slice": kColSlice,
                "x": initY
            }
        else:
            colData1 = None

        rowData1 = comm.bcast(rowData1, )

        # b. Recevie the slices of kthRow and kthColumn that I don't have
        

        # c. Arrange the slices to build up the final kthRow and kthColumn

        # d. Call the function floydWarshallOptimization() for the kth time
        # TODO verify that Python handles the Matrices as reference parameters
        floydWarshallOptimization(thisMat, kRow, kCol)

    



if __name__ == "__main__":
    N = 4
    floydAlgorithm(N)
    
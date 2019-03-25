# Author: Sebastian Rivera
# Date: 20 March. 2019

from mpi4py import MPI
import numpy as np
import sys

# ===== GLOBAL VARIABLES =====
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
worldSize = comm.Get_size()
TASK_MASTER = 0
# ============================


def floydWarshallOptimization(M):
    # M is a matrix with the costs of going through each road
    N = M.shape[0]
    for k in range(N):
            for i in range(N):
                    for j in range(N):
                            M[i][j] = min(M[i][j], M[i][k] + M[k][j])
    print(M)
    return M


def floydAlgorithm():
    global comm
    global rank
    global worldSize
    global TASK_MASTER

    totalRows = int(sys.argv[-2])
    totalCols = int(sys.argv[-1])


    if rank == TASK_MASTER:
        costMatrix = np.random.rand(totalRows, totalCols)
        costMatrix[1] *= 100
        costMatrix[3] *= 30

        totalRows = costMatrix.shape[0]
        # totalCols = costMatrix.shape[1]
        
        rowsPerProcessor = int(totalRows / worldSize)
        remainingRows = int(totalRows % worldSize)
        rowsSent = []
        offset = 0

        print("\n== ORIGINAL MATRIX ==\n")
        print(costMatrix)
        
        # Distribute the rows evenly within the processors
        for rankOfProcessor in range(worldSize):

            if rankOfProcessor == TASK_MASTER:
                taskMasterBatch = costMatrix[offset:offset+rowsPerProcessor]
                offset += rowsPerProcessor
                rowsSent.append(rowsPerProcessor)

            elif rankOfProcessor != TASK_MASTER:
                thisRows = rowsPerProcessor
                if remainingRows != 0:
                    thisRows += 1
                    remainingRows -= 1

                batchRows = costMatrix[offset:offset+thisRows]
                offset += thisRows
                rowsSent.append(thisRows)

                comm.send(batchRows, dest=rankOfProcessor, tag=rankOfProcessor)

        taskMasterBatch = floydWarshallOptimization(taskMasterBatch)
        offset = 0

        for rankOfProcessor in range(worldSize):
            thisRows = rowsSent.pop(0)
            if rankOfProcessor == TASK_MASTER:
                costMatrix[offset:offset+thisRows] = taskMasterBatch

            elif rankOfProcessor != TASK_MASTER:
                data = comm.recv(source=rankOfProcessor, tag=rankOfProcessor)
                costMatrix[offset:offset+thisRows] = data
            
            offset += thisRows
        
        print("\n== FINAL MATRIX ==\n")
        print(costMatrix)
        
        

    elif rank != TASK_MASTER:
        rowsBatch = comm.recv(source=TASK_MASTER, tag=rank)
        rowsBatch = floydWarshallOptimization(rowsBatch)
        comm.send(rowsBatch, dest=TASK_MASTER, tag=rank)


if __name__ == "__main__":
    floydAlgorithm()
    
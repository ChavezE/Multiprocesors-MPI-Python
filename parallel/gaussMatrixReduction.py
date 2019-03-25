# Author: Sebastian Rivera
# Date: 18 March. 2019

from mpi4py import MPI
import numpy as np
import sys

# ===== GLOBAL VARIABLES =====
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
worldSize = comm.Get_size()
TASK_MASTER = 0
# ============================

def isDataEmpty(d):
    return d == {}

# - Gauss reduction
def gaussReductionMPI():
    # == Local Variable Declaration & Global Import ==
    global comm
    global rank
    global worldSize
    global TASK_MASTER

    totalRows = int(sys.argv[-2])
    totalCols = int(sys.argv[-1])

    if rank == TASK_MASTER: # Prepare the Local Variables & Data
        # TODO check if the len(sys.argv) has enough arguments, i.e. rows & cols
        # Rows & Cols are sent as a paramter through the CLI
        gaussMat = np.random.rand(totalRows, totalCols) * 10
        # gaussMat = np.around(gaussMat)
        # If rows is not a multiple of (world size - 1), send one more row until residual is zero
        residualApport = float(1/(worldSize-1)) 
        print("\n ===== INITIAL GAUSS MATRIX =====")
        print(gaussMat)
    
    for pivotPosition in range(0, totalRows-1): # Last row will never be pivot

        # == TASK MASTER will divide the rows within the remaining processors ==
        if rank == TASK_MASTER:
            # print(" ===== GAUSS MATRIX at PIVOT {} =====".format(pivotPosition))
            # print(gaussMat)

            # == Local TASK MASTER variables ==
            numRowsSent = []
            rowsReceived = 0
            offsetToSend =  pivotPosition + 1
            offsetToArrange = offsetToSend
            pivotRow = gaussMat[pivotPosition]

            rowsPerProcessor = int((totalRows-1-pivotPosition) / (worldSize-1))
            residualRows = int((totalRows-1-pivotPosition)) % (worldSize-1)

            # print("For pivot {} the rows per processor are {} and the residual is {}\n".format(pivotPosition, rowsPerProcessor, residualRows))

            # == Loop to distribute & send the rows ==
            for rankOfProcessor in range(worldSize):

                if rankOfProcessor != TASK_MASTER:
                    thisRows = rowsPerProcessor
                    try:
                        # Try to add the last element, if exists
                        offsetToSend += numRowsSent[-1]
                    except IndexError as error:
                        pass

                    data = {}

                    if residualRows != 0.0: 
                        thisRows += 1
                        # residualRows -= residualApport
                        residualRows -= 1

                    numRowsSent.append(thisRows)

                    if thisRows > 0:
                        data = {
                            "pivRow"    : pivotRow,
                            "pivPos"    : pivotPosition,
                            "batchRows" : gaussMat[int(offsetToSend):int(offsetToSend+thisRows)]
                        }

                    comm.send(data, dest=rankOfProcessor, tag=rankOfProcessor)

            # == Loop to receive the rows & rearrange them ==
            for rankOfProcessor in range(worldSize):

                if rankOfProcessor != TASK_MASTER:
                    # sizeOfBatchRows = numRowsSent.pop(0)
                    sizeOfBatchRows = numRowsSent[rankOfProcessor-1]
                    if sizeOfBatchRows > 0:
                        batchRows = comm.recv(source=rankOfProcessor, tag=rankOfProcessor)

                        tempOffset = offsetToArrange + rowsReceived 
                        rowsReceived += sizeOfBatchRows

                        gaussMat[tempOffset:tempOffset + sizeOfBatchRows] = batchRows
            
            if pivotPosition % 100 == 0:
                print("\n == Gauss Matrix at pivot {}".format(pivotPosition))
                print(gaussMat)

        # == RANK IS NOT TASK MASTER ==
        if rank != TASK_MASTER:
        
            data = comm.recv(source=TASK_MASTER, tag=rank)

            if not isDataEmpty(data):
                pivotRow = data["pivRow"]
                pivotPos = data["pivPos"]
                batchRows = data["batchRows"]
                sizeOfBatchRows = batchRows.shape[0]
                                        

                for idxRow in range(sizeOfBatchRows):
                    row = batchRows[idxRow]

                    pivotCoeff = -(row[pivotPos] / pivotRow[pivotPos])
                    thisPivRow = pivotCoeff * pivotRow

                    batchRows[idxRow] = np.add(row, thisPivRow)

                # print("Hello from processor {} in pivot {} the data is: {}\n".format(rank, pivotPos, batchRows))
                comm.send(batchRows, dest=TASK_MASTER, tag=rank)



    if rank == TASK_MASTER:
        print("\n\n ===== FINAL GAUSS MATRIX =====")
        gaussMat = np.around(gaussMat)
        print(gaussMat)
        # for r in gaussMat:
        #     print(r)
# - Floyd's minimal route

# - Bucket sort

# - Search

if __name__ == "__main__":
    gaussReductionMPI()
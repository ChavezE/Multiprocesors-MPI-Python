#!/usr/bin/env python
"""
    -- Author:  
        Emilio Chavez Madero, chaaveze@gmail.com
    --Description:
        Multiplyes two matrices using mpi4py. 
        Naive row distribution implementation.
"""
# LIBRARIES
from mpi4py import MPI
import sys
import numpy as np

# GENERAL CONSTANTS
MOCK_MATRIX_DATA = True

# MPI DEFINITIONS
comm = MPI.COMM_WORLD
worldSize = comm.Get_size()
rank = comm.Get_rank()
processorName = MPI.Get_processor_name()
TASK_MASTER = 0

# Method for TASK_MASTER
def sendWorkToProcess(mat_a):
    print("Sending work")

    num_rows, num_cols = mat_a.shape

    # CALCULATE NUMBER OF ROWS PER WORKER
    rowsToComputePerP = int(num_rows / (worldSize-1))

    # Missing values will be handled by the last procesor
    # TODO: implement better load balance, however this wont affec the result
    residualWork = num_rows % (worldSize-1)
    
    # SENT ROWS TO EACH WORKER
    for processorID in range(1, worldSize):
        rowsOffset = (processorID-1)*rowsToComputePerP

        # LAST PROCESOR WILL HANDLE THE RESIDUAL
        if (processorID == worldSize -1):
            rowsToComputePerP = rowsToComputePerP + residualWork

        # SEND HOW MANY ROWS AND WHAT OFFSET EACH PROCESS WILL DO
        comm.send(rowsToComputePerP, dest=processorID, tag=processorID)
        
        # SEND THE OFFSET SO PROCESOR CAN COMPUTE PROPER INDEX
        comm.send(rowsOffset, dest=processorID, tag=processorID)

        # SEND ROWS
        for j in range(0, rowsToComputePerP):
            rowIndex = j + rowsOffset
            comm.Send([mat_a[rowIndex, :], MPI.INT], dest=processorID, tag=rowIndex)

# Method for workers
def receiveRowsAndComputeWork(mat_b):
    num_rows, num_cols = mat_b.shape
    # print ("Mat B shape : {},{}".format(num_rows,num_cols))

    rowsToCompute = comm.recv(source=TASK_MASTER, tag=rank)
    rowsOffset = comm.recv(source=TASK_MASTER, tag=rank)

    recev_data = []
    # RECEIVE ROWS AND STACK THEM
    for j in range(0, rowsToCompute):
        rowIndex = j + rowsOffset
        c = np.empty(shape=num_cols)
        comm.Recv([c, MPI.INT], source=TASK_MASTER, tag=rowIndex)
        recev_data.append(c)

    # print("procesor {}, has the recev_data {}".format(rank, recev_data))

    # PREPARE RESPONSE OBJECT
    response = []

    # LOOP AND PROCESS CORRESPONDING COLUMNS
    t_start = MPI.Wtime()
    for row_num in range(0, rowsToCompute):
        r = recev_data[row_num]

        row_result = []
        # MULTIPLY ROW BY COLUMN
        for j in range(0, num_cols):
            mult_result = 0
            # GET COLUMN FROM MATRIX B
            q = mat_b[:, j]

            for x in range(0, num_rows):
                mult_result = mult_result + (r[x]*q[x])
            
            # print ("Added {} to the row result".format(mult_result))
            row_result.append(mult_result)

        response.append(row_result)

    comm.send(response, dest=TASK_MASTER, tag=rank)

# Method to carry out the multiplication
def matrixMultiply(row_num, col_num, printExpexted=False):
    # LET ALL PROCESSORS HAVE A COPUY OF THE SECOND MATH
    mat_b = retrieveMatrix(row_num, col_num)

    #####################################################
    #               DISTRIBUTE  WORK                    #
    #####################################################
    if rank == TASK_MASTER:
        mat_a = retrieveMatrix(row_num,col_num)

        if (printExpexted):
            print ("Expected result is")
            print (np.matmul(mat_a,mat_b))
        
        # CALL FUNCTION TO DISTRIBUTE WORK
        sendWorkToProcess(mat_a)
        print("Work sent")

    #####################################################
    #               WORKERS COMPUTE                    #
    #####################################################
    if rank != TASK_MASTER:
        receiveRowsAndComputeWork(mat_b)

    #####################################################
    #               GATHER AND REDUCE                   #
    #####################################################
    if rank == TASK_MASTER:
        print("Work received")

        result = []
        for processorID in range(1, worldSize):
            row_result = comm.recv(source=processorID, tag=processorID)
            result.append(row_result)

        print("End")
        print("Result AxB.\n")
        print(result, end='\n')

# Method for grabing the matrix to multiply
def retrieveMatrix(row_num, col_num):
    def populateMatrix(matrix, rows, cols):
        for r in range(0, rows):
            for j in range(0, cols):
                matrix[r][j] = r+j
    
    if MOCK_MATRIX_DATA:
        # Create a mock mat and fill it
        mock_mat = np.zeros(shape=(row_num, col_num))
        populateMatrix(mock_mat,row_num, col_num)
    
        return mock_mat

if __name__ == "__main__":
    rows = int(sys.argv[-2])
    cols = int(sys.argv[-1])
    
    matrixMultiply(rows, cols)

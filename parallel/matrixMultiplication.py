#!/usr/bin/env python

"""
    --Description:
    Multiplyes two matrices using mpi4py.
"""

from mpi4py import MPI
import sys
import numpy as np

numberRows = int( sys.argv[1])
numberColumns = int( sys.argv[2])
TaskMaster = 0

assert numberRows == numberColumns


a = np.zeros(shape=(numberRows, numberColumns))
b = np.zeros(shape=(numberRows, numberColumns))
c = np.zeros(shape=(numberRows, numberColumns))


def populateMatrix( p ):
    for processorID in range(0, numberRows):
        for j in range(0, numberColumns):
            p[processorID][j] = processorID+j

comm = MPI.COMM_WORLD
worldSize = comm.Get_size()
rank = comm.Get_rank()
processorName = MPI.Get_processor_name()

#print ("Process %d started.\n" % (rank))

# All processors need having the second matrix
# TODO 
# send this matrix by some clean way to function like use
populateMatrix(b)

comm.Barrier()

# TASK MASTER PROCESOR SHOULD THEN THE SECOND MATRIX TO 
# OTHERS PROCESORS AND THEN RETRIEVE THE CALCULATIONS
if rank == TaskMaster:
    def sendWorkToProcess():
        #print ("Initialising Matrix A and B (%d,%d).\n" % (numberRows, numberColumns))
        print ("Start")

        # Matrix a will be splited into workers
        populateMatrix(a)
        print (a)

        """
        Sending criteria

        each process will calulate 
            rowsPerP = numberRows/(woldsize - 1)
        rows_per_process = 
        [0]     [ . . . . . ]   lower_bound
        [1]     [ . . . . . ]   upper_bound
        [2]     [ . . . . . ]
        [.]     [ . . . . . ]
        [.]     [ . . . . . ]
        [.]     [ . . . . . ]
        [n]     [ . . . . . ]

        NOTE -> THE LAST PROCESSOR WILL HANDLE THE MODULE OF THE DIVISION

        """
        # CALCULATE NUMBER OF ROWS PER WORKER
        rowsToComputePerP = numberRows / (worldSize-1) 

        # SENT ROWS TO PROCESS
        for processorID in range(1, worldSize):
            rowsOffset = (processorID-1)*rowsToComputePerP 
            print ("rowsOffset is {}".format(rowsOffset))

            # SEND HOW MANY ROWS AND WHAT OFFSET EACH PROCESS WILL DO
            # TODO: MAKE MORE EFFICIENT
            comm.send(rowsToComputePerP, dest=processorID, tag=processorID)
            comm.send(rowsOffset, dest=processorID, tag=processorID)

            # send corresponding rows to Processors
            for j in range(0, rowsToComputePerP):
                rowIndex = j + rowsOffset
                print ("\t sending {} to {} with tag {}".format(a[rowIndex,:], processorID, rowIndex))
                comm.Send([a[rowIndex,:], MPI.INT], dest=processorID, tag=rowIndex)
        
        #print ("All sent to workers.\n")

    # CALL FUNCTION TO DISTRIBUTE WORK
    sendWorkToProcess()

# AT THIS POINT ALL WORK HAS BEEN SENT 
comm.Barrier()

if rank != TaskMaster:
    def receiveRowsAndComputeWork():
        #print ("Data Received from process %d.\n" % (rank))
        # offset = comm.recv(source=0, tag=rank)
        # recev_data = comm.recv(source=0, tag=rank)

        rowsToCompute = comm.recv(source=TaskMaster, tag=rank)
        rowsOffset = comm.recv(source=TaskMaster, tag=rank)

        
        recev_data = []
        # RECEIVE ROWS AND STACK THEM 
        for j in range(0, rowsToCompute):
            rowIndex = j + rowsOffset
            c = np.empty(shape=numberColumns)
            comm.Recv([c, MPI.INT],source=TaskMaster, tag=rowIndex)
            recev_data.append(c)
            
        
        print ("procesor {}, has the recev_data {}".format(rank, recev_data))
        #print ("Start Calculation from process %d.\n" % (rank))

        #Loop through rows
        # t_start = MPI.Wtime()
        # for row_num in range(0, rowsToCompute):
        #     res = np.zeros(shape=(numberColumns))
        #     if (rowsToCompute == 1):
        #         r = recev_data
        #     else:
        #         r = recev_data[row_num,:]

        #     for j in range(0, numberColumns):
        #         # GET COLUMN FROM B
        #         q = b[:,j]
        #         for x in range(0, numberColumns):
        #             res[j] = res[j] + (r[x]*q[x])

        #     if (row_num > 0):
        #         send = np.vstack((send, res))
        #     else:
        #         send = res
        # t_diff = MPI.Wtime() - t_start
        
        # print("Process %d finished in %5.4fs.\n" %(rank, t_diff))
        # #Send large data
        # #print ("Sending results to Master %d bytes.\n" % (send.nbytes))
        # comm.Send([send, MPI.FLOAT], dest=0, tag=rank) #1, 12, 23
    
    # CALL FUNCTION TO RECEIVE WORK AND COMPUTE IT
    receiveRowsAndComputeWork()

comm.Barrier()

# if rank == TaskMaster:  
#     #print ("Checking response from Workers.\n")
#     res1 = np.zeros(shape=(rowsToCompute, numberColumns))
#     comm.Recv([res1, MPI.FLOAT], source=1, tag=1)
#     #print ("Received response from 1.\n")
#     kl = np.vstack((res1))
#     for processorID in range(2, worldSize):
#         resx= np.zeros(shape=(rowsToCompute, numberColumns))
#         comm.Recv([resx, MPI.FLOAT], source=processorID, tag=processorID)
#         #print ("Received response from %d.\n" % (processorID))
#         kl = np.vstack((kl, resx))
#     print ("End")
#     print ("Result AxB.\n")
#     print (kl)   

comm.Barrier()





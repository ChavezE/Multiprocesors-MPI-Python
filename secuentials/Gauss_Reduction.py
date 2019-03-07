# GAUSS REDUCTION
# Author: Emilio Chavez Madero
# 7-March-2019

# Description:
# Implements Gauss Reduction on a Matrix.
# Important Note: 
#	Up to now, it is not check if a pivot is zero, 
# 	if so, it is necesary to exange row.


def gauss_reduce(matrix):
	N = len(matrix)
	for k in range(N):
		# Normalice pivot
		for j in range(k+1,N):
			matrix[k,j] = matrix[k,j] / matrix[k,k]
		


# for (k = 1; k <= N; k++)
# 	//Normalize pivoting row
# 	for (j = k+1; j <= N; j++)
# 			A[k,j] = A[k,j] / A[k,k]
# 	y[k] = b[k] / A[k,k]
# 	A[k,k] = 1
#  	//Reduce rows below pivot
# 	for (i = k+1; i <= N; i++)
# 			//Reduce columns after pivot
# 			for (j = k+1; j <= N; j++)
# 				A[i,j] = A[i,j] - A[i,k] * A[k,j]
# 			b[i] = b[i] - A[i,k] * y[k]

if __name__ == '__main__':
	gauss_reduce([[1,2,3], [4,5,6], [7,8,9]])
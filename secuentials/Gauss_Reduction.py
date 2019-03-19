# GAUSS REDUCTION
# Author: Emilio Chavez Madero
# 7-March-2019

# Description:
# Implements Gauss Reduction on a Matrix.
# Important Note: 
#	Up to now, it is not check if a pivot is zero, 
# 	if so, it is necesary to exange row.


def gauss_reduce(matrix, b):
	N = len(matrix)
	for k in range(N):
		# Normalice pivot
		for j in range(k+1,N):
			matrix[k,j] = matrix[k,j] / matrix[k,k]
		y[k] = b[k] / A[k,k]
		matrix[k,k] = 1
 		# Reduce rows below pivot
		for i in range(k+1,N)
			# Reduce columns after pivot
			for j in range(k+1, N)
				matrix[i,j] = matrix[i,j] - matrix[i,k] * matrix[k,j]
			b[i] = b[i] - matrix[i,k] * y[k]
			matrix[i,k] = 0

if __name__ == '__main__':
	gauss_reduce([[1,2,3], [4,5,6], [7,8,9]])
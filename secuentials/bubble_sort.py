# Bubble Sort | Bucket Sort
# Author: Emilio Chavez Madero
# 7-March-2019

# Description:
# Implementation of a simple bubble sort and a bucket Sort

import numpy as np

def msbits(x,k):
	# # convert number into binary first 
	# binary = bin(x) 
	# # remove first two characters 
	# binary = binary[2:] 
	
	# try:
	# 	return (int(binary,2) >> (len(binary) - k))
	# except:
	# 	return 0
	# return int(x/k)
	return 0

def bubble_sort(array):
	N = len(array)
	for i in range(N-1):
		swapped = False 
		for j in range(N-1):
			# compare adjacent elements
			if (array[j] > array[j+1]):
				swapped = True 
				array[j], array[j+1] = array[j+1], array[j]
		if (not swapped):
			break

	return array

def bucketSort(array, k):
	buckets = []
	for x in range(k):
		buckets.append([])

	sortedArray = []
	N = array.shape[0]
	# divide in buckets
	for i in range(N-1):
		buckets[msbits(array[i],k)].append(array[i])

	# print (buckets)
	# sort each bucket
	for i in range(k):
		buckets[i] = bubble_sort(buckets[i])
	
	# build sorted array of buckets
	for i in range(k):
		for j in range(len(buckets[i])):
			sortedArray.append(buckets[i][j])

	return sortedArray

# returns -1 if index not found
def isPresent(array, x):
	for i in range(array.shape[0]):
		if (array[i] == x):
			return i
	return -1

if __name__ == '__main__':
	randArray = np.random.randint(1000, size=10)
	print ("Original array :", randArray)
	print ("Sorted from buckets: ", bucketSort(randArray,10)) # k = 10 buckets
	print ("Sorted from bubble: ", bubble_sort(randArray))
	a =	randArray[np.random.randint(10)]
	print ("Index of ", a, " is", isPresent(randArray,a))
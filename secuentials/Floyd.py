# FLOYD
# Author: Emilio Chavez Madero
# 7-March-2019

# Description:
# Implements FLOYD shortest path on a matrix representing a graph.

INF = 999999999

def printGraph(graph):
	for x in range(len(graph)):
		for j in range(len(graph[x])):
			print(graph[x][j],"\t", end='')
		print("")

def floyds_shortest_paths(graph):
	N = len(graph) 
	for k in range(N):
		for i in range(N):
			for j in range(N):
				graph[i][j] = min(graph[i][j],graph[i][k] + graph[k][j])


if __name__ == '__main__':
	graph = [ [0,8,3,5, INF],
			  [8,0,2,INF,5],
			  [INF,1,0,3,4],
			  [6,INF,INF,0,7],
			  [INF,5,INF,INF,0]]
	floyds_shortest_paths(graph)
	printGraph(graph)



from Optimizer.Building import BaseBuilding, BuildingList
from Optimizer.SearchTree import NodeId, Node, NodeList, SearchTree
from Optimizer.Map import BaseMap
from Optimizer.Map import MapGeometry

from Graphics.GMap import printMap

import sys
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import timeit
from datetime import datetime, timedelta

# Garbage collector to releas unreferenced memory
import gc

def memory_usage_resource():
    import sys
    import resource
    rusage_denom = 1024.
    if sys.platform == 'darwin':
        # ... it seems that in OSX the output is different units ...
        rusage_denom = rusage_denom * rusage_denom
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
    return mem


buildingList = BuildingList(buildingList = [
        BaseBuilding(name = "Townhall", size = [7,6], number = 1),
        BaseBuilding(name = "SimpleRoad", size = [1,1], number = 0, nearBuildingList = ["SimpleRoad", "DoubleRoad", "Townhall"]),
        BaseBuilding(name = "DoubleRoad", size = [2,2], number = 0, nearBuildingList = ["DoubleRoad", "Townhall"]),
        BaseBuilding(name = "KnowledgeSanctuary", size = [2,2], number = 27, nearBuildingList = ["DoubleRoad", "SimpleRoad"]),
        BaseBuilding(name = "AdmirationSanctuary", size = [2,2], number = 2, nearBuildingList = ["DoubleRoad", "SimpleRoad"]),
        BaseBuilding(name = "AdmirationSanctuary", size = [2,2], number = 2, nearBuildingList = ["DoubleRoad", "SimpleRoad"]),
        BaseBuilding(name = "SmallWishingWell", size = [3,2], number = 6, nearBuildingList = ["DoubleRoad", "SimpleRoad"]),
        BaseBuilding(name = "WishingWell", size = [3,3], number = 1, nearBuildingList = ["DoubleRoad", "SimpleRoad"]),
        BaseBuilding(name = "TribalSquare", size = [4,3], number = 15, nearBuildingList = ["DoubleRoad", "SimpleRoad"]),
        BaseBuilding(name = "SeaScraper", size = [5,5], number = 6, nearBuildingList = ["DoubleRoad"]),
        BaseBuilding(name = "HoloHolidayPark", size = [6,6], number = 2, nearBuildingList = ["DoubleRoad"])
        ])

print(str(buildingList))

mappedGeometry = MapGeometry([[0,0],[50,0],[50,30],[35,30],[35,50],[0,50],[0,0]])
emptyMap = BaseMap(mappedGeometry)

"""buildingType = buildingList.get("SmallWishingWell")
emptyMap.placeBuildingInCorner(buildingType, [17,10])
emptyMap.placeBuildingInCorner(buildingType, [17,12])
emptyMap.placeBuildingInCorner(buildingType, [17,14])"""


initialNode = Node(buildingList = buildingList, buildingType = buildingList.get("Townhall"), buildingPosition = [10,10], emptyMatrixMap = emptyMap)

print("Size of buildingList: "+ str(sys.getsizeof(buildingList))+" bytes")
print("Size of emptyMap: "+ str(sys.getsizeof(emptyMap))+" bytes")
print("Size of initial node: "+ str(sys.getsizeof(initialNode))+" bytes")

searchTree = SearchTree([initialNode])


start = timeit.default_timer()

#for index in range(5000):
#    searchTree.expandLowerWeightNode()

num_iterations = 500
for index in range(num_iterations):
    start1 = timeit.default_timer()
    searchTree.expandAllNodesWithLowerWeight()
    stop1 = timeit.default_timer()
    print("\nIteration " + str(index) + " took " + str(stop1 - start1) + " nodeList contains up to " + str(len(searchTree.nodeList)) + " nodes (of "+str(searchTree.totalNodesNum)+" generated). Memory usage is : " + str(memory_usage_resource()) + " MB")
    gc.collect()

stop = timeit.default_timer()


time = datetime(1,1,1) + timedelta(seconds=int(stop - start))

print("\n"+str(num_iterations) + " iterations performed")
print("Time exploring tree: [%d day, %d h, %d min, %d sec]" % (time.day-1, time.hour, time.minute, time.second))
print("Memory usage is: " + str(memory_usage_resource()) + " MB")
print("Generated " + str(searchTree.totalNodesNum) + " nodes")
print("Time per node (all nodes): "+ str((stop - start)/searchTree.totalNodesNum) + " seconds")
print("At this stage there are "+str(len(searchTree.nodeList))+" horizon nodes")
print("Memory per node (all nodes): " + str(memory_usage_resource()/searchTree.totalNodesNum) + " MB/node\n")


print("Last node exploded is: "+str(searchTree.getLastExpandedNode()))
#searchTree.getLastExpandedNode().matrixMap.findUnbiltHolesRounded()
printMap((searchTree.getLastExpandedNode()).getRegressedMatrix().matrixMap)

print("Lowe weight's node exploded is: "+str(searchTree.getLowerWeightNode()))
#searchTree.getLowerWeightNode().matrixMap.findUnbiltHolesRounded()
printMap((searchTree.getLowerWeightNode()).getRegressedMatrix().matrixMap)

"""
for node in searchTree.nodeList[0::1000]:
    print("Node: "+str(node))
    node.matrixMap.findUnbiltHolesRounded()
    printMap(node.matrixMap.matrixMap)
"""

"""
## Animation with all matrix
matrixList = []

for node in searchTree.nodeList:
    matrixList.append(node.matrixMap.matrixMap)

printMatrixAnimation(matrixList)
"""
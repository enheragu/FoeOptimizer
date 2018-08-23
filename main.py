
from Optimizer.Building import BaseBuilding, BuildingList
from Optimizer.SearchTree import NodeId, Node, NodeList, SearchTree
from Optimizer.Map import BaseMap
from Optimizer.Map import MapGeometry

from Graphics.GMap import printMap

import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import timeit

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

validNodeList = NodeList()

nodeIdObj = NodeId()
initialNode = Node(nodeIdObj = nodeIdObj, buildingList = buildingList, buildingType = buildingList.get("Townhall"), buildingPosition = [10,10], matrixMap = emptyMap)

searchTree = SearchTree([initialNode])


start = timeit.default_timer()

#for index in range(5000):
#    searchTree.expandLowerWeightNode()

for index in range(15):
    start1 = timeit.default_timer()
    searchTree.expandAllNodesWithLowerWeight()
    stop1 = timeit.default_timer()
    print("\nIteration " + str(index) + " took " + str(stop1 - start1) + " nodeList contains up to " + str(len(searchTree.nodeList)) + " nodes (total of "+str(nodeIdObj.getCurrentId())+"). Memory usage is : " + str(memory_usage_resource()) + " MB")

stop = timeit.default_timer()

print("\nTime exploring tree: ", stop - start)
print("Memory usage is : " + str(memory_usage_resource()) + " MB")
print("Generated " + str(nodeIdObj.getCurrentId()) + " nodes")
print("Time per node (all nodes): "+ str((stop - start)/nodeIdObj.getCurrentId()))
print("At this stage there are "+str(len(searchTree.nodeList))+" horizon nodes")
print("Memory per node (stored horizon nodes) " + str(memory_usage_resource()/len(searchTree.nodeList)) + " MB/node\n")


print("Last node exploded is: "+str(searchTree.getLastExpandedNode()))
searchTree.getLastExpandedNode().matrixMap.findUnbiltHolesRounded()
printMap(searchTree.getLastExpandedNode().matrixMap.matrixMap)


print("Lowe weight's node exploded is: "+str(searchTree.getLowerWeightNode()))
searchTree.getLowerWeightNode().matrixMap.findUnbiltHolesRounded()
printMap(searchTree.getLowerWeightNode().matrixMap.matrixMap)

"""
## Animation with all matrix
matrixList = []

for node in searchTree.nodeList:
    matrixList.append(node.matrixMap.matrixMap)

def update(data):
    mat.set_data(data)
    return mat 

fig, ax = plt.subplots()
mat = ax.matshow(initialNode.matrixMap.matrixMap)
plt.colorbar(mat)
ani = animation.FuncAnimation(fig, update, matrixList, interval=100)
plt.show()
"""
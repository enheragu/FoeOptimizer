
from Optimizer.Building import BaseBuilding, BuildingList
from Optimizer.Map import BaseMap

import numpy as np
import copy as cp

import concurrent.futures

import timeit

class NodeId:
    def __init__(self):
        self.lastID = 0;

    def getNewId(self):
        self.lastID += 1
        return self.lastID

    def getCurrentId(self):
        return self.lastID

class Node:

    def __init__(self, buildingList, buildingType, buildingPosition, parentNode = None, emptyMatrixMap = None):
        self.buildingType = buildingType
        self.buildingPosition = buildingPosition

        self.parentNode = parentNode
        self.buildingList = buildingList

        if parentNode is not None:
            #regressedMatrixMap = cp.deepcopy(parentNode.matrixMap)
            self.emptyMatrixMap = parentNode.emptyMatrixMap
        else:
            #regressedMatrixMap = cp.deepcopy(matrixMap)
            self.emptyMatrixMap = emptyMatrixMap


        regressedMatrixMap = cp.deepcopy(self.emptyMatrixMap)
        self.regressMatrixMapFromAncestryNodes(regressedMatrixMap)
        self.regressedMatrixMap = regressedMatrixMap

        # Places the building in both building list and map matrix
        if not self.buildingType.placeBuilding(regressedMatrixMap):
            raise Exception("All building of this type ("+str(self.buildingType.name)+") had already been placed")

        if not regressedMatrixMap.placeBuildingInCorner(self.buildingType, self.buildingPosition):
            raise Exception("Cannot place building in position "+str(self.buildingPosition)+" of map matrix")

        self.nodeWeight = self.computeWeight(regressedMatrixMap)
        self.adjustWeightWithMapHoles(regressedMatrixMap)

        ## TOO TIME CONSUMING OPERATION BELOW ##
        # Penalize empty holes between buildings
        # self.nodeWeight += regressedMatrixMap.findUnbiltHolesRounded() * 30
        ##                                    ##

        self.childNodes = NodeList()

        #debug print("Create "+str(self))


    def computeWeight(self, regressedMatrixMap):
        # NodeWeight is builtBuildingArea / builtRoadArea | ONCE THE MAP IT'S BEEN UPDATED
        builtArea, numberBuiltBuildings = self.buildingList.getBuiltArea(regressedMatrixMap)
        roadBuiltArea = self.buildingList.getRoadArea(regressedMatrixMap)
        numberBuildings = self.buildingList.numberOfBuildings

        # Whole map area (forbidden parts of the map are not taken into account to avoid losing time, 
        # this operation is much faster and the same error applies to ALL nodes)
        wholeArea = regressedMatrixMap.matrixMap.shape[0]*regressedMatrixMap.matrixMap.shape[1]

        if builtArea == 0 or numberBuiltBuildings == 0:
            # Penalize "only" roads city
            nodeWeight = roadBuiltArea * 40
        else:
            nodeWeight = (roadBuiltArea * 100 / builtArea)
            nodeWeight += (numberBuildings / numberBuiltBuildings)
            nodeWeight += (wholeArea / builtArea)

        return int(round(nodeWeight))


    # This operation is made appart as it is very time consuming, it will be decided wheter use it from time to time or not
    # Search for map holes and penalize the weight with it
    def adjustWeightWithMapHoles(self, regressedMatrixMap):

        regressedMatrixMap = self.getRegressedMatrix()
        self.nodeWeight = self.computeWeight(regressedMatrixMap)
        #debug start1 = timeit.default_timer()
        self.nodeWeight += regressedMatrixMap.findUnbiltHolesRounded() * 200
        #debug stop1 = timeit.default_timer()
        #debug print("Time spent finding holes is: ", stop1 -start1)


    def computeByBuilding(self, buildingName):

        regressedMatrixMap = self.regressedMatrixMap

        validNeighbourCells = regressedMatrixMap.getValidNeighbourCellsTo(self.buildingType, self.buildingPosition)
        buildingType = self.buildingList.get(buildingName)
        cornerCells = []
        childNodes = []

        for neigbourCell in validNeighbourCells:
            # For each neighbourCell gets all valid corner cells for a building's footprint to intersect this cell (neighbour)
            cornerCells = regressedMatrixMap.getPossibleCornerOccupying(buildingType,neigbourCell)
            #debug print("Valid corner cells are: " + str(cornerCells))

            for cell in cornerCells: 
                # Check that there are still buildings of this type to add and it can be added in the matrix cell decided
                if buildingType.placeBuilding(regressedMatrixMap) and regressedMatrixMap.placeBuildingInCorner(buildingType, cell, False):
                    found = False

                    # Checks that the new building is placed at least next to one of the nearBuildings needed
                    for buildingType2Name in buildingType.nearBuildingList:
                        buildingType2 = self.buildingList.get(buildingType2Name)
                        if regressedMatrixMap.isBuildingNextTo(buildingType, cell, buildingType2):
                            found = True
                            break

                    # Checks that the new building is placed next to all bonus building if there are
                    if buildingType.bonusBuildingList is not None and found is True:
                        for buildingType2Name in buildingType.bonusBuildingList:
                            buildingType2 = self.buildingList.get(buildingType2Name)
                            if not regressedMatrixMap.isBuildingNextTo(buildingType, cell, buildingType2):
                                found = False
                                break

                    # If both conditions matchs
                    if found is True:
                        childNodes.append([buildingType, cell])

        return childNodes

    def computeChildNodes(self):

        start = timeit.default_timer()
        possibleBuildingsToPlace = self.buildingType.buildingListToNear

        generateNodes = []

        self.regressedMatrixMap = self.getRegressedMatrix()

        # Child nodes are all possible cominations of validNeighbourCells with possibleBuildingsToPlace
        # and bonus building. Only valid combinations generate new Nodes
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Analyces cell row with PoolExecutor
            for childNodes in executor.map(self.computeByBuilding, possibleBuildingsToPlace):
                generateNodes += childNodes

        # Avoid creation of repeated nodes
        for generateNode in generateNodes:
            if not self.childNodes.contains(generateNode[0], generateNode[1]):
                self.childNodes.append(Node(self.buildingList, generateNode[0], generateNode[1], self))

        del self.regressedMatrixMap

        stop = timeit.default_timer()
        #debug print("Compute child nodes took: ", stop-start)
        return self.childNodes


    def regressMatrixMapFromAncestryNodes(self, emptyMatrix):

        nextNode = self.parentNode

        while nextNode != None:
            emptyMatrix.placeBuildingInCorner(nextNode.buildingType, nextNode.buildingPosition)
            nextNode = nextNode.parentNode 

    def getRegressedMatrix(self):

        regressedMatrixMap = cp.deepcopy(self.emptyMatrixMap)
        self.regressMatrixMapFromAncestryNodes(regressedMatrixMap)

        # Place this building:
        regressedMatrixMap.placeBuildingInCorner(self.buildingType, self.buildingPosition)

        return regressedMatrixMap

    ## Check if this is the searched building based on name or mapIdentifier
    # @param tag                    Name or mapIdentifier of the building
    # @return                        True if the tag matchs either the name or the map identifier, False otherwise    
    def __eq__(self, tag):
        if type(tag) is Node and tag.buildingType.name == self.buildingType.name and tag.buildingPosition == self.buildingPosition:
            return True 
        else:
            return False

                
    ## To string method overload
    def __str__(self):
        childNodes = ( "[NotExpanded]" if not self.childNodes else str(self.childNodes))
        string = "Node -> Place building " + str(self.buildingType.name) + "("+str(self.buildingType.mapIdentifier)+") at " + str(self.buildingPosition) + " with weight = ["+str(self.nodeWeight)+"] | Child nodes includes: " + str(childNodes)
        return string



class NodeList(list):

    def __init__(self, nodeList = []):
        list.__init__(self,nodeList)

    ## To string method overload
    def __str__(self):
        string = ""
        for node in self[:]:
            string += " · " + str(node) + "\n"
        return string

    # getitem operator overload
    def get(self, tag):
        for node in self[:]:
            if node == tag:
                return node

    # Delete node from list based on nodeID
    def delete(self, tag):
        for index, node in enumerate(self[:]):
            if node == tag:
                del self[index]

    # Returns all nodes that match a given weight value
    def getAllNodesWithWeight(self, weight):
        nodeWithSameWheight = []
        for index, node in enumerate(self[:]):
            if node.nodeWeight == weight:
                nodeWithSameWheight.append(node)

        return nodeWithSameWheight

    def contains(self, buildingType, cell):
        for node in self[:]:
            if node.buildingType == buildingType and node.buildingPosition == cell:
                return True

        return False


import math

class SearchTree:
    def __init__(self, initialNode):
        self.nodeList = NodeList(initialNode)
        self.expandedNodeList = NodeList()
        self.repeatedNodeList = NodeList()
        self.totalNodesNum = 0

    def getChildNodesOf(self, nodeList):
        return self.nodeList[nodeList].computeChildNodes()

        # For ProcessPool
        #childNodeList = []
        #for node in nodeList:
        #    childNodeList += node.computeChildNodes()
        #return childNodeList


    def expandAllNodesWithLowerWeight(self):

        # Sorts list from lower Weight to then loop over and take self.numberThreads of them
        self.nodeList = sorted(self.nodeList, key=lambda node: node.nodeWeight)

        # Number of "lowerWeight" nodes get analyzed
        self.numberOfNodes = 30
        # How many nodes gets each process to get its childs
        CHUNKSIZE = 1

        n = self.numberOfNodes if len(self.nodeList) > self.numberOfNodes else len(self.nodeList)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Analyces cell row with PoolExecutor

            # With threads
            for childNodes in executor.map(self.getChildNodesOf, range(0,n)):
                if childNodes is not None:
                    self.nodeList += NodeList(childNodes)
            
            # With ProcessPool (can get very slow ¿?)
            #for childNodes in executor.map(self.getChildNodesOf, (self.nodeList[i:i+CHUNKSIZE] for i in (range(0, n, CHUNKSIZE)))):
            #    if childNodes is not None:
            #        #debug print("Append " + str(len(childNodes)) + " nodes to list")
            #        self.nodeList += NodeList(childNodes)


        #debug print("Node list len: " + str(len(self.nodeList)))
        self.expandedNodeList += NodeList(self.nodeList[0:n])
        self.nodeList = NodeList(self.nodeList[n:])
        self.totalNodesNum = len(self.expandedNodeList) + len(self.nodeList)


    def getLowerWeightNode(self):
        lowerWeight = math.inf
        lowerWeightNode = 0

        for node in self.nodeList:
            if node.nodeWeight < lowerWeight:
                lowerWeightNode = node
                lowerWeight = node.nodeWeight

        return self.nodeList.get(lowerWeightNode)


    def getLastExpandedNode(self):
        return self.nodeList[-1]


    def pruneNodeList(self, nodeList):
        for node in nodeList:
            node.adjustWeightWithMapHoles(node.getRegressedMatrix())


        for index1, node in enumerate(nodeList):
            node1RegressedMatrix = node.getRegressedMatrix()
            for idenx2, node2 in enumerate(nodeList):
                if node.nodeWeight == node2.nodeWeight:
                    print ("Two nodes with the same weight found with index: "+str(index1)+" and "+str(index2))
                    if index1 != index2:
                        if node1RegressedMatrix == node2.getRegressedMatrix(): ## Avoid deleting due to comparing the same node with itself
                            print("Repeated matrix found")


    def pruneTree(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Analyces cell row with PoolExecutor

            # With ProcessPool (can get very slow ¿?)
            CHUNKSIZE = 100
            executor.map(self.pruneNodeList, (self.nodeList[i:i+CHUNKSIZE] for i in (range(0, len(self.nodeList) , CHUNKSIZE))))


    def searchTreeFor(self, numiterations):

        # Garbage collector to releas unreferenced memory
        import gc
        import sys

        for index in range(numiterations):
            start1 = timeit.default_timer()
            self.expandAllNodesWithLowerWeight()
            stop1 = timeit.default_timer()
            print("\nIteration " + str(index) + " took " + str(stop1 - start1) + " nodeList contains up to " + str(len(self.nodeList)) + " nodes (of "+str(self.totalNodesNum)+" generated). Memory usage is : " + str(memory_usage_resource()) + " MB")
            gc.collect()

            """start1 = timeit.default_timer()
            self.pruneTree()
            stop1 = timeit.default_timer()
            print("\nPrune tree " + str(index) + " took " + str(stop1 - start1) + " nodeList contains now to " + str(len(self.nodeList)) + " nodes (of "+str(self.totalNodesNum)+" generated).")
            gc.collect()"""

def memory_usage_resource():
    import sys
    import resource
    rusage_denom = 1024.
    if sys.platform == 'darwin':
        # ... it seems that in OSX the output is different units ...
        rusage_denom = rusage_denom * rusage_denom
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
    return mem

from Optimizer.Building import BaseBuilding, BuildingList
from Optimizer.Map import BaseMap

import numpy as np
import copy as cp

import threading

class NodeId:
    def __init__(self):
        self.lastID = 0;

    def getNewId(self):
        self.lastID += 1
        return self.lastID

    def getCurrentId(self):
        return self.lastID

class Node:

    def __init__(self, nodeIdObj, buildingList, buildingType, buildingPosition, parentNode = None, matrixMap = None):
        self.nodeIdObject = nodeIdObj
        self.nodeId = self.nodeIdObject.getNewId()
        self.buildingType = buildingType
        self.buildingPosition = buildingPosition

        self.parentNode = parentNode
        self.buildingList = buildingList

        weightIncrement = 1 # TBD!! Based on heuristic

        if parentNode is not None:
            self.matrixMap = cp.deepcopy(parentNode.matrixMap)
            #self.nodeWeight = (parentNode.nodeWeight + weightIncrement)   # (BuiltArea - ToBuildArea) + RoadsArea
        else:
            self.matrixMap = cp.deepcopy(matrixMap)
            #self.nodeWeight = (0 + weightIncrement)                       # (BuiltArea - ToBuildArea) + RoadsArea


        # Places the building in both building list and map matrix
        if not self.buildingType.placeBuilding(self.matrixMap):
            raise Exception("All building of this type ("+str(self.buildingType.name)+") had already been placed")

        if not self.matrixMap.placeBuildingInCorner(self.buildingType, self.buildingPosition):
            raise Exception("Cannot place building in position "+str(self.buildingPosition)+" of map matrix")


        # NodeWeight is builtBuildingArea / builtRoadArea | ONCE THE MAP IT'S BEEN UPDATED
        if self.buildingList.getBuiltArea(self.matrixMap) == 0:
            # Penalize "only" roads city
            self.nodeWeight = self.buildingList.getRoadArea(self.matrixMap) * 30
        else:
            self.nodeWeight = int(round(self.buildingList.getRoadArea(self.matrixMap) * 100 / self.buildingList.getBuiltArea(self.matrixMap)))


        self.childNodes = NodeList()

        #debug print("Create "+str(self))

    def computeChildNodes(self):

        possibleBuildingsToPlace = self.buildingType.buildingListToNear
        validNeighbourCells = self.matrixMap.getValidNeighbourCellsTo(self.buildingType, self.buildingPosition)

        #debug print("Building list near is: " + str(possibleBuildingsToPlace))
        #debug print("Valid neighbour cells are: " + str(validNeighbourCells))
        # Child nodes are all possible cominations of validNeighbourCells with possibleBuildingsToPlace
        # and bonus building. Only valid combinations generate new Nodes
        for buildingName in possibleBuildingsToPlace:

            buildingType = self.buildingList.get(buildingName)
            cornerCells = []

            for neigbourCell in validNeighbourCells:
                # For each neighbourCell gets all valid corner cells for a building's footprint to intersect this cell (neighbour)
                cornerCells = self.matrixMap.getPossibleCornerOccupying(buildingType,neigbourCell)
                #debug print("Valid corner cells are: " + str(cornerCells))

                for cell in cornerCells: 
                    # Check that there are still buildings of this type to add and it can be added in the matrix cell decided
                    if buildingType.placeBuilding(self.matrixMap) and self.matrixMap.placeBuildingInCorner(buildingType, cell, False):
                        found = False

                        # Checks that the new building is placed at least next to one of the nearBuildings needed
                        for buildingType2Name in buildingType.nearBuildingList:
                            buildingType2 = self.buildingList.get(buildingType2Name)
                            if self.matrixMap.isBuildingNextTo(buildingType, cell, buildingType2):
                                found = True
                                break

                        # Checks that the new building is placed next to all bonus building if there are
                        if buildingType.bonusBuildingList is not None and found is True:
                            for buildingType2Name in buildingType.bonusBuildingList:
                                buildingType2 = self.buildingList.get(buildingType2Name)
                                if not self.matrixMap.isBuildingNextTo(buildingType, cell, buildingType2):
                                    found = False
                                    break

                        # If both conditions matchs, and it has not been added before, adds the new node
                        if found is True and not self.childNodes.contains(buildingType, cell):
                            self.childNodes.append(Node(self.nodeIdObject, self.buildingList, buildingType, cell, self))

        return self.childNodes


    ## Check if this is the searched building based on name or mapIdentifier
    # @param tag                    Name or mapIdentifier of the building
    # @return                        True if the tag matchs either the name or the map identifier, False otherwise    
    def __eq__(self, tag):
        if type(tag) is int and tag == self.nodeId:
            return True
        elif type(tag) is Node and tag.buildingType.name == self.buildingType.name and tag.buildingPosition == self.buildingPosition:
            return True 
        else:
            return False

                
    ## To string method overload
    def __str__(self):
        parentId = ( "None" if self.parentNode is None else self.parentNode.nodeId )
        childNodes = ( "[NotExpanded]" if not self.childNodes else str(self.childNodes))
        string = "Node (" + str(self.nodeId) + ") -> Place building " + str(self.buildingType.name) + "("+str(self.buildingType.mapIdentifier)+") at " + str(self.buildingPosition) + " with weight = ["+str(self.nodeWeight)+"] | Parent is node (" + str(parentId) + "). Child nodes includes: " + str(childNodes)
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

        self.lock = threading.Lock()

        # Number of threads created to expand the nodes
        self.numberThreads = 100

    def expandNode(self, node):
        childNodes = node.computeChildNodes()

        # Thread safe operation: add members
        self.lock.acquire()
        self.nodeList = NodeList(self.nodeList + childNodes)
        self.lock.release()

        #print("Expand node: " + str(node))

        # Thread safe operation: remove members
        self.lock.acquire()
        # Once a node is expanded it is deleted from the list
        self.nodeList.delete(node.nodeId)
        self.lock.release()

        print('.', end='', flush=True)


    def expandLowerWeightNode(self):
        lowerWeightNode = self.getLowerWeightNode()
        lowerWeightNodeId = lowerWeightNode.nodeId

        self.expandNode(lowerWeightNode.computeChildNodes())

        #debug print("Lower weight in node: " + str(lowerWeightNode))


    def expandNodeWithId(self, id):
        nodeWithId = self.nodeList.get(id)

        self.expandNode(nodeWithId)


    def expandAllNodesWithLowerWeight(self):

        # Sorts list from lower Weight to then loop over and take self.numberThreads of them
        self.nodeList = sorted(self.nodeList, key=lambda node: node.nodeWeight)

        #lowerWeightNode = self.getLowerWeightNode()
        #lowerWeightNodeId = lowerWeightNode.nodeId
        #nodesWithLowerWeight = self.nodeList.getAllNodesWithWeight(lowerWeightNode.nodeWeight)

        threads = []
        for index, node in enumerate(self.nodeList):

            th = threading.Thread(target = self.expandNode, args=[node])
            th.start()
            threads.append(th)

            if index > self.numberThreads: break
            

        # Wait for all threads to complete
        for t in threads:
           t.join()

    def getLowerWeightNode(self):
        lowerWeight = math.inf
        lowerWeightId = 0

        for node in self.nodeList:
            if node.nodeWeight < lowerWeight:
                lowerWeightId = node.nodeId
                lowerWeight = node.nodeWeight

        return self.nodeList.get(lowerWeightId)


    def getLastExpandedNode(self):
        nodeId = 0

        for node in self.nodeList:
            if node.nodeId > nodeId:
                higherId = node.nodeId

        return self.nodeList.get(higherId)
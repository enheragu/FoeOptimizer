
import numpy as np
from shapely import geometry
import concurrent.futures

import time 

class MapGeometry:

    def __init__(self, borderCoordinates):

        self.borderCoordinates = borderCoordinates

        self.sizeX = 0
        self.sizeY = 0
        for point in self.borderCoordinates:
            self.sizeX = ( point[0] if point[0] > self.sizeX else self.sizeX )
            self.sizeY = ( point[1] if point[1] > self.sizeY else self.sizeY )

        self.polygon = geometry.Polygon(self.borderCoordinates)

        self.matrixMap = np.full(shape = (self.sizeX, self.sizeY), fill_value = -1, dtype = np.int8)


        for coordX in range(self.sizeX):
            for coordY in range(self.sizeY):
                if self.polygon.intersects(geometry.Point(coordX, coordY)):
                    self.matrixMap[coordX][coordY] = 0



class BaseMap:

    def __init__(self, availableAreaGeometry):
        self.matrixMap = availableAreaGeometry.matrixMap

    ## Place building of given type in map matrix, using coordinates position as the upper left corner of the building
    # @param buildingType             Buildin to place
    # @param position                Coordinates of the upper left corner
    # @param place                   True if wants to place it, false if just want to check
    # @return                        True if it can be placed, false otherwise
    def placeBuildingInCorner(self, buildingType, position, place = True):

        #debug print ("Matrix size is: (" + str(self.matrixMap.shape[0]) + "," + str(self.matrixMap.shape[0])+")")
        # Check that the space for this building is empty in the map
        for x in range(position[0], buildingType.size[0]+position[0]):
            for y in range(position[1], buildingType.size[1]+position[1]):

                if x >= self.matrixMap.shape[0] or y >= self.matrixMap.shape[1] or x < 0 or y < 0:
                    return False

                if self.matrixMap[x][y] != 0:
                    return False

        # If everything is ok, fills the map (given position and size) with the identifier
        if place:
            for x in range(position[0], buildingType.size[0]+position[0]):
                for y in range(position[1], buildingType.size[1]+position[1]):
                    self.matrixMap[x][y] = buildingType.mapIdentifier
        
        return True


    ## Gets all valid neighbour cells of a given building (identifier size and position) inside
    #  the map
    # @param buildingType            Buildin to place
    # @param position                Coordinates of the upper left corner
    # @return                        List of cells
    def getNeighbourCellsToBuilding(self, buildingType, position):
        return self.getNeighbourCellsToArea(buildingType.size, position)

    ## Gets all valid neighbour cells of a given building (identifier size and position) inside
    #  the map
    # @param size                    Area to search
    # @param position                Coordinates of the upper left corner
    # @return   
    def getNeighbourCellsToArea(self, size, position):
        neighbourCells = []
        # Gets neighbours of the building (it thery are inside the matrix and empty)
        if position[0] >= 1: # Compared against 1, if position[0] is 0 theres no neighbours at its left (end of matrix)
            for cellY in range(position[1], position[1] + size[1]):
                neighbourCells.append([position[0]-1,cellY])

        if position[1] >= 1: # Compared against 1, if position[1] is 0 theres no neighbours over it (end of matrix)
            for cellX in range(position[0], position[0] + size[0]):
                neighbourCells.append([cellX,position[1]-1])

        endPosition = [position[0] + size[0], position[1] + size[1]]
        #debug print("End position is: "+str(endPosition))
        if endPosition[0] < self.matrixMap.shape[0] -1: # Compared against size - 1, if position[0] is matrixSize theres no neighbours at its right (end of matrix)
            for cellY in range(endPosition[1] - size[1], endPosition[1]):
                neighbourCells.append([endPosition[0],cellY])

        if endPosition[1] < self.matrixMap.shape[1] -1: # Compared against size - 1, if position[1] is matrixSize theres no neighbours under it (end of matrix)
            for cellX in range(endPosition[0] - size[0], endPosition[0]):
                neighbourCells.append([cellX,endPosition[1]])

        return neighbourCells

    ## Gets all valid neighbour cells of a given building (identifier size and position) that are 
    #  empty
    # @param buildingType            Buildin to place
    # @param position                Coordinates of the upper left corner
    # @return                        List of cells
    def getValidNeighbourCellsTo(self, buildingType, position):
        validCells = []
        neighbourCells = self.getNeighbourCellsToBuilding(buildingType, position)
        # Gets neighbours of the building (it thery are inside the matrix and empty)

        for cell in neighbourCells:
            if self.matrixMap[cell[0]][cell[1]] == 0:
                validCells.append([cell[0],cell[1]])

        #debug print ("Neighbours found in: "+str(validCells))

        #debug for cell in validCells:
            #debug print("Neighbour in [" + str(cell[0])+"," + str(cell[1]) + "]. Matrix with dimensions: " + str(self.matrixMap.shape))
            #debug print("Cell " + str(cell))
            #debug self.matrixMap[cell[0]][cell[1]] = 10

        return validCells

    ## Checks in map if building at a given corner position is next to another building
    #  the map
    # @param buildingType1           Buildin to check
    # @param position                Coordinates of the upper left corner
    # @param buildingType2           Building to search next to first building
    # @return                        True if the building is found next to the buinding1, false otherwise
    def isBuildingNextTo(self, buildingType1, position, buildingType2):
        neighbourCells = self.getNeighbourCellsToBuilding(buildingType1, position)

        for cell in neighbourCells:
            if self.matrixMap[cell[0]][cell[1]] == buildingType2.mapIdentifier:
                
                # Must be re-done in a better way...
                # Double road must connect to itself by two cells:
                #
                #   NOT VALID:  |   VALID:
                #
                #     ##        |    ####
                #     ####      |    ####
                #       ##      |    ##
                #       ##      |    ##

                if (buildingType1.name == "DoubleRoad" and buildingType2.name == "DoubleRoad")\
                or (buildingType1.name == "DoubleRoad" and buildingType2.name == "Townhall")\
                or (buildingType1.name == "Townhall" and buildingType2.name == "DoubleRoad"):

                    from Optimizer.Building import BaseBuilding
                    # Uses SimpleRoad type is its 1 cell sized, gets neighbours of cell
                    neighbourCellsToCell = self.getNeighbourCellsToBuilding(BaseBuilding(name = "SimpleRoad", size = [1,1], number = 0, nearBuildingList = ["SimpleRoad", "DoubleRoad", "Townhall"]), cell)
                    # Intersection between both lists
                    commonCellList = [element for element in neighbourCells if element in neighbourCellsToCell]
                    #commonCellList = (set(neighbourCells).intersection(neighbourCellsToCell))
                    for commonCell in commonCellList:
                            # Checks that in the cell theres actually the Road
                            if self.matrixMap[commonCell[0]][commonCell[1]] == buildingType2.mapIdentifier:
                                return True
                    return False

                return True

        return False

    ## Checks in map if an area in a corner position is next to an id set
    # @param size                    Size of the area
    # @param position                Coordinates of the upper left corner
    # @param buildingType2           ID to search
    # @param matrix                  Give matrix if search should be performed in a given matrix and not the map one
    # @return                        True if the building is found next to the buinding1, false otherwise
    def isAreaNextToID(self, size, position, id, matrix = None):
        neighbourCells = self.getNeighbourCellsToArea(size, position)

        for cell in neighbourCells:
            if matrix is None:
                if self.matrixMap[cell[0]][cell[1]] == id:
                    return True
            else:
                if matrix[cell[0]][cell[1]] == id:
                    return True
        return False

    ## Computes all corner positions valids for a building to be over a given cell
    # @param buildingType1           Buildin to check
    # @param position                Coordinates building should occupy
    # @return                        List of valid corner coordinates where the building could be located with its footprint over the given cell
    def getPossibleCornerOccupying(self, buildingType, position):

        cornerValidCells = []
        # Checks from using original position as corner and then moves the building all of its size to get the new "corner" positions
        # from : position[0] - buildingType.size[0] + 1 -> minus 1 to avoid leaving a white space between both buildings, should be oned next to another
        for coordX in range(position[0] - buildingType.size[0] +1, position[0] +1):
            for coordY in range(position[1] - buildingType.size[1] +1, position[1] +1):
                # Checks if it can be located using new coordinates as corner
                if self.placeBuildingInCorner(buildingType = buildingType, position = [coordX, coordY], place = False):
                    cornerValidCells.append([coordX, coordY])

        return cornerValidCells

    def getAreaUsedBy(self, buildingId):
        return len(np.nonzero(self.matrixMap == buildingId)[0])  # Tonwhall is 1, SimpleRoad is 2, DoubleRoad is 3




    # TOO TIME CONSUMING FOR NOW
    def findUnbiltHolesRounded(self):
        # Returns matrix with all 0 as TRUE and the rest as FALSE

        maskedMap = self.matrixMap > 0
        self.maskedMap = maskedMap != 0
        np.set_printoptions(threshold=np.inf)


        #debug print(maskedMap)
        #debug time.sleep(10)

        # Searchs for whole patterns like (true when it is 0):
        #
        #  FALSE FALSE FALSE          FALSE FALSE FALSE FALSE         FALSE FALSE FALSE
        #  FALSE TRUE  FALSE          FALSE TRUE  TRUE  FALSE         FALSE TRUE  FALSE
        #  FALSE FALSE FALSE          FALSE FALSE FALSE FALSE         FALSE TRUE  FALSE
        #                                                             FALSE FALSE FALSE

        #holePatterns = []
        #holePatterns.append(np.array([[False, False, False], [False, True, False], [False, False, False]]))
        #holePatterns.append(np.array([[False, False, False, False], [False, True, True, False], [False, False, False, False]]))
        #holePatterns.append(np.array([[False, False, False], [False, True, False], [False, True, False], [False, False, False]]))


        if np.count_nonzero(maskedMap == True) > np.count_nonzero(maskedMap == False):
            cellList = np.argwhere(maskedMap == False)
        else:
            cellList = np.argwhere(maskedMap == True)

        countHoles = 0
        
        # Non threaded is faster
        for cell in cellList:
            countHoles += self.checkCellListForPattern(cell)

        #with concurrent.futures.ThreadPoolExecutor() as executor:
        #    # Analyces cell row with PoolExecutor
        #    for result in executor.map(self.checkCellListForPattern, cellList):
        #        countHoles += result


        del self.maskedMap
        #debug print ("Found " + str(countHoles) + " holes")
        return countHoles

    def checkCellListForPattern(self, cell):

        # Uses the area of the pattern to look at neighbours of it at a given coordinate
        holePatternsAreas = []
        holePatternsAreas.append([1,1])
        holePatternsAreas.append([2,1])
        holePatternsAreas.append([1,2])

        countedHoles = 0
        for pattern in holePatternsAreas:
            #debug print("search in cell " + str(cell))
            if not self.isAreaNextToID(cell, pattern, True, self.maskedMap): # Cheks -1 to go up left and look for the whole pattern
                countedHoles += 1

        return countedHoles


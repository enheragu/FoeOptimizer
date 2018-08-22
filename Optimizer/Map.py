
import numpy as np
from shapely import geometry

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
        self.sizeX = availableAreaGeometry.sizeX
        self.sizeY = availableAreaGeometry.sizeY

        self.matrixMap = availableAreaGeometry.matrixMap

    def getAreaUsedBy(self, buildingId):
        return len(np.nonzero(self.matrixMap == buildingId)[0])  # Tonwhall is 1, SimpleRoad is 2, DoubleRoad is 3

    ## Place building of given type in map matrix, using coordinates position as the upper left corner of the building
    # @param buildingType             Buildin to place
    # @param position                Coordinates of the upper left corner
    # @param place                   True if wants to place it, false if just want to check
    # @return                        True if it can be placed, false otherwise
    def placeBuildingInCorner(self, buildingType, position, place = True):

        # Check that the space for this building is empty in the map
        for x in range(position[0], buildingType.size[0]+position[0]):
            for y in range(position[1], buildingType.size[1]+position[1]):
                if x > self.sizeX or y > self.sizeY:
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
    def getNeighbourCellsTo(self, buildingType, position):
        neighbourCells = []
        # Gets neighbours of the building (it thery are inside the matrix and empty)
        if position[0] >= 1:
            for cellY in range(position[1], position[1] + buildingType.size[1]):
                neighbourCells.append([position[0]-1,cellY])

        if position[1] >= 1:
            for cellX in range(position[0], position[0] + buildingType.size[0]):
                neighbourCells.append([cellX,position[1]-1])

        endPosition = [position[0] + buildingType.size[0], position[1] + buildingType.size[1]]
        #debug print("End position is: "+str(endPosition))
        if endPosition[0] <= self.sizeX:
            for cellY in range(endPosition[1] - buildingType.size[1], endPosition[1]):
                neighbourCells.append([endPosition[0],cellY])

        if endPosition[1] <= self.sizeY:
            for cellX in range(endPosition[0] - buildingType.size[0], endPosition[0]):
                neighbourCells.append([cellX,endPosition[1]])

        return neighbourCells


    ## Gets all valid neighbour cells of a given building (identifier size and position) that are 
    #  empty
    # @param buildingType            Buildin to place
    # @param position                Coordinates of the upper left corner
    # @return                        List of cells
    def getValidNeighbourCellsTo(self, buildingType, position):
        validCells = []
        neighbourCells = self.getNeighbourCellsTo(buildingType, position)
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
        neighbourCells = self.getNeighbourCellsTo(buildingType1, position)

        for cell in neighbourCells:
            if self.matrixMap[cell[0]][cell[1]] == buildingType2.mapIdentifier:
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
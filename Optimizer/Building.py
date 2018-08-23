
class BaseBuilding:

    ## Constructor
    # @param name                     Str with name of the building
    # @param size                     Two dimension vector with size of the building (as int)
    # @param number                 Number of buildings of each type (0 means that no exact number is needed, the optimizer can decide, is thought for roads)
    # @param nearBuildingList          List of buildings of which this building needs one by its side (the optimizer will use at least one) [building1 or building2]
    # @param bonusBuildingList         List with buildings that will be located next to it to produce bonus (None by default) (the optimizer must locate them together)
    def __init__(self, name, size, number = 0, nearBuildingList = None, bonusBuildingList = None):
        self.name = name
        self.size = size
        self.number = number
        # nearBuildingList -> list of buildings that this building needs/want
        # buildingListToNear -> list of buildings that needs/want to go next to this
        self.nearBuildingList = nearBuildingList
        self.bonusBuildingList = bonusBuildingList
        self.mapIdentifier = 0

        self.buildingListToNear = []

        self.numberPlaced = 0

    
    def getArea(self):
        return self.size[0]*self.size[1]

    ## Interface method to set a new map identifier
    # @param mapIdentifier             Number that will identify this building in the map
    def setMapIdentifier(self, identifier):
        self.mapIdentifier = identifier


    ## Once the whole buildingList is generated, each building computes its buildingListToNear (get list of other buildings that need to go next to this one)
    # @param buildingList              List of buildings on which to search
    def computeNearBuilding(self, buildingList):
        self.buildingListToNear = []

        for building in buildingList:
            if self.name is building:
                continue
            # If current building is in its needed neighbour list appends it to this building possible neighbour list
            if building.nearBuildingList is not None and self.name in building.nearBuildingList:
                self.buildingListToNear.append(building.name)

            # If current building is in its bonus neighbour list appends it to this building possible neighbour list
            if building.bonusBuildingList is not None and self.name in building.bonusBuildingList:
                self.buildingListToNear.append(building.name)

        # Adds roads as possible candidates (if haven't been added previously)
        if "DoubleRoad" not in self.buildingListToNear:
            self.buildingListToNear.append("DoubleRoad")
        if "SimpleRoad" not in self.buildingListToNear:
            self.buildingListToNear.append("SimpleRoad")

    ## Checks if another building of this type can be added, if so, increments its number of buildings placed
    # @param matrix       Map in which to search for buildings
    # @return             True if building can be incremented, false if all buildings of this type have already been placed
    def placeBuilding(self, matrixMap):
        # Number 0 means that any number of this building can be placed

        numberPlaced = matrixMap.getAreaUsedBy(self.mapIdentifier)/self.getArea()

        if self.number == 0:
            return True

        if numberPlaced == self.number:
            return False
        else:
            return True

    ## To string method overload
    def __str__(self):
        stringBuilding = str(self.name) + " of size " + str(self.size) + ", repeated " + str(self.number) + " time(s). Identified in map as: " + str(self.mapIdentifier )+\
                        "\n\t· Building needed close: " + str(self.nearBuildingList) + \
                        "\n\t· Buildings close to bonus: " + str(self.bonusBuildingList) + \
                        "\n\t· Buildings that may go close to this building: " + str(self.buildingListToNear)
        return stringBuilding


    ## Check if this is the searched building based on name or mapIdentifier
    # @param tag                    Name or mapIdentifier of the building
    # @return                        True if the tag matchs either the name or the map identifier, False otherwise    
    def __eq__(self, tag):
        if tag == self.name or tag == self.mapIdentifier:
            return True
        else:
            return False




class BuildingList(list):

    def __init__(self, buildingList):
        list.__init__(self,buildingList)

        if len(self[:]) > 127:
            raise Exception("No more than 127 building types are accepted (map representation uses int8 types)")

        for index, building in enumerate(self[:]):
            building.setMapIdentifier(index+1)
            building.computeNearBuilding(self[:])

        self.numberOfBuildings = 0
        for building in self[3:]:
            self.numberOfBuildings += building.number

    def getBuiltArea(self, matrixMap):
        area = 0
        numberBuildings = 0
        for buildingType in self[:]:
            if buildingType == "SimpleRoad" or buildingType == "DoubleRoad" or buildingType == "Townhall":
                continue
            else:
                areaThisBuilding = matrixMap.getAreaUsedBy(buildingType.mapIdentifier)
                numberBuildings += (areaThisBuilding/buildingType.getArea())
                area += areaThisBuilding

        return area, numberBuildings

    def getRoadArea(self, matrixMap):
        areaSimpleRoad = matrixMap.getAreaUsedBy(self.get("SimpleRoad").mapIdentifier)
        areaDoubleRoad = matrixMap.getAreaUsedBy(self.get("DoubleRoad").mapIdentifier)

        return areaSimpleRoad + areaDoubleRoad

    ## To string method overload
    def __str__(self):
        string = ""
        for building in self[:]:
            string += " · " + str(building) + "\n"
        return string

    # getitem operator overload
    def get(self, tag):
        for building in self[:]:
            if building == tag:
                return building

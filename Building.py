
class BaseBuilding:

	def __init__(self, name, size, number = 0, nearBuildingList = None, bonusBuildingList = None):
		self.name = name
		self.size = size
		self.number = number
		self.nearBuildingList = nearBuildingList
		self.bonusBuildingList = bonusBuildingList
		self.mapIdentifier = 0
	
	def getArea(self):
		return size[0]*size[1]

	def setMapIdentifier(self, identifier):
		self.mapIdentifier = identifier

	def isBuilding(self, tag):
		if tag == self.name:
			return True
		elif tag == self.mapIdentifier:
			return True
		else:
			return False


class BuildingList:

	def __init__(self, buildingList):
		self.buildingList = buildingList

		for index, building in enumerate(buildingList):
			building.setMapIdentifier(index+1)
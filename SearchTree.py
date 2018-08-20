
class Node:

	def __init__(self, buildingList, buildingType, buildingPosition, parentNode = None):

		self.parentNode = parentNode
		self.buildingList = buildingList
		self.buildingType = buildingType
		self.buildingPosition = buildingPosition

		self.nodeWeight = 0 # (BuiltArea - ToBuildArea) + RoadsArea

	def updateInfo(self):
		
		BuiltBuildingArea = 0
		ToBuildBuildingArea = sum( building.getArea()*building.number for building in self.buildingList )
		BuiltRoadArea = 0

		nextNode = self
		while (nextNode != None):
			self.matrixMap.placeBuilding(self.buildingType.mapIdenfifier, self.buildingType.size, self.buildingPosition)
			
			if nextNode.buildingType.isBuilding("SipleRoad") or nextNode.buildingType.isBuilding("DoubleRoad"):
				BuiltRoadArea += nextNode.buildingType.getArea()
			else:
				BuiltBuildingArea += nextNode.buildingType.getArea()

			nextNode = nextNode.parentNode

		# Heuristic to measure node weight:
		# Takes into account:
		#   - Distance from origin to now: Built area
		#   - Distance from origin to now: Area still to build
		#   - Roads placed

		distanceFromOrigin = BuiltBuildingArea
		distanceToEnd = ToBuildArea - BuiltBuildingArea

		self.nodeWeight = (BuiltBuildingArea - ToBuildArea)

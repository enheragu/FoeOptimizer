
import numpy as np

class BaseMap:
	def __init__(self, borderCoordinates):

		sizeX = 0
		sizeY = 0
		[ sizeX = point[0] for point in borderCoordinates if point[0] > sizeX ]
		[ sizeY = point[1] for point in borderCoordinates if point[1] > sizeY ]

		self.matrixMap = np.full((sizeX, sizeY), np.inf)

	def placeBuilding(self, mapIdenfifier, size, position):
		return True
		return False


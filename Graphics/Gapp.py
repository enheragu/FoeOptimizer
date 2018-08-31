
from Optimizer.Building import BaseBuilding, BuildingList
from Optimizer.SearchTree import NodeId, Node, NodeList, SearchTree, memory_usage_resource

import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, DrawingArea, HPacker
import math


def printNode(node):


    fig, ax = plt.subplots()

    infoBox = TextArea("        -- Node -- " + \
    					"\n · Placed: " + str(node.buildingType.name) + \
    					"\n · At cell " + str(node.buildingPosition) + \
					    "\n · Node weight: " + str(node.nodeWeight) + \
					    "\n · Expanded "+ str(node.getSearchLevel()) + " levels" + \
					    "\n · Contains " + str((node.getRegressedMatrix()).findUnbiltHolesRounded()) + " holes")
    
    box = HPacker(children=[infoBox],
              align="center",
              pad=5, sep=5)

    anchored_box = AnchoredOffsetbox(loc=3,
                                 child=box, pad=0.,
                                 frameon=True,
                                 bbox_to_anchor=(1.02, 0.8),
                                 bbox_transform=ax.transAxes,
                                 borderpad=0.,
                                 )

    matrix = node.getRegressedMatrix().matrixMap
    ax.matshow(matrix)

    ax.add_artist(anchored_box)
    fig.subplots_adjust(right=0.9)
    fig.subplots_adjust(top=0.97)
    fig.subplots_adjust(bottom=0.02)

    for x in range(matrix.shape[0]):
        for y in range(matrix.shape[1]):
            c = matrix[x,y]
            #if not math.isinf(c) and  c != float("inf") and c != float("-inf"):
            #    c = int(c)
            ax.text(y,x, str(int(c)), va='center', ha='center')

    plt.show()
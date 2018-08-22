
import matplotlib.pyplot as plt
import math
def printMap(matrix):


    fig, ax = plt.subplots()
    
    ax.matshow(matrix)


    for x in range(matrix.shape[0]):
        for y in range(matrix.shape[1]):
            c = matrix[x,y]
            #if not math.isinf(c) and  c != float("inf") and c != float("-inf"):
            #    c = int(c)
            ax.text(y,x, str(int(c)), va='center', ha='center')

    plt.show()



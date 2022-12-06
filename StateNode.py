
import math
from TSPClasses import *
class StateNode:
    """
    CALL ONLY IN STATENODE CLASS DEF
    path:               the current path that that is at this depth in the tree. The root will take an empty path, etc
    reducedCostMatrix:  the reduced cost matrix for this node.
    lowerBound:         The lowerBound guess for this path
    city:               The city that is represented by this node.
    """
    def __init__(self, path: list = None, reducedCostMatrix: list = None, lowerBound: int = None, city: City = None, scenario: Scenario = None, isRoot: bool = False):
        if scenario is None:
            self.pathNodes: set = set()
            for city in path:
                if not city is None:
                    self.pathNodes.add(city.getName())
            self.path: list = path
            self.reducedCostMatrix: list = reducedCostMatrix
            self.lowerBound: int = lowerBound
            self.city: City = city
            self.isRoot = isRoot
        else:
            cities = scenario.getCities()
            # make the list for the reduced cost matrix
            self.reducedCostMatrix = []
            for i in range(len(cities)):
                self.reducedCostMatrix.append([])
                for j in range(len(cities)):
                    self.reducedCostMatrix[i].append(cities[i].costTo(cities[j]))
            self.lowerBound = self.reduce(0, self.reducedCostMatrix)
            self.path = [cities[0]]
            self.pathNodes = set()
            self.pathNodes.add(cities[0].getName())
            self.city = cities[0]
            self.isRoot = isRoot

    def __gt__(self, other):
        if self.lowerBound > other.lowerBound:
            return True
        else:
            return False

    """
    returns all of the children of the current node
    """
    def makeChildren(self, scenario: Scenario):
        children = []
        cities = scenario.getCities()
        for i in range(len(cities)):
            city = cities[i]
            if city.getName() not in self.pathNodes:
                children.append(self.makeChild(city))
        return children

    def makeChild(self, childCity: City):
        # self is the parent
        childReducedMatrix = []
        for i in range(len(self.reducedCostMatrix)):
            childReducedMatrix.append([])
            for j in range(len(self.reducedCostMatrix)): # This assumes that the matrix is square
                if childCity.getIndex() == j or self.city.getIndex() == i:
                    childReducedMatrix[i].append(math.inf)
                else:
                    childReducedMatrix[i].append(self.reducedCostMatrix[i][j])
        childPath = []
        for city in self.path:
            childPath.append(city)
        childPath.append(childCity)
        costToChild = self.reducedCostMatrix[self.city.getIndex()][childCity.getIndex()] # This is very important. Without this, all of the optiomistic gueses will be too optimistic, and so you will need to check far too many things.

        childLowerBound = self.reduce(self.lowerBound, childReducedMatrix) + costToChild

        # print(f'lowerBound = {self.lowerBound}! childLowerBound {childLowerBound}')
        return StateNode(childPath, childReducedMatrix, childLowerBound, childCity, None, False)


    def reduce(self, parentLowerBound: int, matrix):
        # find the minimum in each row and subtract it

        lowerBound = parentLowerBound
        for i in range(len(matrix)):
            rowMin = min(matrix[i])
            if not rowMin == math.inf:
                for j in range(len(matrix[i])):
                    matrix[i][j] -= rowMin
                lowerBound += rowMin
        # find the minimum in each column and subtract it.
        for i in range(len(matrix[0])):
            colMin = math.inf
            for j in range(len(matrix)):
                if matrix[j][i] < colMin:
                    colMin = matrix[j][i]
            if not colMin == math.inf:
                for j in range(len(matrix)):
                    matrix[j][i] -= colMin
                lowerBound += colMin
        return lowerBound

    def getPath(self):
        pathNodes = []
        for city in self.path:
            pathNodes.append(city.getName())
        return pathNodes
    def getDepth(self):
        return len(self.path)




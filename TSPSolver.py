#!/usr/bin/python3

from which_pyqt import PYQT_VER

if PYQT_VER == "PYQT5":
  from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == "PYQT4":
  from PyQt4.QtCore import QLineF, QPointF
else:
  raise Exception("Unsupported Version of PyQt: {}".format(PYQT_VER))


import time
import numpy as np
from TSPClasses import *
from StateNode import *
import heapq
import itertools

# Solution to the minimal matching problem
from hungarian import hungarian


def get_cycles(match):
  N = len(match)
  cycles = []
  used = set()
  for i in range(N):
    if i not in used:
      used.add(i)
      c = [i]
      p = match[i]
      while p != i:
        used.add(p)
        c.append(p)
        p = match[p]
      cycles.append(c)
  cycles.sort(key=len, reverse=True)
  return cycles


def merge_cycles(adj, match, cs):
  c1 = cs[0]
  c2 = cs[1]
  next = lambda i: match[i]
  mcost = (
    lambda i, j: adj[i][match[j]]
    + adj[j][match[i]]
    - adj[i][match[i]]
    - adj[j][match[j]]
  )

  min_cost = mcost(c1[0], c2[0])
  min_swap = (c1[0], c2[0])
  for i in c1:
    for j in c2:
      c = mcost(i, j)
      if c < min_cost:
        min_cost = c
        min_swap = (i, j)
  # print(f'{min_cost=}')
  i, j = min_swap
  # print(f'{min_swap=}')
  ni = next(i)
  nj = next(j)
  match[i] = nj
  match[j] = ni
  # print(f'{match=}')
  return match


def get_sol(adj, match):
  path = [0]
  last = 0
  N = len(adj)
  for i in range(N - 1):
    next = match[last]
    path.append(next)
    last = next
  return path


class TSPSolver:
  def __init__(self, gui_view):
    self._scenario = None

  def setupWithScenario(self, scenario):
    self._scenario = scenario

  """ <summary>
    This is the entry point for the default solver
    which just finds a valid random tour.  Note this could be used to find your
    initial BSSF.
    </summary>
    <returns>results dictionary for GUI that contains three ints: cost of solution, 
    time spent to find solution, number of permutations tried during search, the 
    solution found, and three null values for fields not used for this 
    algorithm</returns> 
  """

  def defaultRandomTour(self, time_allowance=60.0):
    results = {}
    cities = self._scenario.getCities()
    ncities = len(cities)
    foundTour = False
    count = 0
    bssf = None
    start_time = time.time()
    while not foundTour and time.time() - start_time < time_allowance:
      # create a random permutation
      perm = np.random.permutation(ncities)
      route = []
      # Now build the route using the random permutation
      for i in range(ncities):
        route.append(cities[perm[i]])
      bssf = TSPSolution(route)
      count += 1
      if bssf.cost < np.inf:
        # Found a valid route
        foundTour = True
    end_time = time.time()
    results["cost"] = bssf.cost if foundTour else math.inf
    results["time"] = end_time - start_time
    results["count"] = count
    results["soln"] = bssf
    results["max"] = None
    results["total"] = None
    results["pruned"] = None
    return results

  """ <summary>
    This is the entry point for the greedy solver, which you must implement for 
    the group project (but it is probably a good idea to just do it for the branch-and
    bound project as a way to get your feet wet).  Note this could be used to find your
    initial BSSF.
    </summary>
    <returns>results dictionary for GUI that contains three ints: cost of best solution, 
    time spent to find best solution, total number of solutions found, the best
    solution found, and three null values for fields not used for this 
    algorithm</returns> 
  """

  def greedy(self, time_allowance=60.0):
    results = {}
    cities = self._scenario.getCities()
    ncities = len(cities)
    count = 0
    bssf = TSPSolution(cities)
    best_cost = bssf.cost
    best_route = list(range(ncities))
    costBetween = lambda i,j:np.inf if i==j else cities[i].costTo(cities[j])
    graph = [[costBetween(j,i) for i in range(ncities)] for j in range(ncities)]
    start_city = 0
    start_time = time.time()
    while start_city < ncities:
      cur_city = start_city
      other_cities = set(range(ncities))
      route = [cur_city]
      cost = 0
      for _ in range(ncities-1):
        other_cities.remove(cur_city)
        next = min(other_cities, key=lambda o: graph[cur_city][o])
        route.append(next)
        cost += graph[cur_city][next]
        cur_city = next
      cost += graph[cur_city][start_city]
      if cost < best_cost:
        best_cost = cost
        best_route = route
      count += 1
      start_city += 1
    bssf = TSPSolution([cities[i] for i in best_route])
    end_time = time.time()
    results["cost"] = bssf.cost
    results["time"] = end_time - start_time
    results["count"] = count
    results["soln"] = bssf
    results["max"] = None
    results["total"] = None
    results["pruned"] = None
    print(results['time'])
    print(results['cost'])
    return results

  """ <summary>
    This is the entry point for the branch-and-bound algorithm that you will implement
    </summary>
    <returns>results dictionary for GUI that contains three ints: cost of best solution, 
    time spent to find best solution, total number solutions found during search (does
    not include the initial BSSF), the best solution found, and three more ints: 
    max queue size, total number of states created, and number of pruned states.</returns> 
  """

  def branchAndBound(self, time_allowance=60.0):
    greedy = self.greedy(time_allowance)
    bssf = greedy["soln"]  # {costOfBestSolution, timeSpent, theBestSolutionFound}
    numCompletePaths = 0
    nCities = len(self._scenario.getCities())
    rootNode = StateNode(None, None, None, None, self._scenario, True)
    startTime = time.time()
    heap = []  # will contain StateNodes. I will need to find some way to get a specific value as the value to be minimized.
    heapq.heapify(heap)
    maxQueueSize = 0
    numPruned = 0
    totalCreated = 0
    heapq.heappush(heap, (0, rootNode))

    while (time.time() - startTime < time_allowance):
      if len(heap) == 0:
        break
      nodeBeingExplored: StateNode = heapq.heappop(heap)[1]

      if nodeBeingExplored.lowerBound > bssf.cost:
        # If this node is not viable, skip it.
        numPruned += 1

      if nodeBeingExplored.getDepth() == nCities:  # Then it is a potential end.
        newBSSF = TSPSolution(nodeBeingExplored.path)  # nodeBeingExplored.lowerBound
        if newBSSF.cost < bssf.cost:
          bssf = newBSSF
          numCompletePaths += 1
        else:
          numPruned += 1
      children = nodeBeingExplored.makeChildren(self._scenario)
      totalCreated += len(children)
      for child in children:
        if child.lowerBound <= bssf.cost:
          priority = (child.lowerBound / nodeBeingExplored.getDepth())
          heapq.heappush(heap, (priority, child))
          if len(heap) > maxQueueSize:
            maxQueueSize = len(heap)
        else:
          numPruned += 1

    endTime = time.time()
    numPruned += len(heap)
    results = {}
    results['cost'] = bssf.cost
    results['time'] = endTime - startTime
    results['count'] = numCompletePaths
    results['soln'] = bssf
    results['max'] = maxQueueSize
    results['total'] = totalCreated
    results['pruned'] = numPruned
    return results

  def fancy(self, time_allowance=60.0):
    results = {}
    cities = self._scenario.getCities()
    ncities = len(cities)
    start_time = time.time()

    # initialize the reduced cost matrix and priority queue
    costBetween = lambda i, j: np.inf if i == j else cities[i].costTo(cities[j])
    adj = [[costBetween(j, i) for i in range(ncities)] for j in range(ncities)]
    # Compute the minimal matching for the graph
    mcost, match = hungarian(adj)
    # Find the distinct cycles in the match permutation
    cycles = get_cycles(match)
    # print(cycles)
    # print(mcost)
    count = 0
    # While the permutation isn't a full cycle
    while len(cycles) > 1:
      count += 1
      # print(cycles)
      merged_match = merge_cycles(adj, match, cycles)
      match = merged_match
      cycles = get_cycles(merged_match)
    path = get_sol(adj, match)
    # print(path)
    city_path = [cities[i] for i in path]
    sol = TSPSolution(city_path)
    end_time = time.time()

    results["cost"] = sol.cost
    results["time"] = end_time - start_time
    results["soln"] = sol
    results["count"] = count
    results["max"] = None
    results["total"] = None
    results["pruned"] = None
    print(results)
    return results

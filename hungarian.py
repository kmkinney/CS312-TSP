import numpy as np

# Using KTHs implementation for this
def hungarian(graph):
  n = len(graph)+1
  m = len(graph[0])+1
  u = [0]*n
  v = [0.0]*m
  p = [0]*m
  ans = [0]*(n-1)
  for i in range(1,n):
    p[0] = i
    j0 = 0
    dist = [np.inf]*m
    prev = [-1]*m
    done = [False]*(m+1)
    while p[j0]:
      done[j0] = True
      i0 = p[j0]
      j1 = -1
      delta = np.inf
      for j in range(1,m):
        if not done[j]:
          cur = graph[i0-1][j-1] - u[i0] - v[j]
          if cur < dist[j]:
            dist[j] = cur
            prev[j] = j0
          if dist[j] < delta:
            delta = dist[j]
            j1 = j
      for j in range(0,m):
        if done[j]:
          u[p[j]] += delta
          v[j] -= delta
        else:
          dist[j] -= delta
      j0 = j1
    while j0:
      j1 = prev[j0]
      p[j0] = p[j1]
      j0 = j1
  for j in range(1,m):
    if p[j]:
      ans[p[j] - 1] = j - 1
  return (-v[0], ans)

import numpy as np
import itertools

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
  print(min_swap)
  i, j = min_swap
  # print(f'{min_swap=}')
  ni = next(i)
  nj = next(j)
  match[i] = nj
  match[j] = ni
  # print(f'{match=}')
  return match

if __name__ == '__main__':
  g = [
    [np.inf,3,7,8,9],
    [6,np.inf,2,32,5],
    [13,1,np.inf,8,12],
    [1,4,90,np.inf,3],
    [32,4,32,1,np.inf]
  ]
  c, a = hungarian(g)
  print(c)
  print(a)
  print(get_cycles(a))
  print(merge_cycles(g,a,get_cycles(a)))

  def cost(p):
    pl = (*p,p[0])
    c = 0
    for a,b in itertools.pairwise(pl):
      c += g[a][b] 
    return c
  
  min_tour = (cost([0,1,2,3,4]),[0,1,2,3,4])
  for perm in itertools.permutations([0,1,2,3,4]):
    pc = cost(perm)
    min_tour = min(min_tour, (pc,perm), key=lambda t: t[0])
  print(min_tour)


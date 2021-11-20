from amplify import BinarySymbolGenerator
from amplify import einsum
from amplify.constraint import one_hot
from amplify import sum_poly
from amplify import Solver
from amplify.client import FixstarsClient
import numpy as np

def index(i, j, n):
  return i * n + j


def app_body():
  # n = 4
  # N = 16
  n = 9
  N = n ** 2
  # del_node = [5] #削除するノードのリスト, 必ず空の配列は渡すこと！
  del_node = []

  INF = 100

  #空のQUBO行列を作成
  Q = np.full(N * N, INF).reshape(N, N)

  for i in range(n):
    for j in range(n):
      if i - 1 >= 0 and not(index(i - 1, j, n) in del_node):
        Q[index(i, j, n)][index(i - 1, j, n)] = 0
      if i + 1 < n and not(index(i + 1, j, n) in del_node):
        Q[index(i, j, n)][index(i + 1, j, n)] = 0
      if j - 1 >= 0 and not(index(i, j - 1, n) in del_node):
        Q[index(i, j, n)][index(i, j - 1, n)] = 0
      if j + 1 < n and not(index(i, j + 1, n) in del_node):
        Q[index(i, j, n)][index(i, j + 1, n)] = 0

  Q = np.delete(Q, del_node, 0) #いらない列の削除
  Q = np.delete(Q, del_node, 1) #いらない行の削除

  N = N - len(del_node) #ノード数の初期化

  gen = BinarySymbolGenerator()
  q = gen.array(N, N)

  #コスト関数定義
  cost_1 = einsum("ij,ni,nj->", Q, q, q.roll(-1, axis=0))

  cost_2 = 0
  for i in range(N):
    for j in range(N):
      cost_2 = cost_2 - Q[i][j] * q[0][i] * q[N - 1][j]

  # 行に対する制約
  row_constraints = [one_hot(q[n]) for n in range(N)]

  # 列に対する制約
  col_constraints = [one_hot(q[:, i]) for i in range(N)]

  constraints = sum(row_constraints) + sum(col_constraints)

  model = cost_1 + cost_2 + 30 * constraints

  client = FixstarsClient()
  client.parameters.timeout = 10000  # タイムアウト5秒
  client.token = "mQHgBQDdqlRgkEuRIT4vScWJEbvoK4ru"

  solver = Solver(client)

  print("start optimization")

  result = solver.solve(model)
  if len(result) == 0:
      raise RuntimeError("Any one of constraints is not satisfied.")

  energy, values = result[0].energy, result[0].values

  q_values = q.decode(values)

  ans = []

  for i in range(N):
    for i, x in enumerate(q_values[i]):
      if x != 0:
        ans.append(i % N)

  print(ans)
  print(energy)
  return ans

if __name__ == "__main__":
  app_body()
import numpy as np
from graphviz import Digraph

size = 15
matrix = np.zeros((size, size))

with open("Варіант №10.txt", "r") as file:
    i = j = 0
    row = col = 0
    for line in file:
        for char in line:
            if char != ' ' and (char == '1' or char == '0'):
                matrix[i][col] = int(char)
                col += 1
            else:
                j += 1
        else:
            i += 1
            col = 0


print("Matrix:")
for row in matrix:
    print(' '.join(map(str, map(int, row))))



# Create a Digraph object from graphviz
graph = Digraph('G', filename='relation_graph', format='png')

# Add nodes starting from 1
for node in range(1, size + 1):
    graph.node(str(node), label=str(node))

# Add edges based on the binary relation matrix
for i in range(size):
    for j in range(size):
        if matrix[i][j] == 1:
            graph.edge(str(i + 1), str(j + 1))  # Adjust indices to start from 1

# Save the DOT file
graph.render()

# Optionally, you can display the graph
graph.view()


def check_acyclic():
    visited = [False] * size
    stack = [False] * size
    cycle = []

    def dfs(node):
        if not visited[node]:
            visited[node] = True
            stack[node] = True

            for neighbor in range(size):
                if matrix[node][neighbor] == 1:
                    if not visited[neighbor]:
                        if dfs(neighbor):
                            cycle.append(node + 1)
                            return True
                    elif stack[neighbor]:
                        cycle.extend([neighbor + 1, node + 1])
                        return True

            stack[node] = False

        return False

    for node in range(size):
        if not visited[node]:
            if dfs(node):
                cycle.reverse()
                print(f"Cycle found: {cycle}")
                return True

    return False



# Neumann-Morgenstern solution

def get_upper_contour_set(node):
    up_set = set()
    for i in range(size):
        if matrix[i][node] == 1:
            up_set.add(i)
    return up_set


# get S sets
def get_S_NM():
    S = []
    up_sets = []
    for i in range(size):
        s = get_upper_contour_set(i)
        up_sets.append(s)
    S0 = []
    for i in range(size):
        if len(up_sets[i]) == 0:
            S0.append(i)
    print('S0:', [val + 1 for val in S0])
    S.append(S0)
    count_s = 1
    while S[-1] != list(range(size)):
        Si = []
        for i in range(size):
            if up_sets[i].issubset(S[-1]):
                Si.append(i)
        print('S{}: {}'.format(count_s, [val + 1 for val in Si]))
        S.append(Si)
        count_s += 1
    return S


# get Q sets
def get_Q_NM(S):
    Q = [S[0]]
    print('Q0: {}'.format([val + 1 for val in Q[0]]))
    up_sets = []
    for i in range(size):
        s = get_upper_contour_set(i)
        up_sets.append(s)
    for i in range(1, len(S)):
        Q.append(Q[-1].copy())

        dif = list(set(S[i]) - set(S[i - 1]))
        for j in dif:
            if len(set(up_sets[j]).intersection(Q[i - 1])) == 0:
                Q[i].append(j)
        print('Q{}: {}'.format(i, [val + 1 for val in Q[i]]))

    return Q


def check_internal_stability(arr):
    for row in arr:
        for col in arr:
            if matrix[row][col] == 1:
                return False
    return True


def check_external_stability(arr):
    for col in range(size):
        if (col in arr):
            continue
        res = False
        for row in arr:
            if matrix[row][col] == 1:
                res = True
                break
        if not res:
            return False
    return True


# K-optimization

# form symmetric, asymmetric and incomparable parts
def get_pin():
    res_mat = []
    for row in range(len(matrix)):
        res_mat.append([])
        for col in range(len(matrix[row])):
            if matrix[row][col] == 1 and matrix[col][row] == 1:
                res_mat[row].append('I')
            elif matrix[row][col] == 0 and matrix[col][row] == 0:
                res_mat[row].append('N')
            elif matrix[row][col] == 1 and matrix[col][row] == 0:
                res_mat[row].append('P')
            else:
                res_mat[row].append('.')
    return res_mat


def check_null(matrix, col):
    for row in range(len(matrix)):
        if matrix[row][col] != 0:
            return False
    return True

def get_S(pin, pin_str):
    S1 = np.zeros((size, size))
    for row in range(len(pin)):
        for col in range(len(pin[row])):
            if pin[row][col] in pin_str:
                S1[row][col] = 1

    for row in S1:
        print(' '.join(map(str, map(int, row))))


    max = []
    opt = []

    for row in range(size):
        is_max_element = True
        is_opt_element = True
        for col in range(size):
            if S1[row][col] != 1:
                is_opt_element = False
                if not check_null(S1, col):
                    is_max_element = False
        if is_max_element:
            max.append(row)
            if is_opt_element:
                opt.append(row)

    return max, opt


is_relation_cyclic = check_acyclic()
if not is_relation_cyclic:
    print("\nВідношення: ациклічне")
    print('Оптимізація за Нейманом-Моргенштерном\n')
    S = get_S_NM()
    Q = get_Q_NM(S)

    int_stab = check_internal_stability(Q[-1])
    ext_stab = check_external_stability(Q[-1])
    print('Внутрішня стійкість: ', int_stab)
    print('Зовнішня стійкість: ', ext_stab)
    print("Ядро Неймана-Моргенштерна: ", [val + 1 for val in Q[-1]])  # last Q is solution
else:
    print("\nВідношення: неациклічне")
    print('K-оптимізація\n')
    pin = get_pin()
    for row in pin:
        print(' '.join(map(str, map(str, row))))


    print('\nK1')
    max_k1, opt_k1 = get_S(pin, 'NPI')
    print('k1-max: ', [val + 1 for val in max_k1])
    print('k1-opt: ', [val + 1 for val in opt_k1])
    print('\nK2')
    max_k2, opt_k2 = get_S(pin, 'NP')
    print('\nk2-max: ', [val + 1 for val in max_k2])
    print('k2-opt: ', [val + 1 for val in opt_k2])
    print('\nK3')
    max_k3, opt_k3 = get_S(pin, 'PI')
    print('\nk3-max: ', [val + 1 for val in max_k3])
    print('k3-opt: ', [val + 1 for val in opt_k3])
    print('\nK4')
    max_k4, opt_k4 = get_S(pin, 'P')
    print('\nk4-max: ', [val + 1 for val in max_k4])
    print('k4-opt: ', [val + 1 for val in opt_k4])

from operator import attrgetter
import pulp as pulp
import numpy as np


def solve_ilp(objective, constraints):
    # print(objective)
    # print(constraints)
    prob = pulp.LpProblem('LP1', pulp.LpMinimize)
    prob += objective
    for cons in constraints:
        prob += cons
    # print(prob)
    status = prob.solve()
    if status != 1:
        # print('status')
        # print(status)
        return None
    else:
        # return [v.varValue.real for v in prob.variables()]
        return [v.varValue.real for v in prob.variables()]




def ILP_packing(resource, flavor_list):
    '''
    利用整数线性规划求解每个flavor的数量，并以字典的形式返回
    '''
    flavor_list = sorted(flavor_list, key=attrgetter('ram'))

    # using PuLP to solve the ILP problem
    flavor_num = 5
    # 变量，直接设置下限
    variables = [pulp.LpVariable('X%d' % i, lowBound=0, cat=pulp.LpInteger) for i in range(0, flavor_num)]
    # 目标函数
    c = [1, 1, 2, 4, 8]
    objective = sum([c[i] * variables[i] for i in range(0, flavor_num)])
    # 约束条件
    constraints = []

    a1 = [1, 1, 2, 4, 8]
    constraints.append(sum([a1[i] * variables[i] for i in range(0, flavor_num)]) >= resource.vcpus)
    a2 = [0.5, 2, 4, 8, 16]
    constraints.append(sum([a2[i] * variables[i] for i in range(0, flavor_num)]) >= resource.ram)
    a3 = [1, 20, 40, 80, 160]
    constraints.append(sum([a3[i] * variables[i] for i in range(0, flavor_num)]) >= resource.ram)
    # print(constraints)

    res = solve_ilp(objective, constraints)
    for r in range(len(res)):
        res[r] = int(res[r])
    print(res)
    flavor_id = []
    for fl in flavor_list:
        flavor_id.append(fl.id)

    #print(flavor_id)

    # dict_value = [0 for _ in range(len(dict_id))]
    vnf_group = dict(zip(flavor_id, res))
    return vnf_group

def ski_rental(rb_ratio):
    '''ski-rental model -'''
    prob_distribution=[]
    rental = lambda i:pow((rb_ratio - 1) / rb_ratio, rb_ratio - i) * \
                                1 / (rb_ratio * (1 - pow((1 - 1 / rb_ratio), rb_ratio)))
    for i in range(1,rb_ratio+1):
        prob_distribution.append(rental(i))

    return np.random.choice(range(1, rb_ratio+1), p=prob_distribution)

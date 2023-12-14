#STUDENT NAME: Cristiano Nicolau
#STUDENT NUMBER: 108536

#DISCUSSED TPI-1 WITH: (names and numbers): Vasco Faria 107323; Pedro Rei 107463; Tiago Cruz 108615

import math
from tree_search import *

class OrderDelivery(SearchDomain):

    def __init__(self, connections, coordinates):
        self.connections = connections
        self.coordinates = coordinates

    def actions(self, state):
        city = state[0]
        actlist = []
        for (C1, C2, D) in self.connections:
            if C1 == city:
                actlist.append((C1, C2))
            elif C2 == city:
                actlist.append((C2, C1))
        return actlist

    def result(self, state, action):
        current_city, targets, start_city = state
        _, next_city = action
        new_targets = tuple(city for city in targets if city != next_city)
        return (next_city, new_targets, start_city)

    def satisfies(self, state, goal):
        return state[0] == state[2] and len(state[1]) == 0

    def cost(self, state, action):
        source_city, destination_city = action
        return next(D for C1, C2, D in self.connections if (C1 == source_city and C2 == destination_city) or (C1 == destination_city and C2 == source_city))

    def heuristic(self, state, goal):
        x1, y1 = self.coordinates[state[0]]
        if len(state[1]) == 0:
            return 0
        min_dist = math.inf
        for city in state[1]:
            x2, y2 = self.coordinates[city]
            min_dist = min(min_dist, math.hypot(x1 - x2, y1 - y2))
        return min_dist

class MyNode(SearchNode):

    def __init__(self,state,parent,depth=0,cost=0,heuristic=0, action=None):
        self.depth = depth
        self.cost = cost
        self.heuristic = heuristic
        self.eval = cost + heuristic
        self.action = action
        self.marked_for_deletion = False
        super().__init__(state,parent)
        
class MyTree(SearchTree):

    def __init__(self,problem, strategy='breadth',maxsize=None):
        super().__init__(problem,strategy)
        self.maxsize = maxsize
        self.root = MyNode(problem.initial, None)
        self.open_nodes = [self.root]
        self.strategy = strategy
        self.solution = None
        self.non_terminals = 0
        self.terminals = 0

        self.highest_cost_nodes = [self.root]

    def astar_add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':  # adds new nodes in the beggining
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'A*':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda node: node.eval)

    def search2(self):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            if self.problem.goal_test(node.state):
                self.solution = node
                self.terminals = len(self.open_nodes)+1
                return self.get_path(node)
            self.non_terminals += 1
            lnewnodes = []
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,a)
                if newstate not in self.get_path(node):
                    depth = node.depth + 1
                    cost = node.cost + self.problem.domain.cost(node.state, a)
                    heuristic = self.problem.domain.heuristic(newstate, self.problem.goal)
                    action = a
                    newnode = MyNode(newstate,node,depth,cost,heuristic,action)
                    lnewnodes.append(newnode)
            self.add_to_open(lnewnodes)
            if self.maxsize is not None and len(self.open_nodes) + self.non_terminals  > self.maxsize and self.strategy == 'A*':
                self.manage_memory()
        return None
    
    def manage_memory(self):
        self.open_nodes.sort(key=lambda node: node.eval)
        all_nodes = len(self.open_nodes) + self.non_terminals
        while all_nodes > self.maxsize:
            node = self.open_nodes.pop()
            self.non_terminals -= 1
            if not node.marked_for_deletion:
                node.marked_for_deletion = True
                
                siblings = [n for n in self.open_nodes if n.parent == node.parent and not n.marked_for_deletion]

                if len(siblings) == 0:
                    continue
            
                min_cost = min(c.eval for c in siblings)

                node.parent.eval = min_cost

                all_nodes -= len(siblings)

        self.open_nodes.sort(key=lambda node: (node.eval, node.state[0]))

def orderdelivery_search(domain, city, targetcities, strategy='breadth', maxsize=None):
    problem = SearchProblem(domain, (city, tuple(targetcities), city), city)
    tree = MyTree(problem, strategy, maxsize)
    path = tree.search2()
    if path is None:
        return None, None
    path = [node[0] for node in path]
    return tree, path


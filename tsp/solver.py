import math
import itertools
from collections import namedtuple
from itertools import combinations
import time
from time import time


class TspSolver(object):
    def __init__(self, points):
        self.CMP_THRESHOLD = 10 ** -6
        self.points = points
        self.cycle = list(range(len(points))) + [0]
        self.obj = self.cycle_length()

    def __str__(self):
        obj = self.cycle_length()
        opt = 0
        if not self.is_valid_soln():
            raise ValueError("Solution not valid")
        output_str = "{:.2f} {}\n".format(obj, opt)
        output_str += ' '.join(map(str, self.cycle[:-1]))
        return output_str

    @staticmethod
    def point_dist(p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def is_valid_soln(self):
        return len(set(self.cycle[:-1])) == len(self.points) == len(self.cycle[:-1])

    def edge_length(self, v1, v2):
        p1 = self.points[v1]
        p2 = self.points[v2]
        return self.point_dist(p1, p2)

    def cycle_length(self):
        return sum(self.edge_length(v1, v2) for v1, v2 in zip(self.cycle[:-1], self.cycle[1:]))

    def greedy(self):
        cycle = [0]
        candidates = set(self.cycle[1:-1])
        while candidates:
            curr_point = cycle[-1]
            nearest_neighbor = None
            nearest_dist = math.inf
            for neighbor in candidates:
                neighbor_dist = self.edge_length(curr_point, neighbor)
                if neighbor_dist < nearest_dist:
                    nearest_neighbor = neighbor
                    nearest_dist = neighbor_dist
            cycle.append(nearest_neighbor)
            candidates.remove(nearest_neighbor)
        cycle.append(0)
        self.cycle = cycle
        self.obj = self.cycle_length()
        return self.__str__()


class TwoOptSolver(TspSolver):
    def swap(self, start, end):
        improved = False
        new_cycle = self.cycle[:start] + self.cycle[start:end + 1][::-1] + self.cycle[end + 1:]
        new_obj = self.obj - (self.edge_length(self.cycle[start - 1], self.cycle[start]) +
                              self.edge_length(self.cycle[end], self.cycle[(end + 1)])) + \
            (self.edge_length(new_cycle[start - 1], new_cycle[start]) +
             self.edge_length(new_cycle[end], new_cycle[(end + 1)]))
        if new_obj < self.obj - self.CMP_THRESHOLD:
            self.cycle = new_cycle
            self.obj = new_obj
            improved = True
        return improved

    def solve(self, t_threshold=None):
        improved = True
        t = time()
        while improved:
            if t_threshold and time() - t >= t_threshold:
                break
            improved = False
            for start, end in combinations(range(1, len(self.cycle) - 1), 2):
                if self.swap(start, end):
                    improved = True
                    break
        return self.__str__()


Point = namedtuple("Point", ['x', 'y'])


def edge_length(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


def cycle_length(cycle, points):
    return sum(edge_length(points[cycle[i - 1]], points[cycle[i]]) for i in range(len(cycle)))


def solve_it(input_data):
    lines = input_data.split('\n')

    point_count = int(lines[0])

    points = []
    for i in range(1, point_count + 1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))

    solver = TwoOptSolver(points)

    output_data = solver.solve()

    return output_data


def k_swap(cycle, length, endpoints, points):
    k = len(endpoints) + 1
    segments = [cycle[endpoints[i]:endpoints[i + 1]] for i in range(len(endpoints) - 1)]
    best_cycle = cycle
    best_length = length
    for num_reversed in range(k):
        for reversed_parts in itertools.combinations(range(len(segments)), k):
            new_segments = []
            for i, segment in enumerate(segments):
                if i in reversed_parts:
                    new_segments.append(segment[::-1])
                else:
                    new_segments.append(segment)
            for i, permuted_segments in enumerate(itertools.permutations(new_segments)):
                if num_reversed == 0 and i == 0:
                    continue
                new_cycle = cycle[:endpoints[0]] + list(itertools.chain.from_iterable(permuted_segments)) +\
                            cycle[endpoints[-1] + 1:]
                new_length = cycle_length(new_cycle, points)
                if new_length < best_length:
                    best_cycle = new_cycle
                    best_length = best_length
    return best_cycle, best_length


def k_swap_iteration(cycle, points, k):
    point_count = len(points)
    length = cycle_length(cycle, points)
    improved = False
    for endpoints in itertools.combinations(range(1, point_count), k):
        new_cycle, new_length = k_swap(cycle, length, endpoints, points)
        if new_length < length:
            cycle = new_cycle
            length = new_length
            improved = True
            break
    return cycle, length, improved


def k_opt(points, k_max=2, initial=None, time_limit=None):
    if initial:
        cycle = initial
    else:
        _, _, cycle = points.greedy()
    t = time.clock()
    for k in range(2, k_max + 1):
        improved = True
        while improved:
            if time_limit and time.clock() - t > time_limit:
                break
            cycle, length, improved = k_swap_iteration(cycle, points, k)
    return cycle_length(cycle, points), 0, cycle


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print(
            'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

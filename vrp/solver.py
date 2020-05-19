import math
from collections import namedtuple
import random
import time
from copy import deepcopy

global DEPOT
Customer = namedtuple("Customer", ['index', 'demand', 'x', 'y'])


def length(customer1, customer2):
    return math.sqrt((customer1.x - customer2.x) ** 2 + (customer1.y - customer2.y) ** 2)


def trivial_sol(customers, depot, vehicle_count, vehicle_capacity):
    vehicle_tours = []

    remaining_customers = set(customers)
    remaining_customers.remove(depot)

    for v in range(0, vehicle_count):
        vehicle_tours.append([])
        capacity_remaining = vehicle_capacity
        while sum([capacity_remaining >= customer.demand for customer in remaining_customers]) > 0:
            used = set()
            order = sorted(remaining_customers, key=lambda customer: -customer.demand)
            for customer in order:
                if capacity_remaining >= customer.demand:
                    capacity_remaining -= customer.demand
                    vehicle_tours[v].append(customer)
                    used.add(customer)
            remaining_customers -= used
    return vehicle_tours


def parametrize(customer_count):
    if customer_count < 50:
        return 600, find_neighbour_2
    elif customer_count < 90:
        return 300, find_neighbour_2
    elif customer_count < 400:
        return 300, find_neighbour
    else:
        return 300, find_neighbour


def check_minimum(current, novel, temperature):
    prev_value = state_value(current)
    curr_value = state_value(novel)
    if curr_value <= prev_value:
        return True
    if math.exp(-abs(curr_value - prev_value) / temperature) > random.random():
        return True
    return False


def state_value(veh_tours):
    global DEPOT
    obj = 0
    for v in range(len(veh_tours)):
        vehicle_tour = veh_tours[v]
        if len(vehicle_tour) > 0:
            obj += length(DEPOT, vehicle_tour[0])
            for i in range(0, len(vehicle_tour) - 1):
                obj += length(vehicle_tour[i], vehicle_tour[i + 1])
            obj += length(vehicle_tour[-1], DEPOT)
    return obj


def find_neighbour(curr_sol, customers, vehicle_capacity):
    neighbours = deepcopy(curr_sol)
    client = random.randint(1, len(customers) - 1)
    d = customers[client].demand
    available = []
    for veh_tour in neighbours:
        if customers[client] in veh_tour:
            veh_tour.remove(customers[client])
        cap = vehicle_capacity
        for i in veh_tour:
            cap -= i.demand
        available.append(cap)
    s = [(i, x) for (i, x) in enumerate(available) if x >= d]
    vehicle = s[random.randint(0, len(s) - 1)][0]
    position = random.randint(0, len(curr_sol[vehicle]))
    neighbours[vehicle].insert(position, customers[client])
    return neighbours


def find_neighbour_2(curr_sol, vehicle_capacity):
    neighbour = deepcopy(curr_sol)
    vehicle1 = random.randint(0, len(curr_sol) - 1)
    while len(curr_sol[vehicle1]) == 0:
        vehicle1 = random.randint(0, len(curr_sol) - 1)
    client = random.randint(0, len(curr_sol[vehicle1]) - 1)
    tmp = neighbour[vehicle1][client]
    cap1, cap2 = vehicle_capacity + 1, 0
    while cap1 > vehicle_capacity or cap2 < tmp.demand:
        vehicle2 = random.randint(0, len(curr_sol) - 1)
        position = random.randint(0, len(curr_sol[vehicle2]))
        cap1 = sum(curr_sol[vehicle1][x].demand for x in range(len(curr_sol[vehicle1])) if x != client)
        if position < len(curr_sol[vehicle2]):
            cap1 += curr_sol[vehicle2][position].demand
        cap2 = vehicle_capacity - sum(curr_sol[vehicle2][x].demand for x in range(len(curr_sol[vehicle2])) if x != position)
    if position < len(curr_sol[vehicle2]):
        neighbour[vehicle1][client] = neighbour[vehicle2][position]
        neighbour[vehicle2][position] = tmp
    else:
        neighbour[vehicle1].remove(tmp)
        neighbour[vehicle2].insert(position, tmp)
    return neighbour


def local_search(customers, guess, vehicle_capacity, time_limit=120, fnc=find_neighbour):
    best = deepcopy(guess)
    current = guess
    restart = 0
    counter = 0
    t = len(customers)
    alpha = 0.999
    minimum = 1e-8
    start = time.time()
    diff = time.time() - start
    while diff < time_limit:
        if t <= minimum:
            t = len(customers)
            restart += 1
        neigh = fnc(current, customers, vehicle_capacity)
        if neigh is not None:
            if check_minimum(current, neigh, t):
                current = neigh
                if state_value(current) < state_value(best):
                    best = deepcopy(current)
        counter += 1
        t *= alpha
        diff = time.time() - start

    return best


def solve_it(input_data):
    global DEPOT
    random.seed(1659163401)
    lines = input_data.split('\n')

    parts = lines[0].split()
    customer_count = int(parts[0])
    vehicle_count = int(parts[1])
    vehicle_capacity = int(parts[2])

    customers = []
    for i in range(1, customer_count + 1):
        line = lines[i]
        parts = line.split()
        customers.append(Customer(i - 1, int(parts[0]), float(parts[1]), float(parts[2])))

    # склад - это всегда первый 'клиент' во входном файле
    depot = customers[0]
    DEPOT = depot

    vehicle_tours = trivial_sol(customers, depot, vehicle_count, vehicle_capacity)

    limit, neigh_fnc = parametrize(customer_count)
    vehicle_tours = local_search(customers, vehicle_tours, vehicle_capacity, time_limit=limit, fnc=neigh_fnc)

    # проверяет правильность количества клиентов
    assert sum([len(v) for v in vehicle_tours]) == len(customers) - 1

    # рассчитываем стоимость решения; для каждого транспортного средства длина маршрута
    obj = state_value(vehicle_tours)

    outputData = '%.2f' % obj + ' ' + str(0) + '\n'
    for v in range(0, vehicle_count):
        outputData += str(depot.index) + ' ' + ' '.join(
            [str(customer.index) for customer in vehicle_tours[v]]) + ' ' + str(depot.index) + '\n'

    return outputData


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:

        print(
            'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/vrp_5_4_1)')
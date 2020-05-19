#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple

Item = namedtuple("Item", ['index', 'value', 'weight'])


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count + 1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i - 1, int(parts[0]), int(parts[1])))

    if len(items) <= 200 or len(items) == 1000:
        value, taken = dp(items, capacity)
    else:
        value, taken = greedy_density(items, capacity)

    output_data = str(value) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


def greedy(items, capacity):
    value = 0
    weight = 0
    taken = [0] * len(items)

    for item in items:
        if weight + item.weight <= capacity:
            taken[item.index] = 1
            value += item.value
            weight += item.weight
    return value, taken


def greedy_density(items, capacity):
    sorted_data = sorted(items, key=lambda item: item.value / item.weight, reverse=True)
    return greedy(sorted_data, capacity)


def dp(items, capacity):
    taken = [0] * len(items)

    a = [[0 for i in range(capacity + 1)] for j in range(len(items) + 1)]

    capacity_range = capacity + 1
    items_range = len(items) + 1

    for k in range(1, len(items) + 1):
        for s in range(1, capacity + 1):
            curr_item = items[k - 1]
            if curr_item.weight <= s:
                a[k][s] = max(a[k - 1][s], a[k - 1][s - curr_item.weight] + curr_item.value)
            else:
                a[k][s] = a[k - 1][s]

    i = items_range - 1
    j = capacity_range - 1
    value = a[i][j]
    taken = [0] * len(items)

    while i > 0 and j > 0:
        if a[i][j] != a[i - 1][j]:
            taken[i - 1] = 1
            j -= items[i - 1].weight
        i -= 1
    return value, taken


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print(
            'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')
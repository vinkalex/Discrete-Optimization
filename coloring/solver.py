from collections import namedtuple  # вместо классов
from random import shuffle
import time

Colors = namedtuple('Colors', ['label', 'current_color', 'colors_domain', 'adj_vertexes', 'checked'])
Solution = namedtuple('Solution', ['colors_count', 'colors'])


def update_vertex(vertexes, current_vertex, adj_vertex, vertex_count):
    if not current_vertex in vertexes:
        vertexes[current_vertex] = Colors(current_vertex, 0, range(0, vertex_count), [adj_vertex], False)
    elif not adj_vertex in vertexes[current_vertex].adj_vertexes:
        vertexes[current_vertex].adj_vertexes.append(adj_vertex)


def update_adj_vertexes(vertexes, current_vertex, current_colors_count):
    if current_vertex.checked == False:
        for v in current_vertex.adj_vertexes:
            adj_vertex = vertexes[v]
            if current_vertex.current_color in adj_vertex.colors_domain:
                adj_vertex.colors_domain.remove(current_vertex.current_color)
                vertexes[v] = Colors(v, adj_vertex.colors_domain[0], adj_vertex.colors_domain, adj_vertex.adj_vertexes,
                                     adj_vertex.checked)

                used_colors, num_colors = get_used_colors(vertexes)
                if num_colors >= current_colors_count:
                    return False

        vertexes[current_vertex.label] = Colors(current_vertex.label, current_vertex.colors_domain[0],
                                           current_vertex.colors_domain, current_vertex.adj_vertexes, True)

    return True


def get_used_colors(vertexes):
    used_colors = map(lambda vertex: vertexes[vertex].current_color, vertexes.keys())  
    num_colors = len(set(used_colors))

    return used_colors, num_colors


def solve_it(input_data):
    lines = input_data.split('\n')

    first_line = lines[0].split()
    vertex_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    vertexes = dict()
    solution = Solution(vertex_count, [])
    number_of_randomizations = 5
    start_time = time.time()
    max_time = min(60 * 60 * 4, edge_count)

    for i in range(1, edge_count + 1):
        line = lines[i]
        vertex = line.split()
        edges.append((int(vertex[0]), int(vertex[1])))

    randomizations = 0
    p = 0
    while randomizations < number_of_randomizations and time.time() - start_time < max_time:
        shuffle(edges)

        vertexes = dict()
        i = 0
        while i < edge_count:
            current_edge = edges[i]
            vertex_1 = current_edge[0]
            vertex_2 = current_edge[1]

            update_vertex(vertexes, vertex_1, vertex_2, vertex_count)
            update_vertex(vertexes, vertex_2, vertex_1, vertex_count)

            i += 1

        i = 0
        while i < edge_count:
            current_edge = edges[i]
            vertex_1 = current_edge[0]
            vertex_2 = current_edge[1]

            if not update_adj_vertexes(vertexes, vertexes[vertex_1], solution.colors_count) or not \
                    update_adj_vertexes(
                    vertexes, vertexes[vertex_2], solution.colors_count):
                break

            i += 1

        used_colors, num_colors = get_used_colors(vertexes)

        if num_colors < solution.colors_count:
            solution = Solution(num_colors, used_colors)
            randomizations += 1

    output_data = str(solution.colors_count) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution.colors))

    return output_data


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print(
            'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')
def indexloop(value, max_index):
    return value if value <= max_index else value - max_index - 1


def set_solid_block_texture(matrix):
    a = 0
    edges, vertices = (matrix[0][1], matrix[1][0], matrix[2][1], matrix[1][2]), (matrix[0][0], matrix[2][0], matrix[2][2], matrix[0][2])
    edgecount, verticescount = edges.count(0), vertices.count(0)
    if edgecount == 0:
        if verticescount == 0:
            a = 19
        elif verticescount == 1:
            a = 15 + vertices.index(0)
        elif verticescount == 2:
            a = {(1, 0, 1, 0): 40,
                 (0, 1, 0, 1): 41,
                 (0, 1, 1, 0): 28,
                 (0, 0, 1, 1): 29,
                 (1, 0, 0, 1): 30,
                 (1, 1, 0, 0): 31
                 }[vertices]
        elif verticescount == 3:
            a = {(0, 0, 1, 0): 36,
                 (0, 0, 0, 1): 37,
                 (1, 0, 0, 0): 38,
                 (0, 1, 0, 0): 39,
                 }[vertices]
        elif verticescount == 4:
            a = 42
    elif edgecount == 1:
        a = edges.index(0)
        for i in range(4):
            if a == i:
                if vertices[indexloop(2 + i, 3)] == 0 and vertices[indexloop(1 + i, 3)] == 0:
                    a = 32 + i
                elif vertices[indexloop(1 + i, 3)] == 0:
                    a = 20 + i
                elif vertices[indexloop(2 + i, 3)] == 0:
                    a = 24 + i

    elif edgecount == 2:
        a = {(0, 0, 1, 1): 4,
            (1, 0, 0, 1): 5,
             (1, 1, 0, 0): 6,
             (0, 1, 1, 0): 7,
             (0, 1, 0, 1): 13,
             (1, 0, 1, 0): 14}[edges]
        if 4 <= a <= 7:
            for i in range(4):
                if a == 4 + i:
                    if vertices[indexloop(2 + i, 3)] == 0:
                        a = 43 + i
    elif edgecount == 3:
        a = {(1, 0, 0, 0): 9,
             (0, 1, 0, 0): 10,
             (0, 0, 1, 0): 11,
             (0, 0, 0, 1): 8}[edges]
    elif edgecount == 4:
        a = 12
    return a

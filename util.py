from pandas import DataFrame

SHIFT = [[-1, 0],  # go north
         [0, 1],  # go east
         [1, 0],  # go south
         [0, -1]]  # go west

LARGE_INT = 999


def build_visit_grid(n):
    grid = [[0] * n for _ in range(n)]
    grid[n - 1][0] = 1  # first node is visited
    return grid


def build_maze(n):
    maze = [[0] * n for _ in range(n)]
    open_up_wall(maze, n - 1, 0)
    open_bottom_wall(maze, n - 2, 0)
    return maze


def open_up_wall(maze, i, j):
    maze[i][j] |= 1 << 0


def open_right_wall(maze, i, j):
    maze[i][j] |= 1 << 1


def open_bottom_wall(maze, i, j):
    maze[i][j] |= 1 << 2


def open_left_wall(maze, i, j):
    maze[i][j] |= 1 << 3


def in_range(i, j, n):
    if 0 <= i < n and 0 <= j < n:
        return True
    return False


def update_maze(maze, heading, sensors, i, j):
    n = len(maze)
    north, east, south, west = 0, 0, 0, 0
    left, front, right = sensors[0], sensors[1], sensors[2]
    if heading == 'up':
        west, north, east = left, front, right
    elif heading == 'right':
        north, east, south = left, front, right
    elif heading == 'down':
        east, south, west = left, front, right
    elif heading == 'left':
        south, west, north = left, front, right
    if north > 0:
        open_up_wall(maze, i, j)
        for offset in range(1, north):
            i_ = i - offset
            if in_range(i_, j, n):
                open_bottom_wall(maze, i_, j)
                open_up_wall(maze, i_, j)
        open_bottom_wall(maze, i - north, j)
    if east > 0:
        open_right_wall(maze, i, j)
        for offset in range(1, east):
            j_ = j + offset
            if in_range(i, j_, n):
                open_left_wall(maze, i, j_)
                open_right_wall(maze, i, j_)
        open_left_wall(maze, i, j + east)
    if south > 0:
        open_bottom_wall(maze, i, j)
        for offset in range(1, south):
            i_ = i + offset
            if in_range(i_, j, n):
                open_up_wall(maze, i_, j)
                open_bottom_wall(maze, i_, j)
        open_up_wall(maze, i + south, j)
    if west > 0:
        open_left_wall(maze, i, j)
        for offset in range(1, west):
            j_ = j - offset
            if in_range(i, j_, n):
                open_left_wall(maze, i, j_)
        open_right_wall(maze, i, j - west)


# Checks bounds and walls
def can_move_one(maze, i, j, shift):
    n = len(maze[0])
    if not 0 <= shift < len(SHIFT):
        return False
    if not in_range(i, j, n):
        return False
    if not (0 <= i + SHIFT[shift][0] < n and 0 <= j + SHIFT[shift][1] < n):
        return False
    pos = 1 << shift
    return maze[i][j] & pos != 0


def possible_moves(maze, visit, i, j):
    options = []
    visit_m = False
    if visit:
        visit_m = True
    for shift in range(len(SHIFT)):
        off_i = SHIFT[shift][0]
        off_j = SHIFT[shift][1]
        if can_move_one(maze, i, j, shift):
            i_ = i + off_i
            j_ = j + off_j
            if visit_m:
                options.append((visit[i_][j_], i_, j_))
            else:
                options.append((i_, j_))
            if can_move_one(maze, i_, j_, shift):
                i_ += off_i
                j_ += off_j
                if visit_m:
                    options.append((visit[i_][j_], i_, j_))
                else:
                    options.append((i_, j_))
                if can_move_one(maze, i_, j_, shift):
                    i_ += off_i
                    j_ += off_j
                    if visit_m:
                        options.append((visit[i_][j_], i_, j_))
                    else:
                        options.append((i_, j_))
    if visit_m:
        options.sort()
    return options


def robot_moves(heading, i, j, i_, j_):
    if i != i_ and j != j_:
        print 'robot can move in one way only!'
    v_d = abs(i - i_)
    h_d = abs(j - j_)
    if v_d > 3 or h_d > 3:
        print 'robot can move maximum 3 spaces'
    if i != i_:
        if i > i_:
            inv = 1  # north
        else:
            inv = -1  # south
        if heading == 'up':
            return 0, inv * v_d
        if heading == 'right':
            return -90, inv * v_d
        if heading == 'down':
            return 0, inv * -v_d
        if heading == 'left':
            return 90, inv * v_d
    if j != j_:
        if j < j_:
            inv = 1  # east/right
        else:
            inv = -1
        if heading == 'up':
            return 90, inv * h_d
        if heading == 'right':
            return 0, inv * h_d
        if heading == 'down':
            return -90, inv * h_d
        if heading == 'left':
            return 0, inv * -h_d
    return 0, 0


def change_rotation(heading, rotation):
    if rotation == 90:
        if heading == 'up':
            return 'right'
        elif heading == 'right':
            return 'down'
        elif heading == 'down':
            return 'left'
        elif heading == 'left':
            return 'up'
    elif rotation == -90:
        if heading == 'up':
            return 'left'
        elif heading == 'right':
            return 'up'
        elif heading == 'down':
            return 'right'
        elif heading == 'left':
            return 'down'
    return heading


########################################################
# 2nd phase


def get_coord_min_matrix(dist_m, visit_m):
    n = len(dist_m)
    i_, j_ = -1, -1
    min_ = LARGE_INT
    for i in range(n):
        for j in range(n):
            if dist_m[i][j] < min_ and not visit_m[i][j]:
                min_ = dist_m[i][j]
                i_ = i
                j_ = j
    return i_, j_


def dijkstra(maze):
    n = len(maze)
    dist_m = [[LARGE_INT] * n for _ in range(n)]
    prev_m = [[None] * n for _ in range(n)]
    visit_m = [[False] * n for _ in range(n)]
    to_visit = n * n - 1  # source node is visited
    dist_m[n - 1][0] = 0
    while to_visit > 0:
        i, j = get_coord_min_matrix(dist_m, visit_m)
        visit_m[i][j] = True
        to_visit -= 1
        neighbors = possible_moves(maze, None, i, j)
        for v in neighbors:
            i_, j_ = v
            if not visit_m[i_][j_]:
                alt = dist_m[i][j] + 1
                if alt < dist_m[i_][j_]:
                    dist_m[i_][j_] = alt
                    prev_m[i_][j_] = (i, j)
    return dist_m, prev_m


def shortest_path(maze):
    n = len(maze)
    dist_m, prev_m = dijkstra(maze)
    centers_dist = []
    for r in range(-1, 1):
        for c in range(-1, 1):
            i, j = n / 2 + r, n / 2 + c
            centers_dist.append((dist_m[i][j], i, j))
    centers_dist.sort()
    steps, i, j = centers_dist[0]  # i,j from optimal center
    path = [(i, j)]
    for _ in range(steps - 1):
        i, j = prev_m[i][j]
        path.append((i, j))
    path.reverse()
    print 'optimal # moves: ', len(path)
    return path

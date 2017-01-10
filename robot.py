import util as u
import random
from pandas import DataFrame


class Robot(object):
    def __init__(self, maze_dim):

        self.heading = 'up'
        self.n = maze_dim
        self.to_discover = self.n * self.n - 1
        self.location = [self.n - 1, 0]
        self.visit = u.build_visit_grid(self.n)
        self.maze = u.build_maze(self.n)
        self.times = 0
        self.first_exploration = True
        self.optimal_path = None

    def next_move(self, sensors):

        if self.first_exploration:
            i, j = self.location[0], self.location[1]
            u.update_maze(self.maze, self.heading, sensors, i, j)
            visit_count, i_, j_ = u.possible_moves(self.maze, self.visit, i, j)[0]
            # For random choice, uncomment the following line.
            # visit_count, i_, j_ = random.choice(u.possible_moves(self.maze, self.visit, i, j))
            self.location = [i_, j_]
            if self.visit[i_][j_] == 0:
                self.to_discover -= 1
                if self.to_discover == 0:
                    self.visit[i_][j_] += 1
                    print 'Time took to explore: ', self.times
                    self.first_exploration = False
                    self.times = 0
                    self.optimal_path = u.shortest_path(self.maze)
                    print self.optimal_path
                    self.heading = 'up'
                    self.location = [self.n - 1, 0]
                    print DataFrame(self.visit)
                    print DataFrame(self.maze)
                    return 'Reset', 'Reset'
            self.visit[i_][j_] += 1
            rotation, movement = u.robot_moves(self.heading, i, j, i_, j_)
            self.heading = u.change_rotation(self.heading, rotation)
            self.times += 1
            if self.times == 1000:
                print DataFrame(self.visit)
                print DataFrame(self.maze)
            return rotation, movement
        else:
            i, j = self.location[0], self.location[1]
            i_, j_ = self.optimal_path[self.times]
            self.times += 1
            self.location = [i_, j_]
            rotation, movement = u.robot_moves(self.heading, i, j, i_, j_)
            self.heading = u.change_rotation(self.heading, rotation)
            return rotation, movement

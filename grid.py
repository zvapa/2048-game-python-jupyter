import random
from typing import List, Dict, Tuple
import numpy as np


class Grid:
    """Creates a grid of 'rows' by 'columns'"""

    def __init__(self, rows: int, columns: int) -> None:
        self.r_size = rows
        self.c_size = columns
        # initialize the empty grid as a dict, where keys are tuples of (row_index, column_index)
        self.grid: Dict[Tuple[int, int], int] = {(r, c): 0 for r in range(self.r_size) for c in range(self.c_size)}
        self.directions = {
            "right": (self.r_size, self.get_row_coords, self.move_fwd),
            "down": (self.c_size, self.get_column_coords, self.move_fwd),
            "left": (self.r_size, self.get_row_coords, self.move_bwrd),
            "up": (self.c_size, self.get_column_coords, self.move_bwrd)}
        self.score: int = 0
        self.still_playing = True

    def to_numpy(self):
        """Returns the grid values as a 2d numpy array."""
        return np.array([v for v in self.grid.values()]).reshape((self.r_size, self.c_size))

    def update_grid(self) -> None:
        """Updates grid with some values. (used in debugging)"""

        self.grid[(0, 0)] = 16
        self.grid[(0, 1)] = 8
        self.grid[(0, 2)] = 4
        self.grid[(0, 3)] = 0
        self.grid[(1, 0)] = 8
        self.grid[(1, 1)] = 2
        self.grid[(1, 2)] = 0
        self.grid[(1, 3)] = 0
        self.grid[(2, 0)] = 4
        self.grid[(2, 1)] = 0
        self.grid[(2, 2)] = 0
        self.grid[(2, 3)] = 0
        self.grid[(3, 0)] = 0
        self.grid[(3, 1)] = 2
        self.grid[(3, 2)] = 0
        self.grid[(3, 3)] = 0

    def get_empty(self):
        """Returns a list of coordinates of empty tiles."""
        return [k for k, v in self.grid.items() if v == 0]

    def spawn(self) -> None:
        """Inserts value 2 or 4 at random empty slots on the grid. If no empty tiles, the game is over."""
        empty_coords = self.get_empty()
        self.grid[random.choice(empty_coords)] = random.choices([2, 4], [0.8, 0.2])[0]

    def get_column_coords(self, column_index: int) -> List[Tuple[int, int]]:
        """Returns a list of coordinates representing a column on the grid."""
        return [(r, c) for (r, c) in self.grid.keys() if c == column_index]

    def get_row_coords(self, row_index: int) -> List[Tuple[int, int]]:
        """Returns a list of coordinates representing a row on the grid."""
        return [(r, c) for (r, c) in self.grid.keys() if r == row_index]

    def move_fwd(self, l: List[Tuple[int, int]]) -> None:
        """Iterates from right to left over a given row or column, to move or add to the next available position.

        Start with penultimate position. For each non-zero tile, move the value all the way to the right,
        until another non-zero value or the end of the line is encountered.
        If the value encountered is the same, add to it, if it hasn't already been added into.
        Else, place the value immediately before it, and keep iterating over the rest of the line.

        eg.:
        [0, 2, 0, 0] -> [0, 0, 0, 2]
        [0, 2, 0, 2] -> [0, 0, 0, 4]
        [2, 2, 0, 2] -> [0, 0, 2, 4]
        [2, 2, 2, 2] -> [0, 0, 4, 4]
        """

        curr, last = len(l) - 2, len(l) - 1
        while curr >= 0:
            if self.grid[l[curr]] == 0 and self.grid[l[last]] == 0:  # 0 -> 0
                curr -= 1
            elif self.grid[l[curr]] == 0 and self.grid[l[last]] != 0:  # 0 -> x
                curr -= 1
            elif self.grid[l[curr]] != 0 and self.grid[l[last]] == 0:  # x -> 0
                self.grid[l[curr]], self.grid[l[last]] = 0, self.grid[l[curr]]
                curr -= 1
            elif self.grid[l[curr]] == self.grid[l[last]]:  # x -> x
                self.score += self.grid[l[curr]]
                self.grid[l[curr]], self.grid[l[last]] = 0, self.grid[l[curr]] * 2
                curr -= 1
                last -= 1
            else:  # x -> y
                self.grid[l[curr]], self.grid[l[last - 1]] = 0, self.grid[l[curr]]
                curr -= 1
                last -= 1

    def move_bwrd(self, l: List[Tuple[int, int]]) -> None:
        """Iterates from left to right over a given row or column, to move or add to the previous available position.

        Start with the second position. For each non-zero tile, move the value all the way to the left, until another
        non-zero value or the beginning of the line is encountered.
        If the value encountered is the same, add to it, if it hasn't already been added into.
        Else, place the value immediately after it, and keep iterating over the rest of the line.

        eg.:
        [0, 2, 0, 0] -> [2, 0, 0, 0]
        [0, 2, 0, 2] -> [4, 0, 0, 0]
        [2, 2, 0, 2] -> [4, 2, 0, 0]
        [2, 2, 2, 2] -> [4, 4, 0, 0]
        """

        prev, curr = 0, 1
        while curr < len(l):
            if self.grid[l[prev]] == 0 and self.grid[l[curr]] == 0:  # 0 <- 0
                curr += 1
            elif self.grid[l[prev]] == 0 and self.grid[l[curr]] != 0:  # 0 <- x
                self.grid[l[prev]], self.grid[l[curr]] = self.grid[l[curr]], 0
                curr += 1
            elif self.grid[l[prev]] != 0 and self.grid[l[curr]] == 0:  # x <- 0
                curr += 1
            elif self.grid[l[prev]] == self.grid[l[curr]]:  # x <- x
                self.score += self.grid[l[curr]]
                self.grid[l[prev]], self.grid[l[curr]] = self.grid[l[curr]] * 2, 0
                curr += 1
                prev += 1
            else:  # x <- y
                self.grid[l[curr]], self.grid[l[prev + 1]] = 0, self.grid[l[curr]]
                curr += 1
                prev += 1

    def slide(self, direction: str) -> bool:
        """Slides in the given direction ('right', 'down', 'left', 'up') and returns True if move generated any change.

        If 'right' -> applies 'move_fwd()' to each row.
        If 'down' -> applies 'move_fwd()' to each column.
        If 'left' -> applies 'move_bwrd()' to each row.
        If 'up' -> applies 'move_bwrd()' to each column.
        """
        prior = self.grid.copy()

        for i in range(self.directions[direction][0]):
            line = self.directions[direction][1](i)
            self.directions[direction][2](line)

        return self.grid != prior

    def no_equal_neigbours(self, coord: Tuple[int, int]) -> bool:
        """Checks if given coordinate has no equal neighbours, i.e. no adjacent equal values column-wise or row-wise."""
        r, c = coord
        neighbours_coord = [(r - 1, c) if r - 1 >= 0 else None,
                            (r + 1, c) if r + 1 < self.r_size else None,
                            (r, c - 1) if c - 1 >= 0 else None,
                            (r, c + 1) if c + 1 < self.c_size else None]
        neighbours = [self.grid[t] for t in neighbours_coord if t]
        return self.grid[coord] not in neighbours

    def game_over(self) -> bool:
        """Checks the entire board for no empty tiles and no equal neighbours."""
        return all(self.no_equal_neigbours(k) for k in self.grid.keys()) and not self.get_empty()

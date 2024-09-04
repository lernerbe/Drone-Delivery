import sys
import math
import argparse
from enum import Enum
from typing import List

class LocationType(Enum):
    MAIN_CAMPUS = 1
    MEDICAL_CAMPUS = 2
    BORDER = 3

class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.location = None

def set_location(p: Point):
    if p.x < 0 and p.y < 0:
        p.location = LocationType.MEDICAL_CAMPUS
    elif (p.y == 0 and p.x <= 0) or (p.x == 0 and p.y <= 0):
        p.location = LocationType.BORDER
    else:
        p.location = LocationType.MAIN_CAMPUS

def calc_distance_rootless(p1: Point, p2: Point, isA: bool) -> float:
    if isA and ((p1.location == LocationType.MEDICAL_CAMPUS and p2.location == LocationType.MAIN_CAMPUS) or 
                (p1.location == LocationType.MAIN_CAMPUS and p2.location == LocationType.MEDICAL_CAMPUS)):
        return math.inf
    first = float(p2.x) - float(p1.x)
    second = float(p2.y) - float(p1.y)
    return (first * first) + (second * second)

def calc_distance_exact(p1: Point, p2: Point) -> float:
    first = float(p2.x) - float(p1.x)
    second = float(p2.y) - float(p1.y)
    return math.sqrt((first * first) + (second * second))

class Prim:
    def __init__(self):
        self.K = False
        self.D = math.inf
        self.P = None

class A:
    def __init__(self, entries: List[Point]):
        self.running_total = 0.0
        self.prim = []
        self.entries = entries

    def solve_prim(self):
        n = len(self.entries)
        self.prim = [Prim() for _ in range(n)]
        self.prim[0].D = 0

        for i in range(n):
            smallest = math.inf
            smallest_index = 0
            for j in range(n):
                if not self.prim[j].K and self.prim[j].D < smallest:
                    smallest = self.prim[j].D
                    smallest_index = j

            self.prim[smallest_index].K = True
            self.running_total += math.sqrt(smallest)

            for h in range(n):
                distance = calc_distance_rootless(self.entries[smallest_index], self.entries[h], True)
                if not self.prim[h].K and distance < self.prim[h].D:
                    self.prim[h].D = distance
                    self.prim[h].P = smallest_index

    def print_output(self):
        self.solve_prim()
        print(f"{self.running_total:.2f}")
        for i in range(1, len(self.entries)):
            print(f"{min(i, self.prim[i].P)} {max(i, self.prim[i].P)}")

    def mst_estimator(self, perm_length: int, path: List[int]) -> float:
        n = len(path) - perm_length
        self.prim = [Prim() for _ in range(n)]
        self.prim[0].D = 0
        for i in range(n):
            smallest = math.inf
            smallest_index = 0
            for j in range(n):
                if not self.prim[j].K and self.prim[j].D < smallest:
                    smallest = self.prim[j].D
                    smallest_index = j
            self.prim[smallest_index].K = True
            self.running_total += math.sqrt(smallest)
            for h in range(n):
                distance = calc_distance_rootless(self.entries[path[smallest_index + perm_length]], self.entries[path[h + perm_length]], True)
                if not self.prim[h].K and distance < self.prim[h].D:
                    self.prim[h].D = distance
                    self.prim[h].P = smallest_index
        return self.running_total

class B:
    def __init__(self, entries: List[Point]):
        self.entries = entries
        self.route = []
        self.total_length = 0.0

    def find_insertion_index(self, new_point: Point, current_route: List[int]) -> int:
        best_index = 0
        min_distance = math.inf

        for i in range(len(current_route) - 1):
            distance = (calc_distance_exact(self.entries[current_route[i]], new_point) +
                        calc_distance_exact(new_point, self.entries[current_route[i + 1]]) -
                        calc_distance_exact(self.entries[current_route[i]], self.entries[current_route[i + 1]]))
            if distance < min_distance:
                min_distance = distance
                best_index = i + 1

        self.total_length += min_distance
        return best_index

    def solve_arbitrary_insertion(self):
        self.route = [0, 0]
        self.total_length = 0.0
        for i in range(1, len(self.entries)):
            insertion_index = self.find_insertion_index(self.entries[i], self.route)
            self.route.insert(insertion_index, i)
        self.route.pop()

    def print_output(self):
        self.solve_arbitrary_insertion()
        print(f"{self.total_length:.2f}")
        print(" ".join(map(str, self.route)))

class C:
    def __init__(self, entries: List[Point]):
        self.entries = entries
        self.path = []
        self.best_path = []
        self.cur_length = 0.0
        self.min_distance = math.inf

    def initialize_path(self):
        path_init = B(self.entries)
        path_init.solve_arbitrary_insertion()
        self.min_distance = path_init.total_length
        self.path = path_init.route
        self.best_path = path_init.route

    def gen_perms(self, perm_length: int):
        if perm_length == len(self.path):
            temp_distance = calc_distance_exact(self.entries[self.path[-1]], self.entries[self.path[0]])
            self.cur_length += temp_distance
            if self.cur_length < self.min_distance:
                self.min_distance = self.cur_length
                self.best_path = self.path[:]
            self.cur_length -= temp_distance
            return

        if not self.promising(perm_length):
            return

        for i in range(perm_length, len(self.path)):
            self.path[perm_length], self.path[i] = self.path[i], self.path[perm_length]
            temp_distance = calc_distance_exact(self.entries[self.path[perm_length - 1]], self.entries[self.path[perm_length]])
            self.cur_length += temp_distance

            self.gen_perms(perm_length + 1)
            self.cur_length -= temp_distance
            self.path[perm_length], self.path[i] = self.path[i], self.path[perm_length]

    def promising(self, perm_length: int) -> bool:
        min_first = math.inf
        min_second = math.inf
        for i in range(perm_length, len(self.path)):
            cur_min = calc_distance_exact(self.entries[self.path[0]], self.entries[self.path[i]])
            if cur_min < min_first:
                min_first = cur_min
            cur_min = calc_distance_exact(self.entries[self.path[perm_length - 1]], self.entries[self.path[i]])
            if cur_min < min_second:
                min_second = cur_min
        if self.cur_length + min_first + min_second > self.min_distance:
            return False
        path_rest = A(self.entries)
        remainder = path_rest.mst_estimator(perm_length, self.path)
        return self.cur_length + remainder + min_first + min_second < self.min_distance

    def print_output(self):
        self.initialize_path()
        self.gen_perms(1)
        print(f"{self.min_distance:.2f}")
        print(" ".join(map(str, self.best_path)))

def read_input(opt) -> List[Point]:
    num_vertices = int(input())
    points = [Point(0, 0) for _ in range(num_vertices)]
    for i in range(num_vertices):
        x, y = map(int, input().split())
        points[i].x = x
        points[i].y = y
        if opt.m == "MST":
            set_location(points[i])
    return points

def print_help():
    print("Usage: [-m MST|FASTTSP|OPTTSP] | -h\n< inputFile")

def get_mode():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', choices=['MST', 'FASTTSP', 'OPTTSP'], required=True)
    args = parser.parse_args()
    return args

def main():
    sys.stdout.write("{:.2f}\n".format(0))
    opt = get_mode()
    points = read_input(opt)

    if opt.m == "MST":
        m = A(points)
        m.print_output()
    elif opt.m == "FASTTSP":
        m = B(points)
        m.print_output()
    elif opt.m == "OPTTSP":
        m = C(points)
        m.print_output()

if __name__ == "__main__":
    main()

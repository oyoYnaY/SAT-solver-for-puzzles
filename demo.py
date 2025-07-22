#!/usr/bin/env python3
from z3 import *
import re
import time

def parse_puzzle(path):
    """
    Read and parse an n*n puzzle from file.
    First line: column targets
    Next n lines: row target and n cells ('.' or 'T')
    Returns:
      - nrows, ncols: dimensions
      - row_targets: list of integers
      - col_targets: list of integers
      - board: list of lists of characters
      - tree_positions: set of (row, col) of trees (1-based)
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.read().splitlines() if line.strip()]
    tokens = [re.split(r'\s+', line) for line in lines]
    col_targets = list(map(int, tokens[0]))
    ncols = len(col_targets)

    row_targets = []
    board = []
    for row in tokens[1:]:
        if len(row) < ncols + 1:
            raise ValueError(f"Bad input line (expected {ncols+1} tokens): {row}")
        row_targets.append(int(row[0]))
        board.append(row[1:1 + ncols])
    nrows = len(board)

    tree_positions = {
        (i+1, j+1)
        for i in range(nrows)
        for j in range(ncols)
        if board[i][j] == "T"
    }

    return nrows, ncols, row_targets, col_targets, board, tree_positions

def build_solver(nrows, ncols, row_targets, col_targets, tree_positions):
    """
    Build a Z3 Solver with all puzzle constraints.
    Returns:
      - solver instance
      - p: matrix of Bool variables p[i][j]
    Constraints:
      1) No tent on a tree cell.
      2) Exact row/column counts.
      3) No two tents adjacent (8 directions).
      4a) Tent-to-tree pairing: each tent adjacent to a tree.
      4b) Tree-to-tent pairing: each tree adjacent to a tent.
    """
    # Declare Bool variables
    p = [[Bool(f"p_{i+1}_{j+1}") for j in range(ncols)]
         for i in range(nrows)]
    s = Solver()

    # 1) Exclusion: no tent on a tree cell
    for (ti, tj) in tree_positions:
        s.add(p[ti-1][tj-1] == False)

    # 2) Row and column count constraints
    for i in range(nrows):
        s.add(AtMost(*[p[i][j] for j in range(ncols)], row_targets[i]))
        s.add(AtLeast(*[p[i][j] for j in range(ncols)], row_targets[i]))
    for j in range(ncols):
        s.add(AtMost(*[p[i][j] for i in range(nrows)], col_targets[j]))
        s.add(AtLeast(*[p[i][j] for i in range(nrows)], col_targets[j]))

    # 3) Privacy: no two adjacent tents (in 8 directions)
    def all_neighbors(i, j):
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < nrows and 0 <= nj < ncols:
                    yield ni, nj

    for i in range(nrows):
        for j in range(ncols):
            for (ni, nj) in all_neighbors(i, j):
                s.add(Or(Not(p[i][j]), Not(p[ni][nj])))

    # Helper for orthogonal neighbors (up/down/left/right)
    def orth_neighbors(i, j):
        for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < nrows and 0 <= nj < ncols:
                yield ni, nj

    # 4a) Tent-to-tree pairing
    for i in range(nrows):
        for j in range(ncols):
            tree_consts = [
                BoolVal((ni+1, nj+1) in tree_positions)
                for ni, nj in orth_neighbors(i, j)
            ]
            s.add(Implies(p[i][j], Or(*tree_consts)))

    # 4b) Tree-to-tent pairing (pure CNF: at least one neighbor p[ ] is true)
    for (ti, tj) in tree_positions:
        i, j = ti-1, tj-1
        neigh_tents = [p[ni][nj] for ni, nj in orth_neighbors(i, j)]
        if neigh_tents:
            s.add(Or(*neigh_tents))

    return s, p

def solve_and_display(path):
    """
    Parse the puzzle, build solver, solve, and display results.
    Also exports constraints to 'z3_constraints.smt2'.
    """
    nrows, ncols, row_targets, col_targets, board, trees = parse_puzzle(path)
    solver, p = build_solver(nrows, ncols, row_targets, col_targets, trees)

    # Solve and measure time
    start = time.time()
    result = solver.check()
    duration = time.time() - start
    print(f"Z3 status: {result}, time: {duration:.4f} sec")

    # Export SMT-LIB v2
    with open("z3_constraints.smt2", "w", encoding="utf-8") as fout:
        fout.write(solver.to_smt2())

    # If satisfiable, print board solution
    if result == sat:
        model = solver.model()
        header = "      " + "".join(f"{'c'+str(j+1):^4}" for j in range(ncols))
        print(header)
        for i in range(nrows):
            row_str = ""
            for j in range(ncols):
                if (i+1, j+1) in trees:
                    row_str += " T  "
                elif is_true(model[p[i][j]]):
                    row_str += " X  "
                else:
                    row_str += " .  "
            print(f"r{i+1}: {row_str}")
    else:
        print("No solution found.")

if __name__ == "__main__":
    solve_and_display("5*5 example1.txt")


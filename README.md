# SAT-Solver-for-Puzzles 🎄⛺️

A simple **Python solver for the "Tents and Trees" logic puzzle** using **constraint programming techniques** and **Z3 SMT solver**.

This project demonstrates how to formalize grid-based puzzles into SAT/SMT problems and solve them programmatically. It is a minimal but complete example of encoding constraints into formal logic and using modern solvers.

---

## What is Tents and Trees?

**Tents and Trees** is a classic grid-based logic puzzle.  
Objective: Place tents (`X`) next to trees (`T`) following these rules:
1. Each tent must be **orthogonally adjacent to exactly one tree**.
2. A tree may only be connected to **one tent**.
3. **Tents cannot touch each other**, even diagonally.
4. The number of tents per **row and column is fixed** (given as constraints).

---

## My Approach

### Formal Modeling
Each cell is assigned a boolean variable `pᵢⱼ`:
- `pᵢⱼ = True` means this cell contains a **tent**
- Otherwise, it is either empty or a tree.

### Encode Constraints into SAT / SMT
I express the rules as formal logic constraints:

**Example formulas:**  
(Using `pᵢⱼ` to represent whether there is a tent at cell `(i, j)`)

**Row / Column count constraints**  
For each row `i` and column `j`, the number of `True` in that row/column must match the given count.

**pairing constraint**  
If `pᵢⱼ` is `True`, there must exist a neighboring cell with a tree.
For each **tree cell** `(i, j)`, there must exist **exactly one tent** orthogonally adjacent.

**Privacys constraint**  
No two adjacent (including diagonally) cells can both be tents.

**Exclusion constraint**
No Tent on Tree Cells

All these constraints are encoded into **Z3 SMT-LIB** format through Python.

---

## Input Format (Example)
Puzzle definition from text file:
  2 1 1 2       
1 . T . .
1 . T T .
1 . . . .
0 . . . .
1 . . T .
1 . . . .
1 T . . T

## Expected output format:
       c1  c2  c3  c4  c5 
r1:  X   T   .   .   .  
r2:  T   .   X   T   X  
r3:  X   .   T   .   .  
r4:  .   .   .   .   .  
r5:  .   .   .   X   T 

Legend:
- `X`: Tent
- `T`: Tree
- `.`: Empty

---

## Run solver
```bash
python demo.py



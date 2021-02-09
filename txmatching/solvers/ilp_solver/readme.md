# TXMatching models

## Requirements

The program was tested in `Python 3.9`.
Installing dependencies

```sh
pip3 install -r requirements.txt
```

TODO: Gurobi

## Implemented models

- `anderson_recursive.py`
    - recursive model from `[1]` with lazy constraints
    - uses python-mip API, can use both Gurobi or CBC
        - works well with Gurobi, but CBC solver may hang while solving
- `anderson_recursive_gurobi.py`
    - recursive model from `[1]` with lazy constraints
    - only Gurobi (uses Gurobi API)
- `anderson_recursive_nocb.py`
    - recursive model from `[1]`
    - no lazy constraints: solves relaxed model to optimality, checks the solution and if infeasible, adds cutting constraint and resolves the new model
    - uses python-mip API (can use both Gurobi or CBC)

Currently, the program uses `anderson_recursive_nocb.py` (other models might not be up-to date with API interface).

## Run the program

For example,

```sh
python3 ilp_solver.py --objective max_trans_max_weights patients_26_01_2021.json
```

runs the program on instance `patients_26_01_2021.json` with objective to maximize the number of transplants.
The solution of the model is written into `result.json` in the current working directory.

The full documentation of the program can be obtained with `-h` or `--help` flags

```sh
python3 ilp_solver.py --help
```



## References

- [`[1]`](https://www.pnas.org/content/112/3/663) Finding long chains in kidney exchange Ross Anderson, Itai Ashlagi, David Gamarnik, Alvin E. Roth Proceedings of the National Academy of Sciences Jan 2015, 112 (3) 663-668; DOI: 10.1073/pnas.1421853112

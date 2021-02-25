# TXMatching models

## Implemented models

`anderson_recursive_nocb.py`
    - recursive model from `[1]`
    - no lazy constraints: solves relaxed model to optimality, checks the solution and if infeasible, adds cutting constraint and resolves the new model
    - uses python-mip API (can use both Gurobi or CBC), but at the moment only CBC is used.


## References

- [`[1]`](https://www.pnas.org/content/112/3/663) Finding long chains in kidney exchange Ross Anderson, Itai Ashlagi, David Gamarnik, Alvin E. Roth Proceedings of the National Academy of Sciences Jan 2015, 112 (3) 663-668; DOI: 10.1073/pnas.1421853112

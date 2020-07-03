# Kidney Exchange

Solver for kidney exchange problems. 

## Algorithm API
The file structure containing the key classes of the algoritm API is: 
```
kidney_exchange
    ├── filters
    │   └── filter_base.py
    ├── patients
    │   ├── donor.py
    │   ├── patient.py
    │   └── recipient.py
    ├── scorers
    │   ├── additive_scorer.py
    │   └── scorer_base.py
    └── solvers
        ├── solver_base.py
        └── matching
            ├── cycle.py
            ├── matching.py
            ├── round.py
            └── sequence.py

```
The optimal matchings are found in several steps.
1. Define list of donors and recipients 
    - `Donor(id: str, parameters: PatientParameters)`
    - `Recipient(id: str, parameters: PatientParameters, related_donors: Donor)`
     
2. Define scorer, that can optionally have some <b>parameters</b>
    - `scorer = ScorerBase() [HLAAdditiveScorer, ...]`
    
3. Find list of suitable transplant matchings by running a solver on the 
lists of donors, recipients using scorer.
    - `SolverBase().solve(donors, recipients, scorer)`
    
    which returns a list of matchings in the form:      
    - `Matching(donor_recipient_list: List[Tuple[Donor, Recipient]])`

    which consist of several disjoint rounds. 
    - `Round(donor_recipient_list: List[Tuple[Donor, Recipient]])`  
    
    These can be either a closed cycle or sequence of transplants
    - `Cycle[Round]`
    - `Sequence[Round]`
    
4. These matchings can then be optionally filtered according to some <b>parameters</b> 
    - `Filter.keep(matching) -> bool`
    
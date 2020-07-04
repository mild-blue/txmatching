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
            ├── transplant_cycle.py
            ├── matching.py
            ├── transplant_round.py
            └── transplant_sequence.py

```
The optimal matchings are found in several steps.
1. Define list of donors and recipients 
    - `Donor(patient_id: str, parameters: PatientParameters)`
    - `Recipient(patient_id: str, parameters: PatientParameters, related_donors: Donor)`
     
2. Define scorer, that can optionally have some <b>parameters</b>
    - `scorer = ScorerBase() [HLAAdditiveScorer, ...]`
    
3. Find list of suitable transplant matchings by running a solver on the 
lists of donors, recipients using scorer.
    - `SolverBase().solve(donors, recipients, scorer)`
    
    which returns a list of matchings in the form:      
    - `Matching(donor_recipient_list: List[Tuple[Donor, Recipient]])`

    which consist of several disjoint rounds. 
    - `TransplantRound(donor_recipient_list: List[Tuple[Donor, Recipient]])`  
    
    These can be either a closed cycle or sequence of transplants
    - `TransplantCycle[TransplantRound]`
    - `TransplantSequence[TransplantRound]`
    
4. These matchings can then be optionally filtered according to some <b>parameters</b> 
    - `Filter.keep(matching) -> bool`
    
## Loading Excel Data
For testing purposes the patient data can be loaded from `.xlsx` file using the utility `utils/excel_parsing/parse_excel_data.py`. This requires that you set environment variable 
```
PATIENT_DATA_PATH=/home/user/path/to/your/patient_data.xlsx
``` 

## Graph Tool
Currently some of the solvers use [graph-tool](https://graph-tool.skewed.de/) package. This can't 
easily be installed via pip and you have to use for example conda to install it. For more info see the official website. 
```
conda install -c conda-forge graph-tool
```
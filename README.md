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
    
## Loading Excel Data
For testing purposes the patient data can be loaded from `.xlsx` file using the utility `utils/excel_parsing/parse_excel_data.py`. This requires that you set environment variable 
```
PATIENT_DATA_PATH=/home/user/path/to/your/patient_data.xlsx
``` 

## Dependencies management
We are using `conda` for managing dependencies as [graph-tool](https://graph-tool.skewed.de/)
can be installed just from the `conda-forge` repository.

#### Project installation
After you cloned the repository, execute `make conda-create` which creates Conda env for you.

#### Development
One must switch to `conda` env before development - use `conda activate kidney-exchange`
to switch to correct environment.
This must be execute every time when you try to use new terminal.

#### Adding new dependencies
To add new package execute `conda install <package>` and then put `<package>` to `conda.yml`.
Please try to install specific version which you put to `conda.yml` in order to guarantee that whole team has same 
packages versions.
To learn which version you installed, run `conda env export | grep <package>`, then copy the version 
(something like `1.18.5`, without `py38h1f821a2_0` suffix).

If the package for some reason can not be installed by `conda install <>` use `pip install`
and then put the package to `- pip:` part of the `conda.yml`:
```yaml
  - pip:
      - flask=1.1.2
```

#### Updating packages
When there's new change in the `conda.yml` (a teammate added new package) execute `make conda-update`.


## Graph Tool
Currently some of the solvers use [graph-tool](https://graph-tool.skewed.de/) package. This can't 
easily be installed via pip and you have to use for example conda to install it. For more info see the official website. 
```
conda install -c conda-forge graph-tool
```
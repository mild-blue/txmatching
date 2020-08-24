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
    - `Matching(donor_recipient_list: List[DonorRecipientTuple])`

    which consist of several disjoint rounds.
    - `TransplantRound(donor_recipient_list: List[DonorRecipientTuple])`

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

## Swagger
We'have a swagger UI running on `/doc/` route (so for example, `localhost:8080/doc/`).
How to use it and some useful info [here on doc](https://flask-restx.readthedocs.io/en/latest/swagger.html).

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
To add new package put `<package>` to `conda.yml` and execute `make conda-update`.
Please try to install specific version which you put to `conda.yml` in order to guarantee that whole team has same 
packages versions.
Try to put package to `dependencies` part of yaml, that are the packages installed from conda repository,
if the package is not in the conda repo, put it in the `pip` part of yaml.

#### Updating packages
when someone updates and you pull new version from git do the following:
```
make conda-update
```

## Git hooks
there are some githooks in this project. It is advised to use them. After installing dependecies in conda it should be enough to run
```
pre-commit install
```
then everytime you commit it first fails in case there were some changes done by the pre-commit script.
If you recommit it will pass, because all the needed changes were done. Its especially so we do not push notebooks
that would contain data to git.

## Application configuration
Right now Flask web server tries to load configuration from the environment
with fallback to loading from [`local_config.py`](kidney_exchange/web/local_config.py).
All current configuration can be found [here](kidney_exchange/web/app_configuration/application_configuration.py).
To obtain configuration in the code, one should call `get_application_configuration()`
 from [application_configuration.py](kidney_exchange/web/app_configuration/application_configuration.py).

## Graph Tool
Currently some of the solvers use [graph-tool](https://graph-tool.skewed.de/) package. This can't 
easily be installed via pip and you have to use for example conda to install it.
This is the reason we're using Conda. There's also no package for Windows, thus we support only
mac and linux.

### Testing
To run tests that need database do the following:

```
make setup-db-for-tests
```

run tests

### Frontend

For detailed FE related stuff see [README.md](kidney_exchange/web/frontend/README.md).

#### Build FE for BE
In order to build FE for the app one must run `make build-fe`. 
One must do that ever time when something was changed in the FE code in order to have up to date FE.
What this does is that it builds FE code to `kidney_exchange/web/frontend/dist/frontend` directory, 
where it is picked up by the Flask.

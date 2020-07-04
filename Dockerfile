FROM datavid19/conda-base AS build

WORKDIR /app

# install dependencies
COPY conda.yml .
RUN conda env create -f conda.yml
# all RUN commands from now use the kidney-exchange environment
SHELL ["conda", "run", "-n", "kidney-exchange", "/bin/bash", "-c"]

# copy rest of the app
COPY kidney_exchange .

# entry point - replace last part with start of the actual command
ENTRYPOINT ["conda", "run", "-n", "kidney-exchange", "/bin/bash", "-c"]
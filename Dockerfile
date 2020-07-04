FROM datavid19/conda-base AS build

WORKDIR /app

# install dependencies
COPY conda.yml .
RUN conda env create -f conda.yml
# all RUN commands from now use the kidney-exchange environment
SHELL ["conda", "run", "-n", "kidney-exchange", "/bin/bash", "-c"]

# do all your magic from here
# copy rest of the app
COPY kidney_exchange ./kidney_exchange

# entry point - replace last part with start of the actual command
ENTRYPOINT ["conda", "run", "-n", "kidney-exchange", "/bin/bash", "-c", "gunicorn --bind 0.0.0.0:8080 kidney_exchange.web.app:app"]
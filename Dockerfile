FROM datavid19/conda-base AS build

WORKDIR /app

# install dependencies
COPY conda.yml .
RUN conda env create -f conda.yml
# activate shell
RUN conda init bash

# do all your magic from here
# copy rest of the app
COPY kidney_exchange ./kidney_exchange

# start the app - one must initialize shell beforehand
CMD . ~/.bashrc && \
    conda activate kidney-exchange && \
    gunicorn --bind 0.0.0.0:8080 kidney_exchange.web.app:app
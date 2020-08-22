FROM mildblue/txmatching-base AS build
LABEL description="Mild Blue - Transplant Kidney Matching"
LABEL project="mildblue:txmatching"

WORKDIR /app

# install dependencies
COPY conda.yml .
RUN conda env create -f conda.yml
# register conda in the .bashrc
RUN conda init bash

# do all your magic from here
# copy rest of the app
COPY kidney_exchange ./kidney_exchange

# create version file
ARG release_version=development-docker
ENV RELEASE_FILE_PATH=./release.txt
RUN echo $release_version > $RELEASE_FILE_PATH

# start the app - one must initialize shell beforehand
CMD . ~/.bashrc && \
    conda activate kidney-exchange && \
    gunicorn --bind 0.0.0.0:8080 kidney_exchange.web.app:app
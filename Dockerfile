# Build frontend
FROM node:16.14.0-alpine as frontend-build

COPY txmatching/web/frontend ./frontend
WORKDIR ./frontend
RUN npm i
RUN npm run build-prod

# Build backend
FROM ghcr.io/mild-blue/txmatching-conda-dependencies:1.0.19 AS backend-build
LABEL description="Mild Blue - TXMatching"
LABEL project="mildblue:txmatching"



WORKDIR /app

RUN apt-get install xfonts-75dpi -y && \
    wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb  && \
    dpkg -i wkhtmltox_0.12.6-1.buster_amd64.deb && \
    echo "export PATH=/usr/bin/wkhtmltopdf/bin:$PATH" > ~/.bashrc && \
    . ~/.bashrc

ENTRYPOINT [ "wkhtmltopdf" ]
# check that the base image has same conda as the repo
COPY conda.yml conda.yml.repo
RUN diff --strip-trailing-cr conda.yml conda.yml.repo

# Do all your magic from here
# Copy rest of the app
COPY txmatching ./txmatching
RUN mkdir -p /logs

# Copy pre-built frontend
COPY --from=frontend-build ./frontend/dist/frontend /app/txmatching/web/frontend/dist/frontend

# Create version file
ARG release_version=development-docker
ENV RELEASE_FILE_PATH=/app/release.txt
RUN echo $release_version > $RELEASE_FILE_PATH

ENV PORT=8080


# Start the app - one must initialize shell beforehand
CMD . ~/.bashrc && \
    conda init bash && \
    conda activate txmatching && \
    gunicorn  \
        --config txmatching/web/gunicorn_configuration.py \
        --bind 0.0.0.0:${PORT} \
        --timeout 1800 \
        --graceful-timeout 1800 \
         txmatching.web.app:app && \


   # apt-get purge wkhtmltopdf -y && \
# RUN apt-get install xfonts-75dpi -y && \
#     wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb  && \
#     dpkg -i wkhtmltox_0.12.6-1.buster_amd64.deb && \
#     echo "export PATH=/usr/bin/wkhtmltopdf/bin:$PATH" > ~/.bashrc && \
#     . ~/.bashrc


# install wkhtmltopdf 0.12.6
# RUN apt-get remove wkhtmltopdf --purge -y && \
#     wget -O /tmp/wkhtmltopdf.deb https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb  && \
#     apt install /tmp/wkhtmltopdf.deb -y && \
#     echo "export PATH=/usr/bin/wkhtmltopdf/bin:$PATH" > ~/.bashrc && \
#     . ~/.bashrc && \
#     rm /tmp/wkhtmltopdf.deb

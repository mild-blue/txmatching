# Build frontend
FROM node:16.14.0-alpine as frontend-build

COPY txmatching/web/frontend ./frontend
WORKDIR ./frontend
RUN npm i
RUN npm run build-prod

# Build backend
FROM ghcr.io/mild-blue/txmatching-conda-dependencies:1.0.22 AS backend-build
LABEL description="Mild Blue - TXMatching"
LABEL project="mildblue:txmatching"

WORKDIR /app

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
    conda activate txmatching && \
    gunicorn  \
        --config txmatching/web/gunicorn_configuration.py \
        --bind 0.0.0.0:${PORT} \
        --timeout 1800 \
        --graceful-timeout 1800 \
         txmatching.web.app:app

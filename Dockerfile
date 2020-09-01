# Build frontend
FROM node:12.16.1-alpine as frontend-build

COPY txmatching/web/frontend ./frontend
WORKDIR ./frontend
RUN npm i
RUN npm run build-prod

# Build backend
FROM mildblue/txmatching-base AS backend-build
LABEL description="Mild Blue - Transplant Kidney Matching"
LABEL project="mildblue:txmatching"

WORKDIR /app

# Install dependencies
COPY conda.yml .
RUN conda env create -f conda.yml
# Register conda in the .bashrc
RUN conda init bash

# Do all your magic from here
# Copy rest of the app
COPY txmatching ./txmatching

# Copy pre-built frontend
COPY --from=frontend-build ./frontend/dist/frontend /app/txmatching/web/frontend/dist/frontend

# Create version file
ARG release_version=development-docker
ENV RELEASE_FILE_PATH=./release.txt
RUN echo $release_version > $RELEASE_FILE_PATH

# Start the app - one must initialize shell beforehand
CMD . ~/.bashrc && \
    conda activate txmatching && \
    gunicorn --bind 0.0.0.0:8080 txmatching.web.app:app
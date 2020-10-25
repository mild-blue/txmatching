#!/bin/bash

GIT_TOKEN="SET_ME"

is_running() {
    service="${1}"
    container_id="$(docker-compose ps -q ${service})"
    health_status="$(docker inspect -f "{{.State.Status}}" "${container_id}")"

    if [ "${health_status}" = "running" ]; then
        echo "${service} status is ${health_status}."
        return 0
    else
        echo "${service} status is ${health_status}."
        return 1
    fi
}

function redeploy {
  echo "Redeploying backend."

  export VERSION_TAG="${1}"

  echo "Pull mildblue/txmatching:${VERSION_TAG} image."
  docker pull "mildblue/txmatching:${VERSION_TAG}"

  echo "Stop backend service."
  docker-compose -f docker-compose.yml stop backend
  docker-compose rm -f backend || true

  echo "Deploying new backend version ${VERSION_TAG}."
  docker-compose -f docker-compose.yml up -d backend

  echo "Checking pod status and waiting until ready."
  while ! is_running "backend"; do sleep 1; done

  echo "Backend is ready."
  docker ps
}

function run_db_migration() {
  PROD_POSTGRES_USER=$(grep POSTGRES_USER ".env" | cut -d '=' -f2)
  PROD_POSTGRES_PASSWORD=$(grep POSTGRES_PASSWORD ".env" | cut -d '=' -f2)
  sudo docker exec –it "backend" /bin/bash -c "cd /app/txmatching;PROD_POSTGRES_USER=${PROD_POSTGRES_USER} PROD_POSTGRES_PASSWORD=${PROD_POSTGRES_PASSWORD} make migrate-db-prod"
}

echo "Getting latest version info from Git repository."
PROJECT_CONFIGURATION="project-configuration"
git clone https://${GIT_TOKEN}@github.com/mild-blue/${PROJECT_CONFIGURATION}.git || true
cd "${PROJECT_CONFIGURATION}"
git fetch --all
git reset --hard origin/master
cd ..

echo "Updating files from ${PROJECT_CONFIGURATION} Git repository."
rm -rf "docker-compose.yml" ".env.enc" ".env" "version"
cp "${PROJECT_CONFIGURATION}/txmatching/docker-compose.yml" "docker-compose.yml"
cp "${PROJECT_CONFIGURATION}/txmatching/version" "version"

read -p "Set txmatching encryption secret: " PASSWORD
PASSWORD="${PASSWORD}" FILE="${PROJECT_CONFIGURATION}/txmatching/.env.enc" make -f "${PROJECT_CONFIGURATION}/Makefile" decrypt
cp "${PROJECT_CONFIGURATION}/txmatching/.env" ".env"
VERSION_TAG=$(grep VERSION_TAG "version" | cut -d '=' -f2)

while true; do
    read -p "Do you want to redeploy backend with version ${VERSION_TAG} [yn]? " yn
    case $yn in
        [Yy]* ) redeploy "${VERSION_TAG}"; break;;
        [Nn]* ) echo "Ok, exit."; break;;
        * ) echo "Please answer yes or no.";;
    esac
done

while true; do
    read -p "Do you want to run DB migrations [yn]? " yn
    case $yn in
        [Yy]* ) run_db_migration; break;;
        [Nn]* ) echo "Ok, exit."; break;;
        * ) echo "Please answer yes or no.";;
    esac
done

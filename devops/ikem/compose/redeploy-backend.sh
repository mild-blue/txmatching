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

  export BACKEND_TAG="${1}"

  echo "Pull mildblue/txmatching:${BACKEND_TAG} image."
  docker pull "mildblue/txmatching:${BACKEND_TAG}"

  echo "Stop backend service."
  docker-compose -f docker-compose.yml stop backend
  docker-compose rm -f backend || true

  echo "Deploying new backend version ${BACKEND_TAG}."
  docker-compose -f docker-compose.yml up -d backend

  echo "Checking pod status and waiting until ready."
  while ! is_running "backend"; do sleep 1; done

  echo "Backend is ready."
  docker ps
}

echo "Getting latest version info from Git repository."
git clone https://${GIT_TOKEN}@github.com/mild-blue/txmatching.git || true
cd txmatching
git fetch --all
git reset --hard origin/master
LATEST_TAG=$(git describe --tags --abbrev=0)
cd ..

echo "Updating docker-compose.yml with version from Git repository."
rm -rf docker-compose.yml
cp txmatching/devops/compose/docker-compose.yml docker-compose.yml

while true; do
    read -p "Do you want to redeploy backend with version ${LATEST_TAG} [yn]?" yn
    case $yn in
        [Yy]* ) redeploy "${LATEST_TAG}"; break;;
        [Nn]* ) echo "Ok, exit."; break;;
        * ) echo "Please answer yes or no.";;
    esac
done

#!/bin/bash

GIT_TOKEN="SET_ME"

is_running() {
    service="${1}"
    container_id="$(docker-compose ps -q ${service})"
    health_status="$(docker inspect -f "{{.State.Status}}" "${container_id}")"

    if [ ${health_status} = "running" ]; then
        echo "${service} status is ${health_status}."
        return 0
    else
        echo "${service} status is ${health_status}."
        return 1
    fi
}

function redeploy {
  echo "Redeploying backend."

  echo "Stop backend service."
  export BACKEND_TAG="${LATEST_TAG}"
  docker-compose -f docker-compose.yml stop backend
  docker-compose rm -f backend || true

  echo "Deploying new backend version ${LATEST_TAG}."
  docker-compose -f docker-compose.yml up -d backend

  echo "Checking pod status and waiting until ready."
  while ! is_running "backend"; do sleep 1; done

  echo "Backend is ready."
  docker ps
}

echo "Getting latest version info from Git repository."
git clone https://${GIT_TOKEN}@github.com/mild-blue/txmatching.git | true
cd txmatching
git fetch --all
git reset --hard origin/master
LATEST_TAG=`git describe --tags --abbrev=0`
cd ..

while true; do
    read -p "Do you want to redeploy backend with version ${LATEST_TAG} [yn]?" yn
    case $yn in
        [Yy]* ) redeploy; break;;
        [Nn]* ) echo "Ok, exit."; break;;
        * ) echo "Please answer yes or no.";;
    esac
done

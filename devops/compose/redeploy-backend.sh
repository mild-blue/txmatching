#!/bin/bash

GIT_TOKEN="SET_ME"

is_healthy() {
    service="$1"
    container_id="$(docker-compose ps -q "$service")"
    health_status="$(docker inspect -f "{{.State.Status}}" "$container_id")"

    if [ "$health_status" = "running" ]; then
        return 0
    else
        return 1
    fi
}

function redeploy {
  echo "Redeploying backend."

  echo "Stop backend service."
  docker-compose -f docker-compose.yml stop backend
  docker rm backend || true

  echo "Updating tag version to ${LATEST_TAG}."
  sed "s/TAG/${LATEST_TAG}/" docker-compose.template.yml > docker-compose.yml

  echo "Deploying new backend version ${LATEST_TAG}."
  docker-compose -f docker-compose.yml up -d backend
  docker-compose -f docker-compose.yml restart nginx

  echo "Checking pod status and waiting until ready."
  while ! is_healthy "backend"; do sleep 1; done

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

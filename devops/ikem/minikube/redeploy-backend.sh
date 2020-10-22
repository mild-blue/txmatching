#!/bin/bash

DEPLOYMENT_NAMESPACE="txmatch"
GIT_TOKEN="SET_ME"

function redeploy {
  echo "Redeploying Backend."

  echo "Deleting backend deployment."
  kubectl delete -f backend.yaml --namespace="${DEPLOYMENT_NAMESPACE}"

  echo "Updating tag version to ${LATEST_TAG}."
  sed "s/TAG/${LATEST_TAG}/" backend_template.yaml > backend.yaml

  echo "Deploying new backend version ${LATEST_TAG}."
  kubectl apply -f backend.yaml --namespace="${DEPLOYMENT_NAMESPACE}"

  echo "Checking pod status and waiting until ready."
  kubectl wait --for=condition=ready pod -l app=backend --namespace="${DEPLOYMENT_NAMESPACE}" --timeout=300s

  echo "Backend is ready."
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

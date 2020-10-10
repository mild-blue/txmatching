#!/bin/bash

echo "Getting latest version info from Git repository."
git clone https://TOKEN_FROM_BITWARDEN@github.com/mild-blue/txmatching.git | true
cd txmatching
git fetch --all
LATEST_TAG=`git describe --tags --abbrev=0`
cd ..

echo "Redeploying Backend."
DEPLOYMENT_NAMESPACE=txmatch

echo "Deleting backend deployment."
kubectl delete -f backend.yaml --namespace="${DEPLOYMENT_NAMESPACE}"

echo "Updating tag version to ${LATEST_TAG}."
sed "s/TAG/${LATEST_TAG}/" backend_template.yaml > backend.yaml

echo "Deploying new backend version ${LATEST_TAG}."
kubectl apply -f backend.yaml --namespace="${DEPLOYMENT_NAMESPACE}"

echo "Checking pod status and waiting until ready."
kubectl wait --for=condition=ready pod -l app=backend --namespace="${DEPLOYMENT_NAMESPACE}" --timeout=300s

echo "Backend is ready."

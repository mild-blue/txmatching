#!/bin/bash

echo "Redeploying Backend pod."
DEPLOYMENT_NAMESPACE=txmatch

echo "Deleting pod with label 'app=backend'."
kubectl delete pods -l app=backend --namespace="${DEPLOYMENT_NAMESPACE}"

echo "Checking pod status and waiting until ready."
kubectl wait --for=condition=ready pod -l app=backend --namespace="${DEPLOYMENT_NAMESPACE}" --timeout=300s

echo "Backend pod is ready."

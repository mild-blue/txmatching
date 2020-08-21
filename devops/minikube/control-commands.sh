######################################################################
#
# Cluster setup commands
#
# Use root for installation.
#
######################################################################


# 1. Create namespace
kubectl apply -f namespace.yaml
DEPLOYMENT_NAMESPACE=txmatch

# 2. Deploy Postgres
kubectl apply -f postgres.yaml --namespace="${DEPLOYMENT_NAMESPACE}"
# Check that pod exists
kubectl get pods -o name --namespace="${DEPLOYMENT_NAMESPACE}" | grep "postgres" | xargs kubectl get --namespace="${DEPLOYMENT_NAMESPACE}"
# Show its logs
kubectl get pods -o name --namespace="${DEPLOYMENT_NAMESPACE}" | grep "postgres" | xargs kubectl logs --namespace="${DEPLOYMENT_NAMESPACE}"


# 3. Deploy Backend
kubectl apply -f backend.yaml --namespace="${DEPLOYMENT_NAMESPACE}"
# Check that pod exists
kubectl get pods -o name --namespace="${DEPLOYMENT_NAMESPACE}" | grep "backend" | xargs kubectl get --namespace="${DEPLOYMENT_NAMESPACE}"
# Show its logs
kubectl get pods -o name --namespace="${DEPLOYMENT_NAMESPACE}" | grep "backend" | xargs kubectl logs --namespace="${DEPLOYMENT_NAMESPACE}"

######################################################################
#
# Useful commands
#
# Use root for installation.
#
# Minikube commands: https://minikube.sigs.k8s.io/docs/commands/
#
######################################################################

# Show services
kubectl get services --namespace="${DEPLOYMENT_NAMESPACE}"

# Show backend service nodePort configuration
kubectl get svc -o name --namespace="${DEPLOYMENT_NAMESPACE}" | grep "backend" | xargs kubectl get --namespace="${DEPLOYMENT_NAMESPACE}" -o yaml | grep nodePort -C 5

# Expose backend service to be accessible outside of Minikube
minikube service backend -n="${DEPLOYMENT_NAMESPACE}"


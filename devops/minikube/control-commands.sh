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

# 2. Deploy Secrets
kubectl apply -f secrets.yaml --namespace="${DEPLOYMENT_NAMESPACE}"

kubectl get secret secrets --namespace="${DEPLOYMENT_NAMESPACE}" -o yaml

# 3. Deploy Postgres
kubectl apply -f postgres.yaml --namespace="${DEPLOYMENT_NAMESPACE}"

# Check that pod exists
kubectl get pods -l app=postgres --namespace="${DEPLOYMENT_NAMESPACE}"

# Show its logs
kubectl logs -l app=postgres --namespace="${DEPLOYMENT_NAMESPACE}"

# 4. Deploy Backend
kubectl apply -f backend.yaml --namespace="${DEPLOYMENT_NAMESPACE}"

# Check that pod exists
kubectl get pods -l app=backend --namespace="${DEPLOYMENT_NAMESPACE}"

# Show its logs
kubectl logs -l app=backend --namespace="${DEPLOYMENT_NAMESPACE}"

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
kubectl get svc -l app=backend --namespace="${DEPLOYMENT_NAMESPACE}" -o yaml | grep nodePort -C 5

# Expose backend service to be accessible outside of Minikube
minikube service backend -n="${DEPLOYMENT_NAMESPACE}"

# Get postgres service IP address and port
minikube service postgres -n="${DEPLOYMENT_NAMESPACE}"

# Connect to DB
psql -h IP_ADDRESS -p PORT -U USER datavid

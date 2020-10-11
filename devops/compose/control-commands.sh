######################################################################
#
# Cluster setup commands
#
# Use root for installation.
#
######################################################################


# 1. Deploy
docker-compose -f docker-compose.yml up -d

# 2. Destroy
docker-compose -f docker-compose.yml down

# 2. Stop service
docker-compose -f docker-compose.yml stop SERVICE_NAME

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



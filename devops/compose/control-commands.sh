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

# 3. Stop service
docker-compose -f docker-compose.yml stop SERVICE_NAME

# 4. Forward DB to locahost port 1234
ssh -L 1234:localhost:5432 txmatch-USERNAME@172.17.3.14

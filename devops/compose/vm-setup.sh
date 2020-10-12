######################################################################
#
# Set of scrips for setup Centos 8 VM
#
# Use root for installation.
#
######################################################################

# 1. Update package repository list
yum -y update

# 2. Install docker https://docs.docker.com/engine/install/centos/
yum install -y yum-utils

# Add repository into yum
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install containerd manually cause version required by docker is not available via yum
yum install -y https://download.docker.com/linux/centos/7/x86_64/stable/Packages/containerd.io-1.2.6-3.3.el7.x86_64.rpm

# Install the latest version of Docker Engine
yum install -y docker-ce docker-ce-cli

# Start Docker service
systemctl start docker


# 2. Install docker compose

curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose --version

# 3 Install Postgres client

yum install -y postgresql

# 4. Install Git

yum install -y git

# 5. Setup firewall properly

firewall-cmd --zone=public --add-masquerade --permanent
firewall-cmd --reload
systemctl restart docker

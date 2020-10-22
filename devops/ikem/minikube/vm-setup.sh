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


# 2. Install minikube https://phoenixnap.com/kb/install-minikube-on-centos

# Install KVM Hypervisor
yum install -y epel-release
yum install -y libvirt qemu-kvm virt-install virt-top libguestfs-tools
systemctl start libvirtd
systemctl enable libvirtd
systemctl status libvirtd
usermod -a -G libvirt $(whoami) # Add other users too!

# Make sure that that the following lines in /etc/libvirt/libvirtd.conf are set with the prescribed values and uncomment them:
nano /etc/libvirt/libvirtd.conf
# unix_sock_group = "libvirt"
# unix_sock_rw_perms = "0770"

systemctl restart libvirtd.service
systemctl status libvirtd

# 3. Installing Minikube

wget https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube-linux-amd64
mv minikube-linux-amd64 /usr/local/bin/minikube
minikube version

# KVM drivers
curl -LO https://storage.googleapis.com/minikube/releases/latest/docker-machine-driver-kvm2
chmod +x docker-machine-driver-kvm2
mv docker-machine-driver-kvm2 /usr/local/bin/
docker-machine-driver-kvm2 version


# 4. Installing Kubectl

curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
chmod +x kubectl
mv kubectl  /usr/local/bin/
kubectl version --client -o json
yum install -y conntrack

# 5. Run it

# 5.1 With KVM
minikube config set vm-driver kvm2

# 5.2 With none driver
minikube config set vm-driver none

# Starting Minikube
minikube start
# with KVM: minikube start --driver=kvm2
# with None: minikube start --driver=none # WE ARE USING THIS OPTION CAUSE MACHINE DOES NOT SUPPORT PROPER VIRTUALIZATION.


# 6. Managing Minikube
# https://phoenixnap.com/kb/install-minikube-on-ubuntu#htoc-managing-kubernetes-with-minikube

# View Minikube config
kubectl config view

# Show cluster info
kubectl cluster-info

# Get nodes
kubectl get nodes

# Get Minikube status
minikube status

# Minikube dashboard
minikube dashboard --url

# Install Postgres client
yum install -y postgresql

# Install Git
yum install -y git

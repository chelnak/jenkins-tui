#!/bin/sh

if [ ! -f "/etc/ssh/ssh_host_rsa_key" ]; then
	# generate fresh rsa key
	ssh-keygen -f /etc/ssh/ssh_host_rsa_key -N '' -t rsa
fi
if [ ! -f "/etc/ssh/ssh_host_dsa_key" ]; then
	# generate fresh dsa key
	ssh-keygen -f /etc/ssh/ssh_host_dsa_key -N '' -t dsa
fi

# prepare run dir
if [ ! -d "/var/run/sshd" ]; then
  mkdir -p /var/run/sshd
fi

TARGET_GID=$(stat -c "%g" /var/data)
addgroup -g $TARGET_GID tempgroup
addgroup agent tempgroup
chmod 770 /var/data
chmod g+s  /var/data
chown agent:jenkins /var/data

echo Added user agent to group GID $TARGET_GID

# Execute the CMD from the Dockerfile:
exec "$@"

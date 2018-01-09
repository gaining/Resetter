#!/bin/bash
# add default user

PASSWORD='Kaliko123'
USERNAME='gainingG'

if id -u $USERNAME >/dev/null 2>&1; then
	echo "$USERNAME already exists not adding"

else
	useradd -m -p $PASSWORD -s /bin/bash $USERNAME
	usermod -a -G sudo $USERNAME
	echo $USERNAME:$PASSWORD | chpasswd
fi

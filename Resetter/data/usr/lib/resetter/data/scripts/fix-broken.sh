#!/bin/bash
#fix broken packages after package removals by resetter
rm -f /var/cache/apt/archives/lock
rm -f /var/lib/dpkg/lock
dpkg --configure -a
apt install -fy
apt autoremove -y
apt clean

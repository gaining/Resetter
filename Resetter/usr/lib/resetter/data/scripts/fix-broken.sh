#!/bin/bash
#fix broken packages after package removals by resetter
dpkg --configure -a
apt install -fy
#apt-get is used instead of apt because trusty doesn't support the new apt
apt-get autoremove -y
apt-get clean

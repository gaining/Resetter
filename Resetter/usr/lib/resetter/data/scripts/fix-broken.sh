#!/bin/bash
#fix broken packages after package removals by resetter
dpkg --configure -a
apt install -fy
#apt autoremove -y need to use apt-get because earlier version of ubuntu 14.04 don't support apt
apt-get autoremove -y

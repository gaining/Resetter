#!/bin/bash
#fix broken packages after package removals by resetter

apt install -fy
dpkg --configure -a
apt autoremove -y

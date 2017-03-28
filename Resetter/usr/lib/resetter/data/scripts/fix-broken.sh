#!/bin/bash
#fix broken packages after app removals by resetter

apt install -fy
dpkg --configure -a
apt autoremove -y

#!/bin/bash
#find old kernels

kernels=("linux-image" "linux-headers" "linux-image-extra")
for item in "${kernels[@]}"; 
    do dpkg-query -W -f'${Package} ${Status}\n' "$item-[0-9]*.[0-9]*.[0-9]*" | 
    sort -V |
    awk '$NF == "installed"{print $1}'|
    awk 'index($0,k){exit} //' k=$(uname -r | cut -d- -f1,2); 
done


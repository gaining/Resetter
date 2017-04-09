# Resetter beta-0.0.6 
![alt tag](https://github.com/gaining/Resetter/blob/master/Resetter/resetter-screenshot.png)

It is an application built with python and pyqt that will help to reset an Ubuntu or Linux-Mint system to stock, as if it's been just installed without having to manually re-install by using a live cd/dvd image. It will detect packages that have been installed after the initial system install. 

# Status
- The software is currently in beta stage. Feedback will be greatly appreciated.
- If you're on a version lower than beta-0.0.6, please remove resetter with "sudo apt remove resetter" to install the new one. 
- beta-0.0.6 is a milestone release that has performance improvements, new features, and critical bug fixes hence it's a lot more stable than previous versions.
- Please check the changelog for more details.


# How to install
Install via deb file. PPA will be created soon.

# Options comparison

MPIA means missing pre-installed apps

<center>

| Features List                          | Option 1: Automatic Reset | Option 2: Custom Reset |
|----------------------------------------|:-------------------------:|:----------------------:|
| Auto remove apps for reset             |             ✓             |            ✓           |
| Choose which apps to remove for reset  |             ✗             |            ✓           |
| Remove old kernels                     |             ✗             |            ✓           |
| Choose to only delete user             |             ✗             |            ✓           |
| Delete both users and home directories |             ✓             |            ✓           |
| Choose which user to delete            |             ✗             |            ✓           |
| Create default backup user             |             ✓             |            ✓           |
| Create custom backup user              |             ✗             |            ✓           |
| Auto install MPIAs                     |             ✓             |            ✓           |
| Choose which MPIAs to install          |             ✗             |            ✓           |


</center>

# Officially supported distros [64-bit]
- Linux Mint 18.1
- Linux Mint 18
- Linux Mint 17.3
- Ubuntu 17.04 ~coming soon
- Ubuntu 16.10 
- Ubuntu 16.04
- Ubuntu 14.04

# Upcoming changes in the near future
- command line options
- different install options
- pick from backup list to install or remove
- option to install missing pre-installed packages

# distant future plans
- translations
- migrate to python3 and pyqt5
- more reset options
- support more debian based distro 
- stabilize resetter



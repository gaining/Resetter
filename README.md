# Resetter
![alt tag](https://github.com/gaining/Resetter/blob/master/Resetter/resetter-screenshot.png)

It is an application built with python and pyqt that will help to reset an Ubuntu or Linux-Mint system to stock, as if it's been just installed without having to manually re-install by using a live cd/dvd image. It will detect packages that have been installed after the initial system install. 

# Status
- The software is currently in beta stage. Feedback will be greatly appreciated.
- If you're on a version lower than beta-0.0.6, please remove resetter with `sudo apt remove resetter` before installing a newer version. 
- current version is beta 0.1.2
- Please check the changelog for more details.
- if you find a bug, please create an issue or email me about it. Everyone benefits once a bug is fixed.


# How to install
Install via deb file found ![here](https://github.com/gaining/Resetter/releases/tag/0.1.2-beta). PPA will be created soon.
It is easier to install any deb files via gdebi, especially on elementary os with no graphical way of installing a deb file. 
On the terminal, run `sudo apt install gdebi`.


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
- Ubuntu 17.04
- Ubuntu 16.10 
- Ubuntu 16.04
- Ubuntu 14.04
- Elementary OS 0.4 
- Debian jessie ~ coming soon via resetter-cli

# Upcoming changes in the near future
- command line options - in the works
- different install options
- pick from backup list to install or remove
- option to install missing pre-installed packages

# distant future plans
- translations - 
- migrate to python3 and pyqt5
- more reset options
- support more debian based distro 
- stabilize resetter

# Donate

If you like this project and are willing to make a monetary donation, here's my paypal link. Thanks in advance.

[![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=8FET8RGU2ZKQ8)




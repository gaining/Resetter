# Resetter 0.2.5-rc2
![alt tag](https://github.com/gaining/Resetter/blob/master/Resetter/resetter-screenshot.png)

It is an application built with python and pyqt that will help to reset an Ubuntu or Linux-Mint system to stock, as if it's been just installed without having to manually re-install by using a live cd/dvd image. It will detect packages that have been installed after the initial system install. 

# Status
- Release candidate 0.2.5 contains new looks, tons of new useful features, and more. 
- Feedback will be greatly appreciated.
- current version is 0.2.5-rc2
- Please check the changelog for more details.
- If you find a bug, please create an issue on github. 
- If you do not have a github account please send your bug report at gaining7@outlook.com.


# How to install
Install via deb file found ![here](https://github.com/gaining/Resetter/releases/tag/v0.2.5-rc2). PPA will be created soon.
It is easier to install any deb files via gdebi, especially on elementary os with no graphical way of installing a deb file. 
On the terminal, run `sudo apt install gdebi`.
- Linux deepin isn't based on ubuntu but on debian so some modules aren't available in their repos by default.
1. Fetch the python-evdev module.

..*`wget -c http://mirrors.kernel.org/ubuntu/pool/universe/p/python-evdev/python-evdev_0.4.1-0ubuntu3_amd64.deb`
2.Then install it with: 

..*`sudo gdebi python-evdev_0.4.1-0ubuntu3_amd64.deb` 

3. Fetch the add-apt-key package

..* `wget -c http://mirrors.kernel.org/ubuntu/pool/universe/a/add-apt-key/add-apt-key_1.0-0.5_all.deb`
4. Install it with:

..* `sudo gdebi add-apt-key_1.0-0.5_all.deb`

Then you can begin installing resetter

# Options comparison

MPIA means missing pre-installed apps

<center>

| Features List                          | Option 1: Automatic Reset | Option 2: Custom Reset |
|----------------------------------------|:-------------------------:|:----------------------:|
| Auto remove apps for reset             |             ✓             |            ✓           |
| Choose which apps to remove for reset  |             ✗             |            ✓           |
| Remove old kernels                     |             ✗             |            ✓           |
| Choose to only delete user             |             ✗             |            ✓           |
| Delete users and home directories      |             ✓             |            ✓           |
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
- Debian jessie ~ delayed but will come via resetter-cli
- Linux Deepin 15.4 

# Upcoming changes in the near future
- command line options - delayed but in the works
- different install options - implemented
- pick from backup list to install or remove - implemented
- option to install missing pre-installed packages - implemented

# Distant future plans
- translations - 
- migrate to python3 and pyqt5 
- more reset options
- support more debian based distro - progressing well
- stabilize resetter - very stable so far

# Contact
- If you wish to contact me about anything else reach me via gaining7@outlook.com.

# Donate

If you like this project and are willing to make a monetary donation, here's my paypal link. Thanks in advance.

[![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=8FET8RGU2ZKQ8)




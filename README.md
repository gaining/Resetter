# Resetter v2.2.3-stable (Deprecated)
![alt tag](https://github.com/gaining/Resetter/blob/master/Resetter/resetter-screenshot.png)

<h4> Hi all, this version of resetter is deprecated because it is behind the OSs manifests and new technologies. Please wait for Resetter 3.0 which I will be releasing in or before January 1st 2019 coming with new features and fixes or use this version at your own risk. Thank you, happy holidays and God bless! </h4>

It is an application built with python and pyqt that will help to reset an Ubuntu, Linux-Mint, and some other distros to stock, without having to manually re-install by using a live usb/cd/dvd image. For the list of supported distros, please see the *Officially supported distros* section.

If you would like for Resetter to work on your debian/ubuntu based distro, watch the videos explaining how to do it. Users have followed these videos to make resetter work on Ubuntu Budgie and Linux Mint 18.3 It is very easy to do, all it requires is a little time and patience.

# How to install
Download the deb files found [here](https://github.com/gaining/Resetter/releases/latest) then on the terminal, run the following commands:

1. `sudo apt install gdebi`
2. `sudo gdebi add-apt-key_1.0-0.5_all.deb`
3. `sudo gdebi resetter_2.2.3-stable_all.deb`


# New video tutorial on how to make any debian based distro compatible with Resetter with [resetter-helper](https://github.com/gaining/ResetterHelper)

[![](http://img.youtube.com/vi/5VfSvEryOWU/0.jpg)](http://www.youtube.com/watch?v=5VfSvEryOWU "compatible")


# How to share your distro's manifest and userlist by creating a github pull request

[![Tutorial link](http://img.youtube.com/vi/k0wsPzO355o/0.jpg)](http://www.youtube.com/watch?v=k0wsPzO355o "share")


# How to make Resetter fetch the latest manifests and userlists available.

[![Tutorial link](http://img.youtube.com/vi/k0wsPzO355o/0.jpg)](https://youtu.be/k0wsPzO355o?t=236 "update")


# Official video tutorial - courtesy of *Byte of Linux*

[![Tutorial link](http://i3.ytimg.com/vi/PSmzWdGrs1M/maxresdefault.jpg)](https://youtu.be/PSmzWdGrs1M "Resetter Tutorial")


# Status

- Thanks to those who sent me their manifest and userlist files by email and also for properly following the instructional videos. Now, due to your contributions, everyone will be able to use Resetter on *Ubuntu Bugie 18.04* and *Linux Mint Mate 18.3* Others are welcome to do the same to have their favourite distros supported.

- Version 2.2.3 supports virtually all debian based distros, a video demonstrating how to easily support your favourite debian based distro is already uploaded. Version 2.2.3 is the last version of resetter based on python 2.7 and PyQt4.

- The next version will be resetter 3.0.0 and will be based in python 3. I don't know when I will release it. It may be a while since I'll probably have to rewrite a lot of the current code.

- Working Project: Resetter-cli, a version of resetter that runs terminally.
- Please check the [changelog](https://github.com/gaining/Resetter/blob/master/changelog) for more details.

# Bug reports
- If you find a bug or problem please create an issue on github.
- If you do not have a github account do not hesitate to contact me and send your bug report to gaining7@outlook.com.

# Options comparison

MPA means missing pre-installed apps

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
| Auto install MPAs                      |             ✓             |            ✓           |
| Choose which MPAs to install           |             ✗             |            ✓           |
| Remove non-default users               |             ✓             |            ✓           |
| Dependent package view                 |             ✗             |            ✓           |
| Remove snap packages                   |             ✓             |            ✓           |

</center>

# Other features:
- Manifest and userlist updater: By clicking on *"help"*>*"update files"*
- Easy install: Basically, you will be able to build your own list of apps that you'd like to mass install after a reset or fresh install. It can also be used anytime to install a package. If you saved a backup file using the save feature prior to your reset or fresh install, you will be able to restore the apps from that list if they're available to install.

- Easy PPA: With this feature, you can search launchpad.net for PPAs containing apps directly from resetter and install it into your system. It will also grab the ppa's key automatically. This eliminates the need of using a terminal to add ppas from launchpad making distros more user friendly.

- Source Editor: It is a normal editor that can disable, enable, or remove ppas from a user's system but what makes this different from other source editors is that you can search for the ppa that you want to edit.

# Officially supported distros [64-bit]

- Debian 9.2 (stable) Gnome edition
- Linux Mint 17.3+ {Cinnamon and Mate}
- Ubuntu 14.04+, {Unity, Gnome, and Budgie(18.04)}
- Elementary OS 0.4+
- Linux Deepin 15.4+


# Non stingy people donation link ;)

[![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=8FET8RGU2ZKQ8)

# Contact
- If you wish to contact me about anything else reach me via gaining7@outlook.com.

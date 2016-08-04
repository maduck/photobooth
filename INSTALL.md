## Raspberry Pi preparation
1. Download and install Raspbian Jessie lite.
1. Plug in your Raspberry Pi, provide a screen, network and a keyboard, and let it boot.
1. Prepare the system environment:
  * Log in with user & password: pi / raspberry. Become super user: `sudo -i`
  * Update the installed packages (including raspy-config) by typing `apt-get update && apt-get upgrade`
  * Edit file `/boot/config.txt`, and add the following lines:

        `framebuffer_depth=32`  
        `framebuffer_ignore_alpha=1`

  * Install some more needed packages by typing
      
      `apt-get install python-picamera python-pygame python-pip python-imaging xorg cups cups-bsd git`
      
  * Optional: install more standard tools:

     `apt-get install htop iotop vnstat vim-nox`
  * Change hostname to photobooth
     
     `echo photobooth > /etc/hostname`
  * Add a new local user, make up a safe password.
  
     `adduser photobooth`
  * Grant camera access for the newly created user
    
     `usermod -a -G video photobooth`
  * Install the printer (I can't tell you how right now, because this is a mess)
  * Start `raspi-config`
     * Choose Expand Filesystem
     * then select Enable camera and hit Enter
     * Go to Finish and choose to reboot.

## user autologin and app autostart
    
1. Install application and dependencies from github repository
  * log in as photobooth
  * Check out software into local folder:
    `git clone https://github.com/maduck/photobooth.git`
1. Set up automatic login and program start
  * create file `/etc/systemd/system/getty@tty1.service.d/autologin.conf`, with the following content:

         `[Service]`  
         `ExecStart=`  
         `ExecStart=-/sbin/agetty --autologin "photobooth" %I`

1. Let the graphical user interface / X server automatically start on login:

     `echo startx >/home/photobooth/.bash_profile`

1. Change the file owner to our photobooth user:

     `chown photobooth.photobooth /home/photobooth/.bash_profile`
 
1. Create a script for executing the photobooth app, named /home/photobooth/start_app.sh, with the following content:

      `sleep 5`  
      `# disable screensaver`  
      `xset s off`  
      `# disable energy saving`  
      `xset -dpms`  
      `# start photobooth app`  
      `python photobooth/booth_app.py`

1. Change the ownership of this script, and make it executable:

     `chown photobooth.photobooth /home/photobooth/start_app.sh`  
     `chmod u+x /home/photobooth/start_app`

1. Let the xorg server automatically start the app script:
	
	`echo ~/start_app.sh >/home/photobooth/.xinitrc`
	
1. update your `/home/photobooth/photobooth/settings.cfg`, if needed.


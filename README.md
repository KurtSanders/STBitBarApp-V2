# STBitBarApp-V2 (For Apple![macOS logo](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/macos_logo.jpg))
### Version: 4.0.0 (Beta Testing)

<img src="https://raw.githubusercontent.com/KurtSanders/STAmbientWeather/master/images/readme.png" width="50">[Change-log & Version Release Features](https://github.com/KurtSanders/STBitBarApp-V2/wiki/Features-by-Version)

![STBitBarApp-V2 logo](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/STBitBarApp-V2-Macbook-Pro.png)

![STBitBarApp-V2 logo](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/STBitBarApp-V2-Menu.png)

### New Beta Features:

1. Allow one ST device of either a lock, contact, switch, or temperature sensor to be designated in the BitBar Top Menu.  Red & green emoji's will be shown in the top Mac menu bar  for the selected device status with a contact (Open/Close) or switch (On/Off).  An integer value with degree symbol will be displayed when a temperature sensor is designated.
 
	Example Lock emoji in Top Menu Bar when a 'Lock' is designated
	
	<img src=https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/Lock%20Menu%20Bar.jpg width="400"/>

2. Provide a MacOS right sidebar notification when:
	* Confirming a device change from the BitBar Menu Bar 
	* Showing the timed device status refresh

		<img src=https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/Notification.jpg width="300"/>

3. Allow user to turn On|Off MacOS sidebar notifications from BitBar Output App

4. Provide an user defined automatic device refresh after a ST device change from BitBar Output (default 5 sec after device change which allows time for the device to report status to ST Cloud API)
5. Allow the secret API strings to be SMS delivered (unencrypted) to a USA mobile phone number from the API Setup Page. 
6. Added the following information in the mobile ST BitBar Output SmartApp main menu for:
	* ST BitBar Output SmartApp Version
	* ST_Python_Logic.py Version
	* ST.xm.sh Version (where 'x' is an integer number (default is now 1) reflecting the number of minutes for normal pooling of devices defined to BitBar Output App.  Please do not change this to less than 1m which pools to frequently and will impact Mac performance.  If you would like a slower polling rate, I recommend '3m' or '5m' for 'x' in ST.xm.sh file
	* BitBar Plugin Folder Location
7. New Install/Upgrade command script for ease of setting up or maintaining the BitBar Plugin Folder
8. Added a 'Download ST BitBar Installation/Upgrade script to your 'Downloads' directory' to the 'STBitBarApp Actions and Shortcuts' choice on the BitBar Menu (located at the bottom of the screen).  This choice will download the command file to your Downloads folder so you can double click in Finder to execute.


## Overview:
Monitor and control [SmartThings](https://www.smartthings.com/) devices, sensors, Smart Home Monitor, Modes & Routines from the Apple MacOS Menu Bar.  This application is controlled via the SmartThings Mobile Client named **BitBar Output App**.  Selected program and configuration files are installed localled on the Apple macOS.

The STBitBarApp-V2 application works with the [MacOS BitBar application](https://getbitbar.com/) as a custom BitBar Plugin and controlled via the SmartThings SmartApp.  STBitBarApp-V2 **displays** SmartThings thermostat information, temperature, relative humidity, event-log statistics, contacts, music players, presence devices, locks, lights, and motion sensors.  It can also **control** color control device levels, switch/dimmer level devices, locks and also thermostat control via the MacOS menubar.  The menubar icon dislays a thermostat reading and upon clicking, renders the information on all the SmartThings selected in the SmartApp GUI.

One can click on any controllable SmartThings device, mode or routine in the Mac's Bitbar display to invoke the default action for that device, mode or routine.  Non-controllable devices (eg. presence sensors, motion sensors, temperarture sensors) can show their event history.

Battery levels can be dipslayed for devices that have a battery capability by depressing the Apple {option} key as the BitBar menu is activated {being displayed}.

## Prerequisities

* [Apple macOS with Python 2.7](https://en.wikipedia.org/wiki/MacOS)
* [BitBar Software \*Freeware\* ](https://getbitbar.com/)
* [SmartThings Hub & Devices](https://shop.smartthings.com/)
* [Knowledge of installing software on macOS and SmartThings IDE](https://www.google.com/search?q=how+to+install+software+on+mac&rlz=1C5CHFA_enUS503US503&oq=how+to+install+softwate&aqs=chrome.2.69i57j0l5.9308j0j4&sourceid=chrome&ie=UTF-8)
* Member of [SmartThings Community](https://community.smartthings.com/) for support and new releases


## Section 1: Installation:

#### Create/Upgrade STBitBar Plugin Folder: <img src=https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/new-logo.png />


1. Download and Install [BitBar Core Software \*Freeware\* ](https://github.com/matryer/bitbar/releases/download/v1.9.2/BitBar-v1.9.2.zip)
	1. Download [BitBar-v1.9.2.zip](https://github.com/matryer/bitbar/releases/download/v1.9.2/BitBar-v1.9.2.zip) to your Downloads folder and double click the zip file to unzip the file contents.  
	2. Move the BitBar.app to your Mac's Applications folder
	3. Launch BitBar.app in your Mac's application folder
	4. Locate the BitBar icon in the Mac's Top Menu Bar.  Click the Icon.
	5. Scroll list to set BitBar preferences to 'Open at Login' and 'Change Plugin Folder'
2. Launch the **Terminal.app** from the Mac Applications **'Utility'** SubFolder
3. Enter **CD $HOME/Downloads** and press <kbd>Return</kbd> 
 * Changes the current default file folder to your 'Downloads' folder
4. Select, copy and paste the following entire string into the Mac's Terminal Console Window.  Press <kbd>Return</kbd>.  

	curl -s -O -J -L "https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/installation/STBitBarInstall.command" && sh ./STBitBarInstall.command

5. Your ST BitBar Plugin's directory has been created or upgraded to the latest release.

---

### Select from one of the two sections below (Either 1a or 1b).

The recommended approach for SmartThings installation is using the integration of your SmartThings IDE and GitHub so that updates to the BitBar Output SmartApp are visual and easier.

A new Install or Version Updates to the shell scripts and Python source code located on your MacOS is either by STBitBarInstall.command script or a manual method by downloading the source code from the Github repository. This manual will not go into detail about setting up your SmartThings IDE with GitHub as that is documented in the [SmartThings GitHub Documentation](http://docs.smartthings.com/en/latest/tools-and-ide/github-integration.html?highlight=github).


### Section 1a: Making the STBitBar SmartApp available via the ST IDE using GitHub Integration
1. Setup the SmartApp: Find your SmartThings IDE Link
	* [US Users](https://graph.api.smartthings.com/)
	* [UK Users](https://graph-eu01-euwest1.api.smartthings.com/)
2. Find the **My SmartApps** link on the top of the page.
3. Find the **Settings** button at the upper-right corner of your SmartThings IDE page (this will only appear after you have configured with GitHub).
4. Clicking this button will open the GitHub Repository Integration page. To find the **StBitBarApp** SmartApp code, enter the information below: 

	| Name | Value |
	|------|-------|
	|Owner | kurtsanders |
	|Name: | STBitBarApp-V2|
	|Branch| **master**|

5. Close the GitHub Repository Integration page by clicking the **Save** button.
6. Click the **Update from Repo** button at the upper-right corner of your SmartThings IDE and select STBitBarApp-V2 (master) from the list.
7. In the right-hand column you will see smartapps/kurtsanders/stbitbar.src/stbitbar.groovy, select this using the checkbox.
8. At the bottom-right corner of the Update from Repo page, select **Publish** using the checkbox and then click **Execute Update**.
9. When done syncing, the new SmartApp should now appear in your IDE.
10. If they ever change color, that indicates a new version is available.
11. **Enable OAuth:** Back at the My SmartApps page, click the little edit icon for the BitBar Output App, then click **OAuth section**, then click **Enable OAuth in SmartApp**.
12. Skip to Section 2 below

### Section 1b: (Manual Method) Making the SmartApp available via the IDE 

1. Setup the SmartApp: Find your SmartThings IDE Link
	* [US Users](https://graph.api.smartthings.com/)
	* [UK Users](https://graph-eu01-euwest1.api.smartthings.com/)
2. Click My SmartApps > then New SmartApp (top-right green button)
3. Click the From Code tab and paste the [SmartApp code from GitHub](https://raw.githubusercontent.com/kurtsanders/STBitBarApp-V2/master/SmartThings%20SmartApp/STBitBar.groovy) then click Create. 
4. Enable OAuth: Back at the My SmartApps page, click the little edit icon for the BitBar Output App, then click OAuth section, then click Enable OAuth in SmartApp.


## Section 2: Installing the BitBar Output SmartApp

1. Now for actually installing the SmartApp: On your mobile device in the SmartThings app > tap Automation > SmartApps > + Add a SmartApp (at the bottom). Go down to My Apps > select BitBar Output App.
2. Open the IDE in a separate browser tab.
	* [Live Logging IDE (USA)](https://graph.api.smartthings.com/ide/logs)
	* [Live Logging IDE (Outside USA)](https://graph-eu01-euwest1.api.smartthings.com/ide/logs)  
3. In the mobile client, tap to **Enable the API** then tap Done. You should have a **URL and secret** displayed in the Live Logging screen tab.
4. Copy/Save these two lines to input in the **ST_Python_Logic.cfg** in the step ahead.
5. Select Devices: choose the devices you want to display/control then tap Done.
6. Select Options: select the display options for the MacOS menu.  Please note that some option values are required.

## Section 3: Setting up BitBar and ST Plugin

> *In Version V4, these manual steps below are now automated in [Section 1 Installation](https://github.com/KurtSanders/STBitBarApp-V2#section-1-installation).  If you prefer the manual install method, follow the steps below.*

### Example Directory Structure of the BitBar Plugin Folder

<img src=https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/BitBarFolder.jpg width="600"/>

1. Required: You **must download** and install the core [BitBar app](https://github.com/matryer/bitbar/releases/tag/v1.9.2) on your Mac.  *This program is required to allow ST BitBar SmartApp to access the top menubar on the Mac.*
2. After downloading and installing the BitBar App & moving the BitBar App file to your applications folder, launch the BitBar App so that you can set the path for your Plugin directory.

	*IMPORTANT: When selecting a plugin directory where the plugins will reside, make sure you create one that does not contain spaces. There were issues in an older release of BitBar if the path contained spaces, but supposedly it’s fixed, but I still had issues in some cases. If there were no spaces, it always worked.*
3. In the BitBar application menu, the last option is labeled 'Preferences', make sure you select 'Open at Login' and specify the Plugin directory where you will place the plugin files from this Github in the next step.   	
4. Download the [ST plugin from GitHub](https://github.com/kurtsanders/STBitBarApp-V2/tree/master/BitBar%20Plugin). Copy **ONLY** the ST.5m.sh file to the plugin directory you specified along with the ST subfolder containing the Python script and the ST_Python_Logic.cfg (make sure these two files stay in the folder named ST).  *These files should be the only files in the plugins directory and the ST subfolder.*
5. Launch the SmartThings BitBar Output App on your mobile device. Select API Setup and Activate.  Follow the screen instructions and record the SmartThings URL and secret strings.  One can view the ST IDE Live Logging screen to copy the strings when launching and exiting the BitBar Output App on your mobile screen. 
	* Note: You can also choose to have your API strings send unencrypted to a mobile device with a USA phone number.  This will allow one to copy and paste these into your ST_Python_Logic.py file from the Mac messaging app.
5. Add your URL and secret to the ST_Python_Logic.cfg file ***without any quotes***: Open the ST_Python_Logic.cfg with a text editor of your choice (eg. textedit). Put the URL that was displayed in step 5 in the smartAppURL variable and Secret in the secret variable without any quotes. 
6. **Save** the **ST_Python_Logic.cfg** file in the ST subfolder.
7. Ensure **execution rights** for the plugins:
	* Launch the MacOS Terminal Application
	* Navigate to your BitBar Plugins directory (eg. cd)
	* Issue the admin commands on the following files: 
		* **chmod +x ST.1m.sh**
		* **chmod +x ST_Python_Logic.py**
	* Exit the MacOS Terminal
8. **Start** the BitBar app and you should see your SmartThings devices and status’ in the MacOS menubar!

### Color Light Control Features:
* Dimmer and Color Controls in BitBar Sub-Menus

![](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/new-logo.png)
![STBitBarApp-V2 logo](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/Color-Control.jpg)


## Issues / Limitations

1. The BitBar App is capable of cycling through multiple status bar items.  However, this ST BitBar Plugin is designed to only display **one temperature sensor** at the top with the rest of the sensors displayed in the dropdown. 
2. The ST BitBar app only allows a selection of one temp sensor and an optional custom title.   You do not want to use the full sensor name since menubar real estate is top dollar.  The title can be left blank and the termpeature will only show in the menubar.
3. There is no hotizontal alignment supported by BitBar so it’s all done by character spacing, which means using Apple system monospace fonts for data content. Menlo is the default font, but feel free to change it in the ST BitBar App in the mobile client Display Options.
4. Selection of a proportional spaced font, pitch and color can be used for all other text areas of the display, like the ST Categories and the ...more... sections.  Be aware that some fonts, colors and sizes may cause the menu to become illegible.  Blank field defaults in the options fields will return the display to nornal.
5. Most areas of the menu will accomodate extended ascii character sets, but there might be areas that not.  If so, please rename these devices with US ascii characters and send a PM to me on the SmartThings Community Forum.
6. ![](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/new-logo.png)Be mindful of the # of devices selected, event history days/number settings as the SmartThings Computing Cloud has implemented strict SmartApp [rate runtime limits](https://smartthings.developer.samsung.com/develop/guides/smartapps/rate-limits.html?highlight=rate) that will prevent the BitBar Output App SmartApp from execution.  When a client application exceeds the rate limits for a given SmartThings API, the SmartThings API responds with the standard HTTP 429 (Too Many Requests) error code.

## Misc Features / Tips
* Hold the **Option** key while the BitBar menu is open to display battery information for devices that can report battery level status.
* The max items per sensor category can be set in BitBar Output SmartApp Menu Options (if you want to save space but still have access to the sensors)
* Use **Command-R** while viewing the STBitBarApp-V2 menu to **Refresh** the devices, otherwise it will automatically refresh every 5 minutes.
* You can download the latest version of the Python code at the bottom of the STBitBarApp  Menu under **STBitBarApp Action & Shortcuts**
* **Emoji short-names** are special graphical icons that can be displayed for custom device status.  Please note that these short naming convention is ':xxxxx:' and the name must be entered exactly as they are named on the [Emoji Website Valid Names List](http://www.webpagefx.com/tools/emoji-cheat-sheet/)
* Many other display options are provided and activated in the STBitBarApp SmartApp and are either optional or required.

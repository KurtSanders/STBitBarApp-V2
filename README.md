# STBitBarApp-V2 (For Apple![macOS logo](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/macos_logo.jpg))
### Current Versions: 
* 5.0x (Alpha) 
* 4.01 (Stable) ([zip file](https://github.com/KurtSanders/STBitBarApp-V2/releases/tag/4.0.1))

	[Change-log & Version Release Features](https://github.com/KurtSanders/STBitBarApp-V2/wiki/Features-by-Version) <img src="https://raw.githubusercontent.com/KurtSanders/STAmbientWeather/master/images/readme.png" width="50">

![STBitBarApp-V2 logo](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/STBitBarApp-V2-Macbook-Pro.png)

![STBitBarApp-V2 logo](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/STBitBarApp-V2-Menu.png)

### New V5.0.x Features:

1. Integration of Hubitat™ and SmartThings into a reduced code stream multi-platform release.  Both Hubitat™ and SmartThings™ BitBar apps can run together or independently depending on if you have one or both hubs.
2. Integration of [hubitat-packagemanager](https://github.com/dcmeglio/hubitat-packagemanager#hubitat-packagemanager) for the App Code install on the the Hubitat™ platform.  The remaining manual install of the macOS files and scripts are still required and documented below in the [Hubitat Section Installation](https://github.com/KurtSanders/STBitBarApp-V2#hubitat-installation).

## Overview:
Monitor and control [SmartThings](https://www.smartthings.com/) and [Hubitat™](https://hubitat.com/) devices, sensors, Smart Home Monitor, Modes & Routines from the Apple MacOS Menu Bar.  This application is controlled via the SmartThings Mobile Client named **BitBar Output App**.  Selected program scripts and configuration files are installed locally on the Apple Mac in the BitBar plugin folder.

The STBitBarApp-V2 application works with the [macOS BitBar application](https://getbitbar.com/) as a custom BitBar Plugin and is controlled via the BitBar Output App.  STBitBarApp-V2 **displays** thermostat information, temperature, relative humidity, event-log statistics, contacts, music players, presence devices, locks, lights, and motion sensors.  It can also **control** color control (RGB) device levels, switch/dimmer level devices, locks and also thermostat control via the MacOS menubar.  The Mac menubar icon can be a thermostat reading, contact sensor, lock sensor or switch sensor and upon clicking the displayed state icon, renders more detailed information on all the SmartThings selected in the SmartApp GUI.

One can click on any controllable SmartThings or Hubitat device, mode or routine in the Mac's BitBar display to invoke the default action for that device, mode or routine.  Non-controllable devices (eg. presence sensors, motion sensors, temperature sensors) can show their event history.

Sensor battery levels can be displayed for devices that have a battery capability by depressing the Apple {option} key as the BitBar menu is activated {being displayed}.

## Prerequisites

* [Apple macOS 10.x with Python 2.7](https://en.wikipedia.org/wiki/MacOS)
* [BitBar Software Installed and Preferences set as 'Open at Login' and BitBar plugin folder designted \*Freeware\* ](https://getbitbar.com/)
* [SmartThings Hub & Devices](https://shop.smartthings.com/) or Hubitat™ Hub & devices
* [Knowledge of installing and configuring software on macOS and either Hubitat and/or SmartThings IDE](https://www.google.com/search?q=how+to+install+software+on+mac&rlz=1C5CHFA_enUS503US503&oq=how+to+install+softwate&aqs=chrome.2.69i57j0l5.9308j0j4&sourceid=chrome&ie=UTF-8)
* Member of the [SmartThings Community](https://community.smartthings.com/) or [Hubitat Community](https://community.hubitat.com/) for support and new release information.


## Section 1: Required Installation of core BitBar Application:

> * Note: Mat Ryer's BitBar core app lets one put the output from any macOS script or program right in your macOS menu bar. And it's completely free. An impressive number of other plugins have already been contributed by a wide range of developers, and [his website](https://getbitbar.com/) makes it easy to find them.  

> * This STBitBarApp-V2 plugin is uniquely specific to users of SmartThings™ and Hubitat™ and the installation and configuration are well documented below. 

#### Create/Upgrade BitBar Plugin Folder: <img src=https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/new-logo.png />

1. Download and Install [BitBar Core Software \*Freeware\* ](https://github.com/matryer/bitbar/releases/download/v1.9.2/BitBar-v1.9.2.zip)
	1. Download [BitBar-v1.9.2.zip](https://github.com/matryer/bitbar/releases/download/v1.9.2/BitBar-v1.9.2.zip) to your Downloads folder.
	2. Launch Finder and navigate to your Downloads folder
	3. Double click the BitBar-v1.9.2.zip file to unzip the file contents.  
	4. Drag/Move the BitBar.app into your Mac's Applications folder
	5. Launch BitBar.app from your Mac's Application folder
	6. Locate the BitBar icon displayed in the Mac's Top Menu Bar.  Click the BitBar icon to display preferences dialogue menu.
	7. In the Mac Menu Bar, click the BitBar Icon and set BitBar preferences to: 
		* √ Open at Login
		* Select the 'Plugin Folder' on the Mac (.ie `/Users/smith/BitBar` )
2. Launch the **Terminal.app** from the Mac Applications **'Utility'** SubFolder
3. In the terminal console window, enter the following:

 	`cd ~\Downloads`
 
4. Press <kbd>Return</kbd> 
5. Select, copy and paste the following entire string into the Mac's Terminal Console Window.  

	#### 	SmartThings:

	`curl -s -O -J -L "https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/installation/STBitBarInstall.command" && sh ./STBitBarInstall.command`

	#### 	Hubitat:
	`curl -s -O -J -L "https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/installation/HEBitBarInstall.command" && sh ./HEBitBarInstall.command`

6. Press <kbd>Return</kbd>  
7. Read install/upgrade messages from the script.
8. Your BitBar Plugin's directory has been created or upgraded to the latest BitBar-V2 release.

---

## SmartThings™ Installation

### Select from **ONE** of the sections below (Either 1a or 1b).

The recommended approach for BitBar SmartThings installation on the Mac is to use the integration of your SmartThings IDE and GitHub so that updates to the BitBar Output SmartApp are visual and easier.

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

---

### Section 2: Installing the BitBar Output SmartApp

1. Now for actually installing the SmartApp: On your mobile device in the SmartThings app > tap Automation > SmartApps > + Add a SmartApp (at the bottom). Go down to My Apps > select BitBar Output App.
2. Open the IDE in a separate browser tab.
	* [Live Logging IDE (USA)](https://graph.api.smartthings.com/ide/logs)
	* [Live Logging IDE (Outside USA)](https://graph-eu01-euwest1.api.smartthings.com/ide/logs)  
3. In the mobile client, tap to **Enable the API** then tap Done. 
4. Your secret **URL and API secret** is displayed in the Live Logging screen tab when you exit the ST BitBar SmartApp on the mobile phone.
4. :New: One can also select 'Send API to a Mobile Device' in the 'API Setup'.  This will send the two secret strings to a mobile phone as SMS message. Indicate a USA mobile phone number and select send to mobile phone.
4. Copy/Save these two lines to input in the **ST_Python_Logic.cfg** in the step ahead.  Use Textedit.app to edit the **ST_Python_Logic.cfg** on the Mac.  Input the two secret strings exactly as the template shows, using double quotes.
5. Launch the ST BitBar Output SmartApp in mobile SmartThings client and you should now see local file version information if your local Mac setup is completed correctly.  You may complete/customize your BitBar Top menu by:
	* Selecting Devices: choose the devices you want to display/control then tap Done.
	* Selecting Display Options: select the display options for the MacOS menu.  Please note that some option values are required.

## Section 3: Setting up BitBar and ST Plugin

> *In Version V4, these manual steps below are now automated in [Section 1 Installation](https://github.com/KurtSanders/STBitBarApp-V2#section-1-installation).  If you prefer the manual install method, follow the steps below.*

### Example Directory Structure of the BitBar Plugin Folder

<img src=https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/BitBarFolderST.jpg width="600"/>

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

## Hubitat™ Installation

### Section 1: Installing the BitBar Output App Code

Install the App Code to your Hubitat platform via the [hubitat-packagemanager](https://github.com/dcmeglio/hubitat-packagemanager#hubitat-packagemanager). Do NOT select to launch BitBar Output App after hubitat-packagemanager completes.  The BitBar application is listed in [hubitat-packagemanager](https://github.com/dcmeglio/hubitat-packagemanager#hubitat-packagemanager) under the categories of “Utility”, “Control”, “Convenience” and the tags of “Integrations”, “Monitoring”, “Dashboards”, “Tools & Utilities”.

After install of the BitBar Output App Code on Hubitat, you will need to follow the rest of the manual file & scripts install below where it is specific to Hubitat. After all macOS files & scripts are installed, you may then return to Hubitat™ web page and launch the BitBar Output App  You will need to authorize the Oauth and record the two API strings, add these two API strings to the HE_Python_Logic.cfg file and configure the BitBar Output App preferences for devices and display options.

### Section 2: Setting up BitBar and HE Plugin

> * Please make sure that the core BitBar application is installed and configured [per the instructions above](https://github.com/KurtSanders/STBitBarApp-V2#section-1-required-installation-of-core-bitbar-application).
>   
### Example Directory Structure of the BitBar Plugin Folder

<img src=https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/BitBarFolderHE.jpg width="600"/>
 	
1. Launch the BitBar Output App. Select API Setup and activate it.  Follow the on screen instructions and record the Hubitat URL and secret strings. 
2. Add your Hubitat URL and secret to the HE_Python_Logic.cfg file ***without any quotes***: Open the HE_Python_Logic.cfg with a text editor of your choice (eg. textedit). Put the Hubitat URL that was displayed in step 1 in the smartAppURL variable and Secret in the secret variable without any quotes. 
3. **Save** the **HE_Python_Logic.cfg** file in the ST subfolder.
4. Ensure **execution rights** for the plugins:
	* Launch the MacOS Terminal Application
	* Navigate to your BitBar Plugins directory (eg. cd)
	* Issue the admin commands on the following files: 
		* **chmod +x HE.5m.sh**
		* **chmod +x HE_Python_Logic.py**
	* Exit the MacOS Terminal

### Section 3: Configuring the BitBar Output App

1. Select the 'BitBar Output App' from the Hubitat Web Page 'Apps'.
2. Complete/customize your BitBar Top menu preferences by:
	* Selecting Devices: you must choose the devices you want to display/control then tap Done.
	* Selecting Display Options: you must select the display options for the MacOS menu.  Please note that some option values are required.
3. Exit the BitBar Output App and *refresh* the BitBar menu Bar on the macOS
3. You should see your Hubitat™ devices and status states’ in the MacOS menubar!

----

## Color Light Control Features:
* Dimmer and Color Controls in BitBar Sub-Menus

![](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/new-logo.png)
![STBitBarApp-V2 logo](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/Color-Control.jpg)


## Issues / Limitations

1. The BitBar App is capable of cycling through multiple status bar items.  However, this ST BitBar Plugin is designed to only display a ** temperature sensor, contact sensor, lock status, or switch sensor** at the top with the rest of the sensors displayed in the dropdown. 
2. The SBitBar app only allows a selection of one temp, lock, contact or switch sensor or a default 'BitBar' title.   It is not recommended to use the full sensor name since menubar real estate is top dollar.
3. There is no hortizontal alignment supported by BitBar so it’s all done by character spacing, which means using Apple system monospace fonts for data content. Menlo is the default font, but feel free to change it in the ST BitBar App in the mobile client Display Options.
4. Selection of a proportional spaced font, pitch and color can be used for all other text areas of the display, like the ST Categories and the ...more... sections.  Be aware that some fonts, colors and sizes may cause the menu to become illegible.  Blank field defaults in the options fields will return the display to normal.
5. Most areas of the menu will accomodate extended ascii character sets, but there might be areas that not.  If so, please rename these devices with US ascii characters and send a PM to me on the SmartThings Community Forum.
6. ![](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/new-logo.png)Be mindful of the # of devices selected, event history days/number settings as the SmartThings Computing Cloud has implemented strict SmartApp [rate runtime limits](https://smartthings.developer.samsung.com/develop/guides/smartapps/rate-limits.html?highlight=rate) that will prevent the BitBar Output App SmartApp from execution.  When a client application exceeds the rate limits for a given SmartThings API, the SmartThings API responds with the standard HTTP 429 (Too Many Requests) error code.

## Misc Features / Tips
* Hold the **Option** key while the BitBar menu is open to display battery information for devices that can report battery level status.
* The max items per sensor category can be set in BitBar Output SmartApp Menu Options (if you want to save space but still have access to the sensors)
* Use **Command-R** while viewing the STBitBarApp-V2 menu to **Refresh** the devices, otherwise it will automatically refresh every 5 minutes.
* You can download the latest version of the Python code at the bottom of the STBitBarApp  Menu under **STBitBarApp Action & Shortcuts**
* **Emoji short-names** are special graphical icons that can be displayed for custom device status.  Please note that these short naming convention is ':xxxxx:' and the name must be entered exactly as they are named on the [Emoji Website Valid Names List](http://www.webpagefx.com/tools/emoji-cheat-sheet/)
* Many other display options are provided and activated in the STBitBarApp SmartApp and are either optional or required.

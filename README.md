# STBitBarApp (For Apple macOS)

### SmartThings BitBar App
![STBitBarApp logo](https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/BitBarMenu.jpg)

## Overview:
Monitor and control smartThings sensors, modes & routines from the Apple MacOS Menu Bar.  This application has a GUI interface named BitBar Output App that can be accessed via the StartThings mobile client and local application code installed on the Mac.

The STBitBarApp application can display thermostat information, temperature, contact, presence, and motion sensors, as well as control switch/dimmer level devices, locks and also thermostat control via the MacOS menubar.  The menubar icon dislays a thermostat reading and upon clicking, renders the information on all the SmartThings selected in the SmartApp GUI.

You can click on any controllable device, mode or routine in the Mac's Bitbar display to invoke the default action for that device, mode or routine.  Non-controllable devices (eg. presence sensors, motion sensors, temperarture sensors) can show their event history.

Battery levels can be dipslayed for devices that have batteries by using the {option} key once the BitBar meny is displayed.


## Section 1: Installation:

Select from one of the two sections below (Either 1a or 1b).

The recommended approach for SmartThings installation is using the integration of your SmartThings IDE and GitHub so that updates to the BitBar Output SmartApp are visual and easier.

Updates to the Python source code located on your MacOS is currently by a manual method by downloading the source code from the Github repository. This manual will not go into detail about setting up your SmartThings IDE with GitHub as that is documented in the [SmartThings GitHub Documentation](http://docs.smartthings.com/en/latest/tools-and-ide/github-integration.html?highlight=github).


### Section 1a: Making the STBitBar SmartApp available via the ST IDE using GitHub Integration
1. Setup the SmartApp: Find your SmartThings IDE Link
	* [US Users](https://graph.api.smartthings.com/)
	* [UK Users](https://graph-eu01-euwest1.api.smartthings.com/)
2. Find the **My SmartApps** link on the top of the page.
3. Find the **Settings** button at the upper-right corner of your SmartThings IDE page (this will only appear after you have configured with GitHub).
4. Clicking this button will open the GitHub Repository Integration page. To find the **StBitBarApp** SmartApp code, enter the information below:
	* **Owner:** kurtsanders
	* **Name:** STBitBarApp
	* **Branch:** master
5. Close the GitHub Repository Integration page by clicking the **Save** button.
6. Click the **Update from Repo** button at the upper-right corner of your SmartThings IDE and select STBitBarApp (master) from the list.
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
3. Click the From Code tab and paste the [SmartApp code from GitHub](https://raw.githubusercontent.com/kurtsanders/STBitBarApp/master/SmartThings%20SmartApp/STBitBar.groovy) then click Create. 
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

1. Required: You **must download** and install the core [BitBar app](https://github.com/matryer/bitbar/releases/tag/v1.9.2) on your Mac.  *This program is required to allow ST BitBar SmartApp to access the top menubar on the Mac.*
2. After downloading and installing the BitBar App & moving the BitBar App file to your applications folder, launch the BitBar App so that you can set the path for your Plugin directory.

	*IMPORTANT: When selecting a plugin directory where the plugins will reside, make sure you create one that does not contain spaces. There were issues in an older release of BitBar if the path contained spaces, but supposedly it’s fixed, but I still had issues in some cases. If there were no spaces, it always worked.*
3. In the BitBar application menu, the last option is labeled 'Preferences', make sure you select 'Open at Login' and specify the Plugin directory where you will place the plugin files from this Github in the next step.   	
4. Download the [ST plugin from GitHub](https://github.com/kurtsanders/STBitBarApp/tree/master/BitBar%20Plugin). Copy **ONLY** the ST.5m.sh file to the plugin directory you specified along with the ST subfolder containing the Python script and the ST_Python_Logic.cfg (make sure these two files stay in the folder named ST).  *These files should be the only files in the plugins directory and the ST subfolder.*
5. Add your URL and secret to the ST_Python_Logic.cfg file ***without any quotes***: Open the ST_Python_Logic.cfg with a text editor of your choice (eg. textedit). Put the URL that was displayed in step 5 in the smartAppURL variable and Secret in the secret variable without any quotes. 
6. **Save** the ST_Python_Logic.cfg file in the ST subfolder.
7. Ensure **execution rights** for the plugins:
	* Launch the MacOS Terminal Application
	* Navigate to your BitBar Plugins directory (eg. cd)
	* Issue the admin commands on the following files: 
		* **chmod +x ST.5m.sh**
		* **chmod +x ST_Python_Logic.py**
	* Exit the MacOS Terminal
8. **Start** the BitBar app and you should see your SmartThings devices and status’ in the MacOS menubar!

## Issues / Limitations

1. The BitBar App is capable of cycling through multiple status bar items.  However, this ST BitBar Plugin is designed to only display **one temperature sensor** at the top with the rest of the sensors displayed in the dropdown. 
2. The ST BitBar app only allows a selection of one temp sensor and an optional custom title.   You do not want to use the full sensor name since menubar real estate is top dollar.  The title can be left blank and the termpeature will only show in the menubar.
3. There is no hotizontal alignment supported by BitBar so it’s all done by character spacing, which means using Apple system monospace fonts for data content. Menlo is the default font, but feel free to change it in the ST BitBar App in the mobile client Display Options.
4. Selection of a proportional spaced font, pitch and color can be used for all other text areas of the display, like the ST Categories and the ...more... sections.  Be aware that some fonts, colors and sizes may cause the menu to become illegible.  Blank field defaults in the options fields will return the display to nornal.
5. Most areas of the menu will accomodate extended ascii character sets, but there might be areas that not.  If so, please rename these devices with US ascii characters and send a PM to me. 

## Misc Features / Tips
* Hold the **Alt** key while the BitBar menu is open to display battery information for devices that can report battery level status.
* The max items per sensor category can be set in BitBar Output SmartApp Menu Options (if you want to save space but still have access to the sensors)
* Use **Command-R** while viewing the STBitBarApp menu to **Refresh** the devices, otherwise it will automatically refresh every 5 minutes.
* You can download the latest version of the Python code at the bottom of the STBitbarApp Menu under **STBitBarApp Configuration**
* **Emoji short-names** are special graphical icons that can be displayed for custom device status.  Please note that these short naming convention is ':xxxxx:' and the name must be entered exactly as they are named on the [Emoji Website Valid Names List](http://www.webpagefx.com/tools/emoji-cheat-sheet/)
* Many other display options are provided and activated in the STBitBarApp SmartApp and are required.

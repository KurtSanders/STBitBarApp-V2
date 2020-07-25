#!/bin/bash
# Author: SandersSoft (c) 2020
# HEBitBar-V2
# https://raw.githubusercontent.com/KurtSanders/HEBitBarApp-V2/master/installation/HEBitBarInstall.command
version="4.04"

echo "HEBitBar-V2 Installer/Upgrader (c) SanderSoft"
echo "============================================="
echo "Version ${version}"

# Begin Define Variables #
HEBitBarPlistFilename="${HOME}/Library/Preferences/com.matryer.BitBar"
HEBitBarPlistPluginVar="pluginsDirectory"
HEBitBarGitHubRawHttp="https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/hubitat"
HEBitBarPluginScriptFilename="HE.5m.sh"
HEBitBarPythonCfgFilename="HE_Python_Logic.cfg"
HEBitBarPythontFilename="HE_Python_Logic.py"
HEBitBarManifestFilename="manifest.json"
BitBarSoftwareURL="https://github.com/matryer/bitbar/releases/download/v1.9.2"
BitBarSoftwareFilename="BitBar-v1.9.2.zip"
downloadsFolder="$HOME/Downloads"
debugMode=false

### TESTING MODE CHECK
if [[ "${1}" == "debug" ]]
then
	debugMode=true
	echo "DEBUG MODE = ${debugMode}"
	cd "${downloadsFolder}" || exit
fi

echo "Checking BitBar software installation and reading the BitBar plist file..."
if [[ ! -f ${HEBitBarPlistFilename}.plist ]]; then
	echo "The BitBar plist file '${HEBitBarPlistFilename}' was not found!"
	echo "BitBar base software NOT installed... conecting to developers github website and will download BitBar.app to your 'Downloads' directory"
	cd "${downloadsFolder}" || exit
	curl -s -O -J -L "${BitBarSoftwareURL}/${BitBarSoftwareFilename}"
	unzip -qq ${BitBarSoftwareFilename}
	echo "Open Finder to Downlaods folder and move BitBar.app to your Applications folder and click on BitBar.app and set BitBar plugin folder and check 'Open at Login'"
	echo "After successful install and activation of BitBar.app, rerun this install script"
	exit 1
fi

HEBitBarPluginsDirectory="$(defaults read "${HEBitBarPlistFilename}" | grep ${HEBitBarPlistPluginVar} | cut -d\" -f2)"
if [[ ${HEBitBarPluginsDirectory} == "" ]]; then
	echo "The BitBar Plugin directory not found in the ${HEBitBarPlistFilename} file, Exiting..."
	echo "Launch the BitBar.app application and set BitBar plugin folder in the preferences and 'Open at Login'"
	exit 1
fi

echo "The BitBar plugin folder: '${HEBitBarPluginsDirectory}'"

### TESTING MODE CHECK
if [[ "${debugMode}" == "true" ]]
then
	HEBitBarPluginsDirectory="${downloadsFolder}"
	echo "TESTING DEBUG MODE.. Using ${HEBitBarPluginsDirectory} folder as BitBar Plugins folder"
fi

echo "Changing to the ${HEBitBarPluginsDirectory} folder.."
cd "${HEBitBarPluginsDirectory}" || exit
FILE="${HEBitBarPluginsDirectory}/HE/${HEBitBarPythonCfgFilename}"

echo "Checking for the existance of '${FILE}'"
if [[ -f "$FILE" ]]; then
	echo "Found an existing '${HEBitBarPythonCfgFilename}'.  Installation script will not overwrite... "
else
	echo "Creating ${HEBitBarPluginsDirectory}/HE"
	mkdir -p "${HEBitBarPluginsDirectory}/HE"
	cd "${HEBitBarPluginsDirectory}/HE" || exit
	echo "Creating  ${HEBitBarPluginsDirectory}/HE/${HEBitBarPythonCfgFilename}"
	curl -s -O -J -L  ${HEBitBarGitHubRawHttp}/BitBar%20Plugin/HE/${HEBitBarPythonCfgFilename}
	echo "Please edit the '${HEBitBarPluginsDirectory}/HE/${HEBitBarPythonCfgFilename}' file and enter your two API strings and SAVE"
	open "${HEBitBarPluginsDirectory}/HE/${HEBitBarPythonCfgFilename}" -a TextEdit
fi

echo "Locating the 'ST.*.sh' files in your BitBar plugin folder...."
shopt -s nullglob
declare -a arrayOfFiles
for file in HE.[0-9][0-9ms]*.sh
do
	arrayOfFiles=("${arrayOfFiles[@]}" "$file")
done

if [[ "${#arrayOfFiles[@]}" -eq 0 ]]
then
	arrayOfFiles[0]="${HEBitBarPluginScriptFilename}"
elif [[ "${#arrayOfFiles[@]}" -gt 1 ]]
then
	echo "I found more than  ${#arrayOfFiles[@]}  'ST.*.sh' files in the BitBar Plugin Directory."
	echo "Please delete all but 1 ST.*.sh file, exiting installer..."
	for i in "${!arrayOfFiles[@]}"; do
		# shellcheck disable=SC2003
		printf "%s)\t%s\n" "$(expr ${i} + 1) " "${arrayOfFiles[$i]}"
	done
	exit 1
fi
HEBitBar_User_Plugin_ShellScript=${arrayOfFiles[0]}

echo "The STBitBar BitBar plugin file is: '${HEBitBar_User_Plugin_ShellScript}'"
if [[ "${HEBitBar_User_Plugin_ShellScript}" != "${HEBitBarPluginScriptFilename}" ]]
then
	echo "========================================================================================================= "
	echo "Warning: The new STBitBar V4 default for automatically polling SmartThings devices is EVERY 1 MINUTE."
	echo "Please manually rename the '${HEBitBar_User_Plugin_ShellScript}' in the '${HEBitBarPluginsDirectory}' folder to 'ST.1m.sh'"
	echo "This installation script will ask to rename '${HEBitBar_User_Plugin_ShellScript}'.  Answer No if you want to keep your current {different} SmartThings polling frequency"
	echo "Rename your ${HEBitBar_User_Plugin_ShellScript} to  ${HEBitBarPluginScriptFilename}. Are you sure? [y/N]"
	read -r response
	case "$response" in
		[yY][eE][sS] | [yY])
			mv -iv "${HEBitBarPluginsDirectory}/${HEBitBar_User_Plugin_ShellScript}" "${HEBitBarPluginsDirectory}/${HEBitBarPluginScriptFilename}"
			echo "Renamed  ${HEBitBarPluginsDirectory}/${HEBitBar_User_Plugin_ShellScript}" "${HEBitBarPluginsDirectory}/${HEBitBarPluginScriptFilename}"
			HEBitBar_User_Plugin_ShellScript="${HEBitBarPluginScriptFilename}"
		;;
		*)
			echo "Keeping the ${HEBitBar_User_Plugin_ShellScript} file..."
		;;
	esac
fi

echo "Downloading/Updating updated STBitBar-V2 Github's 'ST.1m.sh' as  ${HEBitBarPluginsDirectory}/${HEBitBar_User_Plugin_ShellScript} ..."
cd "${HEBitBarPluginsDirectory}" || exit
curl -s -O -J -L  "${HEBitBarGitHubRawHttp}/BitBar%20Plugin/${HEBitBarPluginScriptFilename}" "\"${HEBitBar_User_Plugin_ShellScript}\""
chmod +x "${HEBitBar_User_Plugin_ShellScript}"
echo "Downloading/Updating STBitBar-V2 Github's 'ST_Python_Logic.py' to the BitBar plugin '${HEBitBarPluginsDirectory}/HE' folder..."
mkdir -p "${HEBitBarPluginsDirectory}/HE"
cd "${HEBitBarPluginsDirectory}/HE" || exit
curl -s -O -J -L "${HEBitBarGitHubRawHttp}/BitBar%20Plugin/HE/${HEBitBarPythontFilename}"
chmod +x "ST_Python_Logic.py"
echo "Downloading/Updating STBitBar-V2 Github's '${HEBitBarManifestFilename}' to the BitBar plugin '${HEBitBarPluginsDirectory}/HE' folder..."
curl -s -O -J -L "${HEBitBarGitHubRawHttp}/installation/manifest.json"
echo "STBitBar-V2 Install/Update completed..."

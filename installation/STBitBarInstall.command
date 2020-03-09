# Author: SandersSoft (c) 2020
# STBitBar-V2
# https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/installation/STBitBarInstall.command

echo "STBitBar-V2 Installer/Upgrader (c) SanderSoft"
echo "============================================="

# Begin Define Variables #
STBitBarPlistFilename="${HOME}/Library/Preferences/com.matryer.BitBar"
STBitBarPlistPluginVar="pluginsDirectory"
STBitBarGitHubRawHttp="https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master"
STBitBarPluginScriptFilename="ST.1m.sh"
STBitBarPythonCfgFilename="ST_Python_Logic.cfg"
STBitBarPythontFilename="ST_Python_Logic.py"
BitBarSoftwareURL="https://github.com/matryer/bitbar/releases/download/v1.9.2"
BitBarSoftwareFilename="BitBar-v1.9.2.zip"
downloadsFolder="$HOME/Downloads"
debugMode=false

### TESTING MODE CHECK
if [[ "${1}" == "debug" ]]
then
	debugMode=true
	echo "DEBUG MODE = ${debugMode}"
	cd "${downloadsFolder}"
fi

echo "Checking BitBar software installation and reading the BitBar plist file..."
if [[ ! -f ${STBitBarPlistFilename}.plist ]]; then
	echo "The BitBar plist file '${STBitBarPlistFilename}' was not found!"
	echo "BitBar base software NOT installed... conecting to developers github website and will download BitBar.app to your 'Downloads' directory"
	cd "${downloadsFolder}"
	curl -s -O -J -L "${BitBarSoftwareURL}/${BitBarSoftwareFilename}"
	unzip -qq ${BitBarSoftwareFilename}
	echo "Open Finder to Downlaods folder and move BitBar.app to your Applications folder and click on BitBar.app and set BitBar plugin folder and check 'Open at Login'"
	echo "After successful install and activation of BitBar.app, rerun this install script"
	exit 1
fi

STBitBarPluginsDirectory="$(defaults read ${STBitBarPlistFilename} | grep ${STBitBarPlistPluginVar} | cut -d\" -f2)"
if [[ ${STBitBarPluginsDirectory} == "" ]]; then
	echo "The BitBar Plugin directory not found in the ${STBitBarPlistFilename} file, Exiting..."
	echo "Launch the BitBar.app application and set BitBar plugin folder in the preferences and 'Open at Login'"
	exit 1
fi

echo "The BitBar plugin folder: '${STBitBarPluginsDirectory}'"

### TESTING MODE CHECK
if [[ "${debugMode}" == "true" ]]
then
	STBitBarPluginsDirectory="${downloadsFolder}"
	echo "TESTING DEBUG MODE.. Using ${STBitBarPluginsDirectory} folder as BitBar Plugins folder"
fi

echo "Changing to the ${STBitBarPluginsDirectory} folder.."
cd "${STBitBarPluginsDirectory}"
FILE="${STBitBarPluginsDirectory}/ST/${STBitBarPythonCfgFilename}"

echo "Checking for the existance of '${FILE}'"
if [[ -f "$FILE" ]]; then
	echo "Found an existing '${STBitBarPythonCfgFilename}'.  Installation script will not overwrite... "
else
	echo "Creating ${STBitBarPluginsDirectory}/ST"
	mkdir -p "${STBitBarPluginsDirectory}/ST"
	cd "${STBitBarPluginsDirectory}/ST"
	echo "Creating  ${STBitBarPluginsDirectory}/ST/${STBitBarPythonCfgFilename}"
	curl -s -O -J -L  ${STBitBarGitHubRawHttp}/BitBar%20Plugin/ST/${STBitBarPythonCfgFilename}
	echo "Please edit the '${STBitBarPluginsDirectory}/ST/${STBitBarPythonCfgFilename}' file and enter your two API strings and SAVE"
	open "${STBitBarPluginsDirectory}/ST/${STBitBarPythonCfgFilename}" -a TextEdit
fi

echo "Locating the 'ST.*.sh' files in your BitBar plugin folder...."
shopt -s nullglob
declare -a arrayOfFiles
for file in ST.[0-9][0-9ms]*.sh
do
	arrayOfFiles=("${arrayOfFiles[@]}" "$file")
done

if [[ "${#arrayOfFiles[@]}" -eq 0 ]]
then
	arrayOfFiles[0]="${STBitBarPluginScriptFilename}"
elif [[ "${#arrayOfFiles[@]}" -gt 1 ]]
then
	echo "I found more than  ${#arrayOfFiles[@]}  'ST.*.sh' files in the BitBar Plugin Directory."
	echo "Please delete all but 1 ST.*.sh file, exiting installer..."
	for i in "${!arrayOfFiles[@]}"; do
		printf "%s)\t%s\n" "$(expr ${i} + 1) " "${arrayOfFiles[$i]}"
	done
	exit 1
fi
STBitBar_User_Plugin_ShellScript=${arrayOfFiles[0]}

echo "The STBitBar BitBar plugin file is: '${STBitBar_User_Plugin_ShellScript}'"
if [[ "${STBitBar_User_Plugin_ShellScript}" != "${STBitBarPluginScriptFilename}" ]]
then
	echo "========================================================================================================= "
	echo "Warning: The new STBitBar V4 default for automatically polling SmartThings devices is EVERY 1 MINUTE."
	echo "Please manually rename the '${STBitBar_User_Plugin_ShellScript}' in the '${STBitBarPluginsDirectory}' folder to 'ST.1m.sh'"
	echo "This installation script will ask to rename '${STBitBar_User_Plugin_ShellScript}'.  Answer No if you want to keep your current {different} SmartThings polling frequency"
	echo "Rename your ${STBitBar_User_Plugin_ShellScript} to  ${STBitBarPluginScriptFilename}. Are you sure? [y/N]"
	read -r response
	case "$response" in
		[yY][eE][sS] | [yY])
			mv -iv "${STBitBarPluginsDirectory}/${STBitBar_User_Plugin_ShellScript}" "${STBitBarPluginsDirectory}/${STBitBarPluginScriptFilename}"
			echo "Renamed  ${STBitBarPluginsDirectory}/${STBitBar_User_Plugin_ShellScript}" "${STBitBarPluginsDirectory}/${STBitBarPluginScriptFilename}"
			STBitBar_User_Plugin_ShellScript="${STBitBarPluginScriptFilename}"
		;;
		*)
			echo "Keeping the ${STBitBar_User_Plugin_ShellScript} file..."
		;;
	esac
fi

echo "Downloading/Updating updated STBitBar-V2 Github's 'ST.1m.sh' as  ${STBitBarPluginsDirectory}/${STBitBar_User_Plugin_ShellScript} ..."
cd "${STBitBarPluginsDirectory}"
curl -s -O -J -L  "${STBitBarGitHubRawHttp}/BitBar%20Plugin/${STBitBarPluginScriptFilename}" "\"${STBitBar_User_Plugin_ShellScript}\""
chmod +x "${STBitBar_User_Plugin_ShellScript}"
echo "Downloading/Updating STBitBar-V2 Github's 'ST_Python_Logic.py' to the BitBar plugin '${STBitBarPluginsDirectory}/ST' folder..."
mkdir -p "${STBitBarPluginsDirectory}/ST"
cd "${STBitBarPluginsDirectory}/ST"
curl -s -O -J -L "${STBitBarGitHubRawHttp}/BitBar%20Plugin/ST/ST_Python_Logic.py"
chmod +x "ST_Python_Logic.py"
echo "Install/Update completed..."

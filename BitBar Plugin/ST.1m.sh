#!/bin/bash

# Author: SandersSoft (c) 2020
# STBitBar-V2
# https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/BitBar%20Plugin/ST.5m.sh
# This executable bash shell file must exist in user defined BitBar Plugins directory with the ST_Python_logic.py file

# Begin Define User Variables #
# Review the ReadMe file on STBitBar-V2 github for explanation of these variables
device_recheck_sleep_time_sec=5
pause_message="\"Pausing ${device_recheck_sleep_time_sec} sec before device status re-check\""
verbose_schedule_notify=false
verbose_request_notify=true
# End Define User Variables #

# Do not modify any lines below
# Main Program

st_python_logic_filename=`dirname $0`/ST/ST_Python_Logic.py
version="4.00"

if [[ ! -f "${st_python_logic_filename}" ]]; then
	osascript -e "display alert \"ST BitBar ERROR\" message \"${st_python_logic_filename} file not found!\""
	exit 99
fi

if [[ $# -eq 0 ]]
then
	if [[ ${verbose_schedule_notify} = true ]]
	then
		osascript -e "display notification \"Routine Device Status Update\" with title \"ST BitBar Device Status\""
	fi
	python "${st_python_logic_filename}" $0 "${version}"
	exit $?
fi

# Check 1st argument and take action
case "$1" in
	request)
		if [[ ${verbose_request_notify} = true ]] && [[ $# -eq 4 ]]
		then
			osascript -e "display notification ${pause_message} with title \"ST BitBar Device Change\" subtitle \"${4}\" "
		fi
		curl -s $2 -H "Authorization: Bearer "$3
		sleep "${device_recheck_sleep_time_sec}"
		python "${st_python_logic_filename}" $0 "${version}"
	;;
	open)
		open $2 $3 $4 $5
	;;
	github_ST_Python_Logic)
		osascript -e 'display notification "Downloading the ST_Python_Logic.py from KurtSanders STBitBarApp GitHub Repo " with title "ST BitBar App Notice" sound name "Frog" '
		temp_file=$(mktemp)
		curl -LkSs https://github.com/KurtSanders/STBitBarApp-V2/archive/master.zip -o "$temp_file"
		unzip -qq -j -o -d ~/Downloads/ "$temp_file" 'STBitBarApp-V2-master/BitBar Plugin/ST/ST_Python_Logic.py'
		rm "$temp_file"
		chmod +x ST_Python_Logic.py
		#        curl -s -H 'Cache-Control: no-cache' --output ~/Downloads/ST_Python_Logic.py --URL https://raw.githubusercontent.com/kurtsanders/STBitBarApp/master/BitBar%20Plugin/ST/ST_Python_Logic.py
		open ~/Downloads/
		sleep 5
		osascript -e 'display notification "Move the new ST_Python_Logic.py located in your Downloads Directory." with title "ST BitBar App Notice" sound name "Frog" '
		sleep 2
		osascript -e 'display notification "into the same folder in your BitBar Plugins Subdirectory" with title "ST BitBar App Notice" sound name "Frog" '
	;;
	github_ST5MSH)
		osascript -e 'display notification "Downloading the ST.5m.sh from KurtSanders STBitBarApp GitHub Repo " with title "ST BitBar App Notice" sound name "Frog" '
		#        curl -s -H 'Cache-Control: no-cache' --output ~/Downloads/ST.5m.sh --URL https://raw.githubusercontent.com/kurtsanders/STBitBarApp/master/BitBar%20Plugin/ST/ST.5m.sh
		temp_file=$(mktemp)
		curl -LkSs https://github.com/KurtSanders/STBitBarApp-V2/archive/master.zip -o "$temp_file"
		unzip -qq -j -o -d ~/Downloads/ "$temp_file" 'STBitBarApp-V2-master/BitBar Plugin/ST.5m.sh'
		rm "$temp_file"
		chmod +x ST.5m.sh
		open ~/Downloads/
		sleep 5
		osascript -e 'display notification "Move the new ST.5m.sh located in your Downloads Directory" with title "ST BitBar App Notice" sound name "Frog" '
		sleep 2
		osascript -e 'display notification "into the same folder in your BitBar Plugins Subdirectory" with title "ST BitBar App Notice" sound name "Frog" '
	;;
	*)
		echo "Invalid parameter '${1}'"
		exit 99
	;;
esac

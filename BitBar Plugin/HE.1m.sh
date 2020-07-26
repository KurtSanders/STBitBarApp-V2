#!/bin/bash

# Author: SandersSoft (c) 2020
# HEBitBar-V2
# https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/BitBar%20Plugin/HE.5m.sh
# This executable bash shell file must exist in user defined BitBar Plugins directory with the HE_Python_logic.py file

# Begin Define User Variables #
# Review the ReadMe file on STBitBar-V2 github for explanation of these variables
device_recheck_sleep_time_sec=5
pause_message="\"Pausing ${device_recheck_sleep_time_sec} sec before device status re-check\""
verbose_schedule_notify=true
verbose_request_notify=true
# End Define User Variables #

# Do not modify any lines below
# Main Program

he_python_logic_filename=`dirname $0`/HE/HE_Python_Logic.py
version="5.00"

if [[ ! -f "${he_python_logic_filename}" ]]; then
	osascript -e "display alert \"HE BitBar ERROR\" message \"${he_python_logic_filename} file not found!\""
	exit 99
fi

if [[ $# -eq 0 ]]
then
	if [[ ${verbose_schedule_notify} = true ]]
	then
		osascript -e "display notification \"Routine Device Status Update\" with title \"HE BitBar Device Status\""
	fi
	python "${he_python_logic_filename}" $0 "${version}"
	exit $?
fi

# Check 1st argument and take action
case "$1" in
	request)
		if [[ ${verbose_request_notify} = true ]] && [[ $# -eq 4 ]]
		then
			osascript -e "display notification ${pause_message} with title \"HE BitBar Device Change\" subtitle \"${4}\" "
		fi
		curl -s $2 -H "Authorization: Bearer "$3
		sleep "${device_recheck_sleep_time_sec}"
		python "${he_python_logic_filename}" $0 "${version}"
	;;
	open)
		open $2 $3 $4 $5
	;;
	upgrade)
		cd "$HOME/Downloads/"
		curl -s -O -J -L "https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/installation/HEBitBarInstall.command"
		osascript -e 'display alert "Downloaded HE BitBar Install Script!" message "After this window closes, double click the \"HEBitBarInstall.command\" file to upgrade the HE BitBar plugins files."'
		open "$HOME/Downloads/"
	;;
	*)
		echo "Invalid parameter '${1}'"
		exit 99
	;;
esac

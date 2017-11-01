#!/bin/bash
# Version 2.4
if [ $# -gt 0 ]
  then
  	if [ $1 = "request" ]
  	then
  		curl -s $2 -H "Authorization: Bearer "$3
  		exit
    elif [ $1 = "open" ]
    then
        open $2 $3 $4 $5
        exit
    elif [ $1 = "github_ST_Python_Logic" ]
    then
        osascript -e 'display notification "Downloading the ST_Python_Logic.py from KurtSanders STBitBarApp GitHub Repo " with title "ST BitBar App Notice" sound name "Frog" '
        curl -s -H 'Cache-Control: no-cache' --output ~/Downloads/ST_Python_Logic.py --URL https://raw.githubusercontent.com/kurtsanders/STBitBarApp/master/BitBar%20Plugin/ST/ST_Python_Logic.py
        open ~/Downloads/
        sleep 5
        osascript -e 'display notification "Move the ST_Python_Logic.py from the Downloads Directory to BitBar Plugins Subdirectory" with title "ST BitBar App Notice" sound name "Frog" '
        exit
	fi
fi
python `dirname $0`/ST/ST_Python_Logic.py $0
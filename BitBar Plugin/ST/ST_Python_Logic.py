# -*- coding: utf-8 -*-
import ConfigParser
import decimal
import json
import re
import subprocess
import sys
import time
from subprocess import check_output
from urlparse import urlparse
import urllib
reload(sys)
sys.setdefaultencoding('utf8')

##################################
# Set Required SmartApp Version as Decimal, ie 2.0, 2.1, 2.12...
# Supports all minor changes in BitBar 2.1, 2.2, 2.31...
PythonVersion = 2.31  # Must be float or Int
##################################


# Define class for formatting numerical outputs (temp sensors)
# Define NumberFormatter class
class NumberFormatter:
    def __init__(self):
        self.decimalRounding = 0
        self.staticDecimalPlaces = -1

    def setRoundingPrecision(self, precision):
        self.decimalRounding = precision

    def setStaticDecimalPlaces(self, places):
        self.staticDecimalPlaces = places

    def getNumberOfDecimals(self, number):
        r = round(number, self.decimalRounding)
        if r % 1 == 0: return 0
        return abs(decimal.Decimal(str(r)).as_tuple().exponent)

    # noinspection PyShadowingNames
    def formatNumber(self, number):
        r = round(number, self.decimalRounding)
        if self.staticDecimalPlaces is not -1:
            formatter = "{0:." + str(self.staticDecimalPlaces) + "f}"
            return formatter.format(r)
        else:
            if r % 1 == 0:
                return str(int(r))
            else:
                return str(r)


# String Case Formatter
def TitleCase(var):
    return var if var is None else var.capitalize()


# Format percentages
def formatPercentage(val):
    if type(val) is int:
        return str(val) + "%"
    else:
        return val


# Format Timespan values in milliseconds
def formatTimespan(eventTime):
    minutes = (eventTime / (1000 * 60)) % 60
    hours = (eventTime / (1000 * 60 * 60)) % 24
    timespanString = ''
    if hours > 0: timespanString += str(hours) + " hour"
    if hours > 1: timespanString += "s"
    if hours == 0:
        if minutes == 0: timespanString += "less than a minute"
        if minutes == 1: timespanString += "a minute"
        if minutes > 1: timespanString += " " + str(minutes) + " minute"
    else:
        timespanString += " " + str(minutes) + " minute"
    if minutes > 1: timespanString += "s"
    return timespanString


# Return hex color code based on multiple step gradient (for thermo colors)
def numberToColorGrad(val, color):
    if color == 'red':
        if val == 5: return "#E50008"
        if val == 4: return "#EB1B20"
        if val == 3: return "#F23739"
        if val == 2: return "#F85352"
        if val == 1: return "#FF6F6B"
        if val == 0: return "#FF757A"
    if color == 'blue':
        if val == 5: return "#002FE5"
        if val == 4: return "#1745EA"
        if val == 3: return "#2E5BEF"
        if val == 2: return "#4671F4"
        if val == 1: return "#5D87F9"
        if val == 0: return "#759DFF"
    return "green"


# Define and Assign Display Options and check for None
def getOptions(dictvarname, nonedefault):
    tmp = options.get(dictvarname, nonedefault)
    return tmp if tmp is not None else nonedefault


# Setting Class
class Setting(object):
    def __init__(self, cfg_path):
        self.cfg = ConfigParser.ConfigParser()
        self.cfg.read(cfg_path)

    # noinspection PyShadowingNames
    def get_setting(self, my_setting, default_value, severe_bool=False):
        try:
            ret = self.cfg.get("My Section", my_setting)
        except ConfigParser.NoOptionError as e:
            if severe_bool:
                print "Severe Error:" + str(e)
                raise SystemExit(0)
            else:
                ret = default_value
                # Remove Extra Quotes, etc
        return re.sub(r'^"|"$', '', ret)


# End Class Setting

# Builds the param statement for bitbar to launch the "open" command
# noinspection PyShadowingNames
def openParamBuilder(openCommand):
    rc = " terminal=false bash={} ".format(sys.argv[1])
    i = 0
    for word in openCommand.split():
        i += 1
        rc += "param{}={} ".format(i, word)
    return rc


# Build the SmartThings IDE URL based on the SmartApp URL input
def buildIDEURL(url):
    parsed_uri = urlparse(url)
    ide = '{uri.scheme}://{uri.netloc}/ide/apps'.format(uri=parsed_uri)
    return ide


def verifyInteger(intValue, errorIntValue):
    if isinstance(intValue, int):
        return intValue
    else:
        return errorIntValue


# Begin Read User Config File
cfgFileName = sys.argv[0][:-2] + "cfg"
cfgFileObj = Setting(cfgFileName)
cfgGetValue = cfgFileObj.get_setting
smartAppURL = cfgGetValue('smartAppURL', "", True)
secret = cfgGetValue('secret', "", True)

# Set URLs
statusURL = smartAppURL + "GetStatus/?pythonAppVersion="+PythonVersion.__str__() + "&path=" + sys.argv[0]
contactURL = smartAppURL + "ToggleSwitch/?id="
levelURL = smartAppURL + "SetLevel/?id="
musicplayerURL = smartAppURL + "SetMusicPlayer/?id="
lockURL = smartAppURL + "ToggleLock/?id="
thermoURL = smartAppURL + "SetThermo/?id="
routineURL = smartAppURL + "SetRoutine/?id="
modeURL = smartAppURL + "SetMode/?id="
alarmURL = smartAppURL + "SetAlarm/?id="

# Set the callback script for switch/level commands from parameters
# sys.argv[1] must contain the full path name to bitbar pluggins subdirectory
# an example could be: /Users/[account name]/[directory]/Bitbar/ST/
callbackScript = sys.argv[1]

# Make the call the to the API and retrieve JSON data
attempt = 0
maxRetries = 10
connected = False
output = None
while connected is False:
    try:
        # print 'curl', '-s', statusURL, '-H', 'Authorization: Bearer ' + secret
        output = check_output(['curl', '-s', statusURL, '-H', 'Authorization: Bearer ' + secret])
        connected = True
    except subprocess.CalledProcessError as grepexc:
        attempt += 1
        if attempt == maxRetries:
            print "Unable to Connect to SmartThings"
            print "---"
            print "Please check connection and try again (⌘R)"
            print "Debug information: Error code ", grepexc.returncode, grepexc.output
            raise SystemExit(0)
        time.sleep(3)
        continue

# Parse the JSON data
j = json.loads(output)

# API Return Error Handling
if "error" in j:
    print "Error while communicating with ST API"
    print '---'
    if j['error'] == 'invalid_token':
        print "Please check your SmartApp URL and Secret are both correct and try again."
    print "Error Details: ", j['error']
    if "error_description" in j:
        print "Error Description: ", j['error_description']
    raise SystemExit(0)

# Get the sensor arrays from the JSON data
try:
    alarms          = j['Alarm Sensors']
    temps           = j['Temp Sensors']
    contacts        = j['Contact Sensors']
    switches        = j['Switches']
    motion          = j['Motion Sensors']
    mainDisplay     = j['MainDisplay']
    musicplayers    = j['Music Players']
    locks           = j['Locks']
    presences       = j['Presence Sensors']
    thermostats     = j['Thermostats']
    routines        = j['Routines']
    modes           = j['Modes']
    currentmode     = j['CurrentMode']
    options         = j['Options']

except KeyError, e:
    print "Error in ST API Data"
    print "---"
    print "Error Details: ", e
    print "Source Data: ", output
    raise SystemExit(0)


def eventGroupByDate(tempList, prefix=None, valueSuffix=""):
    strLen = len(tempList)-1
    for x in range(0, strLen):
        curSplitRecord = tempList[x]['date'].split()
        if x == 0:
            print "--{}{} {} {}".format(
                prefix, curSplitRecord[0], curSplitRecord[1], curSplitRecord[2]
            ), buildFontOptions(3)
            sys.stdout.write("--")
        elif curSplitRecord[2] == tempList[x-1]['date'].split()[2]:
            sys.stdout.write("--")
        else:
            print "--{}{} {} {}".format(
                prefix, curSplitRecord[0], curSplitRecord[1], curSplitRecord[2]
            ), buildFontOptions(3)
            sys.stdout.write("--")
        print "--{}{} {} {} = {}{}".format(
            prefix, curSplitRecord[3], curSplitRecord[4], curSplitRecord[5], tempList[x]['value'],
            valueSuffix), buildFontOptions(3)
    return


# Set User Display Options sent from BitBar Output SmartApp
useImages                   = getOptions("useImages",True)
sortSensorsName             = getOptions("sortSensorsName",True)
subMenuCompact              = getOptions("subMenuCompact",False)
sortSensorsActive           = getOptions("sortSensorsActive",True)
showSensorCount             = getOptions("showSensorCount",True)
motionActiveEmoji           = getOptions("motionActiveEmoji",'⇠⇢')
motionInactiveEmoji         = getOptions("motionInactiveEmoji",'⇢⇠')
contactOpenEmoji            = getOptions("contactOpenEmoji",'⇠⇢')
contactClosedEmoji          = getOptions("contactClosedEmoji",'⇢⇠')
presenscePresentEmoji       = getOptions("presenscePresentEmoji",':house:')
presensceNotPresentEmoji    = getOptions("presensceNotPresentEmoji",':x:')
presenceDisplayMode         = getOptions("presenceDisplayMode", 0)
mainFontName                = "'{}'".format(getOptions("mainFontName","Menlo"))
mainFontSize                = getOptions("mainFontSize","14").__str__()
fixedPitchFontSize          = getOptions("fixedPitchFontSize", "14").__str__()
fixedPitchFontName          = "'{}' ".format(getOptions("fixedPitchFontName", "Menlo"))
fixedPitchFontColor         = getOptions("fixedPitchFontColor","Black")
subMenuFontName             = "'{}'".format(getOptions("subMenuFontName","Monaco"))
subMenuFontSize             = getOptions("subMenuFontSize","14").__str__()
subMenuFontColor            = getOptions("subMenuFontColor","Black")
subMenuMoreColor            = getOptions("subMenuMoreColor","black")
hortSeparatorBarBool        = getOptions("hortSeparatorBarBool",True)
shmDisplayBool              = getOptions("shmDisplayBool",True)
# Read Temperature Formatting Settings
numberOfDecimals            = verifyInteger(getOptions("numberOfDecimals","0"),0)

matchOutputNumberOfDecimals = getOptions("matchOutputNumberOfDecimals", False)
colorSwitch                 = True
smallFontPitchSize          = "size={}".format(int(fixedPitchFontSize) - 2)
alarmStates                 = ['away', 'off', 'stay']

# Generates a Horizontal Separator Bar if desired by GUI
def hortSeparatorBar():
    if hortSeparatorBarBool:print "---"
    return

# Check if MacOS is in DarkMode
# noinspection PyBroadException
try:
    if "Dark" in check_output(['defaults', 'read', '-g', 'AppleInterfaceStyle'], stderr=subprocess.STDOUT):
        if "black" in subMenuFontColor.lower(): subMenuFontColor = "white"
        if "black" in subMenuMoreColor.lower(): subMenuMoreColor = "white"
        if "black" in fixedPitchFontColor.lower(): fixedPitchFontColor = "white"
except:
    pass


# Define the Font Options string for BitBar
def buildFontOptions(level=1):
    # Level 0: MainMenu
    if level == 0:
        return " | font={} size={}".format(mainFontName, mainFontSize)
    # Level 1: SubMenu Titles (default)
    elif level == 1:
        return " | font={} size={} color={} ".format(subMenuFontName,subMenuFontSize, subMenuFontColor)
    # Level 2: SubMenu More Text
    elif level == 2:
        return " | font={} size={} color={} ".format(subMenuFontName, subMenuFontSize, subMenuMoreColor)
    # Level 3: Data Fixed Pitch Text
    elif level == 3:
        return " | font={} size={} color={} ".format(fixedPitchFontName, fixedPitchFontSize, fixedPitchFontColor)
    # Level >3: No Formatting
    else:
        return " | "


# Setup the Main Menu and Sub Menu Display Relationship
mainMenuMaxItemsDict = {
    "Temps"         : None,
    "MusicPlayers"  : None,
    "Contacts"      : None,
    "Switches"      : None,
    "Motion"        : None,
    "Locks"         : None,
    "Presences"     : None
    }
mainMenuAutoSizeDict = {}
mainMenuAutoSize = False

for sensorName in mainMenuMaxItemsDict:
    mainMenuMaxItemsDict[sensorName] = options.get("mainMenuMaxItems" + sensorName, None)
    if mainMenuMaxItemsDict[sensorName] is None:
        mainMenuMaxItemsDict[sensorName] = 999
        mainMenuAutoSizeDict[sensorName] = True
        mainMenuAutoSize = True
    else:
        mainMenuAutoSizeDict[sensorName] = False

# Sort Sensors & Values in Dictionary/Lists
if sortSensorsName is True:
    sortkey = 'name'
    temps = sorted(temps, key=lambda k: k[sortkey])
    contacts = sorted(contacts, key=lambda k: k[sortkey])
    switches = sorted(switches, key=lambda k: k[sortkey])
    motion = sorted(motion, key=lambda k: k[sortkey])
    mainDisplay = sorted(mainDisplay, key=lambda k: k[sortkey])
    musicplayers = sorted(musicplayers, key=lambda k: k[sortkey])
    locks = sorted(locks, key=lambda k: k[sortkey])
    presences = sorted(presences, key=lambda k: k[sortkey])
    modes = sorted(modes, key=lambda k: k[sortkey])
    routines = sorted(routines)

if sortSensorsActive is True or mainMenuAutoSize is True:
    sortkey = 'value'
    contacts = sorted(contacts, key=lambda k: k[sortkey], reverse=True)
    switches = sorted(switches, key=lambda k: k[sortkey], reverse=True)
    motion = sorted(motion, key=lambda k: k[sortkey], reverse=True)
    locks = sorted(locks, key=lambda k: k[sortkey], reverse=True)
    presences = sorted(presences, key=lambda k: k[sortkey], reverse=True)
    musicplayers = sorted(musicplayers, key=lambda k: k['status'])

# Presence sort mode by status or in submenu, sort by value desc
if presenceDisplayMode == 1 or presenceDisplayMode == 2:
    presences = sorted(presences, key=lambda k: k['value'], reverse=True)

# Presence display mode only show present sensors
if presenceDisplayMode == 3:
    presences = filter(lambda p: p['value'] == 'present', presences)

# Verify SmartApp Version
try:
    majorBitBarVersion = int(j['Version'].encode('ascii').split('.')[0])
    majorPythonVersion = int(PythonVersion)
    if majorBitBarVersion != majorPythonVersion:
        print "X | color=red"
        print "---"
        print "Please make sure both Python and SmartThings SmartApp are up to date | color=red"
        print "Current BitBar Output SmartAPP Version:", majorBitBarVersion
        print "Current ST_Python_Logic.py Version:", PythonVersion
        raise SystemExit(0)
except KeyError, e:
    print "Error in ST API Data | color=red"
    print "---"
    print "Error Details: ", e
    print "Source Data: ", output
    raise SystemExit(0)

# Create a new NumberFormatter object
formatter = NumberFormatter()
# Set the number of decimals
formatter.setRoundingPrecision(numberOfDecimals)

# Format thermostat status color
thermoColor = ''
if len(thermostats) > 0:
    if "thermostatOperatingState" in thermostats[0]:
        if thermostats[0]['thermostatOperatingState'] == "heating":
            thermoColor += "color=red"
        if thermostats[0]['thermostatOperatingState'] == "cooling":
            thermoColor += "color=blue"

# Print the main display
degree_symbol = u'\xb0'.encode('utf-8')
formattedMainDisplay = u''

# Check if there is a name
if mainDisplay[0]['name'] is not None and mainDisplay[0]['name'] != "N/A":
    formattedMainDisplay += mainDisplay[0]['name'] + ":"

# Check if there is a value
if isinstance(mainDisplay[0]['value'],int) or isinstance(mainDisplay[0]['value'],float):
    formattedMainDisplay += formatter.formatNumber(mainDisplay[0]['value']) + degree_symbol
if formattedMainDisplay == '':
    formattedMainDisplay = "ST BitBar"
print "{} {} {}".format(formattedMainDisplay.encode('utf-8'),buildFontOptions(0), thermoColor)

# Find the max length sensor so values are lined up correctly
maxLength = 0
maxDecimals = 0
for sensor in temps:
    if len(sensor['name']) > maxLength:
        maxLength = len(sensor['name'])
    if formatter.getNumberOfDecimals(sensor['value']) > maxDecimals:
        maxDecimals = formatter.getNumberOfDecimals(sensor['value'])

for sensor in contacts:
    if len(sensor['name']) > maxLength:
        maxLength = len(sensor['name'])
for sensor in switches:
    if len(sensor['name']) > maxLength:
        maxLength = len(sensor['name'])
for sensor in motion:
    if len(sensor['name']) > maxLength:
        maxLength = len(sensor['name'])
for sensor in locks:
    if len(sensor['name']) > maxLength:
        maxLength = len(sensor['name'])
# Increment maxLength by one since contact sensor icon needs to be pulled back a little
maxLength += 1

# Set the static amount of decimal places based on setting
if matchOutputNumberOfDecimals is True:
    formatter.setStaticDecimalPlaces(maxDecimals)
else:
    formatter.setStaticDecimalPlaces(-1)

# Output the separation '---' between status bar items and menu items
print '---'
# Begin outputting sensor data

# Output Thermostat data
if len(thermostats) > 0:
    # noinspection SpellCheckingInspection
    thermoImage = ("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"
                   )
    thermoModeList = ["auto", "cool", "heat", "off"]
    for i, thermostat in enumerate(thermostats):
        if "thermostatMode" in thermostat and \
                        "thermostatOperatingState" in thermostat:
            setpointText = ''
            setpointAction = ' @ '
            currentSetpoint = 0
            # Set the action text based on operation state
            # Example: cooling to 75, idle @ 72, heating to 68
            if thermostat['thermostatOperatingState'] == 'cooling' or thermostat['thermostatOperatingState'] \
                == 'heating' : setpointAction = ' to '
            # Pick the correction setpoint value
            if thermostat['thermostatMode'] == 'cool':
                currentSetpoint = thermostat['coolingSetpoint']
            elif thermostat['thermostatMode'] == 'heat':
                currentSetpoint = thermostat['heatingSetpoint']
            elif thermostat['thermostatMode'] == 'auto':
                if thermostat['thermostatOperatingState'] == 'cooling':
                    currentSetpoint = thermostat['coolingSetpoint']
                if thermostat['thermostatOperatingState'] == 'heating':
                    currentSetpoint = thermostat['heatingSetpoint']
            # Set the display string
            if thermostat['thermostatOperatingState'] not in ["idle","off"]:
                setpointText = "(" + str(thermostat['thermostatOperatingState']) + setpointAction + str(
                    currentSetpoint) + degree_symbol + ")"
            else:
                setpointText = "({})".format(thermostat['thermostatOperatingState'])

            if "displayName" in thermostat:
                print thermostat['displayName'], setpointText, buildFontOptions(3), 'image=', thermoImage
            else:
                print "Thermostat Control", setpointText, buildFontOptions(3), 'image=', thermoImage
            if not subMenuCompact: print "--Current Status", buildFontOptions()
            currentThermoURL = thermoURL + thermostat['id']
            thermoModeURL = currentThermoURL + "&type=mode&val="
            # Mode Menu
            if "thermostatMode" in thermostat:
                print "--Mode ({})".format(TitleCase(thermostat['thermostatMode'])), buildFontOptions(3)
                if not subMenuCompact: print "----Set Mode to:", buildFontOptions(1)
                for thermoMode in thermoModeList:
                    if thermoMode != thermostat['thermostatMode']:
                        print "----{}".format(TitleCase(thermoMode)), buildFontOptions(3), \
                            "bash=" + callbackScript, " param1=request param2=" + thermoModeURL +\
                            thermoMode.lower(), " param3=" + secret, ' terminal=false refresh=true'
            # Cooling Setpoint Menu
            if "coolingSetpoint" in thermostat:
                if thermostat['coolingSetpoint'] is not None:
                    coolSetpointURL = currentThermoURL + "&type=coolingSetpoint&val="
                    currentCoolingSetPoint = int(thermostat['coolingSetpoint'])
                    print "--Cooling Set Point (" + str(currentCoolingSetPoint) + degree_symbol + ")", \
                        buildFontOptions(3), "color=blue"
                    print "----Change Setpoint | ", smallFontPitchSize
                    for c in range(currentCoolingSetPoint - 5, currentCoolingSetPoint):
                        id = currentCoolingSetPoint - c
                        print "----", str(c) + degree_symbol, buildFontOptions(3),\
                            "color=", numberToColorGrad(id, "blue"), \
                            "bash=", callbackScript, " param1=request param2=", str(
                            coolSetpointURL + str(c)), " param3=", secret, " terminal=false refresh=true"
                    print "----", str(currentCoolingSetPoint) + degree_symbol, "(current)|color=", \
                        numberToColorGrad(0,"blue")
                    for c in range(currentCoolingSetPoint + 1, currentCoolingSetPoint + 6):
                        print "----", str(c) + degree_symbol, buildFontOptions(3), "color=gray", \
                            "bash=", callbackScript, " param1=request param2=", str(
                            coolSetpointURL + str(c)), " param3=", secret, " terminal=false refresh=true"
            # Heating Setpoint Menu
            if "heatingSetpoint" in thermostat:
                if thermostat['heatingSetpoint'] is not None:
                    heatingSetpointURL = currentThermoURL + "&type=heatingSetpoint&val="
                    currentHeatingSetPoint = int(thermostat['heatingSetpoint'])
                    print "--Heating Set Point (" + str(currentHeatingSetPoint) + degree_symbol + ")", \
                        buildFontOptions(3),"color=red"
                    print "----Change Setpoint | ", smallFontPitchSize
                    for c in range(currentHeatingSetPoint + 5, currentHeatingSetPoint, -1):
                        id = c - currentHeatingSetPoint
                        print "----", str(
                            c) + degree_symbol, buildFontOptions(3), "color=", numberToColorGrad(id, "red"), \
                            "bash=" + callbackScript, " param1=request param2=" + str(
                            heatingSetpointURL + str(c)), " param3=" + secret, " terminal=false refresh=true"
                    print "----", str(currentHeatingSetPoint) + degree_symbol, "(current)|color=", \
                        numberToColorGrad(0,"red")
                    for c in range(currentHeatingSetPoint - 1, currentHeatingSetPoint - 6, -1):
                        print "----", str(c) + degree_symbol, buildFontOptions(3), "color=gray", \
                            "bash=" + callbackScript, " param1=request param2=" + str(
                            heatingSetpointURL + str(c)), " param3=" + secret, " terminal=false refresh=true"

# Output Temp Sensors
sensorName = "Temps"
countSensors = len(temps)
if countSensors > 0:
    hortSeparatorBar()
    menuTitle = "Temp Sensors"
    mainTitle = menuTitle
    if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
    print "{} {}".format(mainTitle, buildFontOptions())
    colorSwitch = False
    mainMenuMaxItems = mainMenuMaxItemsDict[sensorName]
    subMenuText = ''
    for i, sensor in enumerate(temps):
        currentLength = len(sensor['name'])
        extraLength = maxLength - currentLength
        whiteSpace = ''
        for x in range(0, extraLength): whiteSpace += ' '
        colorText = ''
        currentValue = formatter.formatNumber(sensor['value'])
        colorText = 'color=#333333' if colorSwitch else 'color=#666666'
        if i == mainMenuMaxItems:
            # noinspection PyTypeChecker
            print "{} More...{}".format(countSensors - mainMenuMaxItems, buildFontOptions(2))
            if not subMenuCompact:
                # noinspection PyTypeChecker
                print "--{} ({})".format(menuTitle,str(countSensors - mainMenuMaxItems)), buildFontOptions()
            subMenuText = "--"
        print subMenuText, sensor['name'], whiteSpace, currentValue + degree_symbol, \
            buildFontOptions(3), colorText

        eventGroupByDate(
            [d for d in sensor['eventlog'] if d['name'] in "temperature"], subMenuText, "°"
        )

#        for event in sensor['eventlog']:
#            if event['name'] == 'temperature':
#                print subMenuText + '--' + event['date'], \
#                    '{:>3}'.format(formatter.formatNumber(float(event['value']))) \
#                    + degree_symbol, buildFontOptions(3)

        if sensor['battery'] != 'N/A':
            if sensor['battery'][1] != "": colorText = "color=red"
            print subMenuText, sensor['name'], whiteSpace, formatPercentage(
                sensor['battery'][0]) + sensor['battery'][1], buildFontOptions(3) + " alternate=true", colorText
        colorSwitch = not colorSwitch

# Output Modes
if len(modes) > 0:
    hortSeparatorBar()
    if currentmode['name'] == "Home":
        emoji = " :house: "
    else:
        emoji = ""
    print "Current House Mode: {} {}".format(emoji + currentmode['name'], buildFontOptions())
    print "--Modes (Select to Change)" + buildFontOptions()
    for i, mode in enumerate(modes):
        colorText = ''
        colorText = 'color=#333333' if colorSwitch else 'color=#666666'
        if mode['name'] not in currentmode['name']:
            currentModeURL = modeURL + urllib.quote(mode['name'].encode('utf8'))
            print "--• " + mode[
                'name'], buildFontOptions(3), colorText, ' bash=', callbackScript, ' param1=request param2=', \
                currentModeURL, ' param3=', secret, ' terminal=false refresh=true'
        colorSwitch = not colorSwitch

# Output Routines
if len(routines) > 0:
    print "--Routines (Select to Run)" + buildFontOptions()
    for i, routine in enumerate(routines):
        colorText = ''
        colorText = 'color=#333333' if colorSwitch else 'color=#666666'
        currentRoutineURL = routineURL+urllib.quote(routine.encode('utf8'))
        print "--• " + routine, buildFontOptions(3), colorText, ' bash=', callbackScript, ' param1=request param2=', \
            currentRoutineURL, ' param3=', secret, ' terminal=false refresh=true'
        colorSwitch = not colorSwitch

# Output Smart Home Monitor
if shmDisplayBool:
    colorText = ''
    for i, alarm in enumerate(alarms):
        if alarm['name'] == 'shm':
            shmCurrentState = alarm['value']
# Verify the SHM is configured:
    if shmCurrentState != "unconfigured":
        print "--Smart Home Monitor (Select to Change)" + buildFontOptions()
        for alarmState in alarmStates:
            colorText = 'color=#333333' if colorSwitch else 'color=#666666'
            if alarmState == shmCurrentState:
                currentAlarmStateDisplay = " (Current)"
                currentAlarmURL = ""
            else:
                currentAlarmURL = alarmURL + alarmState
                currentAlarmStateDisplay = ""
                currentAlarmURL = 'bash= ' + callbackScript + ' param1=request param2=' + currentAlarmURL + \
                ' param3=' + secret + ' terminal=false refresh=true'
            print "--• {}{}".format(alarmState.title(), currentAlarmStateDisplay), buildFontOptions(3), \
                colorText, currentAlarmURL
            colorSwitch = not colorSwitch

# Output Contact Sensors
sensorName = "Contacts"
countSensors = len(contacts)
if countSensors > 0:
    hortSeparatorBar()
    menuTitle = "Contact Sensors"
    subMenuTitle = "More..."
    mainTitle = menuTitle
    if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
    print mainTitle, buildFontOptions()
    mainMenuMaxItems = mainMenuMaxItemsDict[sensorName]
    subMenuText = ''
    for i, sensor in enumerate(contacts):
        currentLength = len(sensor['name'])
        extraLength = maxLength - currentLength
        whiteSpace = ''
        for x in range(0, extraLength): whiteSpace += ' '
        sym = ''
        if sensor['value'] == 'closed':
            sym = contactClosedEmoji
            if mainMenuAutoSizeDict[sensorName] is True:
                if mainMenuMaxItems > i: mainMenuMaxItems = i
                subMenuTitle = "More Contact Sensors Closed..."
        else:
            sym = contactOpenEmoji
        colorText = 'color=#333333' if colorSwitch else 'color=#666666'
        if i == mainMenuMaxItems:
            print "{} {} {}".format(countSensors - mainMenuMaxItems, subMenuTitle, buildFontOptions(2))
            if not subMenuCompact: print "--{} ({})".format(menuTitle,str(countSensors - mainMenuMaxItems)), \
                buildFontOptions()
            subMenuText = "--"
        print subMenuText, sensor['name'], whiteSpace, sym, buildFontOptions(3), colorText
        eventGroupByDate(
            [d for d in sensor['eventlog'] if d['name'] in ['status','contact','acceleration']],
            subMenuText, ""
        )
        if sensor['battery'] != 'N/A':
            if sensor['battery'][1] != "": colorText = "color=red"
            print subMenuText, sensor['name'], whiteSpace, formatPercentage(
                sensor['battery'][0]) + sensor['battery'][1], buildFontOptions(3) + "alternate=true", colorText
        colorSwitch = not colorSwitch

# Output Motion Sensors
sensorName = "Motion"
countSensors = len(motion)
if countSensors > 0:
    hortSeparatorBar()
    menuTitle = "Motion Sensors"
    subMenuTitle = "More..."
    mainTitle = menuTitle
    if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
    print mainTitle, buildFontOptions()
    mainMenuMaxItems = mainMenuMaxItemsDict[sensorName]
    subMenuText = ''
    for i, sensor in enumerate(motion):
        currentLength = len(sensor['name'])
        extraLength = maxLength - currentLength
        whiteSpace = ''
        for x in range(0, extraLength): whiteSpace += ' '
        sym = ''
        if sensor['value'] == 'inactive':
            sym = motionInactiveEmoji
            if mainMenuAutoSizeDict[sensorName] is True:
                if mainMenuMaxItems > i: mainMenuMaxItems = i
                subMenuTitle = "More Sensors Inactive..."
        else:
            sym = motionActiveEmoji
        colorText = 'color=#333333' if colorSwitch else 'color=#666666'
        if i == mainMenuMaxItems:
            print "{} {} {}".format(countSensors - mainMenuMaxItems, subMenuTitle, buildFontOptions(2))
            if not subMenuCompact: print "-- " + menuTitle + " (" + str(countSensors - mainMenuMaxItems) + ")"
            subMenuText = "--"
        print subMenuText, sensor['name'], whiteSpace, sym, buildFontOptions(3), colorText

        eventGroupByDate(
            [d for d in sensor['eventlog'] if d['name'] in 'motion'],
            subMenuText, ""
        )

#        for event in sensor['eventlog']:
#            if event['name'] == 'motion':
#                sym = motionInactiveEmoji if event['value'] == 'inactive' else motionActiveEmoji
#                print subMenuText + '--' + event['date'], sym, buildFontOptions(3)
        if sensor['battery'] != 'N/A':
            if sensor['battery'][1] != "": colorText = "color=red"
            print subMenuText, sensor['name'], whiteSpace, formatPercentage(
                sensor['battery'][0]) + sensor['battery'][1], buildFontOptions(3), " alternate=true", colorText
        colorSwitch = not colorSwitch

# Output Presence Sensors
sensorName = "Presences"
countSensors = len(presences)
if countSensors > 0:
    hortSeparatorBar()
    menuTitle = "Presence Sensors"
    subMenuTitle = "More..."
    mainTitle = menuTitle
    if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
    print mainTitle, buildFontOptions()
    mainMenuMaxItems = mainMenuMaxItemsDict[sensorName]
    subMenuText = ''
    notPresentMenuText = ''
    notPresentSubmenu = False
    for i, sensor in enumerate(presences):
        currentLength = len(sensor['name'])
        extraLength = maxLength - currentLength
        whiteSpace = ''
        for x in range(0, extraLength): whiteSpace += ' '
        sym = ''
        if sensor['value'] == 'present':
            emoji = presenscePresentEmoji
        else:
            emoji = presensceNotPresentEmoji
            if mainMenuAutoSizeDict[sensorName] is True:
                if mainMenuMaxItems > i: mainMenuMaxItems = i
                subMenuTitle = "More Sensors Not Present..."
        # Only show the More... menu if there is no presence submenu
        if i == mainMenuMaxItems and notPresentSubmenu is False:
            print "{} {} {}".format(countSensors - mainMenuMaxItems, subMenuTitle, buildFontOptions(2))
            if not subMenuCompact: print "--{} ({}) {}".format(
                menuTitle, str(countSensors - mainMenuMaxItems), buildFontOptions()
            )
            subMenuText = "--"
        # If the presence mode is show not present in submenu
        if presenceDisplayMode == 2 and sensor['value'] != 'present':
            # If this is the first not present sensor
            if not notPresentSubmenu:
                print subMenuText, subMenuTitle, buildFontOptions()
                notPresentSubmenu = True
            # Set the submenu text
            notPresentMenuText = "--"
        colorText = 'color=#333333' if colorSwitch else 'color=#666666'
        print subMenuText + notPresentMenuText, sensor['name'], whiteSpace, emoji, buildFontOptions(3), colorText

        eventGroupByDate(
            [d for d in sensor['eventlog'] if d['name'] in 'presence'],
            subMenuText, ""
        )

        if sensor['battery'] != 'N/A':
            if sensor['battery'][1] != "": colorText = "color=red"
            print subMenuText + notPresentMenuText, sensor['name'], whiteSpace, formatPercentage(
                sensor['battery'][0]) + sensor['battery'][1], buildFontOptions(3) + " alternate=true", colorText
        colorSwitch = not colorSwitch

# Set base64 images for green locked/red unlocked
# noinspection SpellCheckingInspection
greenLocked = ("iVBORw0KGgoAAAANSUhEUgAAABsAAAAbCAYAAACN1PRVAAAACXBIWXMAABYlAAAWJQFJUiTwAAAKT2lDQ1BQaG90b3Nob3Ag"
               "SUNDIHByb2ZpbGUAAHjanVNnVFPpFj333vRCS4iAlEtvUhUIIFJCi4AUkSYqIQkQSoghodkVUcERRUUEG8igiAOOjoCMFVEsDIoK2"
               "AfkIaKOg6OIisr74Xuja9a89+bN/rXXPues852zzwfACAyWSDNRNYAMqUIeEeCDx8TG4eQuQIEKJHAAEAizZCFz/SMBAPh+PDwrIsA"
               "HvgABeNMLCADATZvAMByH/w/qQplcAYCEAcB0kThLCIAUAEB6jkKmAEBGAYCdmCZTAKAEAGDLY2LjAFAtAGAnf+bTAICd+Jl7AQBb"
               "lCEVAaCRACATZYhEAGg7AKzPVopFAFgwABRmS8Q5ANgtADBJV2ZIALC3AMDOEAuyAAgMADBRiIUpAAR7AGDIIyN4AISZABRG8lc88"
               "SuuEOcqAAB4mbI8uSQ5RYFbCC1xB1dXLh4ozkkXKxQ2YQJhmkAuwnmZGTKBNA/g88wAAKCRFRHgg/P9eM4Ors7ONo62Dl8t6r8G/y"
               "JiYuP+5c+rcEAAAOF0ftH+LC+zGoA7BoBt/qIl7gRoXgugdfeLZrIPQLUAoOnaV/Nw+H48PEWhkLnZ2eXk5NhKxEJbYcpXff5n"
               "wl/AV/1s+X48/Pf14L7iJIEyXYFHBPjgwsz0TKUcz5IJhGLc5o9H/LcL//wd0yLESWK5WCoU41EScY5EmozzMqUiiUKSKcUl0v9k4"
               "t8s+wM+3zUAsGo+AXuRLahdYwP2SycQWHTA4vcAAPK7b8HUKAgDgGiD4c93/+8//UegJQCAZkmScQAAXkQkLlTKsz/HCAAARKCBKr"
               "BBG/TBGCzABhzBBdzBC/xgNoRCJMTCQhBCCmSAHHJgKayCQiiGzbAdKmAv1EAdNMBRaIaTcA4uwlW4Dj1wD/phCJ7BKLyBCQRByA"
               "gTYSHaiAFiilgjjggXmYX4IcFIBBKLJCDJiBRRIkuRNUgxUopUIFVIHfI9cgI5h1xGupE7yAAygvyGvEcxlIGyUT3UDLVDuag3Go"
               "RGogvQZHQxmo8WoJvQcrQaPYw2oefQq2gP2o8+Q8cwwOgYBzPEbDAuxsNCsTgsCZNjy7EirAyrxhqwVqwDu4n1Y8+xdwQSgUXACT"
               "YEd0IgYR5BSFhMWE7YSKggHCQ0EdoJNwkDhFHCJyKTqEu0JroR+cQYYjIxh1hILCPWEo8TLxB7iEPENyQSiUMyJ7mQAkmxpFTSEt"
               "JG0m5SI+ksqZs0SBojk8naZGuyBzmULCAryIXkneTD5DPkG+Qh8lsKnWJAcaT4U+IoUspqShnlEOU05QZlmDJBVaOaUt2ooVQRNY9"
               "aQq2htlKvUYeoEzR1mjnNgxZJS6WtopXTGmgXaPdpr+h0uhHdlR5Ol9BX0svpR+iX6AP0dwwNhhWDx4hnKBmbGAcYZxl3GK+YTKYZ"
               "04sZx1QwNzHrmOeZD5lvVVgqtip8FZHKCpVKlSaVGyovVKmqpqreqgtV81XLVI+pXlN9rkZVM1PjqQnUlqtVqp1Q61MbU2epO6iHq"
               "meob1Q/pH5Z/YkGWcNMw09DpFGgsV/jvMYgC2MZs3gsIWsNq4Z1gTXEJrHN2Xx2KruY/R27iz2qqaE5QzNKM1ezUvOUZj8H45hx+Jx"
               "0TgnnKKeX836K3hTvKeIpG6Y0TLkxZVxrqpaXllirSKtRq0frvTau7aedpr1Fu1n7gQ5Bx0onXCdHZ4/OBZ3nU9lT3acKpxZNPTr1r"
               "i6qa6UbobtEd79up+6Ynr5egJ5Mb6feeb3n+hx9L/1U/W36p/VHDFgGswwkBtsMzhg8xTVxbzwdL8fb8VFDXcNAQ6VhlWGX4YSRudE"
               "8o9VGjUYPjGnGXOMk423GbcajJgYmISZLTepN7ppSTbmmKaY7TDtMx83MzaLN1pk1mz0x1zLnm+eb15vft2BaeFostqi2uGVJsuRap"
               "lnutrxuhVo5WaVYVVpds0atna0l1rutu6cRp7lOk06rntZnw7Dxtsm2qbcZsOXYBtuutm22fWFnYhdnt8Wuw+6TvZN9un2N/T0HDYf"
               "ZDqsdWh1+c7RyFDpWOt6azpzuP33F9JbpL2dYzxDP2DPjthPLKcRpnVOb00dnF2e5c4PziIuJS4LLLpc+Lpsbxt3IveRKdPVxXeF60"
               "vWdm7Obwu2o26/uNu5p7ofcn8w0nymeWTNz0MPIQ+BR5dE/C5+VMGvfrH5PQ0+BZ7XnIy9jL5FXrdewt6V3qvdh7xc+9j5yn+M+4zw"
               "33jLeWV/MN8C3yLfLT8Nvnl+F30N/I/9k/3r/0QCngCUBZwOJgUGBWwL7+Hp8Ib+OPzrbZfay2e1BjKC5QRVBj4KtguXBrSFoyOyQr"
               "SH355jOkc5pDoVQfujW0Adh5mGLw34MJ4WHhVeGP45wiFga0TGXNXfR3ENz30T6RJZE3ptnMU85ry1KNSo+qi5qPNo3ujS6P8YuZln"
               "M1VidWElsSxw5LiquNm5svt/87fOH4p3iC+N7F5gvyF1weaHOwvSFpxapLhIsOpZATIhOOJTwQRAqqBaMJfITdyWOCnnCHcJnIi/RN"
               "tGI2ENcKh5O8kgqTXqS7JG8NXkkxTOlLOW5hCepkLxMDUzdmzqeFpp2IG0yPTq9MYOSkZBxQqohTZO2Z+pn5mZ2y6xlhbL+xW6Lty8"
               "elQfJa7OQrAVZLQq2QqboVFoo1yoHsmdlV2a/zYnKOZarnivN7cyzytuQN5zvn//tEsIS4ZK2pYZLVy0dWOa9rGo5sjxxedsK4xUFK"
               "4ZWBqw8uIq2Km3VT6vtV5eufr0mek1rgV7ByoLBtQFr6wtVCuWFfevc1+1dT1gvWd+1YfqGnRs+FYmKrhTbF5cVf9go3HjlG4dvyr+Z"
               "3JS0qavEuWTPZtJm6ebeLZ5bDpaql+aXDm4N2dq0Dd9WtO319kXbL5fNKNu7g7ZDuaO/PLi8ZafJzs07P1SkVPRU+lQ27tLdtWHX+G7"
               "R7ht7vPY07NXbW7z3/T7JvttVAVVN1WbVZftJ+7P3P66Jqun4lvttXa1ObXHtxwPSA/0HIw6217nU1R3SPVRSj9Yr60cOxx++/p3vd"
               "y0NNg1VjZzG4iNwRHnk6fcJ3/ceDTradox7rOEH0x92HWcdL2pCmvKaRptTmvtbYlu6T8w+0dbq3nr8R9sfD5w0PFl5SvNUyWna6YL"
               "Tk2fyz4ydlZ19fi753GDborZ752PO32oPb++6EHTh0kX/i+c7vDvOXPK4dPKy2+UTV7hXmq86X23qdOo8/pPTT8e7nLuarrlca7nue"
               "r21e2b36RueN87d9L158Rb/1tWeOT3dvfN6b/fF9/XfFt1+cif9zsu72Xcn7q28T7xf9EDtQdlD3YfVP1v+3Njv3H9qwHeg89HcR/c"
               "GhYPP/pH1jw9DBY+Zj8uGDYbrnjg+OTniP3L96fynQ89kzyaeF/6i/suuFxYvfvjV69fO0ZjRoZfyl5O/bXyl/erA6xmv28bCxh6+yX"
               "gzMV70VvvtwXfcdx3vo98PT+R8IH8o/2j5sfVT0Kf7kxmTk/8EA5jz/GMzLdsAAAAgY0hSTQAAeiUAAICDAAD5/wAAgOkAAHUwAADq"
               "YAAAOpgAABdvkl/FRgAAAG1JREFUeNpi/P//PwO9AAsyR5KBEZc6YlyEVfNzJK1MRBhCrNcJqmOikkVEqWeiQdT8JyrOiNDESInvSf"
               "EZI4niNAtGRmJ8y8RARzBqGfWLKwLJmNwMzjgaZ6OWjVo2atmoZSPRMgAAAAD//wMAW3URM0dIvkIAAAAASUVORK5CYII=")
# noinspection SpellCheckingInspection
redUnlocked = ("iVBORw0KGgoAAAANSUhEUgAAABsAAAAbCAYAAACN1PRVAAAACXBIWXMAABYlAAAWJQFJUiTwAAAKT2lDQ1BQaG90b3Nob3AgSUND"
               "IHByb2ZpbGUAAHjanVNnVFPpFj333vRCS4iAlEtvUhUIIFJCi4AUkSYqIQkQSoghodkVUcERRUUEG8igiAOOjoCMFVEsDIoK2AfkI"
               "aKOg6OIisr74Xuja9a89+bN/rXXPues852zzwfACAyWSDNRNYAMqUIeEeCDx8TG4eQuQIEKJHAAEAizZCFz/SMBAPh+PDwrIsAHvg"
               "ABeNMLCADATZvAMByH/w/qQplcAYCEAcB0kThLCIAUAEB6jkKmAEBGAYCdmCZTAKAEAGDLY2LjAFAtAGAnf+bTAICd+Jl7AQBblCE"
               "VAaCRACATZYhEAGg7AKzPVopFAFgwABRmS8Q5ANgtADBJV2ZIALC3AMDOEAuyAAgMADBRiIUpAAR7AGDIIyN4AISZABRG8lc88Su"
               "uEOcqAAB4mbI8uSQ5RYFbCC1xB1dXLh4ozkkXKxQ2YQJhmkAuwnmZGTKBNA/g88wAAKCRFRHgg/P9eM4Ors7ONo62Dl8t6r8G/yJi"
               "YuP+5c+rcEAAAOF0ftH+LC+zGoA7BoBt/qIl7gRoXgugdfeLZrIPQLUAoOnaV/Nw+H48PEWhkLnZ2eXk5NhKxEJbYcpXff5nwl/A"
               "V/1s+X48/Pf14L7iJIEyXYFHBPjgwsz0TKUcz5IJhGLc5o9H/LcL//wd0yLESWK5WCoU41EScY5EmozzMqUiiUKSKcUl0v9k4t8s+"
               "wM+3zUAsGo+AXuRLahdYwP2SycQWHTA4vcAAPK7b8HUKAgDgGiD4c93/+8//UegJQCAZkmScQAAXkQkLlTKsz/HCAAARKCBKrBBG/T"
               "BGCzABhzBBdzBC/xgNoRCJMTCQhBCCmSAHHJgKayCQiiGzbAdKmAv1EAdNMBRaIaTcA4uwlW4Dj1wD/phCJ7BKLyBCQRByAgTYSHai"
               "AFiilgjjggXmYX4IcFIBBKLJCDJiBRRIkuRNUgxUopUIFVIHfI9cgI5h1xGupE7yAAygvyGvEcxlIGyUT3UDLVDuag3GoRGogvQZHQ"
               "xmo8WoJvQcrQaPYw2oefQq2gP2o8+Q8cwwOgYBzPEbDAuxsNCsTgsCZNjy7EirAyrxhqwVqwDu4n1Y8+xdwQSgUXACTYEd0IgYR5BS"
               "FhMWE7YSKggHCQ0EdoJNwkDhFHCJyKTqEu0JroR+cQYYjIxh1hILCPWEo8TLxB7iEPENyQSiUMyJ7mQAkmxpFTSEtJG0m5SI+ksqZs"
               "0SBojk8naZGuyBzmULCAryIXkneTD5DPkG+Qh8lsKnWJAcaT4U+IoUspqShnlEOU05QZlmDJBVaOaUt2ooVQRNY9aQq2htlKvUYeoE"
               "zR1mjnNgxZJS6WtopXTGmgXaPdpr+h0uhHdlR5Ol9BX0svpR+iX6AP0dwwNhhWDx4hnKBmbGAcYZxl3GK+YTKYZ04sZx1QwNzHrmOe"
               "ZD5lvVVgqtip8FZHKCpVKlSaVGyovVKmqpqreqgtV81XLVI+pXlN9rkZVM1PjqQnUlqtVqp1Q61MbU2epO6iHqmeob1Q/pH5Z/YkGW"
               "cNMw09DpFGgsV/jvMYgC2MZs3gsIWsNq4Z1gTXEJrHN2Xx2KruY/R27iz2qqaE5QzNKM1ezUvOUZj8H45hx+Jx0TgnnKKeX836K3hTv"
               "KeIpG6Y0TLkxZVxrqpaXllirSKtRq0frvTau7aedpr1Fu1n7gQ5Bx0onXCdHZ4/OBZ3nU9lT3acKpxZNPTr1ri6qa6UbobtEd79up+"
               "6Ynr5egJ5Mb6feeb3n+hx9L/1U/W36p/VHDFgGswwkBtsMzhg8xTVxbzwdL8fb8VFDXcNAQ6VhlWGX4YSRudE8o9VGjUYPjGnGXOMk"
               "423GbcajJgYmISZLTepN7ppSTbmmKaY7TDtMx83MzaLN1pk1mz0x1zLnm+eb15vft2BaeFostqi2uGVJsuRaplnutrxuhVo5WaVYVV"
               "pds0atna0l1rutu6cRp7lOk06rntZnw7Dxtsm2qbcZsOXYBtuutm22fWFnYhdnt8Wuw+6TvZN9un2N/T0HDYfZDqsdWh1+c7RyFDpW"
               "Ot6azpzuP33F9JbpL2dYzxDP2DPjthPLKcRpnVOb00dnF2e5c4PziIuJS4LLLpc+Lpsbxt3IveRKdPVxXeF60vWdm7Obwu2o26/uN"
               "u5p7ofcn8w0nymeWTNz0MPIQ+BR5dE/C5+VMGvfrH5PQ0+BZ7XnIy9jL5FXrdewt6V3qvdh7xc+9j5yn+M+4zw33jLeWV/MN8C3yLf"
               "LT8Nvnl+F30N/I/9k/3r/0QCngCUBZwOJgUGBWwL7+Hp8Ib+OPzrbZfay2e1BjKC5QRVBj4KtguXBrSFoyOyQrSH355jOkc5pDoVQ"
               "fujW0Adh5mGLw34MJ4WHhVeGP45wiFga0TGXNXfR3ENz30T6RJZE3ptnMU85ry1KNSo+qi5qPNo3ujS6P8YuZlnM1VidWElsSxw5L"
               "iquNm5svt/87fOH4p3iC+N7F5gvyF1weaHOwvSFpxapLhIsOpZATIhOOJTwQRAqqBaMJfITdyWOCnnCHcJnIi/RNtGI2ENcKh5O8k"
               "gqTXqS7JG8NXkkxTOlLOW5hCepkLxMDUzdmzqeFpp2IG0yPTq9MYOSkZBxQqohTZO2Z+pn5mZ2y6xlhbL+xW6Lty8elQfJa7OQrAV"
               "ZLQq2QqboVFoo1yoHsmdlV2a/zYnKOZarnivN7cyzytuQN5zvn//tEsIS4ZK2pYZLVy0dWOa9rGo5sjxxedsK4xUFK4ZWBqw8uIq2"
               "Km3VT6vtV5eufr0mek1rgV7ByoLBtQFr6wtVCuWFfevc1+1dT1gvWd+1YfqGnRs+FYmKrhTbF5cVf9go3HjlG4dvyr+Z3JS0qavEuW"
               "TPZtJm6ebeLZ5bDpaql+aXDm4N2dq0Dd9WtO319kXbL5fNKNu7g7ZDuaO/PLi8ZafJzs07P1SkVPRU+lQ27tLdtWHX+G7R7ht7vPY0"
               "7NXbW7z3/T7JvttVAVVN1WbVZftJ+7P3P66Jqun4lvttXa1ObXHtxwPSA/0HIw6217nU1R3SPVRSj9Yr60cOxx++/p3vdy0NNg1VjZ"
               "zG4iNwRHnk6fcJ3/ceDTradox7rOEH0x92HWcdL2pCmvKaRptTmvtbYlu6T8w+0dbq3nr8R9sfD5w0PFl5SvNUyWna6YLTk2fyz4yd"
               "lZ19fi753GDborZ752PO32oPb++6EHTh0kX/i+c7vDvOXPK4dPKy2+UTV7hXmq86X23qdOo8/pPTT8e7nLuarrlca7nuer21e2b36R"
               "ueN87d9L158Rb/1tWeOT3dvfN6b/fF9/XfFt1+cif9zsu72Xcn7q28T7xf9EDtQdlD3YfVP1v+3Njv3H9qwHeg89HcR/cGhYPP/pH1"
               "jw9DBY+Zj8uGDYbrnjg+OTniP3L96fynQ89kzyaeF/6i/suuFxYvfvjV69fO0ZjRoZfyl5O/bXyl/erA6xmv28bCxh6+yXgzMV70"
               "VvvtwXfcdx3vo98PT+R8IH8o/2j5sfVT0Kf7kxmTk/8EA5jz/GMzLdsAAAAgY0hSTQAAeiUAAICDAAD5/wAAgOkAAHUwAADqYAAAOp"
               "gAABdvkl/FRgAAAG1JREFUeNrslMEOgCAMQ+nC//9yPXjRBOM6lAvdjWTL61oAJNuq6rcT8NSXUTQeviwTSVFI9LwKCsGFaWBIppNT"
               "wC7BzkxRyLOwWd3ez2DpbaMtLMN++K6Eayy8NzgzwwwzzLAdYQcAAAD//wMAsSkPOUNoFPgAAAAASUVORK5CYII=")

# Output Locks
sensorName = "Locks"
countSensors = len(locks)
if countSensors > 0:
    hortSeparatorBar()
    menuTitle = sensorName
    subMenuTitle = "More..."
    mainTitle = menuTitle
    if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
    print mainTitle, buildFontOptions()
    mainMenuMaxItems = mainMenuMaxItemsDict[sensorName]
    subMenuText = ''
    for i, sensor in enumerate(locks):
        currentLockURL = lockURL + sensor['id']
        currentLength = len(sensor['name'])
        extraLength = maxLength - currentLength
        whiteSpace = ''
        img = ''
        sym = ''
        for x in range(0, extraLength): whiteSpace += ' '
        if sensor['value'] == 'locked':
            sym = '🔒'
            img = greenLocked
            if mainMenuAutoSizeDict[sensorName] is True:
                if mainMenuMaxItems > i: mainMenuMaxItems = i
                subMenuTitle = "More Locked..."
        elif sensor['value'] == 'unlocked':
            sym = '🔓'
            img = redUnlocked
        elif sensor['value'] is None:
            sensor['name'] = sensor['name'] + "(No Status)"
        else:
            sensor['name'] = sensor['name'] + "(" + str(sensor['value']) + ")"
        if i == mainMenuMaxItems:
            print "{} {} {}".format(countSensors - mainMenuMaxItems, subMenuTitle, buildFontOptions(2))
            if not subMenuCompact: print "--{} ({}) {}".format(
                menuTitle, str(countSensors - mainMenuMaxItems), buildFontOptions()
            )
            subMenuText = "--"
        colorText = 'color=#333333' if colorSwitch else 'color=#666666'
        if useImages is True:
            print subMenuText, sensor['name'], buildFontOptions(3) + colorText + ' bash=', \
                callbackScript, ' param1=request param2=', \
                currentLockURL, ' param3=', secret, ' terminal=false refresh=true image=', img
        else:
            print subMenuText, sensor['name'], whiteSpace, sym, buildFontOptions(3) + colorText + 'bash=', \
                callbackScript, ' param1=request param2=', currentLockURL, ' param3=', \
                secret, ' terminal=false refresh=true'
        eventGroupByDate(
            [d for d in sensor['eventlog'] if d['value'] in ['locked','armed', 'unlocked', 'disarmed']],
            subMenuText, ""
        )
#        for event in sensor['eventlog']:
#            if event['value'] in ['locked','armed', 'unlocked', 'disarmed']:
#                if event['value'] in ['locked', 'armed']:
#                    emoji = ':closed_lock_with_key:'
#                else:
#                    emoji = ':door:'
#                print subMenuText + "--" + event['date'], emoji, buildFontOptions(3)
        if sensor['battery'] != 'N/A':
            if sensor['battery'][1] != "": colorText = "color=red"
            if useImages is True:
                print subMenuText, sensor['name'], whiteSpace, formatPercentage(
                    sensor['battery'][0]) + sensor['battery'][1], \
                    buildFontOptions(3) + " alternate=true", colorText, "image=" + img
            else:
                print subMenuText, sensor['name'], whiteSpace, sym, formatPercentage(
                    sensor['battery'][0]) + sensor['battery'][1], \
                    buildFontOptions(3) + " alternate=true", colorText
        colorSwitch = not colorSwitch


# Set base64 images for status green/red
greenImage = ("iVBORw0KGgoAAAANSUhEUgAAABsAAAAbCAYAAACN1PRVAAAACXBIWXMAABR0AAAUdAG5O1bwAAAKT2lDQ1BQaG90b3Nob3AgSUNDI"
              "HByb2ZpbGUAAHjanVNnVFPpFj333vRCS4iAlEtvUhUIIFJCi4AUkSYqIQkQSoghodkVUcERRUUEG8igiAOOjoCMFVEsDIoK2AfkIaK"
              "Og6OIisr74Xuja9a89+bN/rXXPues852zzwfACAyWSDNRNYAMqUIeEeCDx8TG4eQuQIEKJHAAEAizZCFz/SMBAPh+PDwrIsAHvgABeN"
              "MLCADATZvAMByH/w/qQplcAYCEAcB0kThLCIAUAEB6jkKmAEBGAYCdmCZTAKAEAGDLY2LjAFAtAGAnf+bTAICd+Jl7AQBblCEVAaCRA"
              "CATZYhEAGg7AKzPVopFAFgwABRmS8Q5ANgtADBJV2ZIALC3AMDOEAuyAAgMADBRiIUpAAR7AGDIIyN4AISZABRG8lc88SuuEOcqAAB4"
              "mbI8uSQ5RYFbCC1xB1dXLh4ozkkXKxQ2YQJhmkAuwnmZGTKBNA/g88wAAKCRFRHgg/P9eM4Ors7ONo62Dl8t6r8G/yJiYuP+5c+rcEA"
              "AAOF0ftH+LC+zGoA7BoBt/qIl7gRoXgugdfeLZrIPQLUAoOnaV/Nw+H48PEWhkLnZ2eXk5NhKxEJbYcpXff5nwl/AV/1s+X48/Pf14L"
              "7iJIEyXYFHBPjgwsz0TKUcz5IJhGLc5o9H/LcL//wd0yLESWK5WCoU41EScY5EmozzMqUiiUKSKcUl0v9k4t8s+wM+3zUAsGo+AXuRL"
              "ahdYwP2SycQWHTA4vcAAPK7b8HUKAgDgGiD4c93/+8//UegJQCAZkmScQAAXkQkLlTKsz/HCAAARKCBKrBBG/TBGCzABhzBBdzBC/x"
              "gNoRCJMTCQhBCCmSAHHJgKayCQiiGzbAdKmAv1EAdNMBRaIaTcA4uwlW4Dj1wD/phCJ7BKLyBCQRByAgTYSHaiAFiilgjjggXmYX4Ic"
              "FIBBKLJCDJiBRRIkuRNUgxUopUIFVIHfI9cgI5h1xGupE7yAAygvyGvEcxlIGyUT3UDLVDuag3GoRGogvQZHQxmo8WoJvQcrQaPYw"
              "2oefQq2gP2o8+Q8cwwOgYBzPEbDAuxsNCsTgsCZNjy7EirAyrxhqwVqwDu4n1Y8+xdwQSgUXACTYEd0IgYR5BSFhMWE7YSKggHCQ0"
              "EdoJNwkDhFHCJyKTqEu0JroR+cQYYjIxh1hILCPWEo8TLxB7iEPENyQSiUMyJ7mQAkmxpFTSEtJG0m5SI+ksqZs0SBojk8naZGuyBzm"
              "ULCAryIXkneTD5DPkG+Qh8lsKnWJAcaT4U+IoUspqShnlEOU05QZlmDJBVaOaUt2ooVQRNY9aQq2htlKvUYeoEzR1mjnNgxZJS6Wt"
              "opXTGmgXaPdpr+h0uhHdlR5Ol9BX0svpR+iX6AP0dwwNhhWDx4hnKBmbGAcYZxl3GK+YTKYZ04sZx1QwNzHrmOeZD5lvVVgqtip8FZ"
              "HKCpVKlSaVGyovVKmqpqreqgtV81XLVI+pXlN9rkZVM1PjqQnUlqtVqp1Q61MbU2epO6iHqmeob1Q/pH5Z/YkGWcNMw09DpFGgsV/j"
              "vMYgC2MZs3gsIWsNq4Z1gTXEJrHN2Xx2KruY/R27iz2qqaE5QzNKM1ezUvOUZj8H45hx+Jx0TgnnKKeX836K3hTvKeIpG6Y0TLkxZV"
              "xrqpaXllirSKtRq0frvTau7aedpr1Fu1n7gQ5Bx0onXCdHZ4/OBZ3nU9lT3acKpxZNPTr1ri6qa6UbobtEd79up+6Ynr5egJ5Mb6fe"
              "eb3n+hx9L/1U/W36p/VHDFgGswwkBtsMzhg8xTVxbzwdL8fb8VFDXcNAQ6VhlWGX4YSRudE8o9VGjUYPjGnGXOMk423GbcajJgYmIS"
              "ZLTepN7ppSTbmmKaY7TDtMx83MzaLN1pk1mz0x1zLnm+eb15vft2BaeFostqi2uGVJsuRaplnutrxuhVo5WaVYVVpds0atna0l1rutu"
              "6cRp7lOk06rntZnw7Dxtsm2qbcZsOXYBtuutm22fWFnYhdnt8Wuw+6TvZN9un2N/T0HDYfZDqsdWh1+c7RyFDpWOt6azpzuP33F9JbpL"
              "2dYzxDP2DPjthPLKcRpnVOb00dnF2e5c4PziIuJS4LLLpc+Lpsbxt3IveRKdPVxXeF60vWdm7Obwu2o26/uNu5p7ofcn8w0nymeWTNz"
              "0MPIQ+BR5dE/C5+VMGvfrH5PQ0+BZ7XnIy9jL5FXrdewt6V3qvdh7xc+9j5yn+M+4zw33jLeWV/MN8C3yLfLT8Nvnl+F30N/I/9k/3"
              "r/0QCngCUBZwOJgUGBWwL7+Hp8Ib+OPzrbZfay2e1BjKC5QRVBj4KtguXBrSFoyOyQrSH355jOkc5pDoVQfujW0Adh5mGLw34MJ4WH"
              "hVeGP45wiFga0TGXNXfR3ENz30T6RJZE3ptnMU85ry1KNSo+qi5qPNo3ujS6P8YuZlnM1VidWElsSxw5LiquNm5svt/87fOH4p3iC+N"
              "7F5gvyF1weaHOwvSFpxapLhIsOpZATIhOOJTwQRAqqBaMJfITdyWOCnnCHcJnIi/RNtGI2ENcKh5O8kgqTXqS7JG8NXkkxTOlLOW5hC"
              "epkLxMDUzdmzqeFpp2IG0yPTq9MYOSkZBxQqohTZO2Z+pn5mZ2y6xlhbL+xW6Lty8elQfJa7OQrAVZLQq2QqboVFoo1yoHsmdlV2a/z"
              "YnKOZarnivN7cyzytuQN5zvn//tEsIS4ZK2pYZLVy0dWOa9rGo5sjxxedsK4xUFK4ZWBqw8uIq2Km3VT6vtV5eufr0mek1rgV7ByoLB"
              "tQFr6wtVCuWFfevc1+1dT1gvWd+1YfqGnRs+FYmKrhTbF5cVf9go3HjlG4dvyr+Z3JS0qavEuWTPZtJm6ebeLZ5bDpaql+aXDm4N2dq"
              "0Dd9WtO319kXbL5fNKNu7g7ZDuaO/PLi8ZafJzs07P1SkVPRU+lQ27tLdtWHX+G7R7ht7vPY07NXbW7z3/T7JvttVAVVN1WbVZftJ+7"
              "P3P66Jqun4lvttXa1ObXHtxwPSA/0HIw6217nU1R3SPVRSj9Yr60cOxx++/p3vdy0NNg1VjZzG4iNwRHnk6fcJ3/ceDTradox7rOEH"
              "0x92HWcdL2pCmvKaRptTmvtbYlu6T8w+0dbq3nr8R9sfD5w0PFl5SvNUyWna6YLTk2fyz4ydlZ19fi753GDborZ752PO32oPb++6EH"
              "Th0kX/i+c7vDvOXPK4dPKy2+UTV7hXmq86X23qdOo8/pPTT8e7nLuarrlca7nuer21e2b36RueN87d9L158Rb/1tWeOT3dvfN6b/fF9"
              "/XfFt1+cif9zsu72Xcn7q28T7xf9EDtQdlD3YfVP1v+3Njv3H9qwHeg89HcR/cGhYPP/pH1jw9DBY+Zj8uGDYbrnjg+OTniP3L96fy"
              "nQ89kzyaeF/6i/suuFxYvfvjV69fO0ZjRoZfyl5O/bXyl/erA6xmv28bCxh6+yXgzMV70VvvtwXfcdx3vo98PT+R8IH8o/2j5sfVT0"
              "Kf7kxmTk/8EA5jz/GMzLdsAAAAgY0hSTQAAeiUAAICDAAD5/wAAgOkAAHUwAADqYAAAOpgAABdvkl/FRgAABMRJREFUeNq0lktoXVU"
              "Uhr+19z733HvTpM+kLypJqVId9CmK+EB0pCAd6EChtJOCk+JAEBGFTtSRdOBQnDhSKg5EHPkqaCkG2wZbB60ttmmTNG3uvUlucnPPO"
              "Xvv5eAmsa8oavtz1jmc1/r3Wvtfey85cLqbG5GkIFZQBWNAEt3gi/C4L/yTRVt3h0w3xEAqBm9TriepOZOU7DHnkqNgLkQfgxjF5xA"
              "LiDmodnw7loBNpN/HfN/0aLa3uFa+302upVL0UY5VjFpUIt5km1pybddkz8S+pHem1rO+9HlaTj+OXk/cyafcKTKbykvNydY7rd+r"
              "2/tmd7Cpso3e5Rvpri7HOYcYAVVCiMzMTXNtcozL02cYTU6Sbpm8umpj5QPflg9DTnFjZLeTlfWN+sjcIXthoGvniufZsKYfV7JE9f"
              "hQoAt/AiKCNQ5rHb5QJupjDI1/y9S6X+ndmn4SC/NazJheJNt/fBkIuFSwKW/Wh9vvpxcfMI/1v0BXpYsiZsQYAAVkqaxjjMGZEsEHh"
              "i79xEj3MdY86D6jMPtipOjMmS58zIvTo/nb4Xyf2TnwNLiCqWwcRW6m0DuTLTwWY3jovl2EywXj535+efWW9DyBQ6pEh4CxbMxm47u"
              "Ns3RvW7MDSTzNvAYiS3tdCgHaIgys3crUyBhTXZcOdq9Of4ie710sEIQDjeF8a0VXs2xZF82sjv6j1yUgnQE5m7ChZzPnroyuKFfj6y"
              "Jm0GlkfdFkX7uurKlWKbRN0LAohMWz3mnGZP6QeRJFUUSEwhtc6nCTPbRq9eeqK0u7nAZ9ot3UzQbLbKxxceo3Ulum5CokNsGIQzCL"
              "xMLNgwjRkxdtWsUMbd8kaiB1Xayo9GLFEU2On8GUl+mLLuQ85dvgEkOQjIn2JQTBiMPZhNRWKLkKThJEBEWJMRDw5L5N5ucoYoFqQOh"
              "EORsmaRbXscZSSI7xFp/xiPM5u4hgEkGMYCkBEFUJZMyGNrOhgYj8Jf35dClgjOCMQSS5WUca8HhsYju6yehzsdD1RoDklrpBAHuDC"
              "PW2t38Pc9Nd9FpxGijfMqglRCb8H6giLkYKl3LPEXJwsaAmFTaJFYj3gGU+IX5OMxdzPYPKDpdAvEdkGiBk2nAh48eQsbfUAybcAy"
              "4LeVPxGWdc9BzNmjQqvaw0CXc3lbJABiHnS6PKxXwqHimanW1GnGDuktlUCBm06zqkQb9zGjSPno+mL8c95dV2nUtB412KykBzJIZ8"
              "Vg/bEg0TCohwslXTw43zAevAJJ3wzX8wsWAcuArMjESal/ULEY6oB9v/jJtf0XVwrqYDIrK9e6PB2PmVzvwLk076XEVoXlHGT4UTwA"
              "HjpC5yQ3clghc4eO10cCHnlbU7LWl3pxhjuL1ubt1IxYCdL5/62cjVU/4Ugf02ZXixY+t/1i3+qJFMI1/PXNHYuh53J1UpVVYJSbXj"
              "7FYzrkPgKp1rq66MDUbGh8KnBF41jnOd1Aoit5OB4oGjrev8Mj0ce+YmdKsGsCWwZek0RqV5xQE+g5nRyPhQZGwwDE4Px7eM5T3jqIl"
              "ZmMcO2dJNaolvQpvjtXPx4cYfcU+pSx4tdUtf0kXVJiIxKEWLdt7URjGjp33OVxo5ahImZIk1+88BAGVAXOCp+O+MAAAAAElFTkSuQ"
              "mCC")
redImage = ("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")

# Output Switches
sensorName = "Switches"
countSensors = len(switches)
if countSensors > 0:
    hortSeparatorBar()
    menuTitle = sensorName
    mainTitle = menuTitle
    subMenuTitle = "More..."
    if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
    print mainTitle, buildFontOptions()
    mainMenuMaxItems = mainMenuMaxItemsDict[sensorName]
    subMenuText = ''
    for i, sensor in enumerate(switches):
        indent = ""
        currentLength = len(sensor['name'])
        extraLength = maxLength - currentLength
        whiteSpace = ''
        img = ''
        for x in range(0, extraLength): whiteSpace += ' '
        if sensor['value'] == 'on':
            sym = '🔛'
            img = greenImage
        else:
            sym = '🔴'
            img = redImage
            if mainMenuAutoSizeDict[sensorName] is True:
                if mainMenuMaxItems > i: mainMenuMaxItems = i
                subMenuTitle = "More Switches Off..."
        currentSwitchURL = contactURL + sensor['id']
        colorText = 'color=#333333' if colorSwitch else 'color=#666666'
        if i == mainMenuMaxItems:
            print "{} {} {}".format(countSensors - mainMenuMaxItems, subMenuTitle, buildFontOptions())
            if not subMenuCompact: print "--{} ({}) {}".format(
                menuTitle, str(countSensors - mainMenuMaxItems), buildFontOptions(2)
            )
            subMenuText = "--"
        if useImages is True:
            print subMenuText, sensor[
                'name'], buildFontOptions(3) + colorText + ' bash=', callbackScript, ' param1=request param2=', \
                currentSwitchURL, ' param3=', secret, ' terminal=false refresh=true image=', img
        else:
            print subMenuText, sensor[
                'name'], whiteSpace, sym, buildFontOptions(3) + colorText + ' bash=', callbackScript, \
                ' param1=request param2=', currentSwitchURL, ' param3=', secret, ' terminal=false refresh=true'
        if sensor['isDimmer'] is True:
            subMenuText = subMenuText + '--'
            print subMenuText + 'Set Dimmer Level', buildFontOptions(3), smallFontPitchSize
            currentLevel = 10
            while True:
                currentLevelURL = levelURL + sensor['id'] + '&level=' + str(currentLevel)
                print subMenuText + " {}%".format(currentLevel), buildFontOptions(3), 'bash=', callbackScript, \
                    ' param1=request param2=', currentLevelURL, ' param3=', secret, ' terminal=false refresh=true'
                if currentLevel is 100:
                    break
                currentLevel += 10
            subMenuText = subMenuText[:-2]
            print subMenuText + "-- Event History", buildFontOptions(3)
            indent = '--'
        colorSwitch = not colorSwitch

        eventGroupByDate(
            [d for d in sensor['eventlog'] if d['name'] in ['door', 'switch']],
            subMenuText + indent, ""
        )


# Output MusicPlayers
sensorName = "MusicPlayers"
countSensors = len(musicplayers)
if countSensors > 0:
    hortSeparatorBar()
    menuTitle = "Music Players"
    mainTitle = menuTitle
    subMenuTitle = "More Music Players..."
    if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
    print mainTitle, buildFontOptions()
    mainMenuMaxItems = mainMenuMaxItemsDict[sensorName]
    subMenuText = ''
    musicplayers = sorted(musicplayers, key=lambda x: x['name'], reverse=False)
    for i, sensor in enumerate(sorted(musicplayers, key=lambda x: x['groupBool'], reverse=False)):
        currentLength = len(sensor['name'])
        extraLength = maxLength - currentLength
        whiteSpace = ''
        img = ''
        for x in range(0, extraLength): whiteSpace += ' '
        if sensor['trackData']['status'] == 'playing':
            sym = '🔛'
            img = greenImage
        else:
            sym = '🔴'
            img = redImage
            if mainMenuAutoSizeDict[sensorName] is True:
                if mainMenuMaxItems > i: mainMenuMaxItems = i
                subMenuTitle = "More Music Players Inactive..."
        colorText = 'color=#333333' if colorSwitch else 'color=#666666'
        if i == mainMenuMaxItems:
            print "{} {} {}".format(countSensors - mainMenuMaxItems, subMenuTitle, buildFontOptions())
            if not subMenuCompact: print "--{} ({}) {}".format(
                menuTitle, str(countSensors - mainMenuMaxItems), buildFontOptions(2)
            )
            subMenuText = "--"
        if sensor['groupBool']: sensor['name'] += " - {}{}".format('Grouped',sensor['trackDescription'][1])
        if useImages is True:
            print subMenuText, sensor['name'], buildFontOptions(3) + colorText, 'image=', img
        else:
            print subMenuText, sensor['name'], whiteSpace, sym, buildFontOptions(3) + colorText
        if sensor['level'] is not None:
            print "{}--*Volume Level: ({})".format(subMenuText, sensor['level']), buildFontOptions(3)
            print "{}----Set Music Level".format(subMenuText), buildFontOptions(3), smallFontPitchSize
            currentLevel = 0
            while currentLevel <=100:
                currentMusicPlayerURL = musicplayerURL + sensor['id'] + '&command=' + 'level'
                print "{}----{}".format(subMenuText,currentLevel), \
                    buildFontOptions(3), 'bash=' + callbackScript, 'param1=request param2=' \
                   + currentMusicPlayerURL, ' param3=' + secret, ' terminal=false refresh=true'
                currentLevel += 10
        if sensor['mute'] is not None:
            command = "mute" if sensor['mute'] is "unmuted" else "unmute"
            print "{}--*Mute : {}".format(subMenuText, TitleCase(sensor['mute'])), \
            buildFontOptions(3), 'bash=' + callbackScript, 'param1=request param2=' + musicplayerURL + \
            sensor['id'] + '&command=' + command, ' param3=' + secret, 'terminal=false refresh=true'
        if sensor['trackDescription'] is not None:
#           Check for Music Player playing a Streaming Live Radio Station
            m = re.search('^x-sonosapi-hls:(.+)\?', sensor['trackDescription'][0])
            if m:
                sensor['trackDescription'][0] = m.group(1)
            else:
                sensor['trackDescription'][0] = sensor['trackDescription'][0].replace('\n', ' ')
            print "{}--{}  {}".format(
                subMenuText, "Track:", sensor['trackDescription'][0]), buildFontOptions(3), "font=9"
        if sensor["trackData"] is not None:
                for key, value in sensor["trackData"].items():
                    if key in ["album", "status", "name", "artist", "station", "trackNumber"]:
                        if value is not None:
                            print "{}--{}: {}".format(subMenuText, TitleCase(key), TitleCase(value)), \
                                buildFontOptions(3)
        colorSwitch = not colorSwitch

# Configuration Options
hortSeparatorBar()
print "STBitBarApp Actions and Shortcuts" + buildFontOptions()
print "--Your Current Running Program Version Information" + buildFontOptions()
print "----BitBar Output App v" + j['Version'] + buildFontOptions()
print "----ST_Python_Logic.py v{:1.2f}".format(PythonVersion) + buildFontOptions()
print "----BitBar Plugin GUI Options" + buildFontOptions()
print "------" + sys.argv[0] + buildFontOptions()
printFormatString = "------{:" + len(max(options, key=len)).__str__() + "} = {} {}"
for option in sorted(options.iterkeys()):
    print printFormatString.format(
        option, options[option] if options[option] is not None else "{Default Set in GUI}", buildFontOptions(3)
    )
print "--Launch TextEdit " + cfgFileName + buildFontOptions() + openParamBuilder(
    "open -e " + cfgFileName) + ' terminal=false'
print "--Launch SmartThings IDE" + buildFontOptions() + openParamBuilder(
    "open " + buildIDEURL(smartAppURL)) + ' terminal=false'
print "--Launch Browser to View STBitBarAPP-V2 " + j['Version'] + " GitHub Software Resp" \
      + buildFontOptions() + openParamBuilder(
    "open https://github.com/kurtsanders/STBitBarApp-V2") + ' terminal=false'
print "--Download ST_Python_Logic.py v{:1.2f}".format(PythonVersion) \
      + " to your 'Downloads' directory " + buildFontOptions(),\
    "bash="+callbackScript, ' param1=github_ST_Python_Logic terminal=false'
print "--Download ST.5m.sh to your 'Downloads' directory " + buildFontOptions(), \
    "bash="+callbackScript, ' param1=github_ST5MSH terminal=false'

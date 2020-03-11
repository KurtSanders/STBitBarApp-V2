#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigParser
import decimal
import json
import locale
import os
import re
import subprocess
# noinspection PyUnresolvedReferences
import sys
import tempfile
import urllib
import urllib2
from urlparse import urlparse

reload(sys)
sys.setdefaultencoding('utf8')
locale.setlocale(locale.LC_ALL, '')

##################################
# Set Required SmartApp Version as Decimal, ie 2.0, 2.1, 2.12...
# Supports all minor changes in BitBar 2.1, 2.2, 2.31...
PythonVersion = 4.00  # Must be float or Int

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
        try:
            r = round(float(number), self.decimalRounding)
        except (ValueError, TypeError, AttributeError):
            return 0
        if r % 1 == 0: return 0
        return abs(decimal.Decimal(str(r)).as_tuple().exponent)

    # noinspection PyShadowingNames
    def formatNumber(self, number):
        try:
            r = round(float(number), self.decimalRounding)
        except (ValueError, TypeError, AttributeError):
            return number
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


colorHueList = {
        "Orange"    : 10,
        "Warm White": 20,
        "Soft White": 23,
        "Yellow"    : 25,
        "Green"     : 39,
        "White"     : 52,
        "Daylight"  : 53,
        "Blue"      : 69,
        "DarkBlue"  : 70,
        "Purple"    : 75,
        "Pink"      : 83,
        "Red"       : 100,
        "Cyan"      : 180
}

def getHueLevel(colorMatch):
    return "{} ({})".format(colorMatch, colorHueList.get(colorMatch, None))

def getColorNameHue(hueValue):
    for k, v in colorHueList.iteritems():
        if hueValue == v:
            return k
    return None

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
smartAppURL = cfgGetValue('smartAppURL', "", True).strip('\'"')
secret = cfgGetValue('secret', "", True).strip('\'"')
header = {"Authorization": "Bearer " + secret}

# Version Information of ST BitBar Plugin File
STPluginFilename_argPosition = 1
STPluginVersion_argPosition = 2

try:
    STPluginVersion = sys.argv[STPluginVersion_argPosition]
except IndexError:
    STPluginVersion = None

try:
    STPluginFilename = os.path.basename(sys.argv[STPluginFilename_argPosition])
except IndexError:
    STPluginFilename = None

# Set URLs
statusURL = smartAppURL + "GetStatus/?pythonAppVersion=" + "{:0.2f}".format(PythonVersion) + "&path=" + sys.argv[0] + "&bbpluginfilename=" + STPluginFilename + "&bbpluginversion=" + STPluginVersion
contactURL = smartAppURL + "ToggleSwitch/?id="
valveURL = smartAppURL + "ToggleValve/?id="
levelURL = smartAppURL + "SetLevel/?id="
colorURL = smartAppURL + "SetColor/?id="
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
# Create the urllib2 Request
request = urllib2.Request(statusURL, None, header)
# Getting the response
try:
    response = urllib2.urlopen(request)
except (urllib2.HTTPError, urllib2.URLError) as err:
    print ":rage:"
    print "---"
    print ":thumbsdown: HTTPS Error Encountered: Communicating to ST API caused the following error: {}".format(
        str(err))
    print "==> Please check your Internet Connectivity and Refresh BitBar again when Online"
    exit(99)

# Check for Return Code Status
# noinspection PyUnboundLocalVariable
if response.code != 200:
    print ":rage:"
    print '---'
    print ":thumbsdown: Error Communicating with ST API, HTTPS rc={}".format(response.code)
    print "Content:", response.content
    exit(99)

# Parse the JSON data
j = json.loads(response.read())

# API Return Error Handling
if "error" in j:
    print ":rage:"
    print '---'
    if j['error'] == 'invalid_token':
        print ":thumbsdown: Please verify that both the SmartApp URL and Secret in ST_Python_Logic.cfg are correct."
        print " Please re-try again after verification of these strings."
    print "Error Details: ", j['error']
    if "error_description" in j:
        print ":thumbsdown: Error Description: ", j['error_description']
    exit(99)

# Verify SmartApp and local app version
try:
    majorBitBarVersion = int(j['Version'].encode('ascii').split('.')[0])
    majorPythonVersion = int(PythonVersion)
    if majorBitBarVersion != majorPythonVersion:
        print ":rage:"
        print "---"
        print "Both ST_Python_Logic.py and BitBar Output SmartApp must be on same MAJOR release levels of {}.xx | color=red".format(max(majorBitBarVersion, majorPythonVersion))
        print "Current BitBar Output SmartAPP Version: {}".format(j['Version'])
        print "Current ST_Python_Logic.py Version    : {}".format(PythonVersion)
        print "Current ST BitBar Plugin Version      : {}".format(STPluginVersion)
        print "---"
        print "Launch TextEdit " + cfgFileName + '|' + openParamBuilder("open -e " + cfgFileName) + ' terminal=false'
        print "Launch SmartThings IDE" + '|' + openParamBuilder("open " + buildIDEURL(smartAppURL)) + ' terminal=false'
        print "Launch Browser to View STBitBarAPP-V2 GitHub Software Resp" + '|' + openParamBuilder(
            "open https://github.com/kurtsanders/STBitBarApp-V2") + ' terminal=false'
        print "Download ST_Python_Logic.py v{:1.2f}".format(PythonVersion) + " to your 'Downloads' directory | ", \
            " bash=" + callbackScript, ' param1=github_ST_Python_Logic terminal=false'
        print "Download ST.5m.sh to your 'Downloads' directory |", " bash=" + callbackScript, ' param1=github_ST5MSH terminal=false'

        raise SystemExit(0)
except KeyError, e:
    print "Error in ST API Data | color=red"
    print "---"
    print "Error Details: ", e
    raise SystemExit(0)

# Get the sensor arrays from the JSON data
# print json.dumps(j['Motion Sensors'], indent=2)
# exit(99)
try:
    alarms = j['Alarm Sensors']
    temps = j['Temp Sensors']
    contacts = j['Contact Sensors']
    switches = j['Switches']
    motion = j['Motion Sensors']
    mainDisplay = j['MainDisplay']
    musicplayers = j['Music Players']
    locks = j['Locks']
    relativeHumidityMeasurements = j['RelativeHumidityMeasurements']
    presences = j['Presence Sensors']
    thermostats = j['Thermostats']
    routines = j['Routines']
    modes = j['Modes']
    currentmode = j['CurrentMode']
    options = j['Options']
    waters = j['Waters']
    valves = j['Valves']

except KeyError, e:
    print ":rage:"
    print "---"
    print ":thumbsdown: Json File Error Details: ", e
    exit(99)

# noinspection PyShadowingNames
def eventGroupByDate(tempList, prefix=None, valueSuffix=""):
    strLen = len(tempList)
    if strLen == 0: return
    # noinspection PyShadowingNames
    for x in range(0, strLen):
        curSplitRecord = tempList[x]['date'].split()
        if x == 0:
            print "--{}{} {} {}".format(
                prefix, curSplitRecord[0], curSplitRecord[1], curSplitRecord[2]
            ), buildFontOptions(3)
            sys.stdout.write("--")
        elif curSplitRecord[2] == tempList[x - 1]['date'].split()[2]:
            sys.stdout.write("--")
        else:
            print "--{}{} {} {}".format(
                prefix, curSplitRecord[0], curSplitRecord[1], curSplitRecord[2]
            ), buildFontOptions(3)
            sys.stdout.write("--")
        if tempList[x]['value'] is not None: tempList[x]['value'] = tempList[x]['value'].replace('\n', '')
        try:
            tempList[x]['value'] = "{} ({:4.1f})".format(tempList[x]['name'].title(), float(tempList[x]['value']))
        except (ValueError, TypeError, AttributeError):
            pass
        if eventsTimeFormat == "12 Hour Clock Format with AM/PM":
            print "--{}{} {} {} = {}{}".format(
                prefix, curSplitRecord[3], curSplitRecord[4], curSplitRecord[5], tempList[x]['value'], valueSuffix), \
                buildFontOptions(4)
        else:
            print "--{}{} {} = {}{}".format(
                prefix, curSplitRecord[3], curSplitRecord[4], tempList[x]['value'], valueSuffix), buildFontOptions(4)
    return

# Set User Display Options sent from BitBar Output SmartApp
useImages = getOptions("useImages", True)
sortSensorsName = getOptions("sortSensorsName", True)
subMenuCompact = getOptions("subMenuCompact", False)
sortSensorsActive = getOptions("sortSensorsActive", True)
showSensorCount = getOptions("showSensorCount", True)
motionActiveEmoji = getOptions("motionActiveEmoji", '⇠⇢')
motionInactiveEmoji = getOptions("motionInactiveEmoji", '⇢⇠')
contactOpenEmoji = getOptions("contactOpenEmoji", '⇠⇢')
contactClosedEmoji = getOptions("contactClosedEmoji", '⇢⇠')
presenscePresentEmoji = getOptions("presenscePresentEmoji", ':house:')
presensceNotPresentEmoji = getOptions("presensceNotPresentEmoji", ':x:')
presenceDisplayMode = getOptions("presenceDisplayMode", 0)
mainFontName = "'{}'".format(getOptions("mainFontName", "Menlo"))
mainFontSize = getOptions("mainFontSize", "14").__str__()
fixedPitchFontSize = getOptions("fixedPitchFontSize", "14").__str__()
fixedPitchFontName = "'{}' ".format(getOptions("fixedPitchFontName", "Menlo"))
fixedPitchFontColor = getOptions("fixedPitchFontColor", "Black")
subMenuFontName = "'{}'".format(getOptions("subMenuFontName", "Monaco"))
subMenuFontSize = getOptions("subMenuFontSize", "14").__str__()
subMenuFontColor = getOptions("subMenuFontColor", "Black")
subMenuMoreColor = getOptions("subMenuMoreColor", "black")
hortSeparatorBarBool = getOptions("hortSeparatorBarBool", True)
shmDisplayBool = getOptions("shmDisplayBool", True)
eventsTimeFormat = getOptions("eventsTimeFormat", "12 Hour Clock Format with AM/PM")
sortTemperatureAscending = getOptions("sortTemperatureAscending", False)
favoriteDevices = getOptions("favoriteDevices", None)
colorChoices = getOptions("colorChoices", None)
colorBulbEmoji = getOptions("colorBulbEmoji", "🌈")
dimmerBulbEmoji = getOptions("dimmerBulbEmoji", "🔆")
dimmerValueOnMainMenu = getOptions("dimmerValueOnMainMenu", False)

# Read Temperature Formatting Settings
numberOfDecimals = verifyInteger(getOptions("numberOfDecimals", "0"), 0)

matchOutputNumberOfDecimals = getOptions("matchOutputNumberOfDecimals", False)
colorSwitch = True
smallFontPitchSize = "size={}".format(int(fixedPitchFontSize) - 1)
alarmStates = ['away', 'off', 'stay']

# Generates a Horizontal Separator Bar if desired by GUI
def hortSeparatorBar():
    if hortSeparatorBarBool: print "---"
    return

# Check if MacOS is in Dark Mode
# noinspection PyBroadException
try:
    if not subprocess.call("defaults read -g AppleInterfaceStyle  > /dev/null 2>&1", shell=True):
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
        return " | font={} size={} color={} ".format(subMenuFontName, subMenuFontSize, subMenuFontColor)
    # Level 2: SubMenu More Text
    elif level == 2:
        return " | font={} size={} color={} ".format(subMenuFontName, subMenuFontSize, subMenuMoreColor)
    # Level 3: Data Fixed Pitch Text
    elif level == 3:
        return " | font={} size={} color={} ".format(fixedPitchFontName, fixedPitchFontSize,
                                                     fixedPitchFontColor)
    # Level 4: Data Fixed Pitch Text, Trim=False
    elif level == 4:
        return " | font={} trim={} size={} color={} ".format(fixedPitchFontName, False, fixedPitchFontSize,
                                                             fixedPitchFontColor)
    # Level >4: No Formatting
    else:
        return " | "

# Setup the Main Menu and Sub Menu Display Relationship
mainMenuMaxItemsDict = {
        "Temps"                       : None,
        "MusicPlayers"                : None,
        "Contacts"                    : None,
        "Switches"                    : None,
        "Motion"                      : None,
        "Locks"                       : None,
        "Valves"                      : None,
        "Waters"                      : None,
        "RelativeHumidityMeasurements": None,
        "Presences"                   : None
}
mainMenuAutoSizeDict = {}
# mainMenuAutoSize = False

for sensorName in mainMenuMaxItemsDict:
    mainMenuMaxItemsDict[sensorName] = options.get("mainMenuMaxItems" + sensorName, None)
    if mainMenuMaxItemsDict[sensorName] is None:
        mainMenuMaxItemsDict[sensorName] = 999
        mainMenuAutoSizeDict[sensorName] = True
    #        mainMenuAutoSize = True
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
    relativeHumidityMeasurements = sorted(relativeHumidityMeasurements, key=lambda k: k[sortkey])
    presences = sorted(presences, key=lambda k: k[sortkey])
    modes = sorted(modes, key=lambda k: k[sortkey])
    routines = sorted(routines)

    if favoriteDevices is not None:
        favoriteDevicesBool = True
        favoriteDevices = sorted(favoriteDevices, cmp=locale.strcoll)
    else:
        favoriteDevicesBool = False

# if sortSensorsActive is True or mainMenuAutoSize is True:
if sortSensorsActive is True:
    sortkey = 'value'
    temps = sorted(temps, key=lambda k: k[sortkey], reverse=sortTemperatureAscending)
    contacts = sorted(contacts, key=lambda k: k[sortkey], reverse=True)
    switches = sorted(switches, key=lambda k: k[sortkey], reverse=True)
    motion = sorted(motion, key=lambda k: k[sortkey], reverse=True)
    locks = sorted(locks, key=lambda k: k[sortkey], reverse=True)
    relativeHumidityMeasurements = sorted(relativeHumidityMeasurements, key=lambda k: k[sortkey])
    presences = sorted(presences, key=lambda k: k[sortkey], reverse=True)
    musicplayers = sorted(musicplayers, key=lambda k: k['status'])

# Presence sort mode by status or in submenu, sort by value desc
if presenceDisplayMode == 1 or presenceDisplayMode == 2:
    presences = sorted(presences, key=lambda k: k['value'], reverse=True)

# Presence display mode only show present sensors
if presenceDisplayMode == 3:
    presences = filter(lambda p: p['value'] == 'present', presences)

# Create a new NumberFormatter object
formatter = NumberFormatter()
# Set the number of decimals
formatter.setRoundingPrecision(numberOfDecimals)

# Format thermostat status color
thermoColor = ''
if (thermostats is not None) and (len(thermostats) > 0):
    if "thermostatOperatingState" in thermostats[0]:
        if thermostats[0]['thermostatOperatingState'] == "heating":
            thermoColor += "color=red"
        if thermostats[0]['thermostatOperatingState'] == "cooling":
            thermoColor += "color=blue"

# Print the main display
degree_symbol = u'\xb0'.encode('utf-8')
formattedMainDisplay = u''
mainMenuColor = ""
getImageString = {
        "shmaway"          : "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",
        "shmstay"          : "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",
        "shmoff"      : "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",
        "greenImage"    : "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",
        "redImage"      : "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",
        "thermoImage"   : "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",
        "locked"        : "iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAAAXNSR0IArs4c6QAAAIRlWElmTU0AKgAAAAgABQESAAMAAAABAAEAAAEaAAUAAAABAAAASgEbAAUAAAABAAAAUgEoAAMAAAABAAIAAIdpAAQAAAABAAAAWgAAAAAAAABIAAAAAQAAAEgAAAABAAOgAQADAAAAAQABAACgAgAEAAAAAQAAABmgAwAEAAAAAQAAABkAAAAAq8n6XQAAAAlwSFlzAAALEwAACxMBAJqcGAAAAVlpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KTMInWQAABgtJREFUSA11VklslVUU/u4/vqG0pQNTMRAgYShUYzciKo1DtIlRGi04sECDG9OyILo0Ni50Q7oAXZiQ6AITTMOkJFXZ1AQcFhBToEKDCQktpLQF2tf2vX+8fue+V6mgp/3fzT333O9M99xzVU9Pj3X58mUFUl9fs24/eMTt33ctkPmOr2prsajQrpVuV9CbtcIjZNdTeBIaNzTUJaVVPwqL+k++c++e7Gk/uM7v37c76uwsYzY3N2vV2dlpj4+Pq8aBRo3eX72+/SPFtrY2p7b77IdQSZebxwplAUmokcYwn+UA8tkeVadANIubKrUP3f38qQMDAwNxZ+/KLPZvDcfbiNvYWFaCPppQUdBxtGpj6s4e9WvQEhcJGurIVvVaKd+C1lQnKgmtVKp1kCZ6Ulmecp0MEExjEMX8m6d2zwzNK0IndwA9VmfvYV88eOVYdpuF0hknj2w8q8R25aomN8Ioigmtl6BqfhxTjlkbcNGESI9GCpZ28tqjVyUdZ57/blfxnCjq2783UOUYXgsqHlxwfGTiEAGt9h3VgIl4Aj5Bl7iPIdRTxLepJ4GnanA7+gMBlTU4DYj1BJ1Tge3BT0IUVZhvPfHGzJ9tPaszYhskBzXdP59n/FviOSoAFdDCO/EoHq9+C12tn6ChalnFDdkhpDAxM4Yvzn+M89NHUOc0IabH5AdODj49Gpw6tL1VcsT4ApJkkwNRoOFDuwyNi+tMdMe6vVjVsBZhHGC6NIXZYMaMYVwifw12rHvXyFnKo22uhNOPZxH61Wip6Tr7geBb5pjyFEmSKWCUks2Yx0gYCs/2RQ6f/bIPK06vxK6flptR5kIu4yNyqY44q2ynO7SBRyTpFnxH6kCOaTQDkaIpIhjCUTksY2IlyUI5uxovZ4FGbxuqrHPI27WGryggciIf65A82Z+6aYjIrSJuWmh3tKVfUmUg1hbPvU64oRGFZBi/F6iOp0DoVukqTs8Am/xzGGLWmjJXDT9MAiPX4AwjYzVS0ThhqEhrHnsOxHeU1lsS+sBqZh2kVLAU9+IxJvxtvL9hB1bVrZEwYs/Gj9BR6mKuJJQpajKLDX9V3Vqc3tqHn0dO4kLhG9TaS6lojBFgsJhTwVevHlfjlo0GHUvtupZnNeFi8TqOt13EhuWbqZfVQu9smyX+ACVJYpQqFtCVW5fQMbAFLdnVCNMRSsapcpSVJpiQANYzx2KsZTGukb6DOsY45+UNM5a7hHEXwLlgDsNjQyhylLmQWedmka/nvkjfpRM5gye4pHpRMqloJMMnNnN0y6clpWNkSmIZXnpio//KMaz/vtmMMhe+rMt/Snk5ZQrisfB5XZSdn7QUb1O57JgTogqZ/FOaYg+QATQbH14TVPOJDyTBE1xOb1iEvGTz4HKS/sdWs6ArG59c/Sy28CKUUajML4NWGGYwOMRjCYmxF+mJ6qfXYgSduk9azgFpIU88ebr6Rf5SurIwv25CV7FSeAZPIp6qHxxpOJE1ddPysAKhirjqyg3rGvcoxLBZ/JOY11c14sBzx+E6njnGtrIZ47IxIi/7BJ7WRrxlXOkzgm9JR5OG42R5gjCtHVWLAvf9Ncli4yaxUOpClIgHvps1o8yFL+siJ/Kyz+HtnKCgHd69mrgGX3Tfv4V1SzKXDWJd9OWkPLG4m5WTJZD4TUGDJ8p4KCtzqe4oLeK3u4dgk+eobGDniryF1eDUa7yFMRA/0E/mLth+mtFhNkh1yR+J2DkIXMH731HAV7pUrTKB8mhgYJWQ5FpP7ZwZqvSTBZ3xW3ZGNzjj5NJsMrsozFhNgu8adHHZeEKlwp0n8khRKR3Vdr7AzmiVrMR/4cTO4tl/OqM8JB7u8XNH/eq0JeJ1LbcpQQRKCnf+k2zPf+zxcF3T49UgEvZ4erCwx9t8sljjS8ZV/sv1SXPvdObYexO3lt/efth7dKTIpG7yqlQtk2jzfpJEsMQYFkcp21eWm1O27So7KVk345L96dTrz+z5sW94bF6BvFby+TzUg++utp6vvYGe6/Th3+8uOrOZYTPvLi6Zd5cUmtTBwneX5GCgZ0+48N31NzvBByhuT+gZAAAAAElFTkSuQmCC",
        "unlocked"      : "iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAAAXNSR0IArs4c6QAAAIRlWElmTU0AKgAAAAgABQESAAMAAAABAAEAAAEaAAUAAAABAAAASgEbAAUAAAABAAAAUgEoAAMAAAABAAIAAIdpAAQAAAABAAAAWgAAAAAAAABIAAAAAQAAAEgAAAABAAOgAQADAAAAAQABAACgAgAEAAAAAQAAABmgAwAEAAAAAQAAABkAAAAAq8n6XQAAAAlwSFlzAAALEwAACxMBAJqcGAAAAVlpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KTMInWQAABn1JREFUSA1tVltsFFUY/s9lZna2N9uyNUihWgWNDQoqAaTGVRMMUR98WFBCxMQEFRKMMeqLUfQNvCQYbYLx3UBjolHEeEu9JMolgAaMJd6A5WKXdu3udndnZ+Ycv392G+vlJCdn5sw53/ff/xE7duyQJ0+eFIQxOjRkc3jeVSg4V42N1Xnvu3UrO+crd4WwZrmStIhIpIls1RpxmqQ8lo+CI6sOHCzx2d+y2dQzmUw4i8N7Q8AUuVxOFQoFMYaNPUvKors4KNaPjja+X5ft75HxE0LYDWmlFvpg4GExE4mw1mKDGZ81VuytG7V78YGx/Ovr1nnewgnz6KkOm8WZTCbTJBkFyb5MQY4UMmZsbCzK3zO8haTY1ePoLoAwkAF01KTAzYSG6az2pZa+VlRshKXI0tMD+795K5vN6q3AWw+8HJMQzLXn/AfqHTAnBPcNj/Q4zuPlKKLQ2AB4EuJrSD+rALBBoB1M19o4xMGGcZT0OrSmqSAc6d//zTYmerBcFo8ODhrJPmATzRL0ue7jU40wioyF5OQJS0AjLE09rIVSqTayUUjm/LigoOoIv92LYhPxvb6UuxWWeJPxugcHRQ731P6+Pm/4o48CNlGP67x4CQd5vzWxzBlM4Ppkxz8jkj6ppcNkpybI/PA1iQXXSIpjMRObuMdzVm4Z7L+w5r2PD7091JVKTMBO7tXxCUdQF2vAxpgD3XyEiYTnkwGB98hO6tr0MDnzMhSVSlTa/z7Vdm4mMXgniTCItJIaOKVqrIc4GJKQ4ShiJ7MP/pcAThEwkcmfIH3fk9Sz/Smijk4qfPUlRfBd78aHyN36BtkTXxD57TqMTdDtOp0p4LKEkvOAw5SjiJ38t3fxlR3Ms+Vze+gipe+9n6RS9PsLzyMv7qBfNm6gsFYj7667qfozAAkmlVIyHuMyvu7X3i1pKRZW4whfhWbIBNjxSAAseZZQWGkSS7B0XUZRo0HB0SPk3z5M4SefU8wkvb1UwVX1Z5nS7Sldi0LD+TWf3BWajFnuOw5VYxFBC8QkaABozxwkc2YGkQRqDoNOovgUOMMGNgTZPy6APxGJyuM/EXASfStVmJbqIpXWYUoptxqFyxD/doCFx3VM0EADe/5H8re9Ru7SG4nCsAnK5sR0FvSThFDdzz5Hk5s2kVq9gs7duiZBUDfdQLYRULlmIIBPvd0uUO2AhhfSTXmYAyTslQJsf9da8geuZAsnEmI3EcNAYo6WeWvX0iSqGBPLNaugSQyCEAkFNGCUJ2tUcx0IpNpgLltlgObAk8EhLoFBkBAY2J9iJPW5POn5C0h6HjuW4jrqZ2cnWZwXOGtBItiMAOJVQJJysUZ1T81IHDk9S5HIyoywzGycSdeluFikC4uvpfofF0midCRAHAxR0FITl1oECRa0YaOwUjOV+hkZC3GcqykGJyDfbw1ma422Nqo9sJ4UcmPOgeRj89S/d5NjOkCFkFIdkxfixuEqyrWvlES55AiDFpgQg69aOF66Hg3sfJkckBkkXzJYTA3TJfh/C9R6ijzOFWPyNekeltxwLPoBSHBBIA5RdGvQHu8cuRxJju9T+6JF5KTTiG7ECvYFVrqIXpX0mf9oYnyYE0LvXXXwYCmpUdxw0A+2OEJ0RiaO5IKrdendvVS8bikZaJLYlzM4EQQEiJra+DjR5e1NXyDieDS1EBHywpuO49K0cHcn+9wyudWeRhXOeM6eqaARQVxF+UOierRGSV9tAcyVl7VRK29OzMlStMzERoy7tdbF2D627MjRPftWr/aT9ntbpaK3HzjA5f5N7gcT9SDiiiu9lA6CkKanEcZMBCRGSUIVSWcrZTwnDuSvqN6W5jmOnoyjkRsPH9+2LzfkjtL1seSmzz05i07GHW2i3hjp8Vytw7qOp6cCN6yEHTRj7WSB7KUC0dQlrBNIghKTgdKiJFAAE2nWYJaA8Yq/puwoPir0YLnzbES70JMLfUNi+6dffcgNB99uB1kbck0JV1nlgbYawTGIeiljK0QMxSSiSHcopfH7Uq5Z8cSyI8deYoKthYLc3N1tc4hI1pWymNz0uSfvy+Vc/hnghjMZRK8ExpxNwSZXdKbdwSu6XHQ99zKtXfQfF38wErmQL5ro1UC4Q4kPYCLGWZ/JGMblIXbM/e/CBvfkJynv3jr6LQL5n/9djpaLKqWgrTKNmiLlaWhztCHdQxymfJadPNrf32ATMQ4P/u/6CxhkKuoIBfNEAAAAAElFTkSuQmCC",
        "open"          : "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",
        "closed"        : "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",
        "off"           : "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",
        "on"            : "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",
        "unknown"       : "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAmJLR0QAAKqNIzIAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAAHdElNRQfkAwoSHjHzISF7AAAA7ElEQVQ4y2NgIBEwwlnxDBJY5B8xLMeu0YThP1a4nyGGQQZZIROU5sHpBhWGwwwKmBpwAVGGBwwKDLsRtrAQ0KDNIMzgwMDKwIsu4YDDDwjogM+GpwzrGRgYAlC9i9sPRxgiGcQZxBkiGY7hdiuyk5wY3jL8Z/jP8ApF1AG3DZoMQtAQwgKwaZgCpV9jk8UVDx8ZVjIEMbRgSuCKhw0MhxhWMkgRbwMngzs25bhtsGX4j10Cu4avDJ4MLAyHGLiI1cDGIMzwm4GVeBtYGfbicCrB5E09DV8IqvwMoRCFQAKDBh7l1xkWkuoWKAAAZ3dFtWKDqIkAAAAldEVYdGRhdGU6Y3JlYXRlADIwMjAtMDMtMTBUMTg6MzA6NDkrMDA6MDBnUDQrAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDIwLTAzLTEwVDE4OjMwOjQ5KzAwOjAwFg2MlwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAASUVORK5CYII="
}

# MAIN MAC MENU BAR
# Iterate over the selected Main Menu Bar choices
if mainDisplay is not None:
    mainDisplaylen = len(mainDisplay)
    if mainDisplaylen > 0:
        for x in range(len(mainDisplay)):
            # Check if there is a integer value indicating a temperature value
            if isinstance(mainDisplay[x]['value'], int) or isinstance(mainDisplay[x]['value'], float):
                formattedMainDisplay += formatter.formatNumber(mainDisplay[x]['value']) + degree_symbol
                mainMenuColor = thermoColor
                print "{} | {} {} dropdown=false".format(formattedMainDisplay.encode('utf-8'), 'size=14', mainMenuColor)
            elif mainDisplay[x]['emoji'] is not None:
                print "| image={} dropdown=false".format(getImageString[mainDisplay[x]['emoji']])
            else:
                formattedMainDisplay = "ST BitBar"
                print "{} | {} {} dropdown=false".format(formattedMainDisplay.encode('utf-8'), 'size=14', mainMenuColor)
else:
    formattedMainDisplay = "ST BitBar"
    print "{} | {} {} dropdown=false".format(formattedMainDisplay.encode('utf-8'), 'size=14', mainMenuColor)

hortSeparatorBar()

if favoriteDevicesBool:
    original_stdout = sys.stdout
    favoriteDevicesOutputDict = {}
    fo = tempfile.TemporaryFile()
    sys.stdout = fo


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
for sensor in relativeHumidityMeasurements:
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
# print '---'
# Begin outputting sensor data

# Output Thermostat data
if (thermostats is not None) and (len(thermostats) > 0):
    # noinspection SpellCheckingInspection
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
                    == 'heating': setpointAction = ' to '
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
            if thermostat['thermostatOperatingState'] not in ["idle", "off"]:
                setpointText = "(" + str(thermostat['thermostatOperatingState']) + setpointAction + str(
                    currentSetpoint) + degree_symbol + ")"
            else:
                setpointText = "({})".format(thermostat['thermostatOperatingState'])

            if "displayName" in thermostat:
                print thermostat['displayName'], setpointText, buildFontOptions(3), 'image=', getImageString["thermoImage"]
            else:
                print "Thermostat Control", setpointText, buildFontOptions(3), 'image=', getImageString["thermoImage"]

            if not subMenuCompact: print "--Current Status", buildFontOptions()
            currentThermoURL = thermoURL + thermostat['id']
            thermoModeURL = currentThermoURL + "&type=mode&val="
            # Mode Menu
            if "thermostatMode" in thermostat:
                print "--Mode ({})".format(TitleCase(thermostat['thermostatMode'])), buildFontOptions(3)
                if not subMenuCompact: print "----Set Mode to:", buildFontOptions(1)
                for thermoMode in thermoModeList:
                    if thermoMode != thermostat['thermostatMode']:
                        thermo_param4 = 'param4=\"Setting {} to {}\"'.format(thermostat['displayName'], thermoMode)
                        print "----{}".format(TitleCase(thermoMode)), buildFontOptions(3), \
                            "bash=" + callbackScript, " param1=request param2=" + thermoModeURL + thermoMode.lower(), \
                            " param3=" + secret, thermo_param4, ' terminal=false refresh=false'
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
                        thermo_param4 = 'param4=\"Setting {} to {}\"'.format(thermostat['displayName'], str(c) + degree_symbol)
                        print "----", str(c) + degree_symbol, buildFontOptions(3), \
                            "color=", numberToColorGrad(id, "blue"), \
                            "bash=", callbackScript, " param1=request param2=", str(
                            coolSetpointURL + str(c)), " param3=", secret, thermo_param4, " terminal=false refresh=false"
                    print "----", str(currentCoolingSetPoint) + degree_symbol, "(current)|color=", \
                        numberToColorGrad(0, "blue")
                    for c in range(currentCoolingSetPoint + 1, currentCoolingSetPoint + 6):
                        thermo_param4 = 'param4=\"Setting {} to {}\"'.format(thermostat['displayName'], str(c) + degree_symbol)
                        print "----", str(c) + degree_symbol, buildFontOptions(3), "color=gray", \
                            "bash=", callbackScript, " param1=request param2=", str(
                            coolSetpointURL + str(c)), " param3=", secret, thermo_param4, " terminal=false refresh=false"
            # Heating Setpoint Menu
            if "heatingSetpoint" in thermostat:
                if thermostat['heatingSetpoint'] is not None:
                    heatingSetpointURL = currentThermoURL + "&type=heatingSetpoint&val="
                    currentHeatingSetPoint = int(thermostat['heatingSetpoint'])
                    print "--Heating Set Point (" + str(currentHeatingSetPoint) + degree_symbol + ")", \
                        buildFontOptions(3), "color=red"
                    print "----Change Setpoint | ", smallFontPitchSize
                    for c in range(currentHeatingSetPoint + 5, currentHeatingSetPoint, -1):
                        id = c - currentHeatingSetPoint
                        thermo_param4 = 'param4=\"Setting {} to {}\"'.format(thermostat['displayName'], str(c) + degree_symbol)
                        print "----", str(
                            c) + degree_symbol, buildFontOptions(3), "color=", numberToColorGrad(id, "red"), \
                            "bash=" + callbackScript, " param1=request param2=" + str(
                            heatingSetpointURL + str(c)), " param3=" + secret, thermo_param4, " terminal=false refresh=false"
                    print "----", str(currentHeatingSetPoint) + degree_symbol, "(current)|color=", \
                        numberToColorGrad(0, "red")
                    for c in range(currentHeatingSetPoint - 1, currentHeatingSetPoint - 6, -1):
                        thermo_param4 = 'param4=\"Setting {} to {}\"'.format(thermostat['displayName'], str(c) + degree_symbol)
                        print "----", str(c) + degree_symbol, buildFontOptions(3), "color=gray", \
                            "bash=" + callbackScript, " param1=request param2=" + str(
                            heatingSetpointURL + str(c)), " param3=" + secret, thermo_param4, " terminal=false refresh=false"

# Output Temp Sensors
if temps is not None:
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
                    print "--{} ({})".format(menuTitle, str(countSensors - mainMenuMaxItems)), buildFontOptions()
                subMenuText = "--"
            print subMenuText, sensor['name'], whiteSpace, currentValue + degree_symbol, \
                buildFontOptions(3), colorText
            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                # noinspection PyUnboundLocalVariable
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + \
                                                            currentValue + degree_symbol + buildFontOptions(
                    3) + colorText
            if (sensor['eventlog'] is not None) and (len(sensor['eventlog']) > 0):
                try:
                    eventGroupByDate([d for d in sensor['eventlog'] if d['name'] in "temperature"], subMenuText, "°")
                except (ValueError, TypeError, AttributeError):
                    pass
            if sensor['battery'] != 'N/A':
                if sensor['battery'][1] != "": colorText = "color=red"
                print subMenuText, sensor['name'], whiteSpace, formatPercentage(
                    sensor['battery'][0]) + sensor['battery'][1], buildFontOptions(3) + " alternate=true", colorText
            colorSwitch = not colorSwitch

# Output relativeHumidityMeasurements Sensors
if relativeHumidityMeasurements is not None:
    sensorName = "RelativeHumidityMeasurements"
    countSensors = len(relativeHumidityMeasurements)
    if countSensors > 0:
        hortSeparatorBar()
        menuTitle = "Relative Humidity Sensors"
        mainTitle = menuTitle
        if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
        print "{} {}".format(mainTitle, buildFontOptions())
        colorSwitch = False
        mainMenuMaxItems = mainMenuMaxItemsDict[sensorName]
        subMenuText = ''
        for i, sensor in enumerate(relativeHumidityMeasurements):
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
                    print "--{} ({})".format(menuTitle, str(countSensors - mainMenuMaxItems)), buildFontOptions()
                subMenuText = "--"
            print subMenuText, sensor['name'], whiteSpace, currentValue + "%", buildFontOptions(3), colorText
            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + \
                                                            currentValue + "%" + buildFontOptions(3) + colorText
            if (sensor['eventlog'] is not None) and (len(sensor['eventlog']) > 0):
                eventGroupByDate([d for d in sensor['eventlog'] if d['name'] in "humidity"], subMenuText, "%")
            if sensor['battery'] != 'N/A':
                if sensor['battery'][1] != "": colorText = "color=red"
                print subMenuText, sensor['name'], whiteSpace, formatPercentage(
                    sensor['battery'][0]) + sensor['battery'][1], buildFontOptions(3) + " alternate=true", colorText
            colorSwitch = not colorSwitch

# Output Modes
if (modes is not None) and len(modes) > 0:
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
            mode_param4 = 'param4=\"Setting House Mode to {}\"'.format(mode['name'])
            print "--• " + mode[
                'name'], buildFontOptions(3), colorText, ' bash=' + callbackScript, ' param1=request param2=' + \
                                                                                    currentModeURL, ' param3=' + secret, mode_param4, ' terminal=false refresh=false'
        colorSwitch = not colorSwitch

# Output Routines
if (routines is not None) and len(routines) > 0:
    print "--Routines (Select to Run)" + buildFontOptions()
    for i, routine in enumerate(routines):
        routine_param4 = 'param4=\"{} {}\"'.format('Setting Routine to', routine)
        colorText = ''
        colorText = 'color=#333333' if colorSwitch else 'color=#666666'
        currentRoutineURL = routineURL + urllib.quote(routine.encode('utf8'))
        print "--• " + routine, buildFontOptions(3), colorText, ' bash=' + callbackScript, ' param1=request param2=' + \
                                                                                           currentRoutineURL, ' param3=' + secret, routine_param4, ' terminal=false refresh=false'
        colorSwitch = not colorSwitch

# Output Smart Home Monitor
shmCurrentState = None
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
                alarm_param4 = 'param4=\"{} {}{}\"'.format('Setting Alarm to', alarmState.title(), currentAlarmStateDisplay)
                currentAlarmURL = 'bash= ' + callbackScript + ' param1=request param2=' + currentAlarmURL + \
                                  ' param3=' + secret, alarm_param4, ' terminal=false refresh=false'
            print "--• {}{}".format(alarmState.title(), currentAlarmStateDisplay), buildFontOptions(3), \
                colorText, currentAlarmURL
            colorSwitch = not colorSwitch

# Output Contact Sensors
if contacts is not None:
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
                if not subMenuCompact: print "--{} ({})".format(menuTitle, str(countSensors - mainMenuMaxItems)), \
                    buildFontOptions()
                subMenuText = "--"
            print subMenuText, sensor['name'], whiteSpace, sym, buildFontOptions(3), colorText
            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + \
                                                            sym + buildFontOptions(3) + colorText
            if (sensor['eventlog'] is not None) and (len(sensor['eventlog']) > 0):
                eventGroupByDate([d for d in sensor['eventlog']
                                  if d['name'] in ['status', 'contact', 'acceleration']], subMenuText, "")
            if sensor['battery'] != 'N/A':
                if sensor['battery'][1] != "": colorText = "color=red"
                print subMenuText, sensor['name'], whiteSpace, formatPercentage(
                    sensor['battery'][0]) + sensor['battery'][1], buildFontOptions(3) + "alternate=true", colorText
            colorSwitch = not colorSwitch

# Output Motion Sensors
if motion is not None:
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
            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + \
                                                            sym + buildFontOptions(3) + colorText
            if (sensor['eventlog'] is not None) and (len(sensor['eventlog']) > 0):
                eventGroupByDate([d for d in sensor['eventlog'] if d['name'] == 'motion'], subMenuText, "")
            if sensor['battery'] != 'N/A':
                if sensor['battery'][1] != "": colorText = "color=red"
                print subMenuText, sensor['name'], whiteSpace, formatPercentage(
                    sensor['battery'][0]) + sensor['battery'][1], buildFontOptions(3), " alternate=true", colorText
            colorSwitch = not colorSwitch

# Output Presence Sensors
if presences is not None:
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
            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + \
                                                            emoji + buildFontOptions(3) + colorText
            if (sensor['eventlog'] is not None) and (len(sensor['eventlog']) > 0):
                eventGroupByDate([d for d in sensor['eventlog'] if d['name'] in 'presence'], subMenuText, "")
            if sensor['battery'] != 'N/A':
                if sensor['battery'][1] != "": colorText = "color=red"
                print subMenuText + notPresentMenuText, sensor['name'], whiteSpace, formatPercentage(
                    sensor['battery'][0]) + sensor['battery'][1], buildFontOptions(3) + " alternate=true", colorText
            colorSwitch = not colorSwitch

# Output Locks
if locks is not None:
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
                img = getImageString[sensor['value']]
                lock_param4 = 'param4=\"{} {}\"'.format('Unlocking', sensor['name'])
                if mainMenuAutoSizeDict[sensorName] is True:
                    if mainMenuMaxItems > i: mainMenuMaxItems = i
                    subMenuTitle = "More Locked..."
            elif sensor['value'] == 'unlocked':
                sym = '🔓'
                img = getImageString[sensor['value']]
                lock_param4 = 'param4=\"{} {}\"'.format('Locking', sensor['name'])
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
                print subMenuText, sensor['name'] + ' (' + sensor['value'].capitalize() + ')', buildFontOptions(
                    3) + colorText + ' bash=' + callbackScript, ' param1=request param2=' + currentLockURL, \
                    ' param3=' + secret, lock_param4, ' terminal=false refresh=false image=' + img
            else:
                print subMenuText, sensor['name'] + ' (' + sensor[
                    'value'].capitalize() + ')', whiteSpace, sym, buildFontOptions(3) + colorText + ' bash=' + callbackScript, \
                    ' param1=request param2=' + currentLockURL, ' param3=' + secret, lock_param4, ' terminal=false refresh=false'
            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + \
                                                            sym + buildFontOptions(3) + colorText
            if (sensor['eventlog'] is not None) and (len(sensor['eventlog']) > 0):
                eventGroupByDate(
                    [d for d in sensor['eventlog'] if d['value'] in
                     ['locked', 'armed', 'unlocked', 'disarmed']], subMenuText, "")
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

# Output Switches & Lights
if switches is not None:
    sensorName = "Switches"
    countSensors = len(switches)
    if countSensors > 0:
        hortSeparatorBar()
        menuTitle = "Lights & {}".format(sensorName)
        mainTitle = menuTitle
        subMenuTitle = "More..."
        if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
        print mainTitle, buildFontOptions()
        mainMenuMaxItems = mainMenuMaxItemsDict[sensorName]
        subMenuText = ''
        for i, sensor in enumerate(switches):
            thisSensor = sensor["name"]
            if sensor['isRGB'] is True:
                thisSensor = "{} {}".format(thisSensor, colorBulbEmoji)
            elif sensor['isDimmer'] is True:
                thisSensor = "{} {}".format(thisSensor, dimmerBulbEmoji)
            else:
                pass
            if (sensor['isRGB'] or sensor['isDimmer']) and dimmerValueOnMainMenu:
                thisSensor = "{} ({}%)".format(thisSensor, sensor["dimmerLevel"])
            indent = ""
            currentLength = len(sensor['name'])
            extraLength = maxLength - currentLength
            whiteSpace = ''
            img = ''
            for x in range(0, extraLength): whiteSpace += ' '
            if sensor['value'] == 'on':
                sym = " ✅"
                img = getImageString['greenImage']
                switch_param4 = 'param4=\"{} {}\"'.format('Turning Off', sensor['name'])
            else:
                sym = " 🔴"
                img = getImageString['redImage']
                switch_param4 = 'param4=\"{} {}\"'.format('Turning On', sensor['name'])
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
                print subMenuText, thisSensor, buildFontOptions(3) + colorText + ' bash=' + callbackScript, \
                    ' param1=request param2=' + currentSwitchURL, ' param3=' + secret, switch_param4, ' terminal=false refresh=false image=' + img
            else:
                print subMenuText, thisSensor, whiteSpace, sym, buildFontOptions(
                    3) + colorText + ' bash=' + callbackScript, \
                    ' param1=request param2=' + currentSwitchURL, ' param3=' + secret, switch_param4, ' terminal=false refresh=false'
            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + sym + buildFontOptions(
                    3) + colorText
            indent = ""
            if sensor['isDimmer'] is True:
                subMenuText = subMenuText + '--'
                print subMenuText + dimmerBulbEmoji + ' Current Dimmer Level ({}%)'.format(sensor["dimmerLevel"]), \
                    buildFontOptions(3), smallFontPitchSize
                if sensor['isRGB']: subMenuText = subMenuText + '--'
                print subMenuText + dimmerBulbEmoji + ' Set Dimmer Level to:', buildFontOptions(3), smallFontPitchSize
                count = 0
                for currentLevel in range(10, 110, 10):
                    currentLevelURL = levelURL + sensor['id'] + '&level=' + str(currentLevel)
                    count += 1
                    print subMenuText + "{:>3}. {:>4}".format(count, str(currentLevel) + "%"), buildFontOptions(4), \
                        'bash=' + callbackScript, ' param1=request param2=' + currentLevelURL, \
                        ' param3=' + secret, switch_param4, ' terminal=false refresh=false'
                if sensor['isRGB']:
                    subMenuText = subMenuText[:-4]
                else:
                    subMenuText = subMenuText[:-2]
                indent = '--'
            if sensor['isRGB'] is True and colorChoices > 0:
                subMenuText = subMenuText + '--'
                colorName = getColorNameHue(sensor["hue"])
                if colorName is None: colorName = sensor["colorRGBName"]
                print subMenuText + colorBulbEmoji + " Current Hue Value ({} Hue: {})".format(colorName, sensor["hue"]), \
                    buildFontOptions(3), smallFontPitchSize
                subMenuText = subMenuText + '--'
                print subMenuText + colorBulbEmoji + ' Set Hue to:', buildFontOptions(3), smallFontPitchSize
                count = 0
                for colorChoice in colorChoices:
                    if colorName == colorChoice: continue
                    count += 1
                    if colorChoice == 'White':
                        colorChoiceSafe = 'Black'
                    else:
                        colorChoiceSafe = colorChoice.split(' ', 1)[0]
                    currentColorURL = colorURL + sensor['id'] + '&colorName=' + urllib.quote(colorChoice.encode('utf8'))
                    print subMenuText + "{:>3}. {} ".format(count, getHueLevel(colorChoice)), buildFontOptions(4), \
                        'bash=' + callbackScript, ' param1=request param2=' + currentColorURL, ' param3=' + secret, \
                        switch_param4, ' terminal=false refresh=false', 'color=' + colorChoiceSafe
                subMenuText = subMenuText[:-2]
                print subMenuText + colorBulbEmoji + ' Current Sat Value ({}) '.format(sensor["saturation"]), \
                    buildFontOptions(3), smallFontPitchSize
                subMenuText = subMenuText + '--'
                print subMenuText + colorBulbEmoji + ' Set Saturation to:', buildFontOptions(3), smallFontPitchSize
                count = 0
                for currentLevel in range(0, 110, 10):
                    currentColorURL = colorURL + sensor['id'] + '&saturation=' + str(currentLevel)
                    count += 1
                    print subMenuText + "{:>3}. {:>4}".format(count, str(currentLevel)), buildFontOptions(4), \
                        'bash=' + callbackScript, ' param1=request param2=' + currentColorURL, ' param3=' + secret, \
                        switch_param4, ' terminal=false refresh=false'
                subMenuText = subMenuText[:-4]
                indent = '--'
            if (sensor['eventlog'] is not None) and (len(sensor['eventlog']) > 0):
                print subMenuText + "-- 🎯 Event History", buildFontOptions(3)
                eventGroupByDate(sensor['eventlog'], subMenuText + indent, "")
            colorSwitch = not colorSwitch
    #        print '==>', sensor["name"], sensor

# Output MusicPlayers
if musicplayers is not None:
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
        # noinspection PyShadowingNames
        musicplayers = sorted(musicplayers, key=lambda x: x['name'], reverse=False)
        # noinspection PyShadowingNames
        for i, sensor in enumerate(sorted(musicplayers, key=lambda x: x['groupBool'], reverse=False)):
            currentLength = len(sensor['name'])
            extraLength = maxLength - currentLength
            whiteSpace = ''
            img = ''
            for x in range(0, extraLength): whiteSpace += ' '
            if "status" in sensor['trackData'] and sensor['trackData']['status'] == 'playing':
                sym = '🔛'
                img = getImageString['greenImage']
            else:
                sym = '🔴'
                img = getImageString['redImage']
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
            if sensor['groupBool']: sensor['name'] += " - {}{}".format('Grouped', sensor['trackDescription'][1])
            if useImages is True:
                print subMenuText, sensor['name'], buildFontOptions(3) + colorText, 'image=', img
            else:
                print subMenuText, sensor['name'], whiteSpace, sym, buildFontOptions(3) + colorText

            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + \
                                                            whiteSpace + " " + sym + buildFontOptions(3) + colorText

            if sensor['level'] is not None:
                print "{}--*Volume Level: ({})".format(subMenuText, sensor['level']), buildFontOptions(3)
                print "{}----Set Music Level".format(subMenuText), buildFontOptions(3), smallFontPitchSize
                currentLevel = 0
                while currentLevel <= 100:
                    currentMusicPlayerURL = musicplayerURL + sensor['id'] + '&command=' + 'level'
                    musicplayers_param4 = ' param4=\"{} {}\"'.format('Changing volume to', currentLevel)
                    print "{}----{}".format(subMenuText, currentLevel), buildFontOptions(3), \
                        'bash=' + callbackScript, 'param1=request param2=' + currentMusicPlayerURL, \
                        ' param3=' + secret, musicplayers_param4, ' terminal=false refresh=false'
                    currentLevel += 10
            if sensor['mute'] is not None:
                command = "mute" if sensor['mute'] is "unmuted" else "unmute"
                switch_param4 = 'param4=\"{} {}\"'.format('MusicPlayer:', command)
                print "{}--*Mute : {}".format(subMenuText, TitleCase(sensor['mute'])), \
                    buildFontOptions(3), 'bash=' + callbackScript, \
                    'param1=request param2=' + musicplayerURL + sensor['id'] + '&command=' + command, \
                    ' param3=' + secret, musicplayers_param4, 'terminal=false refresh=false'
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

# Output Valves
if valves is not None:
    sensorName = "Valves"
    countSensors = len(valves)
    if countSensors > 0:
        hortSeparatorBar()
        menuTitle = sensorName
        mainTitle = menuTitle
        subMenuTitle = "More..."
        if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
        print mainTitle, buildFontOptions()
        mainMenuMaxItems = mainMenuMaxItemsDict[sensorName]
        subMenuText = ''
        for i, sensor in enumerate(valves):
            thisSensor = sensor["name"]
            indent = ""
            currentLength = len(sensor['name'])
            extraLength = maxLength - currentLength
            whiteSpace = ''
            img = ''
            for x in range(0, extraLength): whiteSpace += ' '
            if sensor['value'] == 'open':
                sym = " ✅"
                img = getImageString['greenImage']
                valve_param4 = 'param4=\"{} {}\"'.format('Closing valve', sensor['name'])
            else:
                sym = " 🔴"
                img = getImageString['redImage']
                valve_param4 = 'param4=\"{} {}\"'.format('Opening valve', sensor['name'])
                if mainMenuAutoSizeDict[sensorName] is True:
                    if mainMenuMaxItems > i: mainMenuMaxItems = i
                    subMenuTitle = "More Valves Close..."
            currentValveURL = valveURL + sensor['id']
            colorText = 'color=#333333' if colorSwitch else 'color=#666666'
            if i == mainMenuMaxItems:
                print "{} {} {}".format(countSensors - mainMenuMaxItems, subMenuTitle, buildFontOptions())
                if not subMenuCompact: print "--{} ({}) {}".format(
                    menuTitle, str(countSensors - mainMenuMaxItems), buildFontOptions(2)
                )
                subMenuText = "--"
            if useImages is True:
                print subMenuText, thisSensor, buildFontOptions(3) + colorText + ' bash=', callbackScript, \
                    ' param1=request param2=', currentValveURL, ' param3=', secret, valve_param4, ' terminal=false refresh=false image=', img
            else:
                print subMenuText, thisSensor, whiteSpace, sym, buildFontOptions(
                    3) + colorText + ' bash=', callbackScript, ' param1=request param2=', currentValveURL, \
                    ' param3=', secret, valve_param4, ' terminal=false refresh=false'
            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + sym + buildFontOptions(
                    3) + colorText
            indent = ""
            if (sensor['eventlog'] is not None) and (len(sensor['eventlog']) > 0):
                print subMenuText + "-- 🎯 Event History", buildFontOptions(3)
                eventGroupByDate(sensor['eventlog'], subMenuText + indent, "")
            colorSwitch = not colorSwitch

# Output Water Sensors
if waters is not None:
    sensorName = "Waters"
    countSensors = len(waters)
    if countSensors > 0:
        hortSeparatorBar()
        menuTitle = "Water Sensors"
        subMenuTitle = "More..."
        mainTitle = menuTitle
        if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
        print mainTitle, buildFontOptions()
        mainMenuMaxItems = mainMenuMaxItemsDict[sensorName]
        subMenuText = ''
        for i, sensor in enumerate(waters):
            currentLength = len(sensor['name'])
            extraLength = maxLength - currentLength
            whiteSpace = ''
            for x in range(0, extraLength): whiteSpace += ' '
            sym = ''
            if sensor['value'] == 'wet':
                sym = ":potable_water:"
                if mainMenuAutoSizeDict[sensorName] is True:
                    if mainMenuMaxItems > i: mainMenuMaxItems = i
                    subMenuTitle = "More Sensors Inactive..."
            else:
                sym = ":sunny:"
            colorText = 'color=#333333' if colorSwitch else 'color=#666666'
            if i == mainMenuMaxItems:
                print "{} {} {}".format(countSensors - mainMenuMaxItems, subMenuTitle, buildFontOptions(2))
                if not subMenuCompact: print "-- " + menuTitle + " (" + str(countSensors - mainMenuMaxItems) + ")"
                subMenuText = "--"
            print subMenuText, sensor['name'], whiteSpace, sym, buildFontOptions(3), colorText
            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + \
                                                            sym + buildFontOptions(3) + colorText
            if (sensor['eventlog'] is not None) and (len(sensor['eventlog']) > 0):
                eventGroupByDate([d for d in sensor['eventlog'] if d['name'] in 'water'], subMenuText, "")
            if sensor['battery'] != 'N/A':
                if sensor['battery'][1] != "": colorText = "color=red"
                print subMenuText, sensor['name'], whiteSpace, formatPercentage(
                    sensor['battery'][0]) + sensor['battery'][1], buildFontOptions(3), " alternate=true", colorText
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
    if options[option] is not None and option == 'favoriteDevices' and len(favoriteDevices) > 1:
        for i, v in enumerate(options[option]):
            print printFormatString.format(option + "(" + str(i + 1) + ")", v, buildFontOptions(3))
    else:
        print printFormatString.format(
            option, options[option] if options[option] is not None else "{Default Set in GUI}", buildFontOptions(3)
        )
# Get the ST rateLimits from the returned headers
print "----SmartThings HTTP Server Response", buildFontOptions()
for response_info_name in response.info():
    if response_info_name[0:6] == 'x-rate':
        print "------{:20} = {:>3} {}".format(response_info_name, response.info()[response_info_name], buildFontOptions(3))
print "--Launch TextEdit " + cfgFileName + buildFontOptions() + openParamBuilder("open -e " + cfgFileName) + ' terminal=false'
print "--Launch SmartThings IDE " + buildFontOptions() + openParamBuilder("open " + buildIDEURL(smartAppURL)) + ' terminal=false'
print "--Launch Browser to View STBitBarAPP-V2 GitHub Software Resp " + buildFontOptions() + openParamBuilder("open https://github.com/kurtsanders/STBitBarApp-V2") + ' terminal=false'
print "--Download ST BitBar Installation/Upgrade script to your 'Downloads' directory " + buildFontOptions(), "bash=" + callbackScript, ' param1=upgrade terminal=false'

if favoriteDevicesBool:
    # noinspection PyUnboundLocalVariable
    sys.stdout = original_stdout
    # noinspection PyUnboundLocalVariable
    fo.seek(0, 0)
    countSensors = len(favoriteDevices)
    mainTitle = "My Favorite Devices"
    if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
    for key in favoriteDevices:
        # noinspection PyBroadException
        try:
            print favoriteDevicesOutputDict[key]
        except:
            continue
    hortSeparatorBar()
    print fo.read()
    fo.close()

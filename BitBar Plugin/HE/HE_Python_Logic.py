#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
 *
 *  Copyright 2018,2019,2020 Kurt Sanders
 *
 *  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 *  in compliance with the License. You may obtain a copy of the License at:
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
 *  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License
 *  for the specific language governing permissions and limitations under the License.
 *
"""
import ConfigParser
import base64
import cStringIO
import decimal
import json
import locale
import os
import re
import subprocess
import sys
import tempfile
import time
import timeit
import urllib
import urllib2
from urlparse import urlparse
start = timeit.default_timer()

# -------------------------------------------- #
HE_Logic_Python_Py_Local_Version = "4.02"      #
DEBUG = False                                  #
# -------------------------------------------- #

reload(sys)
sys.setdefaultencoding('utf8')
locale.setlocale(locale.LC_ALL, '')
imageLibraryNames = {}
manifestDict = {}
timePollEvery = 600
currentSTBitBarRelease = None
currentSTBitBarNews = None
# Version Information of ST BitBar Plugin File
STPluginFilename_argPosition = 1
STPluginVersion_argPosition = 2

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

# Begin Read User Config File for SmartThings Oauth and global variables
cfgFileName         = sys.argv[0][:-2] + "cfg"
cfgFileObj          = Setting(cfgFileName)
cfgGetValue         = cfgFileObj.get_setting
smartAppURL         = cfgGetValue('smartAppURL', "", True).strip('\'"')
secret              = cfgGetValue('secret', "", True).strip('\'"')
header              = {"Authorization": "Bearer " + secret}
manifest_replace    = cfgGetValue('manifest_replace', "True", False).strip('\'"')
# End Read User Config File

# Get application pathnames and version info
manifestFile        = "manifest.json"
STPluginFolder      = os.path.dirname(sys.argv[0])
try:
    STPluginVersion = sys.argv[STPluginVersion_argPosition]
except IndexError:
    STPluginVersion = None
try:
    STPluginFilename = os.path.basename(sys.argv[STPluginFilename_argPosition])
except IndexError:
    STPluginFilename = None
try:
    bbplugindir = os.path.split(os.path.dirname(sys.argv[0]))[0]
except IndexError:
    bbplugindir = sys.argv[0]

# Read the local manifest.json file for icon images and application variables, re-download from GitHub if changed
try:
    with open("{}/{}".format(STPluginFolder, manifestFile)) as manifest_json_file:
        manifestDict = json.load(manifest_json_file)
        currentSTBitBarRelease = manifestDict.get('current', None)
        currentSTBitBarNews = manifestDict.get('news', None)
except IOError, e:
    print "{}".format(e)
    print "BitBar Error: the {}' file is not accessible in BitBar ST subfolder".format(manifestFile)
    print "BitBar ST Folder = '{}'".format(STPluginFolder)
    print "Please verify the files in the BitBar Plugin Folder per the documentation"
    exit(99)

# Get Application Meta Information from Github
def getManifest():
    # Only get live updates timePollEvery per hour
    if (int(time.strftime("%H%M", time.localtime())) % timePollEvery) == 0:
        global currentSTBitBarRelease
        global currentSTBitBarNews
        req = urllib2.Request("https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/installation/manifest.json")
        try:
            reqdata = urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            print "Error getManifest() RC: {}".format(e.code)
            print e.read()
            return
        except urllib2.URLError as e:
            print 'Error: Failed to reach the STBitBarApp-V2 server for reading manifest file/version check.'
            print 'Reason: ', e.reason
            return
        try:
            gethubManifestDict = json.loads(reqdata.read())
        except (ValueError, TypeError):
            return
        currentSTBitBarRelease = gethubManifestDict.get('current', None)
        currentSTBitBarNews = gethubManifestDict.get('news', None)
        if DEBUG or manifest_replace == "False":
            return
        BitBarNeedUpdate = currentSTBitBarRelease != bitbarOutputSmartAppVersion
        PluginNeedUpdate = currentSTBitBarRelease != HE_Logic_Python_Py_Local_Version
        if BitBarNeedUpdate or PluginNeedUpdate:
            try:
                with open("{}/{}".format(STPluginFolder, manifestFile), 'w') as manifest_json_file:
                    json.dump(gethubManifestDict, manifest_json_file)
            except IOError:
                json.dump(manifestDict, manifest_json_file)
                pass
# Wrapper to get image/icon file
def getImageString(imageName):
    return manifestDict['icons'].get(imageName, "iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAAAXNSR0IArs4c6QAAAIRlWElmTU0AKgAAAAgABQESAAMAAAABAAEAAAEaAAUAAAABAAAASgEbAAUAAAABAAAAUgEoAAMAAAABAAIAAIdpAAQAAAABAAAAWgAAAAAAAABIAAAAAQAAAEgAAAABAAOgAQADAAAAAQABAACgAgAEAAAAAQAAABegAwAEAAAAAQAAABcAAAAAVd28qgAAAAlwSFlzAAALEwAACxMBAJqcGAAAAVlpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KTMInWQAAAzFJREFUSA111FmIT1EcwHGDYexjCGNpGEbMYjfKLiEaEg9EWbJkKx4kMp4kokhZaxJZHoQsqbEkxoO1bJElYx5kGabGkJ3x/d7/nPHH+NXnnnPu/Z/fPdv9J9SqORK4rZ81P47uZnOdgSwkIRFPsB+XUGmCv6M2N+KTNqPdAHb+ineYgGnYiLoYgjLcxzw8wvr45NZlYhPlIB0ZSEFjfEIlOmIycrEYuzACDmINduCSyQxLOxndMBHdUYJzVWU5ZRrysRsX0Rb2e4kp6IKdqMAJRIktjVE4gEU2/hN7uN8EdeKez6Z+HO5DiMJQsXRax9DDBuEU6yM+SVfaBegEw/U2RqJDVIv1s1oYOrquqzEfz2Bi1/cHnHYvLEcmesMBOG33px0G4i1e4zvmoNzkjm4VjsJEa2HnSXiOUqTiA07iGtzs/rgI92sM7uIN3OBBWOexcwNb4TRa4j1S4HH6BuMWXLLRcITL4LFcCAfRBgtQBHOtwFuTu4luhuEoXIpiOIvH8DfGXjSEy+dS+Ny6iT0EnqAXuI5XSLDjUJyC4ci/wPVsDzu6robtQ3AWw2CCJdgAR+wHtAvd4GmqdLfdvM8wniIPW3AWnl/3xdncwSa0wCxUILzYQVovwTg4Q5e31hkvRJi+o82ES2SE0rqnxr+DvyP8pikPtsFZRuc0JLVtOF2FcG0dvXE7VvxzNbm/S8ZHRAfBZXGNfYEPjdQqnnOVwg5GGEhYjtjd39eOVMtgv2jkNymH4wIMpz4eHjk/iHcoxwPcgBFG6susW/pCj6qzcz+i6fqWuTgOZ/IMRTBRMfzIeiIbfjh+hY7OpTKhM06Emz4ThfAg+MJoZwsoB9ggfEFN0Zqbq7Ay7mEOdWdpLIUfT9gf70XRl+theISMegjTdQTxHTyKRnPkIxdpOIgMGNGoY9XYdQbFfsS/wCeN4PFMRmf4uTvTeTDScQQjbRDVA3F0YXN84AvysBlXYWRhOhyxJ0f+ed3DcLhfW1EEozqfFaP6BvU+8A/JpdmHK3DDkuDm+9vBmApP1Hb4ZRvxeaJG7PafD1waT8dY9EPo5JT9Li7jPB7Cf0cj/CbW4voLDfW7VhbDSSIAAAAASUVORK5CYII=")

# def getImageStringOld(imageName):
#     global imageLibraryNames
#     if imageName not in imageLibraryNames:
#         imageURL = "https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/{}.png".format(imageName)
#         try:
#             rawImagegithub = urllib2.urlopen(imageURL)
#         except urllib2.HTTPError, e:
#             print "{}: GitHub is unavailable or the icon '{}.png' was not found in github images folder".format(e, imageName)
#             exit(99)
#         imageLibraryNames[imageName] = base64.b64encode(cStringIO.StringIO(rawImagegithub.read()).getvalue())
#     return imageLibraryNames[imageName]
#
# def imageLibraryGeneration():
#     imageDict = {}
#     for imageName in ['open', 'closed', 'on', 'off','unknown','shmoff','thermoImage','redImage','greenImage','number','shmstay','shmaway','locked','unlocked','new-logo']:
#         imageDict[imageName] = getImageStringOld(imageName)
#     with open('data.txt', 'w') as outfile:
#         json.dump(imageDict, outfile)

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


# Builds the param statement for bitbar to launch the "open" command
# noinspection PyShadowingNames
def openParamBuilder(openCommand):
    rc = " terminal=false bash='{}' ".format(sys.argv[1])
    i = 0
    for word in openCommand.split():
        i += 1
        rc += "param{}='{}' ".format(i, word)
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

# Set URLs
# statusURL = smartAppURL + "GetStatus/?pythonAppVersion=" + "{}".format(HE_Logic_Python_Py_Local_Version) + "&path=" + sys.argv[0] + "&bbpluginfilename=" + STPluginFilename + "&bbpluginversion=" + STPluginVersion
f = dict(pythonAppVersion=HE_Logic_Python_Py_Local_Version, access_token=secret,
         path=bbplugindir, bbpluginfilename=STPluginFilename, bbpluginversion=STPluginVersion)
statusURL = "{}{}{}".format(smartAppURL, "GetStatus/?", urllib.urlencode(f))
contactURL = smartAppURL + "ToggleSwitch/?access_token="+secret+"&id="
valveURL = smartAppURL + "ToggleValve/?access_token="+secret+"&id="
levelURL = smartAppURL + "SetLevel/?access_token="+secret+"&id="
colorURL = smartAppURL + "SetColor/?access_token="+secret+"&id="
musicplayerURL = smartAppURL + "SetMusicPlayer/?access_token="+secret+"&id="
lockURL = smartAppURL + "ToggleLock/?access_token="+secret+"&id="
thermoURL = smartAppURL + "SetThermo/?access_token="+secret+"&id="
routineURL = smartAppURL + "SetRoutine/?access_token="+secret+"&id="
modeURL = smartAppURL + "SetMode/?access_token="+secret+"&id="
alarmURL = smartAppURL + "SetAlarm/?access_token="+secret+"&id="

# Set the callback script for switch/level commands from parameters
# sys.argv[1] must contain the full path name to bitbar pluggins subdirectory
# an example could be: /Users/[account name]/[directory]/Bitbar/ST/
callbackScript = "'{}'".format(sys.argv[1])

# Make the call the to the API and retrieve JSON data
# Create the urllib2 Request
request = urllib2.Request(statusURL, None, header)
# Getting the response
try:
    response = urllib2.urlopen(request)
except (urllib2.HTTPError, urllib2.URLError) as err:
    print ":rage:"
    print "---"
    print ":thumbsdown: HTTPS Error Encountered: Communicating to HE API caused the following error: {}".format(
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
    print "--SmartThings HTTP Server Response"
    for response_info_name in response.info():
        if response_info_name[0:6] == 'x-rate':
            print "----{:20} = {:>3}".format(response_info_name, response.info()[response_info_name])
    exit(99)

# Parse the JSON data
try:
    j = json.loads(response.read())
except (ValueError, TypeError) as err:
    pass

# API Return Error Handling
if "error" in j:
    print ":rage:"
    print '---'
    if j['error'] == 'invalid_token':
        print ":thumbsdown: Please verify that both the SmartApp URL and Secret in HE_Python_Logic.cfg are correct."
        print " Please re-try again after verification of these strings."
    print "Error Details: ", j['error']
    if "error_description" in j:
        print ":thumbsdown: Error Description: ", j['error_description']
    exit(99)

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
    bitbarOutputSmartAppVersion = j['Version']

except KeyError, e:
    print ":rage:"
    print "---"
    print ":thumbsdown: Json File Error Details: ", e
    exit(99)

# Verify SmartApp and local app version

def upgradeAvailable():
    getManifest()
    BitBarNeedUpdate = currentSTBitBarRelease != bitbarOutputSmartAppVersion
    PluginNeedUpdate = currentSTBitBarRelease != HE_Logic_Python_Py_Local_Version
    if BitBarNeedUpdate or PluginNeedUpdate:
        print '---'
        print "STBitBarApp {} - SanderSoft™ | font=arial color=purple".format(bitbarOutputSmartAppVersion)
        print ":computer: SmartApp Upgrade {} Now Available | color=red".format(bitbarOutputSmartAppVersion)
        print "--:newspaper: {} | length=60 color=red font=16".format(currentSTBitBarNews)
        if BitBarNeedUpdate:
            print "--√ Click this to Launch SmartThings IDE and manually 'Update from Repo' | ", openParamBuilder("open " + buildIDEURL(smartAppURL)), ' terminal=false color=blue'
        if PluginNeedUpdate:
            print "--√ Click here to Upgrade ST BitBar Plugins App folder | color=blue bash={} param1=upgrade terminal=false".format(sys.argv[1])

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
useAlbumArtworkImages = getOptions("useAlbumArtworkImages", False)
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
shmCurrentStateDict = {'off': 'Disarmed', 'stay': 'Armed/Stay', 'away': 'Armed/Away'}

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
    if temps is not None:
        temps = sorted(temps, key=lambda k: k[sortkey])
    if contacts is not None:
        contacts = sorted(contacts, key=lambda k: k[sortkey])
    if switches is not None:
        switches = sorted(switches, key=lambda k: k[sortkey])
    if motion is not None:
        motion = sorted(motion, key=lambda k: k[sortkey])
    if mainDisplay is not None:
        mainDisplay = sorted(mainDisplay, key=lambda k: k[sortkey])
    if musicplayers is not None:
        musicplayers = sorted(musicplayers, key=lambda k: k[sortkey])
    if locks is not None:
        locks = sorted(locks, key=lambda k: k[sortkey])
    if relativeHumidityMeasurements is not None:
        relativeHumidityMeasurements = sorted(relativeHumidityMeasurements, key=lambda k: k[sortkey])
    if presences is not None:
        presences = sorted(presences, key=lambda k: k[sortkey])
    if modes is not None:
        modes = sorted(modes, key=lambda k: k[sortkey])
    if routines is not None:
        routines = sorted(routines)

# Add a section to the submenu for special devices designated in the SmartApp
if DEBUG is False and favoriteDevices is not None:
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
    motion = sorted(motion, key=lambda k: k[sortkey], reverse=False)
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
                print "| image={} dropdown=false".format(getImageString(mainDisplay[x]['emoji']))
            else:
                formattedMainDisplay = "ST BitBar"
                print "{} | {} {} dropdown=false".format(formattedMainDisplay.encode('utf-8'), 'size=14', mainMenuColor)
    if mainDisplaylen > 0:
        maxLengthDisplayName = 0
        print "---"
        print "Main Menu Bar Icon Status ({}) | {}".format(mainDisplaylen, buildFontOptions(2))
        for x in range(len(mainDisplay)):
            if isinstance(mainDisplay[x]['value'], int) or isinstance(mainDisplay[x]['value'], float):
                mainDisplay[x]['value'] = str(mainDisplay[x]['value'])
                if mainDisplay[x]['capability'] == 'temperatureMeasurement':
                    mainDisplay[x]['value'] = mainDisplay[x]['value'] + degree_symbol
            elif mainDisplay[x]['capability'] == 'shm':
                mainDisplay[x]['name'] = mainDisplay[x]['label']
                mainDisplay[x]['value'] = shmCurrentStateDict.get(mainDisplay[x]['value'][3:], mainDisplay[x]['value'][3:])
            maxLengthDisplayName = len(mainDisplay[x]['name']) if len(mainDisplay[x]['name']) > maxLengthDisplayName else maxLengthDisplayName
        for x in range(len(mainDisplay)):
            print "--:small_blue_diamond: {} {} {} ".format(mainDisplay[x]['name'].ljust(maxLengthDisplayName, '.'), str(mainDisplay[x]['value']).upper(), buildFontOptions(3))
else:
    formattedMainDisplay = "ST BitBar"
    print "{} | {} {} dropdown=false".format(formattedMainDisplay.encode('utf-8'), 'size=14', mainMenuColor)

upgradeAvailable()
print "---"

if favoriteDevicesBool:
    original_stdout = sys.stdout
    favoriteDevicesOutputDict = {}
    fo = tempfile.TemporaryFile()
    sys.stdout = fo

# Set the static amount of decimal places based on setting
if matchOutputNumberOfDecimals is True:
    formatter.setStaticDecimalPlaces(maxDecimals)
else:
    formatter.setStaticDecimalPlaces(-1)

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
                print thermostat['displayName'], setpointText, buildFontOptions(3), 'image=', getImageString("thermoImage")
            else:
                print "Thermostat Control", setpointText, buildFontOptions(3), 'image=', getImageString("thermoImage")

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
                        print "----• {}".format(TitleCase(thermoMode)), buildFontOptions(3), \
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
                        print "----• ", str(c) + degree_symbol, buildFontOptions(3), \
                            "color=", numberToColorGrad(id, "blue"), \
                            "bash=", callbackScript, " param1=request param2=", str(
                            coolSetpointURL + str(c)), " param3=", secret, thermo_param4, " terminal=false refresh=false"
                    print "----", ':heavy_check_mark:', str(currentCoolingSetPoint) + degree_symbol, "| color=black size=14 font='Menlo Bold'"
                    for c in range(currentCoolingSetPoint + 1, currentCoolingSetPoint + 6):
                        thermo_param4 = 'param4=\"Setting {} to {}\"'.format(thermostat['displayName'], str(c) + degree_symbol)
                        print "----• ", str(c) + degree_symbol, buildFontOptions(3), "color=gray", \
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
                        print "----• ", str(
                            c) + degree_symbol, buildFontOptions(3), "color=", numberToColorGrad(id, "red"), \
                            "bash=" + callbackScript, " param1=request param2=" + str(
                            heatingSetpointURL + str(c)), " param3=" + secret, thermo_param4, " terminal=false refresh=false"
                    print "----", ':heavy_check_mark:', str(currentHeatingSetPoint) + degree_symbol, "| color=black size=14 font='Menlo Bold'"
                    for c in range(currentHeatingSetPoint - 1, currentHeatingSetPoint - 6, -1):
                        thermo_param4 = 'param4=\"Setting {} to {}\"'.format(thermostat['displayName'], str(c) + degree_symbol)
                        print "----• ", str(c) + degree_symbol, buildFontOptions(3), "color=gray", \
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
                                                            currentValue + degree_symbol
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
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + currentValue + "%"
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
        emoji = " :house:"
    elif currentmode['name'] == "Night":
        emoji = ' :zzz:'
    else:
        emoji = ""
    if 20 <= int(time.strftime("%M")) <= 40:
        thirtyMin = '30'
    else:
        thirtyMin = ''
    emojiClock = " :clock{}{}:".format(time.strftime("%-I"), thirtyMin)
    print "Home Mode is {}{}{}{}".format(currentmode['name'], emoji, emojiClock, buildFontOptions())
    print "--Modes (Select to Change)" + buildFontOptions()
    for i, mode in enumerate(modes):
        colorText = ''
        colorText = 'color=#333333' if colorSwitch else 'color=#666666'
        if mode['name'] not in currentmode['name']:
            currentModeURL = modeURL + urllib.quote(mode['name'].encode('utf8'))
            mode_param4 = 'param4=\"Setting House Mode to {}\"'.format(mode['name'])
            print "--• " + mode[
                'name'], buildFontOptions(3), colorText, ' bash=' + callbackScript, ' param1=request param2=' + currentModeURL, \
                ' param3=' + secret, mode_param4, ' terminal=false refresh=false'
        colorSwitch = not colorSwitch

# Output Routines
if (routines is not None) and len(routines) > 0:
    if modes is None:
        hortSeparatorBar()
    print "Routines" + buildFontOptions()
    print "--Select to Run" + buildFontOptions()
    for i, routine in enumerate(routines):
        routine_param4 = 'param4=\"{} {}\"'.format('Setting Routine to', routine)
        colorText = ''
        colorText = 'color=#333333' if colorSwitch else 'color=#666666'
        currentRoutineURL = routineURL + urllib.quote(routine.encode('utf8'))
        print "--• " + routine, buildFontOptions(3), colorText, ' bash=' + callbackScript, ' param1=request param2=' + currentRoutineURL, \
            ' param3=' + secret, routine_param4, ' terminal=false refresh=false'
        colorSwitch = not colorSwitch

# Output Smart Home Monitor
shmCurrentState = None
if shmDisplayBool and alarms is not None:
    if modes is None or routines is None:
        hortSeparatorBar()
    colorText = ''
    for i, alarm in enumerate(alarms):
        if alarm['name'] == 'shm':
            shmCurrentState = alarm['value']
            print "Smart Home Monitor is {}{}".format(shmCurrentStateDict.get(alarm['value'], alarm['value']), buildFontOptions())
    # Verify the SHM is configured:
    if shmCurrentState != "unconfigured":
        print "--Select to Change" + buildFontOptions()
        for alarmState in alarmStates:
            colorText = 'color=#333333' if colorSwitch else 'color=#666666'
            if alarmState == shmCurrentState:
                currentAlarmStateDisplay = " (Current)"
                currentAlarmURL = ""
            else:
                currentAlarmURL = alarmURL + alarmState
                currentAlarmStateDisplay = ""
                alarm_param4 = 'param4=\"{} {}{}\"'.format('Setting Alarm to', alarmState.title(), currentAlarmStateDisplay)
                currentAlarmURL = 'bash=' + callbackScript + ' param1=request param2=' + currentAlarmURL + \
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
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + sym
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
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + sym
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
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + emoji
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
                img = getImageString(sensor['value'])
                lock_param4 = 'param4=\"{} {}\"'.format('Unlocking', sensor['name'])
                if mainMenuAutoSizeDict[sensorName] is True:
                    if mainMenuMaxItems > i: mainMenuMaxItems = i
                    subMenuTitle = "More Locked..."
            elif sensor['value'] == 'unlocked':
                sym = '🔓'
                img = getImageString(sensor['value'])
                lock_param4 = 'param4=\"{} {}\"'.format('Locking', sensor['name'])
            else:
                sym = '🔴'
                img = getImageString(sensor['value'])
                lock_param4 = ''
                sensor['name'] = "{} is {}".format(sensor['name'], sensor['value'])
            if i == mainMenuMaxItems:
                print "{} {} {}".format(countSensors - mainMenuMaxItems, subMenuTitle, buildFontOptions(2))
                if not subMenuCompact: print "--{} ({}) {}".format(
                    menuTitle, str(countSensors - mainMenuMaxItems), buildFontOptions()
                )
                subMenuText = "--"
            colorText = 'color=#333333' if colorSwitch else 'color=#666666'
            if useImages is True:
                print subMenuText, sensor['name'] + ' is ' + sensor['value'].capitalize(), buildFontOptions(
                    3) + colorText + ' bash=' + callbackScript, ' param1=request param2=' + currentLockURL, \
                    ' param3=' + secret, lock_param4, ' terminal=false refresh=false image=' + img
            else:
                print subMenuText, sensor['name'] + ' is ' + sensor[
                    'value'].capitalize(), whiteSpace, sym, buildFontOptions(3) + colorText + ' bash=' + callbackScript, \
                    ' param1=request param2=' + currentLockURL, ' param3=' + secret, lock_param4, ' terminal=false refresh=false'
            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + sym
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
                img = getImageString('greenImage')
                switch_param4 = 'param4=\"{} {}\"'.format('Turning Off', sensor['name'])
            else:
                sym = " 🔴"
                img = getImageString('redImage')
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
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + sym
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
                    print subMenuText + "   • {:>4}".format(str(currentLevel) + "%"), buildFontOptions(4), \
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

# Output Media Players
if musicplayers is not None:
    sensorName = "MusicPlayers"
    countSensors = len(musicplayers)
    if countSensors > 0:
        hortSeparatorBar()
        menuTitle = "Media Players"
        mainTitle = menuTitle
        subMenuTitle = "More Media Players..."
        if showSensorCount: mainTitle += " (" + str(countSensors) + ")"
        print mainTitle, buildFontOptions()
        mainMenuMaxItems = mainMenuMaxItemsDict[sensorName]
        subMenuText = ''
        # noinspection PyShadowingNames
        musicplayers = sorted(musicplayers, key=lambda x: x['name'], reverse=False)
        musicplayers = sorted(musicplayers, key=lambda x: x['manufacturer'], reverse=True)
        # noinspection PyShadowingNames
        for i, sensor in enumerate(sorted(musicplayers, key=lambda x: x['groupRolePrimary'], reverse=True)):
            currentLength = len(sensor['name'])
            extraLength = maxLength - currentLength
            whiteSpace = ''
            img = ''
            for x in range(0, extraLength): whiteSpace += ' '
            if sensor['status'] == 'playing':
                sym = '🔛'
                img = getImageString('greenImage')
            else:
                sym = '🔴'
                img = getImageString('redImage')
                if mainMenuAutoSizeDict[sensorName] is True:
                    if mainMenuMaxItems > i: mainMenuMaxItems = i
                    subMenuTitle = "More Media Players Inactive..."
            colorText = 'color=#333333' if colorSwitch else 'color=#666666'
            if i == mainMenuMaxItems:
                print "{} {} {}".format(countSensors - mainMenuMaxItems, subMenuTitle, buildFontOptions())
                if not subMenuCompact: print "--{} ({}) {}".format(
                    menuTitle, str(countSensors - mainMenuMaxItems), buildFontOptions(2)
                )
                subMenuText = "--"
            if sensor['groupRole'] is not None: sensor['name'] = "{} - ({})".format(sensor['name'], sensor['groupRole'].capitalize())
            if useImages is True:
                print subMenuText, sensor['name'], buildFontOptions(3) + colorText, 'image=' + img
            else:
                print subMenuText, sensor['name'], whiteSpace, sym, buildFontOptions(3) + colorText

            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + whiteSpace + " " + sym
            if sensor['level'] is not None:
                if sensor['manufacturer'] is not None:
                    print "{}--{}".format(subMenuText, sensor['manufacturer']), buildFontOptions(2)
                print "{}--• Volume: {} % of Maximum".format(subMenuText, sensor['level']), buildFontOptions(3)
                print "{}----Change Music Volume".format(subMenuText), buildFontOptions(3), smallFontPitchSize
                currentLevel = 0
                while currentLevel <= 100:
                    currentMusicPlayerURL = "{}{}&command=level&level={}".format(musicplayerURL, sensor['id'], currentLevel)
                    musicplayers_param4 = ' param4=\"{} {}\"'.format('Changing volume to', currentLevel)
                    print "{}----• {}".format(subMenuText, currentLevel), buildFontOptions(3), \
                        'bash=' + callbackScript, 'param1=request param2=' + currentMusicPlayerURL, \
                        ' param3=' + secret, musicplayers_param4, ' terminal=false refresh=false'
                    currentLevel += 5
            if sensor['mute'] is not None:
                for command in ["mute", "unmute"]:
                    musicplayers_param4 = 'param4=\"{} {}\"'.format('MediaPlayer:', TitleCase(command))
                    if sensor['mute'].startswith(command):
                        muteState = " :white_check_mark: "
                    else:
                        muteState = '• '
                    print "{}--{}{}".format(subMenuText, muteState, TitleCase(command)), buildFontOptions(3), 'bash=' + callbackScript, \
                        'param1=request param2=' + musicplayerURL + sensor['id'] + '&command=' + command, ' param3=' + secret, musicplayers_param4, 'terminal=false refresh=false'
            if sensor['supportedCommands'] is not None:
                for supportedCommand in sorted(sensor['supportedCommands']):
                    musicplayers_param4 = 'param4=\"{} {}\"'.format('MusicPlayer:', TitleCase(supportedCommand))
                    print "{}--• {}".format(subMenuText, TitleCase(supportedCommand)), buildFontOptions(3), 'bash=' + callbackScript, \
                        'param1=request param2=' + musicplayerURL + sensor['id'] + '&command=' + supportedCommand, \
                        ' param3=' + secret, musicplayers_param4, 'terminal=false refresh=false'
            if sensor["audioTrackData"] not in [None, '{}', '']:
                albumArtworkImageLink = ''
                albumArtwortkBullet = ''
                errorURL = False
                padwidth = 10
                try:
                    sensor["audioTrackData"] = json.loads(sensor["audioTrackData"])
                except ValueError:
                    errorURL = True
                    useAlbumArtworkImages = False
                print "{}--• Track Now Playing Info".format(subMenuText), buildFontOptions(3)
                albumArtwortkBullet = ''
                if "albumArtUrl" in sensor["audioTrackData"] and sensor["audioTrackData"]['albumArtUrl'].startswith("http"):
                    albumArtwortkBullet = '•'
                    url = sensor["audioTrackData"]['albumArtUrl']
                    if useAlbumArtworkImages:
                        try:
                            req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
                            rawImage = urllib2.urlopen(req)
                            albumArtworkImageLink = " image=" + base64.b64encode(cStringIO.StringIO(rawImage.read()).getvalue())
                        except Exception, e:
                            errorMessage = e
                            albumArtworkImageLink = " href={}".format(url)
                            useAlbumArtworkImages = False
                            errorURL = True
                    else:
                        albumArtworkImageLink = " href={}".format(url)
                else:
                    padwidth = 8
                for key, value in sorted(sensor["audioTrackData"].items()):
                    if key == "album":
                        if errorURL:
                            print "{}----•{:{width}}: {}".format(subMenuText, TitleCase(key), value, width=padwidth), buildFontOptions(3)
                            print "{}------ErrorURL: {}".format(subMenuText, url), buildFontOptions(3)
                            print "{}------ErrorMessage: {}".format(subMenuText, errorMessage), buildFontOptions(3)
                        else:
                            if useAlbumArtworkImages:
                                print "{}----{} {:{width}}: {}".format(subMenuText, albumArtwortkBullet, TitleCase(key), value, width=padwidth), buildFontOptions(3)
                                print "{}------ ".format(subMenuText), buildFontOptions(3), albumArtworkImageLink
                            else:
                                print "{}----{} {:{width}}: {}".format(subMenuText, albumArtwortkBullet, TitleCase(key), value, width=padwidth), buildFontOptions(3), albumArtworkImageLink
                    elif key != "albumArtUrl":
                        print "{}----{:{width}}: {}".format(subMenuText, TitleCase(key), value, width=padwidth+2), buildFontOptions(3)
            if sensor['presets'] is not None:
                print "{}--• {} Favorite Playlists".format(subMenuText, sensor['manufacturer']), buildFontOptions(3)
                print "{}----Select Favorite Playlist Preset".format(subMenuText), buildFontOptions(3), smallFontPitchSize
                for num, preset in enumerate(json.loads(sensor['presets']), start=1):
                    currentMusicPlayerURL = "{}{}&command=preset&presetid={}".format(musicplayerURL, sensor['id'], preset['id'])
                    musicplayers_param4 = ' param4=\"Playing {}\"'.format(preset['name'].replace('"', '\\"').replace("'", ''))
                    print "{}----• {:2d}. {}".format(subMenuText, num, preset['name']), buildFontOptions(3), \
                        'bash=' + callbackScript, 'param1=request param2=' + currentMusicPlayerURL, \
                        ' param3=' + secret, musicplayers_param4, ' terminal=false refresh=false length=40'
            if sensor['alexaPlaylists']:
                print "{}--• {} Favorite Playlists".format(subMenuText, sensor['manufacturer']), buildFontOptions(3)
                print "{}----Favorite Playlists (Voice Cmd Only)".format(subMenuText), buildFontOptions(3), smallFontPitchSize
                for num, alexaPlaylist in enumerate(sensor['alexaPlaylists'][1:-3].split('}], '),start=1):
                    alexaPlaylistObj = re.search("^(.*?)=.*?playlistId=(.*?),.*", alexaPlaylist)
                    if alexaPlaylistObj:
                        print "{}----{:2d}. {}".format(subMenuText, num, alexaPlaylistObj.group(1)), buildFontOptions(3)
                        # Echo Speaks DTH does not support invoking playlists like Sonos at this time.
                        # currentMusicPlayerURL = "{}{}&command=preset&presetid={}".format(musicplayerURL, sensor['id'], alexaPlaylistObj.group(2))
                        # musicplayers_param4 = ' param4=\"Playing {}\"'.format(alexaPlaylistObj.group(1).replace('"', '\\"').replace("'", ''))
                        # print "{}----• {}".format(subMenuText, alexaPlaylistObj.group(1)), buildFontOptions(3), \
                        #     'bash=' + callbackScript, 'param1=request param2=' + currentMusicPlayerURL, \
                        #     ' param3=' + secret, musicplayers_param4, ' terminal=false refresh=false length=40'
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
                img = getImageString('greenImage')
                valve_param4 = 'param4=\"{} {}\"'.format('Closing valve', sensor['name'])
            else:
                sym = " 🔴"
                img = getImageString('redImage')
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
                print subMenuText, thisSensor, buildFontOptions(3) + colorText + ' bash=' + callbackScript, \
                    ' param1=request param2=', currentValveURL, ' param3=', secret, valve_param4, ' terminal=false refresh=false image=', img
            else:
                print subMenuText, thisSensor, whiteSpace, sym, buildFontOptions(
                    3) + colorText + ' bash=' + callbackScript, ' param1=request param2=', currentValveURL, \
                    ' param3=', secret, valve_param4, ' terminal=false refresh=false'
            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + sym
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
                sym = dimmerBulbEmoji
            colorText = 'color=#333333' if colorSwitch else 'color=#666666'
            if i == mainMenuMaxItems:
                print "{} {} {}".format(countSensors - mainMenuMaxItems, subMenuTitle, buildFontOptions(2))
                if not subMenuCompact: print "-- " + menuTitle + " (" + str(countSensors - mainMenuMaxItems) + ")"
                subMenuText = "--"
            print subMenuText, sensor['name'], whiteSpace, sym, buildFontOptions(3), colorText
            if favoriteDevicesBool and sensor['name'] in favoriteDevices:
                favoriteDevicesOutputDict[sensor['name']] = sensor['name'] + whiteSpace + " " + sym
            if (sensor['eventlog'] is not None) and (len(sensor['eventlog']) > 0):
                eventGroupByDate([d for d in sensor['eventlog'] if d['name'] in 'water'], subMenuText, "")
            if sensor['battery'] != 'N/A':
                if sensor['battery'][1] != "": colorText = "color=red"
                print subMenuText, sensor['name'], whiteSpace, formatPercentage(
                    sensor['battery'][0]) + sensor['battery'][1], buildFontOptions(3), " alternate=true", colorText
            colorSwitch = not colorSwitch

# Configuration Options
hortSeparatorBar()
stop = timeit.default_timer()
print ":crystal_ball: STBitBarApp Actions and Shortcuts" + buildFontOptions(2)
print "--• Upgrade ST BitBar Plugins App folder to latest {} release |".format(currentSTBitBarRelease), buildFontOptions(3), "bash=" + callbackScript, ' param1=upgrade terminal=false'
print "--:computer: Your Current Running Program Version Information" + buildFontOptions()
print "----BitBar Output App Version: {} ".format(currentSTBitBarRelease), buildFontOptions()
print "----HE_Python_Logic.py Local Version: {}".format(HE_Logic_Python_Py_Local_Version), buildFontOptions()
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
print "--• Launch SmartThings IDE " + buildFontOptions() + openParamBuilder("open " + buildIDEURL(smartAppURL)) + ' terminal=false'
print "--• Launch Mac Default Browser to View STBitBarAPP-V2 GitHub Software Resp " + buildFontOptions() + openParamBuilder("open https://github.com/kurtsanders/STBitBarApp-V2") + ' terminal=false'
print "--:loop: Program Execution RunTine: {:.1f} secs".format(stop - start), buildFontOptions()

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
            print ":small_blue_diamond: " + favoriteDevicesOutputDict[key] + ' | color=black font=Monaco  size=11'
        except:
            continue
    print '---'
    print fo.read()
    fo.close()

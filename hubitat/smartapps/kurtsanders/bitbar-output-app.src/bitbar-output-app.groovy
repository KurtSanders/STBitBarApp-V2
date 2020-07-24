/**
 *  BitBar Output App
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
 */
// Major BitBar Version requires a change to the Python Version, Minor BitBar Version numbering will still be compatible with lower minor Python versions
def appVersion() { return "4.02" }
import groovy.json.JsonSlurper
// import java.awt.Color;
import java.util.ArrayList;
import groovy.time.*

definition(
    name: "BitBar Output App",
    namespace: "kurtsanders",
    author: "kurtsanders",
    description: "Display SmartThings Device Information in the Apple BitBar (OSX) Application",
    category: "My Apps",
    iconUrl:    "https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/STBitBarApp-V2.png",
    iconX2Url:  "https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/STBitBarApp-V2.png",
    iconX3Url:  "https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/STBitBarApp-V2-120.png")

preferences {
  page(name:"mainPage")
  page(name:"devicesManagementPage")
  page(name:"devicesPage")
  page(name:"devicesTopMenuBarPage")
  page(name:"optionsPage")
  page(name:"fontsPage")
  page(name:"iconsPage")
  page(name:"categoryPage")
  page(name:"eventsPage")
  page(name:"batteryPage")
  page(name:"disableAPIPage")
  page(name:"enableAPIPage")
  page(name:"APIPage")
  page(name:"APISendSMSPage")
}

mappings {

    path("/GetStatus/") {
        action: [
            GET: "getStatus"
        ]
    }
    path("/ToggleSwitch/") {
        action: [
            GET: "toggleSwitch"
        ]
    }
    path("/SetMusicPlayer/") {
        action: [
            GET: "setMusicPlayer"
        ]
    }
    path("/SetLevel/") {
        action: [
            GET: "setLevel"
        ]
    }
    path("/SetColor/") {
        action: [
            GET: "setColor"
        ]
    }
    path("/SetThermo/") {
        action: [
            GET: "setThermo"
        ]
    }
    path("/SetRoutine/") {
        action: [
            GET: "setRoutine"
        ]
    }
    path("/SetMode/") {
        action: [
            GET: "setMode"
        ]
    }
    path("/SetAlarm/") {
        action: [
            GET: "setAlarm"
        ]
    }
    path("/ToggleLock/") {
        action: [
            GET: "toggleLock"
        ]
    }
    path("/ToggleValve/") {
        action: [
            GET: "toggleCloseOpen"
        ]
    }
    path("/Test/") {
        action: [
            GET: "test"
        ]
    }
}

def test() {
    def msg = ["Test Success! BitBar Output App Version: ${appVersion()}"]
    log.debug msg
    return msg
}

def installed() {
    //	log.debug "Installed with settings: ${settings}\n"
	initialize()
}
def uninstalled() {
	if (state.endpoint) {
		try {
			log.debug "Revoking API access token"
			revokeAccessToken()
		}
		catch (e) {
			log.warn "Unable to revoke API access token: $e"
		}
	}
}
def updated() {
	// Added additional logging from @kurtsanders
    log.debug "##########################################################################################"
    log.debug "secret=${state.accessToken}"
    log.debug "smartAppURL=${state.endpointURL}"
    log.debug "##########################################################################################"
    log.debug "The API has been setup. Please enter the next two strings exactly as shown into the HE_Python_Logic.cfg file which is in your BitBar plugins directory."
    log.debug "##########################################################################################"

	unsubscribe()
	initialize()
}

def initialize() {
	subscribe(location, "alarmSystemStatus", alarmHandler)
	if(thermos)
    	thermos.each {
			subscribe(it, "thermostatOperatingState", thermostatOperatingStateHandler)
        }
    state.lastThermostatOperatingState = now()
    state.eventsDays = eventsDays
    state.eventsMax = eventsMax
}
def thermostatOperatingStateHandler(evt) {
	log.debug "thermostatOperatingStateHandler received event"
	state.lastThermostatOperatingState = now()
}

def alarmHandler(evt) {
  log.debug "Alarm Handler value: ${evt.value}"
  state.shm = location.currentState("alarmSystemStatus")?.value
  log.debug "alarm state: ${location.currentState("alarmSystemStatus")?.value}"
}


// Respond to action requests
def setRoutine() {
	log.debug "Begin: setRoutine"
    def command = params.id
    log.debug "CurrentMode Before setRoutine : ${location.mode}"
    log.debug "setRoutine called with command: ${command}"
	location.helloHome?.execute(command)
    log.debug "CurrentMode After setRoutine  : ${location.mode}"
}

def setAlarm() {
	def command = params.id
    log.debug "setAlarm called with id ${command}"
    log.debug "Current Alarm State: ${location.currentState("alarmSystemStatus")?.value}"
    sendLocationEvent(name: "alarmSystemStatus", value: command)
    log.debug "Changed Alarm State: ${location.currentState("alarmSystemStatus")?.value}"
}

def setMode() {
	def command = params.id
    log.debug "CurrentMode Before setMode : ${location.mode}"
	log.debug "setMode called with id ${command}"
    setLocationMode(command)
    log.debug "CurrentMode After setMode  : ${location.mode}"
}

def toggleSwitch() {
    def command = params.id
    log.debug "toggleSwitch called with id ${command}"
    switches.each {
        if(it.id == command)
        {
            log.debug "Found switch ${it.displayName} with id ${it.id} with current value ${it.currentSwitch}"
            if(it.currentSwitch == "on") {
                log.debug "Turning ${it.displayName} OFF"
                it.off()
            } else {
                log.debug "Turning ${it.displayName} ON"
                it.on()
            }
            return
        }
    }
}

def toggleValve() {
	def command = params.id
	log.debug "toggleValve called with id ${command}"
    valves.each {
    	if(it.id == command)
        {
        	log.debug "Found Valve ${it.displayName} with id ${it.id} with current value ${it.currentValve}"
            if(it.currentValve == "close")
            	it.open()
            else
            	it.close()
            return
		}
    }
}
def setMusicPlayer() {
    def id 			= params.id
	def command 	= params.command
    def level 		= params.level
    def presetid 	= params.presetid
    log.debug "setMusicPlayer called with command ${command} for musicplayer id ${id} VolumeParm=${level} and presetid=${presetid}"
    musicplayersWebSocket.each {
        if(it.id == id)  {
            log.debug "Found Music Player: ${it.displayName} with id: ${it.id} with current volume level: ${it.currentVolume}"
            switch (command) {
                case 'level':
                log.debug "Setting New Volume level from ${it.currentVolume} to ${level}"
                it.setVolume(level)
                return
                break
                case 'preset':
                log.debug "Setting Preset to id: ${presetid}"
                it.playPreset(presetid)
                return
                break
                default:
                    if (supportedMusicPlayerDeviceCommands().contains(command)) {
                        log.debug "The Music Playback device was sent command: '${command}'"
                        it."$command"()
                    } else {
                        log.debug "The Music Playback device was sent and invalid playback/track control command: '${command}'"
                    }
                break
                return
            }
        }
    }
}
def setLevel() {
	def command = params.id
    def level = params.level
	log.debug "setLevel called with id ${command} and level ${level}"
    switches.each {
    	if(it.id == command)
        {
        	log.debug "Found switch ${it.displayName} with id ${it.id} with current value ${it.currentSwitch}"
            def fLevel = Float.valueOf(level)
            log.debug "Setting level to ${fLevel}"
            it.setLevel(fLevel)
            return
		}
    }
}
def setColor() {
	def pid = params.id
    def colorName = params?.colorName
    def saturation = params?.saturation
    log.debug "========================================================="
	log.debug "setColor() called with id ${pid}, colorName ${colorName} and saturation ${saturation}"
    switches.each {
        if(it.id == pid)
        {
            log.debug "Found switch ${it.displayName} with id ${it.id} with current color of ${it.currentColor} and is ${it.currentSwitch}"
            if (it.currentSwitch=="off"){it.on()}
			if (it.hasCommand('setColor') & colorName  != null) {
                log.debug "Setting ${it.displayName}'s color to ${colorName}, Hue: ${getHueSatLevel(colorName)} and RGB values: ${colorUtil.hexToRgb(it.currentColor)}"
                it.setColor(getHueSatLevel(colorName))
            }
            if (it.hasCommand('setSaturation') & saturation != null) {
                log.debug "Setting ${it.displayName}'s saturation to: ${saturation.toInteger()}"
                it.setSaturation(saturation.toInteger())
            }
            log.debug "${it.displayName}'s color is now RGB value: ${it.currentColor} = ${colorUtil.hexToRgb(it.currentColor)}, saturation level ${it.currentSaturation}, dimmer level ${it.currentLevel}"
            return
        }
    }
    log.debug "========================================================="
}
def setThermo() {
	def id = params.id
    def cmdType = params.type
    def val = params.val.toInteger()
	log.debug "setThermo called with id ${id} command ${cmdType} and value ${val}"
    if(thermos) {
    thermos.each {
            if(it.id == id) {
            log.debug "setThermo found id ${id}"
                if(cmdType == "mode") {
                    if(val == "auto") {
                        log.debug "Setting thermo to auto"
                        it.auto()
                    }
                    if(val == "heat") {
                        log.debug "Setting thermo to heat"
                        it.heat()
                    }
                    if(val == "cool") {
                        log.debug "Setting thermo to cool"
                        it.cool()
                    }
                    if(val == "off") {
                        log.debug "Setting thermo to off"
                        it.off()
                    }
                }
                if(cmdType == "heatingSetpoint") {
                    log.debug "Setting Heat Setpoint to ${val}"
                    it.setHeatingSetpoint(val)
                }
                if(cmdType == "coolingSetpoint") {
                    log.debug "Setting Cool Setpoint to ${val}"
                    it.setCoolingSetpoint(val)
                }
            }
        }
    }
}
def toggleLock() {
	def command = params.id
	log.debug "toggleLock called with id ${command}"
    def counter = 0

    locks.each {
        if(it.id == command)
        {
            log.debug "Found your lock '${it.displayName}' with device id ${it.id} with current value '${it.currentLock}'"
            if(it.currentLock == "locked") {
                it.unlock()
            }
            else if(it.currentLock == "unlocked") {
                it.lock()
            }
            else {
                log.debug "Non-supported toggle state for lock ${it.displayName} state ${it.currentLock} let's not do anything"
                return
            }
            log.debug "Lock Refresh() Loop: ${counter} & LockStatus: ${it.currentLock}"
            return
        }
    }
}

def getBatteryInfo(dev) {
//    if (dev.capabilities.any { it.name.contains('Lock') } == true) log.debug "${dev} Attributes/Capabilities: ${dev.supportedAttributes}"

//    log.debug "batteryExcludedDevices = ${batteryExcludedDevices}"
    if (batteryExcludedDevices) {
        if (batteryExcludedDevices.contains(dev.id)) {
            log.debug "${dev} Battery Level: Excluded in BitBar Preference"
            return "N/A"
        }
    }
    if (dev.capabilities.any { it.name.contains('Battery') } == true) {
        def batteryMap
        try {
//            batteryMap = dev.currentBattery
            batteryMap = dev.currentValue("battery")
//            log.debug "${dev} Battery Level: ${batteryMap}%"
        }
        catch (all) {
            return "N/A"
        }
        if(batteryMap) {
            if(state.batteryWarningPct == null || state.batteryWarningPct.toInteger() < 0 || state.batteryWarningPct.toInteger() > 100 ) {
                state.batteryWarningPct = 50
            }
            if(batteryMap.toInteger() <= state.batteryWarningPct.toInteger()){
                return ["${batteryMap}%", batteryWarningPctEmoji == null?" :grimacing: ":" " + batteryWarningPctEmoji + " "]
            }
            return ["${batteryMap}%", ""]
        }
    }
    return "N/A"
}

def getAlarmData() {
	def resp = []
    alarms.each {
        resp << [name: it.displayName, value: it.currentAlarm, battery: getBatteryInfo(it)];
//        log.debug "Alarm: ${resp}"
    }
    resp << [ name: "shm", value: state.shm]
    return resp
}
def getTempData() {
	def resp = []
    temps.each {
        resp << [name: it.displayName, value: it.currentTemperature, battery: getBatteryInfo(it), eventlog: getEventsOfDevice(it)];
    }
    resp.sort { -it.value }
    return resp
}
def getContactData() {
	def resp = []
    contacts.each {
        resp << [name: it.displayName, value: it.currentContact, battery: getBatteryInfo(it), eventlog: getEventsOfDevice(it)];
    }
    return resp
}
def getRelativeHumidityMeasurementData() {
	def resp = []
    relativeHumidityMeasurements.each {
        resp << [name: it.displayName, value: it.currentHumidity, battery: getBatteryInfo(it), eventlog: getEventsOfDevice(it)];
    }
    return resp
}
def getPresenceData() {
	def resp = []
    def eventlogData = []
    def timeFormatString = timeFormatBool?'EEE MMM dd HH:mm z':'EEE MMM dd hh:mm a z'
    presences.each {
		it.events().each {
        }
        resp << [name: it.displayName, value: it.currentPresence, battery: getBatteryInfo(it), eventlog: getEventsOfDevice(it)];
    }
    return resp
}
def getMotionData() {
	def resp = []
    motions.each {
        resp << [name: it.displayName, value: it.currentMotion, battery: getBatteryInfo(it), eventlog: getEventsOfDevice(it)];
    }
    return resp
}
def getSwitchData() {
    def resp = []
    switches.each {
        def x, isRGBbool, hue, saturation, colorRGBName, r, g, b, RGBHex, colorRGBList = null
        isRGBbool = it.hasCommand('setColor')
        hue = it.currentHue
        saturation = it.currentSaturation
        if (isRGBbool) {
            if (it.hasCommand('refresh')) {it.refresh()}
            RGBHex = it.currentColor
            try {
                colorRGBList = colorUtil.hexToRgb(RGBHex)
            } catch (all) {
                log.debug "Trapped Error: colorRGBList = colorUtil.hexToRgb(RGBHex): RGBHex = ${RGBHex}"
                colorRGBList=[0,0,0]
            }
            r = colorRGBList[0]
            g = colorRGBList[1]
            b = colorRGBList[2]
            if      (r>=g & g>=b) {colorRGBName = "Red–yellow"}
            else if (g>r  & r>=b) {colorRGBName = "Yellow–green"}
            else if (g>=b & b>r ) {colorRGBName = "Green–cyan"}
            else if (b>g  & g>r ) {colorRGBName = "Cyan–blue"}
            else if (b>r  & r>=g) {colorRGBName = "Blue–magenta"}
            else if (r>=b & b>g ) {colorRGBName = "Magenta–red"}
            else {colorRGBName = ""}
//            log.debug "colorRGBName = ${colorRGBName.padRight(20,"-")}"
            x = [
                name		: it.displayName,
                value		: it.currentSwitch,
                colorRGBList: colorRGBList,
                RGBHex		: RGBHex,
                dimmerLevel : it.currentLevel,
                hue			: hue ? hue.toFloat().round() : hue,
                saturation	: saturation ? saturation.toFloat().round() : saturation
            ]
//            x.each {k, v -> log.debug "${k.padRight(20,"-")}: ${v}" }
        }
        resp << [
            name		: it.displayName,
            value		: it.currentSwitch,
            id 			: it.id,
            isDimmer 	: it.hasCommand('setLevel'),
            colorRGBName: colorRGBName,
            dimmerLevel : it.currentLevel,
            isRGB		: isRGBbool,
            hue			: hue ? hue.toFloat().round() : hue,
            saturation	: saturation ? saturation.toFloat().round() : saturation,
            eventlog	: getEventsOfDevice(it)
        ]
    }
    return resp
}
def getLockData() {
	def resp = []
    locks.each {
        resp << [name: it.displayName, value: it.currentLock, id : it.id, battery: getBatteryInfo(it), eventlog: getEventsOfDevice(it)];
    }
    return resp
}
def getMusicPlayerData() {
    def resp = []
    musicplayersWebSocket.each {
        resp << [
            name							: it.displayName,
            manufacturer					: it?.getManufacturerName()?:it?.currentDeviceStyle?:null,
            groupRolePrimary				: it?.currentGroupRole=='primary',
            groupRole						: it?.currentGroupRole,
            id 								: it.id,
            level							: it.currentVolume,
            mute							: it.currentMute,
            presets							: it.currentPresets?:null,
            status							: it.currentPlaybackStatus,
            audioTrackData					: it.currentAudioTrackData?:null,
            alexaPlaylists 					: it.currentAlexaPlaylists?:null,
            supportedCommands				: supportedMusicPlayerDeviceCommands(),
            groupVolume						: it.currentGroupVolume?:null
        ];
    }

    return resp
}
def getThermoData() {

	def resp = []
    if(thermos) {
        thermos.each {
            def timespan = now() - state.lastThermostatOperatingState
            resp << [displayName: it.displayName,
                    id: it.id,
                    thermostatOperatingState: it.currentThermostatOperatingState,
                    thermostatMode: it.currentThermostatMode,
                    coolingSetpoint: it.currentCoolingSetpoint,
                    heatingSetpoint: it.currentHeatingSetpoint,
                    lastOperationEvent: timespan
                    ];
        }
    }
//    log.debug "getThermoData: ${resp[2]}"
    return resp
}
def getWaterData() {
	def resp = []
    waters.each {
        resp << [name: it.displayName, value: it.currentWater, id : it.id, battery: getBatteryInfo(it), eventlog: getEventsOfDevice(it)];
    }
    return resp
}
def getValveData() {
	def resp = []
    valves.each {
        resp << [name: it.displayName, value: it.currentValve, id : it.id, battery: getBatteryInfo(it), eventlog: getEventsOfDevice(it)];
    }
    return resp
}

def getMainDisplayData() {
    def displaySensorCapabilitySize = displaySensorCapability?displaySensorCapability.size():0
    def returnCapability
    def returnName
    def returnValue
    def returnEmoji
    def fieldName
    def fieldValue
    def resp = []

    if (displaySensorShowName) {
        returnName = "shm"
        returnCapability = returnName
        returnValue = "${returnName}${location.currentState("alarmSystemStatus")?.value}"
        returnEmoji = returnValue
        if (returnValue) {
            resp << [name: returnName, label: 'Smart Home Monitor', value: returnValue, capability: returnCapability, emoji: returnEmoji];
        }
    }

    if (displaySensorCapabilitySize == 0) {
        resp << [name: 'N/A', label: 'N/A', value: 'N/A', capability: 'N/A', emoji: 'unknown'];
    } else {
        for(int i = 0;i<displaySensorCapabilitySize;i++) {
            fieldName = "displaySensor${i}"
            fieldValue = settings.find{ it.key == fieldName }?.value
            if(fieldValue) {
                // log.debug "${i} --> ${key} : ${fieldValue.displayName}"
                // log.debug "${i} --> ${key} : ${fieldValue.currentValue(displaySensorCapability[i].replaceAll(/Measurement$|Sensor$/,''))}"
                returnName = fieldValue.displayName
                returnCapability = displaySensorCapability[i]
                returnValue = fieldValue.currentValue(displaySensorCapability[i].replaceAll(/Measurement$|Sensor$/,''))
                // log.debug "${i}-> returnValue = ${returnValue}"

                switch (returnValue) {
                    case ~/[0-9]*\.?[0-9]+/:
                    returnEmoji = 'number'
                    break
                    case 'on':
                    case 'off':
                    case 'open':
                    case 'closed':
                    case 'locked':
                    case 'unlocked':
                    returnEmoji = returnValue
                    break
                    default:
                        returnEmoji = 'unknown'
                    break
                }
                resp << [name: returnName, label: fieldValue.displayName, 'value' : returnValue, capability: returnCapability, emoji: returnEmoji];
            }
        }
    }
    return resp
}

def getStatus() {
    def timeStamp = new Date().format("h:mm:ss a", location.timeZone)
    log.info "HE BitBar getStatus() started at ${timeStamp}"
    state.bbpluginfilename 	= params.bbpluginfilename
    state.bbpluginversion 	= params.bbpluginversion
    state.pythonAppVersion 	= params.pythonAppVersion
    state.pythonAppPath 	= params.path
    getAppInfo(params)
    if (debugBool) {
        log.info "Mac BitBar Plugin Folder: ${params.path}"
        log.info "BitBar Output App Version: ${appVersion()}, HE_Python_Logic.py Version: ${params.pythonAppVersion}, ${params.bbpluginfilename} Version: ${params.bbpluginversion}"
    }
    def alarmData = getAlarmData()
    def tempData = getTempData()
    def contactData = getContactData()
    def presenceData = getPresenceData()
    def motionData = getMotionData()
    def switchData = getSwitchData()
    def lockData = getLockData()
    def thermoData = getThermoData()
    def mainDisplay = getMainDisplayData()
    def musicData = getMusicPlayerData()
    def relativeHumidityMeasurementData = getRelativeHumidityMeasurementData()
    def waterData = getWaterData()
    def valveData = getValveData()
    def optionsData = [ "useImages" 				: useImages,
                       "useAlbumArtworkImages" 		: useAlbumArtworkImages,
                       "sortSensorsName" 			: sortSensorsName,
                       "sortSensorsActive" 			: sortSensorsActive,
                       "mainMenuMaxItemsTemps" 		: mainMenuMaxItemsTemps,
                       "mainMenuMaxItemsMusicPlayers": mainMenuMaxItemsMusicPlayers,
                       "mainMenuMaxItemsContacts" 	: mainMenuMaxItemsContacts,
                       "mainMenuMaxItemsSwitches" 	: mainMenuMaxItemsSwitches,
                       "mainMenuMaxItemsMotion" 	: mainMenuMaxItemsMotion,
                       "mainMenuMaxItemsLocks" 		: mainMenuMaxItemsLocks,
                       "mainMenuMaxItemsWaters" 	: mainMenuMaxItemsWaters,
                       "mainMenuMaxItemsValves" 	: mainMenuMaxItemsValves,
                       "mainMenuMaxItemsRelativeHumidityMeasurements" : mainMenuMaxItemsRelativeHumidityMeasurements,
                       "showSensorCount"			: showSensorCount,
                       "mainMenuMaxItemsPresences" 	: mainMenuMaxItemsPresences,
                       "motionActiveEmoji"			: motionActiveEmoji,
                       "motionInactiveEmoji"		: motionInactiveEmoji,
                       "contactOpenEmoji"		 	: contactOpenEmoji,
                       "contactClosedEmoji"		 	: contactClosedEmoji,
                       "presenscePresentEmoji"		: presenscePresentEmoji,
                       "presensceNotPresentEmoji"	: presensceNotPresentEmoji,
                       "colorBulbEmoji"				: colorBulbEmoji,
                       "dimmerBulbEmoji"			: dimmerBulbEmoji,
                       "presenceDisplayMode"		: presenceDisplayMode,
                       "numberOfDecimals"			: numberOfDecimals,
                       "matchOutputNumberOfDecimals": matchOutputNumberOfDecimals,
                       "dimmerValueOnMainMenu"		: dimmerValueOnMainMenu,
                       "mainFontName"				: mainFontName,
                       "mainFontSize"				: mainFontSize,
                       "subMenuFontName"			: subMenuFontName,
                       "subMenuFontSize"			: subMenuFontSize,
                       "subMenuFontColor"			: subMenuFontColor,
                       "subMenuMoreColor"			: subMenuMoreColor,
                       "subMenuCompact"				: subMenuCompact,
                       "fixedPitchFontName"			: fixedPitchFontName,
                       "fixedPitchFontSize"			: fixedPitchFontSize,
                       "fixedPitchFontColor"		: fixedPitchFontColor,
                       "hortSeparatorBarBool"       : hortSeparatorBarBool,
                       "batteryWarningPct"			: batteryWarningPct,
                       "batteryWarningPctEmoji"		: batteryWarningPctEmoji,
                       "shmDisplayBool"				: shmDisplayBool,
                       "eventsTimeFormat"			: eventsTimeFormat,
                       "favoriteDevices"			: favoriteDevices,
                       "eventsShow"					: eventsShow,
                       "colorChoices"				: colorChoices ? colorChoices : [
                           "Soft White","White","Daylight","Warm White","Red","Green","Blue","Yellow","Orange","Purple","Pink","Cyan"
                       ],
                       "sortTemperatureAscending"	: (sortTemperatureAscending == null) ? false : sortTemperatureAscending
                      ]
    def resp = [ "Version" : appVersion(),
                "Alarm Sensors" : alarmData,
                "Temp Sensors" : tempData,
                "Contact Sensors" : contactData,
                "Presence Sensors" : presenceData,
                "Motion Sensors" : motionData,
                "Switches" : switchData,
                "Locks" : lockData,
                "Music Players" : musicData,
                "Thermostats" : thermoData,
                "Routines" : routinesDisplayBool?location.helloHome?.getPhrases()*.label:null,
                "Modes" : modesDisplayBool?location.modes:null,
                "CurrentMode" : modesDisplayBool?["name":location.mode]:null,
                "MainDisplay" : mainDisplay,
                "RelativeHumidityMeasurements" : relativeHumidityMeasurementData,
                "Waters" : waterData,
                "Valves" : valveData,
                "Options" : optionsData]

    if (debugDevices != null) {
        log.debug "debugDevices = ${resp."${debugDevices}"}"
        resp."${debugDevices}".each{
            k ->
            k.each{
                m, n ->
                if (m == "name") {return}
                log.debug "${k.name}-> ${m} : ${n}"
            }
        }
    }
    log.info "getStatus routine completed. Returning ${resp.size()} keys"
    return resp
}

private mainPage() {
    if (app.getInstallationState()=='INCOMPLETE'){getAppInfo()}
    def currentYear = new Date().format("yyyy", location.timeZone)
    dynamicPage(name: "mainPage", uninstall:true, install:true, submitOnChange: true) {
        def apiSetupState = (state.accessToken==null)?'Please complete API setup!':'API Setup is complete!'
        section( "API Access Setup" ) {
            if (isST) {
                href name: "APIPageLink", title: "${apiSetupState}", description: (state.endpoint == null)?"You must add these API strings to ST_Python_Logic.cfg":"", page: "APIPage"
            } else {
                app.updateSetting("testAPI", false)
                app.updateSetting("okSend", false)
                app.updateSetting("sendAPI", false)
                href name: "APIPageLink", title: "${apiSetupState}", description: (state.endpoint == null)?"You must add these API strings to HE_Python_Logic.cfg":"", page: "APIPage"
            }
        }
        section("Sensor/Device Management & Setup") {
            href name: "devicesManagementPageLink", title: "Select sensors/devices", description: "", page: "devicesManagementPage"
        }
        section("Mac Menu Bar & SubMenu Display Options") {
            href name: "optionsPageLink", title: "Select display options", description: "", page: "optionsPage"
        }
        section {
            if (isST) {
                paragraph image: "https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/STBitBarApp-V2.png",
                    title: "ST BitBar App Version Information",
                    required: false,
                    "${state.bbFolder?:''}\n\n${state.bbVersions?:''}"
            } else {
                section() {
                    paragraph("${bitBarLogo}" +
                              "<a href='https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=D4PYWK33KARSS&source=url'>Please consider donating to this application via PayPal™.</a><br>" +
                              "<small><i>Copyright \u00a9 2018-${currentYear} SandersSoft™ Inc - All rights reserved.</i></small><br>" +
                              "==> ${state.bbVersions}<br>${state.bbFolder}")
                }

            }
        }
        section(hideable: true, hidden: true, "Debuging Options for IDE Live Logging") {
            input "debugBool", "bool",
                title: "Display general debug and informational messages in the ST IDE Live Logging View",
                default: false,
                required: false
            input "debugDevices", "enum",
                title: "Select a Sensor capability category to send debuging information to IDE Live Logging Window",
                options: ["Alarm Sensors", "Temp Sensors", "Contact Sensors", "Presence Sensors", "Motion Sensors", "Switches", "Locks",
                          "Music Players", "Thermostats", "RelativeHumidityMeasurements"].sort(),
                required: false,
                default: false,
                multiple: false
        }
    }
}

def APIPage() {
    dynamicPage(name: "APIPage") {
        section("API Setup") {
            if (!state.accessToken) {
                paragraph "Required: The API has not been setup. Tap below to enable it."
                href name: "enableAPIPageLink", title: "Enable API", description: "", page: "enableAPIPage"
            }
            if (isST) {
                paragraph "API has been setup. Using a text editor, please enter the following two API strings in your 'ST_Python_Logic.cfg' file located in your Apple Mac BitBar Plugins directory."
                paragraph "smartAppURL=${state.endpointURL}"
                paragraph "secret=${state.accessToken}"
            } else {
                state.endpoint=getFullLocalApiServerUrl()+ "/?access_token=${state.accessToken}"
                def localUri = getFullLocalApiServerUrl()+ "/Test/" + "?access_token=${state.accessToken}"
                paragraph "API has been setup!<br><br>Using a text editor, please enter the following two strings in your 'HE_Python_Logic.cfg' file located in your Apple Mac BitBar Plugins directory."
                paragraph "<html><head><style>p.ex1{border: 5px solid red; padding-left: 50px;}</style></head><body><p class='ex1'><b>smartAppURL=${state.endpointURL}/<br>"+"secret=${state.accessToken}</b></body></html>"
                input "testAPI", "bool",
                    title: "Select to test the http API access to '${app.name}'?",
                    submitOnChange: true,
                    required: false
                if (testAPI) {
                    app.updateSetting("testAPI", false)
                    def hubHttpIp = "http://${location.hub.localIP}:8080"
                    try {
                        log.debug "Testing http GET app access: '${localUri}'"
                        def params = [
                            uri        : hubHttpIp,
                            path       : "/apps/api/${app.getId()}/Test/",
                            query      : ["access_token": "${state.accessToken}"]
                        ]
                        // log.debug "getHttp params Map = '${params}'"
                        // "http://10.0.0.80:8080/apps/api/655/Test/?access_token=5dd86abc-59af-452e-b8c1-fbf676723174"
                        httpGet(params) { resp ->
                            if (resp.success) {
                                paragraph("${resp.data}")
                                paragraph(doneImage)
                            } else {
                                paragraph("Failed: ${resp.data}")
                            }
                        }
                    } catch (Exception e) {
                        log.warn "Test Call to on failed: ${e.message}"
                        paragraph("Test Call to on failed: ${e.message}")
                    }
                }
            }
            // paragraph("Use the following URI to test the access of the '${app.name}' endpoint:<br />Local: <a href='${localUri}'>Local Test URL</a>")

            input "sendAPI", "bool",
                title: "Select to send these two secret strings as a notification message",
                submitOnChange: true,
                required: false
            if (sendAPI) {
                if (isST) {
                    input "phone", "phone",
                        title: "Enter the US mobile phone number",
                        submitOnChange: true,
                        required: true
                    if (sendAPI && phone) {
                        href name: "APISendSMSPageLink", title: "Send API Now to ${phone.replaceFirst('(\\d{3})(\\d{3})(\\d+)', '($1) $2-$3')}", description: "", page: "APISendSMSPage"
                    }
                } else {
                    section("Enable Pushover™ and/or Twilio™ service(s). (Must install virtual device(s) and have an active service account):") {
                        input ("pushoverEnabled", "bool", title: "Use Pushover™ and/or Twilio™ Service(s) for Alert Notifications", required: false, submitOnChange: true)
                        if (pushoverEnabled) {
                            input(name: "pushoverDevices", type: "capability.notification", title: "", required: false, multiple: true,
                                  description: "Select notification device(s)", submitOnChange: true)
                            paragraph ""
                        }
                        if (pushoverDevices) {
                            input ("okSend", "bool", title: "Select to send API strings NOW to ${pushoverDevices}?", defaultValue: false, required: false, submitOnChange: true)
                            if (okSend) {
                                app.updateSetting("okSend", false)
                                def msgData = "Add the following two API strings to your ST_Python_Logic.cfg in the BitBar Plugins Mac Folder"
                                msgData += "\nsmartAppURL=${state.endpointURL}"
                                msgData += "\nsecret=${state.accessToken}"
                                if (settings.pushoverDevices != null) {
                                    settings.pushoverDevices.each {							// Use notification devices on Hubitat
                                        it.deviceNotification(msgData)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        section() {
            href "disableAPIPage", title: "Disable/Reset API (Only use this if you want to generate a new oauth secret)", description: ""
        }
    }
}

def APISendSMSPage() {
    dynamicPage(name: "APISendSMSPage") {
        section() {
            if (sendAPI && phone) {
                paragraph "BitBar Output API strings sent to ${phone.replaceFirst('(\\d{3})(\\d{3})(\\d+)', '($1) $2-$3')}"
                sendPush("BitBar Output API strings sent to ${phone.replaceFirst('(\\d{3})(\\d{3})(\\d+)', '($1) $2-$3')}")
                sendSms(phone, "Add the following two API strings to your ST_Python_Logic.cfg in the BitBar Plugins Mac Folder")
                sendSms(phone, "smartAppURL=${state.endpointURL}")
                sendSms(phone, "secret=${state.accessToken}")
            }
        }
    }
}


def enableAPIPage() {
	dynamicPage(name: "enableAPIPage") {
		section() {
			if (initializeAppEndpoint()) {
				paragraph "Woo hoo! The API is now enabled. Brace yourself, though. I hope you don't mind typing long strings of gobbledygook. Sorry I don't know of an easier way to transfer this to the PC. Anyways, tap Done to continue"
			}
			else {
				paragraph "It looks like OAuth is not enabled. Please login to your SmartThings IDE, click the My SmartApps menu item, click the 'Edit Properties' button for the BitBar Output App. Then click the OAuth section followed by the 'Enable OAuth in Smart App' button. Click the Update button and BAM you can finally tap Done here.", title: "Looks like we have to enable OAuth still", required: true, state: null
			}
		}
	}
}

def disableAPIPage() {
	dynamicPage(name: "disableAPIPage", title: "") {
		section() {
			if (state.endpoint) {
				try {
					revokeAccessToken()
				}
				catch (e) {
					log.debug "Unable to revoke access token: $e"
				}
				state.endpoint = null
			}
			paragraph "It has been done. Your token has been REVOKED. You're no longer allowed in API Town (I mean, you can always have a new token). Tap Done to continue."
		}
	}
}

def devicesManagementPage() {
    dynamicPage(name:"devicesManagementPage") {

        section("Sensors & Devices (Required)") {
            href name: "devicesPageLink", title: "Select the sensors to display/control", required: true, description: "", page: "devicesPage"
        }
        section('Main Menu Bar Icons (Required)') {
            href name: "devicesTopMenuBarPageLink", title: "Select icons for the Main Menu Bar", required: true, description: "", page: "devicesTopMenuBarPage"
        }
        section("Favorite Sensors (Mix & Match) to display in separate 1st category section on subMenu") {
            paragraph "The 'Favorite' sensors submenu is a section on the BitBar submenu to locate a few sensors that you wish to display/monitor quickly.  You cannot control them from this menu, just display."
            input "favoriteDevices", "enum",
                title: "Favorite sensors (Optional)",
                options: getAllDevices(),
                required: false,
                multiple: true
        }
    }
}

def devicesTopMenuBarPage() {
    dynamicPage(name:"devicesTopMenuBarPage") {
        section("MacOS Main Menu BitBar: Select one device to display a status.") {
            paragraph "The MacOS Main Menu Bar runs along the top of the screen on your Mac"
            input name: "displaySensorCapability", type: "enum",
                title: "Mac Menu Bar: Select up to 4 SmartThings Sensor Capabilities for the Menu Bar Icons",
                options: ['contactSensor':'Contact','lock':'Lock','switch':'Switch','temperatureMeasurement':'Temperature Measurement'],
                multiple: true,
                submitOnChange: true,
                required: false
            if (displaySensorCapability) {
                def displaySensorCapabilitySize = displaySensorCapability.size()
                if (displaySensorCapabilitySize>1) {
                    paragraph "The ${displaySensorCapabilitySize} device status icons will cycle every few seconds in the MacOS Main Menu Bar"
                }
                for(int i = 0;i<displaySensorCapabilitySize;i++) {
                    input "displaySensor${i}", "capability.${displaySensorCapability[i]}",
                        title: "Select the one ${displaySensorCapability[i].replaceAll(/Measurement$|Sensor$/,'').toUpperCase()} sensor to place in the Mac Main Menu Bar",
                        multiple: false,
                        submitOnChange: true,
                        required: true
                }
            }
        }
        section("Display Smart Home Monitor in Main Menu Bar") {
            def displaySensorCapabilityMessage = displaySensorCapability?"along with the ${displaySensorCapability.size()} sensor(s) selected above":''
            input "displaySensorShowName", "bool",
                title: "Add the Smart Home Monitor status icon to the Main Menu Bar ${displaySensorCapabilityMessage}",
                submitOnChange: true,
                default: false,
                required: true
        }
    }
}


def devicesPage() {
    dynamicPage(name:"devicesPage") {
        section ("Choose the sensor devices to be displayed & controlled in the ST BitBar menu") {
            paragraph "Select devices that you want to be displayed below the top MacOS Main Menu Bar (in the BitBar Sub-menu)."
            input "alarms", "capability.alarmSensor",
                title: "Which Alarm Sensors?",
                multiple: true,
                hideWhenEmpty: true,
                required: false
            input "contacts", "capability.contactSensor",
                title: "Which Contact Sensors?",
                multiple: true,
                hideWhenEmpty: true,
                required: false
            input "relativeHumidityMeasurements", "capability.relativeHumidityMeasurement",
                title: "Which Relative Humidity Measurement Sensors?",
                multiple: true,
                hideWhenEmpty: true,
                required: false
            input "locks", "capability.lock",
                title: "Which Locks?",
                multiple: true,
                hideWhenEmpty: true,
                required: false
            input "musicplayersWebSocket", "capability.AudioTrackData",
                title: "Which Media Playback Devices (ie. Sonos, Amazon, Google, etc)?",
                multiple: true,
                hideWhenEmpty: true,
                required: false
            input "motions", "capability.motionSensor",
                title: "Which Motion Sensors?",
                multiple: true,
                hideWhenEmpty: true,
                required: false
            input "presences", "capability.presenceSensor",
                title: "Which Presence Sensors?",
                multiple: true,
                hideWhenEmpty: true,
                required: false
            input "switches", "capability.switch",
                title: "Which Lights & Switches?",
                multiple: true,
                hideWhenEmpty: true,
                required: false
            input "temps", "capability.temperatureMeasurement",
                title: "Which Temperature Sensors?",
                multiple: true,
                hideWhenEmpty: true,
                required: false
            input "thermos", "capability.thermostat",
                title: "Which Thermostats?",
                multiple: true,
                hideWhenEmpty: true,
                required: false
            input "waters", "capability.waterSensor",
                title: "Which Water Sensors?",
                multiple: true,
                hideWhenEmpty: true,
                required: false
            input "valves", "capability.valve",
                title: "Which Valves?",
                multiple: true,
                hideWhenEmpty: true,
                required: false
                }
    }
}

def iconsPage() {
    dynamicPage(name:"iconsPage", hideWhenEmpty: true) {
        section("BROWSE Emoji Website Valid 'ShortCodes' List") {
            href(name: "hrefNotRequired",
                 title: "BROWSE Emoji Website Valid 'ShortCodes' List",
                 required: false,
                 image: "http://emojipedia.org/static/img/favicons/mstile-144x144.png",
                 style: "external",
                 url: "http://www.webpagefx.com/tools/emoji-cheat-sheet/",
                 description: "tap here to view valid list of Emoji names in your mobile browser"
                )
        }
        section("Optional: Customize Sensor Type/Status Emoji Naming Display Options") {
            input "motionActiveEmoji", "text",
                title: "Emoji ShortCode ':xxx:' to Display for Motion Sensor = 'Active' Default='⇠⇢'",
                required: false
            input "motionInactiveEmoji", "text",
                title: "Emoji ShortCode ':xxx:' to Display for Motion Sensor = 'Inactive' Default='⇢⇠'",
                required: false
            input "contactOpenEmoji", "text",
                title: "Emoji ShortCode ':xxx:' to Display for Contact Sensor = 'Open' Default='⇠⇢'",
                required: false
            input "contactClosedEmoji", "text",
                title: "Emoji ShortCode ':xxx:' to Display for Contact Sensor = 'Closed' Default='⇢⇠'",
                required: false
            input "presenscePresentEmoji", "text",
                title: "Emoji ShortCode ':xxx:' to Display for Presence Sensor = 'Present' Default=':home:'",
                required: false
            input "presensceNotPresentEmoji", "text",
                title: "Emoji ShortCode ':xxx:' to Display for Presence Sensor = 'Not Present' Default=':x:'",
                required: false
            input "dimmerBulbEmoji", "text",
                title: "Emoji ShortCode ':xxx:' to Display for Switch DTH='Dimmer Capable Bulb'. Default=':sunny:'",
                required: false
            input "colorBulbEmoji", "text",
                title: "Emoji ShortCode ':xxx:' to Display for Switch DTH='Color Capable Bulb'. Default=':rainbow:'",
                required: false
            input "presenceDisplayMode", "enum",
                title: "Presence Display Mode Number (See Numeric Values Explanation Below)",
                multiple: false,
                options: [0,1,2,3],
                required: false
            paragraph image: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Emblem-notice.svg/2000px-Emblem-notice.svg.png",
                title: "Presence Display Mode",
                "0 = Default Mode: Do not sort or hide sensors by presence status\n" +
                "1 = Sort by Presence: Sensors will be sorted by their status; 'Present' shown first\n" +
                "2 = Show Sensors Not Present in Submenu: All sensors that are not present will be moved to a submenu\n" +
                "3 = Hide Sensors Not Present: Sensors that are currently not present will be hidden"
        }
    }
}

def fontsPage() {
    dynamicPage(name:"fontsPage", hideWhenEmpty: true) {
        section("Link: BROWSE List of VALID typeface names included with Apple macOS") {
            href(name: "hrefNotRequired",
                 title: "BROWSE List of typeface names included with Apple macOS",
                 required: false,
                 image: "http://iconion.com/posts/images/scale-to-size-icons.jpg",
                 style: "external",
                 url: "https://en.wikipedia.org/wiki/List_of_typefaces_included_with_macOS",
                 description: "Tap this area to view a list of typeface names included with Apple macOS in your mobile browser")
        }
        section("Optional Main Menu: DISPLAY FONTS, COLORS & SEPARATOR BARS: Mac Font Name for Display (warning: The Font Name MUST exist on the Mac.  Leave blank for 'Menlo'") {
            input "mainFontName", "text",
                title: "Mac 'Main-Menu Bar' Font Name (default font is 'Menlo' if field is left empty).  Color auto-changes based on Primary Thermostat Operation Mode (Heat/Cool) from/to Red/Blue",
                default: "Menlo",
                required: false
            input "mainFontSize", "number",
                title: "Mac 'Main-Menu Bar' Font Pitch Size (default is '14').",
                default: 14,
                required: false
        }
        section("Optional Data Display: DISPLAY FONTS, COLORS & SEPARATOR BARS: Mac Font Name for Display (warning: The Font Name MUST exist on the Mac.  Leave blank for 'Menlo'") {
            input "fixedPitchFontName", "enum",
                title: "Data: Fixed Font Name (default font is 'Menlo' if field is left empty)",
                default: "Menlo",
                options: ["Menlo","Monaco","Consolas","Courier","MingLIU"],
                required: false
            input "fixedPitchFontSize", "number",
                title: "Data: Fixed Font Pitch Size (default is '14').",
                default: 14,
                required: false
            input "fixedPitchFontColor", "enum",
                title: "Data: Fixed Font Color (default Color is 'Black' if field left blank.  If Mac is in 'Dark Mode', Font Color will be set to 'White')",
                default: "black",
                options: colorChoiceList(),
                multiple: false,
                required: false
        }
        section("Sub-Menu Display Options") {
            input "subMenuCompact", "bool",
                title: "Compact Sub-Menus (No repeating title in the submenu header or breakout menus)",
                required: false
            input "hortSeparatorBarBool", "bool",
                title: "Use Horizontal Separator Lines to Separate ST Device Categories (Default is True)",
                required: false
            input "subMenuFontName", "text",
                title: "Mac BitBar Sub-Menu ST Category Names: Font Name (default font is 'Menlo' if field is left empty).",
                default: "Menlo",
                required: false
            input "subMenuFontSize", "number",
                title: "Mac BitBar Sub-Menu ST Category Names: Font Pitch Size (default is '12').",
                default: 12,
                required: false
            input "subMenuFontColor", "enum",
                title: "Mac BitBar Sub-Menu ST Category Names: Font Color (default Color is 'Black' if field left blank.  If Mac is in 'Dark Mode', Font Color will be set to 'White')",
                default: "black",
                options: colorChoiceList(),
                multiple: false,
                required: false
            input "subMenuMoreColor", "enum",
                title: "More... sub-menu: Font Color (default 'black')",
                default: "black",
                options: colorChoiceList(),
                multiple: false,
                required: false
        }

    }
}

def categoryPage() {
    dynamicPage(name:"categoryPage", hideWhenEmpty: true) {
        section("Optional: Number of Items per ST Sensor category to display in the Main Menu before moving additional sensors to a More... sub-menu.  Leave these number fields blank for Auto-Size (Show only Active Sensors in Main Menu)") {
            input "mainMenuMaxItemsContacts", "number",
                title: "Min Number of Contact Sensors to Display - Leave blank to Auto-Size",
                required: false
            input "mainMenuMaxItemsRelativeHumidityMeasurements", "number",
                title: "Min Number of Relative Humidity Measurement Sensors to Display - Leave blank to Auto-Size",
                required: false
            input "mainMenuMaxItemsLocks", "number",
                title: "Min Number of Locks to Display - Leave blank to Auto-Size",
                required: false
            input "mainMenuMaxItemsMusicPlayers", "number",
                title: "Min Number of Music Players to Display - Leave blank to Auto-Size",
                required: false
            input "mainMenuMaxItemsMotion", "number",
                title: "Min Number of Motion Sensors to Display - Leave blank to Auto-Size",
                required: false
            input "mainMenuMaxItemsPresences", "number",
                title: "Min Number of Presence Sensors to Display - Leave blank to Auto-Size",
                required: false
            input "mainMenuMaxItemsSwitches", "number",
                title: "Min Number of Switch Sensors to Display - Leave blank to Auto-Size",
                required: false
            input "mainMenuMaxItemsTemps", "number",
                title: "Min Number of Temperature Sensors to Display - Leave blank to Show All Temperature Sensors",
                required: false
            input "mainMenuMaxItemsValves", "number",
                title: "Min Number of Valves to Display - Leave blank to Show All Valves",
                required: false
            input "mainMenuMaxItemsWaters", "number",
                title: "Min Number of Water Sensors to Display - Leave blank to Show All Water Sensors",
                required: false
        }
    }
}

def eventsPage() {
    dynamicPage(name:"eventsPage", hideWhenEmpty: true) {
        section("Optional: Display Event History for Devices") {
            input "eventsShow", "bool",
                title: "Events: Show Event History?",
                required: false
                }
        section(hideable: true, hidden: true, "Optional: Event History Options for Devices") {
            input "eventsMax", "number",
                title: "Events: Maximum number of Device Events to Display [Default: 10, Max 100]",
                default: "10",
                required: false
            input "eventsDays", "number",
                title: "Events: Number of Days from Today to Retrieve Device Events [Default: 1, Max 7]",
                default: "1",
                required: false
            input "eventsTimeFormat", "enum",
                title: "Events: DateTime Format: [Default = 12 Hour Clock Format with AM/PM]",
                options: ["12 Hour Clock Format with AM/PM", "Military 24 Hour Clock Format"],
                default: "12 Hour Clock Format with AM/PM",
                required: true
        }
        section("BROWSE Emoji Website Valid 'ShortCodes' List") {
            href(name: "hrefNotRequired",
                 title: "BROWSE Emoji Website Valid 'ShortCodes' List",
                 required: false,
                 image: "http://emojipedia.org/static/img/favicons/mstile-144x144.png",
                 style: "external",
                 url: "http://www.webpagefx.com/tools/emoji-cheat-sheet/",
                 description: "tap here to view valid list of Emoji names in your mobile browser"
                )
        }
    }
}
def batteryPage() {
    dynamicPage(name:"batteryPage", hideWhenEmpty: true) {
        section("Optional: Battery Check for Selected Devices") {
            input "batteryExcludedDevices", "enum",
                title: "Battery: Select Any Devices to Exclude from Battery Check [Default='None']",
                options: getAllDevices(),
                required: false,
                multiple: true
        }
        section("Optional: Battery Level Options for Devices") {
            input "batteryWarningPctEmoji", "text",
                title: "Battery: Emoji ShortCode ':xxx:' to Display for Low Battery Warning [Default=':grimacing:']",
                required: false
            input "batteryWarningPct", "number",
                title: "Battery: Percent Level to Warn for Low Battery in Device [Default: 50, Min 0, Max 100]",
                default: "50",
                required: false
        }
    }
}

def optionsPage() {
    dynamicPage(name:"optionsPage", hideWhenEmpty: true) {
        section("Required: Smart Home Monitor, Modes & Routines") {
        paragraph "Display/Hide SmartThings Modes, Routines and SHM to the BitBar SubMenu to display state & allow control?"
            input "modesDisplayBool", "bool",
                title: "Show SmartThings Modes?",
                default: false,
                required: true
            input "routinesDisplayBool", "bool",
                title: "Show SmartThings Routines?",
                default: false,
                required: true
            input "shmDisplayBool", "bool",
                title: "Show Smart Home Monitor",
                default: false,
                required: true
        }
        section("Required: Use High-Res Images (More CPU required) or Low-Res Emojis") {
			input "useImages", "bool",
				title: "Use high-res images for switch & lock status (green/red images) instead of low-res emojis",
                default: true,
				required: true
			input "useAlbumArtworkImages", "bool",
				title: "Display hi-res album artwork images instead of open new browser tab to display	",
                default: false,
				required: true
        }
        section {
            input "showSensorCount", "bool",
                title: "Show the number of sensors in each sensor category title",
                default: false,
                required: true
        }
        section("Required: Sort sensors in menu by Name and Active Status") {
			input "sortSensorsName", "bool",
				title: "Sort sensors in menu by name",
                default: true,
				required: true
			input "sortSensorsActive", "bool",
				title: "Sort sensors in menu by Active Status",
                default: true,
				required: true
        }
        section("Optional: Temperature Values Display Options") {
            input "numberOfDecimals", "number",
                title: "Round temperature values with the following number of decimals",
                default: 1,
                required: true
            input "matchOutputNumberOfDecimals", "bool",
                title: "Match all temperature sensor values with the same amount of decimals",
                default: false,
                required: true
            input "sortTemperatureAscending", "bool",
                title: "Sort all temperature sensor values in High -> Low (decending) direction. Default: Low -> High",
                default: false,
                required: false
        }
        section("Optional: Dimmer Level Main Menu Display Option for Dimmer/Level Capable Switches/Lights") {
            input "dimmerValueOnMainMenu", "bool",
                title: "Display the dimmer level % value on the Main Menu after the name of the device? Note: The dimmer % value is always displayed on the sub-menu of the dimmer where the level can be changed.",
                default: false,
                required: false
        }
        section("Optional: Number of Devices per ST Sensor category to display") {
            href name: "categoryPageLink", title: "Number of Devices per ST Sensor Categories to Display Options", description: "", page: "categoryPage"
        }
        section("Optional: Battery Options") {
            href name: "batteryPageLink", title: "Battery Check/Display/Level", description: "", page: "batteryPage"
        }
        section("Optional: Event History Options for Devices") {
            href name: "eventsPageLink", title: "Event History", description: "", page: "eventsPage"
        }
        section("Optional: Font Names, Pitch Size and Colors") {
            href name: "fontsPageLink", title: "BitBar Output Menu Text Display Settings", description: "", page: "fontsPage"
        }
        section("Optional: Customize Sensor Status & Type Emoji Display Options") {
            href name: "iconsPageLink", title: "Customize Sensor Status & Type Display Settings", description: "", page: "iconsPage"
        }
        section("Optional: Limit Color Choices for 'Color Control' capable devices") {
            input "colorChoices", "enum",
                title: "Only show these checked color choices in list (Default: All]",
                options: [["Soft White":"Soft White - Default"],
                ["White":"White - Concentrate"],
                ["Daylight":"Daylight - Energize"],
                ["Warm White":"Warm White - Relax"],
                "Red","Green","Blue","Yellow","Orange","Purple","Pink","Cyan"],
                required: false,
                multiple: true
        }
    }
}

private initializeAppEndpoint() {
    if(!state.accessToken) {
        createAccessToken()
    }
    try {
        if (isST) {
            state.endpoint = apiServerUrl("/api/token/${state.accessToken}/smartapps/installations/${app.id}/")
            state.endpointURL = apiServerUrl("/api/smartapps/installations/${app.id}/")
        } else {
            state.endpoint=getFullLocalApiServerUrl()+ "/?access_token=${state.accessToken}"
            state.endpointURL=getFullLocalApiServerUrl()
        }
    }
    catch(e) {
        state.remove('endpoint')
    }
}

def getEventsOfDevice(device) {
    def deviceHistory

    if (eventsShow==null || eventsShow==false) {return}

    if (state.eventsDays==null) {
        state.eventsDays = 1
    }
    if (state.eventsMax==null) {
        state.eventsMax = 10
    }
    if (state.eventsDays > 7) {state.eventsDays = 1}
    if (state.eventsMax > 100) {state.eventsMax = 100}

    def today = new Date()
    def then = timeToday(today.format("HH:mm"), TimeZone.getTimeZone('UTC')) - state.eventsDays
    def timeFormatString = eventsTimeFormat=="12 Hour Clock Format with AM/PM"?'EEE MMM dd hh:mm a z':'EEE MMM dd HH:mm z'
    try {
        deviceHistory = device.eventsBetween(then, today, [max: state.eventsMax])?.findAll{"$it.source" == "DEVICE"}?.collect{[date: it.date.format(timeFormatString , location.timeZone), name: it.name, value: it.value]}
    }
    catch (all) {
        return deviceHistory
    }
    return deviceHistory
}

private getAllDevices(BatteryCapabilityOnly=false) {
    def devicePickMap = [:]
    def dev_list =
        ([] + switches
         + dimmers
         + motions
         + accelerations
         + contacts
         + illuminants
         + temps
         + relativeHumidityMeasurements
         + locks
         + alarms
         + batteries
         + thermos
         + medias
         + musicplayers
         + speeches
         + colors
         + valves
         + waters
         + presences
         + leaks)?.findAll()?.unique { it.id }
    dev_list.each {
        if (BatteryCapabilityOnly) {
            if (it.capabilities.any { it.name.contains('Battery') } == true) {
                devicePickMap << ["${it.id}": "${it.displayName}"]
            }
        } else {
            devicePickMap << ["${it.id}": "${it.displayName}"]
        }
    }
    //    dev_list = dev_list.collect{ it.toString() }
    //    return dev_list.sort()
    //    log.debug "devicePickMap: ${devicePickMap}"
    //    log.debug "devicePickMap.sort() {it.value} = ${devicePickMap.sort() {it.value}}"
    return devicePickMap.sort() {it.value}
}

def getHueSatLevel(color) {
    def hueColor = 0
    def saturation = 100
	switch(color) {
		case "White":
			hueColor = 52
			saturation = 19
			break;
		case "Daylight":
			hueColor = 53
			saturation = 91
			break;
		case "Soft White":
			hueColor = 23
			saturation = 56
			break;
		case "Warm White":
			hueColor = 20
			saturation = 80 //83
			break;
		case "Blue":
			hueColor = 69
			saturation = 95
			break;
		case "DarkBlue":
			hueColor = 70
			break;
		case "Green":
			hueColor = 39
			break;
		case "Yellow":
			hueColor = 25
			break;
		case "Orange":
			hueColor = 10
			break;
		case "Purple":
			hueColor = 75
			break;
		case "Cyan":
			hueColor = 180
			break;
		case "Pink":
			hueColor = 83
			break;
		case "Red":
			hueColor = 100
			break;
	}
    return [hue: hueColor, saturation: saturation, level:100]
}

def colorChoiceList() {
    return ["lightseagreen","floralwhite","lightgray","darkgoldenrod","paleturquoise","goldenrod","skyblue","indianred","darkgray","khaki","blue",
            "darkred","lightyellow","midnightblue","chartreuse","lightsteelblue","slateblue","firebrick","moccasin","salmon","sienna","slategray","teal","lightsalmon",
            "pink","burlywood","gold","springgreen","lightcoral","black","blueviolet","chocolate","aqua","darkviolet","indigo","darkcyan","orange","antiquewhite","peru",
            "silver","purple","saddlebrown","lawngreen","dodgerblue","lime","linen","lightblue","darkslategray","lightskyblue","mintcream","olive","hotpink","papayawhip",
            "mediumseagreen","mediumspringgreen","cornflowerblue","plum","seagreen","palevioletred","bisque","beige","darkorchid","royalblue","darkolivegreen","darkmagenta",
            "orange red","lavender","fuchsia","darkseagreen","lavenderblush","wheat","steelblue","lightgoldenrodyellow","lightcyan","mediumaquamarine","turquoise","dark blue",
            "darkorange","brown","dimgray","deeppink","powderblue","red","darkgreen","ghostwhite","white","navajowhite","navy","ivory","palegreen","whitesmoke","gainsboro",
            "mediumslateblue","olivedrab","mediumpurple","darkslateblue","blanchedalmond","darkkhaki","green","limegreen","snow","tomato","darkturquoise","orchid","yellow",
            "green yellow","azure","mistyrose","cadetblue","oldlace","gray","honeydew","peachpuff","tan","thistle","palegoldenrod","mediumorchid","rosybrown","mediumturquoise",
            "lemonchiffon","maroon","mediumvioletred","violet","yellow green","coral","lightgreen","cornsilk","mediumblue","aliceblue","forestgreen","aquamarine","deepskyblue",
            "lightslategray","darksalmon","crimson","sandybrown","lightpink","seashell"].sort()
}

def supportedMusicPlayerDeviceCommands() {
    return ['nextTrack','pause','play','previousTrack','stop']
}

// SmartThings/Hubitat Portability Library (SHPL)
// Copyright (c) 2019, Barry A. Burke (storageanarchy@gmail.com)
String getPlatform()  { (physicalgraph?.device?.HubAction ? 'SmartThings' : 'Hubitat') }	// if (platform == 'SmartThings') ...
boolean getIsST()     { (physicalgraph?.device?.HubAction ? true : false) }					// if (isST) ...
boolean getIsHE()     { (hubitat?.device?.HubAction ? true : false) }						// if (isHE) ...

String getHubPlatform() {
	def pf = getPlatform()
	state?.hubPlatform = pf			// if (state.hubPlatform == 'Hubitat') ...
											// or if (state.hubPlatform == 'SmartThings')...
	state?.isST = pf.startsWith('S')	// if (state.isST) ...
	state?.isHE = pf.startsWith('H')	// if (state.isHE) ...
	return pf
}
boolean getIsSTHub() { return state.isST }					// if (isSTHub) ...
boolean getIsHEHub() { return state.isHE }					// if (isHEHub) ...
String getBitBarLogo(){ return "<img src=https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/STBitBarApp-V2.png width=60 style='float: left; padding: 0px 10px 0px 0px;' alt='BitBar Logo' height=60 align=left /><br>"}
String getDoneImage(){ return "<img src=https://raw.githubusercontent.com/KurtSanders/STBitBarApp-V2/master/Images/done.png width=60 style='float: left; padding: 0px 10px 0px 0px;' alt='Done!' height=60 align=left /><br>"}
String getAppInfo(params=[]) {
    def na="Value not initialized, awiting first run of Mac BitBar app"
    if (isST) {
        state.bbFolder			= "Mac BitBar Plugin Folder:\n${params.path?:na}"
        state.bbVersions		= "Current Installed Versions:\nSmartApp: ${appVersion()}\nST_Python_Logic: ${params.pythonAppVersion?:na}\n${params.bbpluginfilename?:na}: ${params.bbpluginversion?:na}"
    } else {
        state.bbFolder			= "Mac BitBar Plugin Folder: ${params.path?:na}"
        state.bbVersions		= "<b>Current Installed Versions:</b><br>" +
            "SmartApp: ${appVersion()}<br>" +
            "HE_Python_Logic: ${params.pythonAppVersion?:na}<br>" +
                "${params.bbpluginfilename?:''}: ${params.bbpluginversion?:''}"
    }
}
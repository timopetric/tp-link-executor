# -*- coding: utf-8 -*-

import requests
import bs4 as bs
import sys
import datetime
import logging
from dbExecutor import dbExecutor
from logLoader import loadLogger
from config import AUTH, LOCAL_IP, SOURCE

logger = loadLogger(SOURCE)
logger.setLevel(logging.INFO)

def getAuth(username, password):
	import base64
	return base64.b64encode(username+":"+password)

def getConnectedDevicesList():
	urlDevices = "http://"+LOCAL_IP+"/userRpm/AssignedIpAddrListRpm.htm?Refresh=Refresh"
	todayDateStr = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") # today date in the uniform format

	if len(AUTH) < 1:
		logger.error("Unset AUTH key. Set it in the config file or use the getAuth() function in place of \"AUTH\" fields in the main program.")
		sys.exit(1)

	resp = requests.get(urlDevices, headers={"Authorization" : "Basic "+AUTH})
	soup = bs.BeautifulSoup(resp.text, "html.parser")

	scriptText = soup.find("script", language="javascript", type="text/javascript").text.strip()
	devices = scriptText.split("\n")[1:-1]

	logger.info("Number of connected devices: {}".format(len(devices)))

	devicesList = list()
	for device in devices:
		device = [prop.strip(" \"") for prop in device.strip(", ").split(",")]
		device.append(todayDateStr)
		device = tuple(device)
		devicesList.append(device)
		name = device[0]
		macAddr = device[1]
		ipAddr = device[2]
		leaseTime = device[3]
		logger.debug("DEVICE NAME: {}, MAC ADDR: {}, IP: {}, LEASE TIME: {}".format(name, macAddr, ipAddr, leaseTime))
	return devicesList

def reboot():
	urlReboot = "http://"+LOCAL_IP+"/userRpm/SysRebootRpm.htm?Reboot=Reboot"
	todayDateStr = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") # today date in the uniform format

	if len(AUTH) < 1:
		logger.error("Unset AUTH key. Set it in the config file or use the getAuth() function in place of \"AUTH\" fields in the main program.")
		sys.exit(1)

	resp = requests.get(urlReboot, headers={"Authorization" : "Basic "+AUTH, "Referer": "http://"+LOCAL_IP+"/userRpm/SysRebootRpm.htm"})
	if "Please wait a moment, if the browser does not refresh automatically" in resp.text:
		logger.info("Rebooted the device.")
	else:
		logger.error("Could not reboot the device.")


if __name__ == "__main__":
	rebootBool = False
	getDeviceListBool = False
	if len(sys.argv) >= 2:
		if "-R" in sys.argv[1:]:
			rebootBool = True
		if "-D" in sys.argv[1:]:
			getDeviceListBool = True
	try:
		if getDeviceListBool:
			sqlBase = dbExecutor()
			for dev in getConnectedDevicesList():
				sqlBase.insertOne(dev)
		if rebootBool:
			reboot()
		if not getDeviceListBool and not rebootBool:
			logger.info("No arguments provided.")
			
	except Exception:
		logger.exception("")
		sys.exit(1)
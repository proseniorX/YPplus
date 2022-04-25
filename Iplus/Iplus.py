# import only system from os
import os

from datetime import datetime
from xmlrpc.client import DateTime
from pip._vendor import requests
from pathlib import Path

import netifaces
import time

import json
import socket
import struct


allowIPv4Keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
standardInterval = []
currentInterval = []
lastUpdate = []

allTargets = []

class target:
    currentIP = ""
    localIP = ""
    domains = []
    password = ""
    standardInterval = 0
    currentInterval = 0
    lastUpdate = str(datetime.now().strftime("%Y-%m-%d %H:%M"))


#-----------------------------------------------------
#Tạo 1 session và chọn IP cục bộ của network interface
#Request gửi qua giao diện nào thì response gửi về giao
#diện đó.
def bindIP(addr: str) -> requests.Session:    
    session = requests.Session()
    for prefix in ('http://', 'https://'):
        session.get_adapter(prefix).init_poolmanager(
            # those are default values from HTTPAdapter's constructor
            connections=requests.adapters.DEFAULT_POOLSIZE,
            maxsize=requests.adapters.DEFAULT_POOLSIZE,
            # This should be a tuple of (address, port). Port 0 means auto-selection.
            source_address=(addr, 0),
        )
    return session


#Trả lại địa chỉ ip của network interface được chỉ định...
def globalIP(localIP: str):
    req = bindIP(localIP)
    _ip = req.get("https://get.geojs.io/v1/ip").text    
    for character in _ip:
        if character not in allowIPv4Keys:
            _ip = _ip.replace(character, "")
    return _ip


#-----------------------------------------------------
#ifacesIP
#Trả lại danh sách local ip của network interfaces.
def ifacesIP():

    iplist = []

    for iface in netifaces.interfaces():
        iface_details = netifaces.ifaddresses(iface)

        if netifaces.AF_INET in iface_details:
            for ip_interfaces in iface_details[netifaces.AF_INET]:
                for key, ip_add in ip_interfaces.items():
                    if key == 'addr' and ip_add != '127.0.0.1':
                        iplist.append(ip_add)

    return iplist
#-----------------------------------------------------    


#-----------------------------------------------------
#Hàm load file config.
def loadConfig():
    if Path("config.json").exists():

        _raw = open("config.json")
        config = json.load(_raw)
        _raw.close

        for _config in config:
            _target = target()
            _target.localIP = _config["interface"]
            _target.domains = _config["domains"]
            _target.password = _config["password"]
            _target.standardInterval = _config["interval"]

            allTargets.append(_target)

        return config

    else:

        print("config.json not found!")
#-----------------------------------------------------
       

def clearScreen():
    if (os.name == 'nt'):
        os.system("cls")
    else:
        os.system("clear")


#api.dynu.com/nic/update?hostname=example1.dynu.com,example2.dynu.com&myip=198.144.117.32&myipv6=2604:4400:a:8a::f4&password=098f6bcd4621d373cade4e832627b4f6 
def getAPI(target, newip):
    api = "https://api.dynu.com/nic/update?hostname="

    for i in range(0,len(target.domains),+1):
        api += target.domains[i]
        if i < len(target.domains) - 1:
            api += ","
    
    api += "&myip=" + newip + "&password=" + target.password
    return api


config = loadConfig()
iplist = ifacesIP()
    
for i in range(0,len(config),+1):
    standardInterval.append(int(config[i]["interval"]))
    currentInterval.append(0)
    lastUpdate.append(datetime.now)


while 1:

    clearScreen()

    display = ""

    for _target in allTargets:
        if (_target.localIP in iplist):
            print("------------------------------")
            print(_target.localIP + " (" + _target.currentIP + ")")
            print("------------------------------")

            for _domain in _target.domains:
                print("    " + _domain)

            print("")

            _target.currentInterval -= 1
            newip = _target.currentIP

            api = getAPI(_target, newip)

            #Đây là lúc để update địa chỉ ip các tên miền của thằng này.
            if (_target.currentInterval <= 0):
                newip = globalIP(_target.localIP)
                _target.currentIP = newip
                _target.currentInterval = int(_target.standardInterval)
                _target.lastUpdate = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
                r = requests.get(api)

            print("Last update: ", _target.lastUpdate)
            print("Next update in:", _target.currentInterval)
            print("API:", api)

        else:
            print("------------------------------")
            print(_target.localIP + " (!!!)");
            print("------------------------------")
            print("Incorect Network Interface")

            print("")
            print
            print("")  


    time.sleep(1)   


    


        






















#a = bindIP('192.168.50.73')
#resp = a.get('https://get.geojs.io/v1/ip')
#print(resp.text)

#b = bindIP('192.168.42.55')
#resp = b.get('https://get.geojs.io/v1/ip')
#print(resp.text)


#!/usr/bin/env python
from lib import state
from lib.config import config
import socket
import requests
import sys
import os
import json
from git import Repo
#state.StateTable.create_table()

root = config.get("general", "path")

payload = {'format': 'json', 'server__name': socket.gethostname()}
r = json.loads(requests.get("http://" + config.get("general", "confighost") + "/api/v1/module/", params=payload).text)

modules = {}
for module in r['objects']:
	payload = {'format': 'json', 'name': module['name']}
	moduleData = json.loads(requests.get("http://" + config.get("general", "confighost") + "/api/v1/module_list/", params=payload).text)['objects'][0]
        modules[module['id']] =  { "name" : module['name'], "package" : moduleData["package"], "config" : module["config"] };
modules_list = ""
for moduleID, moduleInfo in modules.iteritems():
	try:
		Repo.clone_from(moduleInfo['package'], "modules/" + str(moduleInfo['name']))
	except:
		print "Error cloning " + str(moduleInfo['name'])
	module = str(moduleInfo['name'])
	if moduleInfo['config']:
		configSplit = moduleInfo['config'].split("=")
		try:
			config.add_section(module)
		except:
			pass
		config.set(module, str(configSplit[0]).strip(), configSplit[1])
	target = open ("modules/" + module + "/id.txt", 'w')
	target.write(str(moduleID))
	target.close
        if os.path.isfile(os.path.join(root,module,"setup.py")):
		execfile(os.path.join(root,module,"setup.py"))
	
with open (os.path.dirname(os.path.realpath(__file__)) + '/config.ini', 'wb') as configfile:
	config.write(configfile)

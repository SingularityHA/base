#!/usr/bin/env python
"""
    SingularityHA Setup
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2014- by Internet by Design Ltd
    :license: GPL v3, see LICENSE for more details.

"""
import socket
import requests
import sys
import os
import json
from git import Repo
from lib import state
from lib.config import config

root = config.get("general", "path")

""" Pull in list of modules from the config server """
payload = {'format': 'json', 'server__name': socket.gethostname()}  # Generate payload for request
r = json.loads(requests.get("http://" + config.get("general", "confighost") + "/api/v1/module/", params=payload).text)

""" Loop through returned results and grab core module data """
modules = {}
for module in r['objects']:  # Loop through modules the server says we should have
    payload = {'format': 'json', 'name': module['name']}
    moduleData = json.loads(
        requests.get("http://" + config.get("general", "confighost") + "/api/v1/module_list/", params=payload).text)[
        'objects'][0]  # Pull config options and build a modules list
    modules[module['id']] = {"name": module['name'], "package": moduleData["package"], "config": module["config"]}

""" Run various operations to install modules """
modules_list = ""
for moduleID, moduleInfo in modules.iteritems():
    try:
        Repo.clone_from(moduleInfo['package'], "modules/" + str(moduleInfo['name']))  # Install the module from git
    except:
        print "Error cloning " + str(moduleInfo['name'])
    module = str(moduleInfo['name'])

    """ Import config for the module if it exists """
    if moduleInfo['config']:
        configSplit = moduleInfo['config'].split("=")
        try:
            config.add_section(module)
        except:
            pass
        config.set(module, str(configSplit[0]).strip(), configSplit[1])

    """ Write out an ID to the module folder for it's own setup to use """
    target = open("modules/" + module + "/id.txt", 'w')
    target.write(str(moduleID))
    target.close()

    """ Exec the module's own setup file """
    if os.path.isfile(os.path.join(root, module, "setup.py")):
        execfile(os.path.join(root, module, "setup.py"))

""" Write out config file with new module options """
with open(os.path.dirname(os.path.realpath(__file__)) + '/config.ini', 'wb') as configfile:
    config.write(configfile)

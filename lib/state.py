"""
    SingularityHA
    ~~~~~~~~~~~~~~~~~~~~~

    State storage into MySQL

    :copyright: (c) 2013 - by Internet by Design Ltd
    :license: GPL v3, see LICENSE for more details.

"""
from peewee import *
import datetime
import time
from config import config
import logging

# Pulls configuration from the config module
server = config.get("database", "host")
username = config.get("database", "username")
password = config.get("database", "password")
database = config.get("database", "database")
our_db = MySQLDatabase(database,host=server,user=username,passwd=password)

# Start up logging
logger = logging.getLogger(__name__)
logger.info("State library started...")


# This is the definition of the database model
class StateModel(Model):
    class Meta:
        database = our_db

class StateTable(StateModel):
	device = CharField(max_length=255)
	state = CharField(max_length=255)
	attributes = TextField(null = True)
	lock = BooleanField(default = 0)
	lastChange = DateTimeField(default=datetime.datetime.now)

our_db.connect()

def set(device, state, attributes=None):
	""" Set the state of the specified device"""
	try:
		acquire_lock(device)
	except:
		#state object doesn't exist yet
		pass
	state_object = StateTable()
	state_object.device = device
	state_object.state = state
	state_object.attributes = attributes
	state_object.save()
	release_lock(device)

def get(device):
	""" Simple function to pull the state of a device from the DB """
	state = StateTable.select().where(StateTable.device == device).get()
	return(state)

def acquire_lock(device):
	""" Get lock over the state of a device to prevent clashes """
	loggger.debug("attempting to get lock for device" + device)
	while True:
		if StateTable.select().where(StateTable.device == device).get().lock == False:
			stateObj = StateTable.select().where(StateTable.device == device).get()
			stateObj.lock = True
			stateObj.save()
			loggger.debug("got lock for device" + device)
			break
		time.sleep(1)

def release_lock(device):
	""" Unlock once we have finished editing the state """
	stateObj = StateTable.select().where(StateTable.device == device).get()
        stateObj.lock = False
        stateObj.save()
	loggger.debug("released lock for device" + device)



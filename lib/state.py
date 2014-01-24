# SingularityHA
# Copyright (C) 2014 Internet by Design Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from peewee import *
import datetime
import time
import config

server = config.get("database", "host")
username = config.get("database", "username")
password = config.get("database", "password")
database = config.get("database", "database")
our_db = MySQLDatabase(host=server,user=username,passwd=password,db=database)

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
	acquire_lock(device)
	state_object = StateTable()
	state_object.device = device
	state_object.state = state
	state_object.attributes = attributes
	state_object.save()
	release_lock(device)

def get(device):
	state = StateTable.select().where(StateTable.device == device).get()
	return(state)

def acquire_lock(device):
	while True:
		print "Attempting to acquire lock"
		if StateTable.select().where(StateTable.device == device).get().lock == False:
			stateObj = StateTable.select().where(StateTable.device == device).get()
			stateObj.lock = True
			stateObj.save()
			print "Got lock!"
			break
		time.sleep(1)

def release_lock(device):
	stateObj = StateTable.select().where(StateTable.device == device).get()
        stateObj.lock = False
        stateObj.save()
	print "Lock released!"


import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from lib.config import config
from nose.tools import *

def testExistingConfig():
	assert config.get("test", "test") == "testingconfig"

def testMissingConfig():
	try:
		config.get("test", "noexistent")
		assert False
	except:
		assert True

def testCreateConfig():
	config.set("test", "test2", "testingconfig2")
	assert config.get("test", "test2") == "testingconfig2"

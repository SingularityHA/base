import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from lib import state

def testState():
	state.StateTable.create_table()
	state.set("testing", "akdj1ps")
	#assert state.get("testing") == "akdj1ps"

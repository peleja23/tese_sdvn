#from kind.kindctrl import Kindctrl
from mininetsumo.sdvn import MininetSumo

import subprocess
import math
import requests
import threading
import os
import json


class Service:

    def __init__(self, sdnController):
        self.sdnController = sdnController

    def startRyuController(self):
        user = os.getenv("SUDO_USER") or os.getenv("USER")
        cmd = (f'sudo -u {user} bash -c "ryu-manager {self.sdnController}; exec bash"')
        subprocess.Popen(['konsole','--noclose','-e','bash', '-c', cmd])
        
    def startMininetSumo(self):
        m = MininetSumo()
        m.myNetwork()

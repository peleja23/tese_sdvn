from kind.kindctrl import Kindctrl
from mininetsumo.sdvn import MininetSumo

import subprocess
import os
import json


class Service:

    def __init__(self, kindCLuster, sdnController, mininetSim):
        self.kindCluster = kindCLuster
        self.sdnController = sdnController
        self.mininetSim = mininetSim

    def startKind(self):
        k = Kindctrl(self.kindCluster)
        k.startCluster()

    def startRyuController(self):
        user = os.getenv("SUDO_USER") or os.getenv("USER")
        cmd = (f'sudo -u {user} bash -c "ryu-manager {self.sdnController}; exec bash"')
        subprocess.Popen(['konsole','--noclose','-e','bash', '-c', cmd])
        
    def startMininetSumo(self):
        m = MininetSumo(self.mininetSim)
        m.myNetwork()


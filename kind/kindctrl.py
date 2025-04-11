import yaml
import subprocess

class Kindctrl:


    def __init__(self, configPath):
        self.configPath = configPath

        with open(self.configPath, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.cluster_Name = self.config['name']

    def getCluster(self):
        return subprocess.run(['kind', 'get', 'clusters'], 
                              stdout=subprocess.PIPE).stdout.decode('utf-8')
    
    def eliminateCluster(self):
        return subprocess.run(['kind', 'delete', 'cluster', '--name', self.cluster_Name], 
                              stdout=subprocess.PIPE).stdout.decode('utf-8')
    
    def startCluster(self):
        if self.cluster_Name in self.getCluster():
            self.eliminateCluster()
            subprocess.run(['kind', 'create', 'cluster', '--config', str(self.configPath)], 
                           stdout=subprocess.PIPE).stdout.decode('utf-8')
        else:
            subprocess.run(['kind', 'create', 'cluster', '--config', str(self.configPath)], 
                           stdout=subprocess.PIPE).stdout.decode('utf-8')
    
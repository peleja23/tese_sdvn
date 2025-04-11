import sys
import time
from service.service import Service

def main():
    service = Service("/home/pedro/tese/kind/configs/config-cluster.yml"
                      ,"/home/pedro/tese/ryuctrl/simple_switch_13.py"
                      ,'/home/pedro/tese/mininetsumo/configs/test.json')
    
    service.startKind()
    service.startRyuController()
    time.sleep(2)
    service.startMininetSumo()

if __name__ == '__main__':    
    main()
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Station, OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd, ITSLink
from mn_wifi.wmediumdConnector import interference
from subprocess import call
from mn_wifi.sumo.runner import sumo


def myNetwork():
    net = Mininet_wifi(topo=None,
                       build=False,
                       link=wmediumd,
                       wmediumd_mode=interference,
                       ipBase='10.0.0.0/8')
    # Adding Controller
    c0 = net.addController(name='c0',
                           controller=RemoteController,
                           ip='127.0.0.1',
                           protocol='tcp',
                           port=6653)
    
    info( '*** Add cars/hosts and stations\n') 
    car = []
    for i in range(0,5):
        car.append(i)

    for i in range(0,5):
        car[i] = net.addCar('car%s' % (i + 1) , wlans=2, ip = '10.0.0.%s/8' % i)
         
    info('*** Post configure nodes\n')

    CLI(net)
    net.stop()





if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
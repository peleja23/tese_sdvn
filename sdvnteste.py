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

    info('*** Add switches/APs\n')

    # Adding switches
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)

    # Adding cars (with the possibility of two wireless interfaces for each car)
    for id in range(0, 10):
        net.addCar('car%s' % (id + 1), wlans=2, encrypt=['wpa2', ''], range = 100)

    # Access Point configuration
    kwargs = {'ssid': 'vanet-ssid', 'mode': 'g', 'passwd': '123456789a',
              'encrypt': 'wpa2', 'failMode': 'standalone', 'datapath': 'user'}
    
    e1 = net.addAccessPoint('e1', mac='00:00:00:11:00:01', channel='1',
                            position='2600,3500,0', **kwargs, range = 150)
    e2 = net.addAccessPoint('e2', mac='00:00:00:11:00:02', channel='6',
                            position='2800,3500,0', **kwargs, range = 150)
    e3 = net.addAccessPoint('e3', mac='00:00:00:11:00:03', channel='11',
                            position='3000,3500,0', **kwargs, range = 150)
    e4 = net.addAccessPoint('e4', mac='00:00:00:11:00:04', channel='1',
                            position='2600,3300,0', **kwargs, range = 150)

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=2.8)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info('*** Add links\n')
    net.addLink(s1, s2)
    net.addLink(s2, s3)
    net.addLink(s1, e1)
    net.addLink(s2, e2)
    net.addLink(s3, e3)
    net.addLink(s3, e4)

    # Adding links between cars and APs using ITSLink
    for car in net.cars:
        net.addLink(car, intf=car.wintfs[1].name,
                    cls=ITSLink, band=20, channel=181)

    # Use external SUMO program
    net.useExternalProgram(program=sumo, port=8813,
                           extra_params=["--start --delay 1000"],
                           clients=1, exec_order=0)

    # Assigning IPs to the cars and access points
    for id, car in enumerate(net.cars):
        car.setIP('10.0.0.{}/24'.format(id + 1),
                  intf='{}'.format(car.wintfs[0].name))
        car.setIP('10.0.1.{}/24'.format(id + 1),
                  intf='{}'.format(car.wintfs[1].name))

    # Track the position of the nodes
    nodes = net.cars + net.aps
    net.telemetry(nodes=nodes, data_type='position',
                  min_x=2200, min_y=2800,
                  max_x=3200, max_y=3900)

    info('*** Starting network\n')
    net.build()

    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches/APs\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])
    net.get('e1').start([c0])
    net.get('e2').start([c0])
    net.get('e3').start([c0])
    net.get('e4').start([c0])

    info('*** Post configure nodes\n')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()

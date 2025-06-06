import json
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd, mesh, adhoc
from mn_wifi.wmediumdConnector import interference
from mn_wifi.sumo.runner import sumo

class MininetSumo:

    def __init__(self, configPath):
        self.configPath = configPath
        with open(configPath, 'r') as f:
             self.config = json.load(f)

    def myNetwork(self):
        
        net = Mininet_wifi(topo=None,
                        build=False,
                        link=wmediumd,
                        wmediumd_mode=interference,
                        ipBase='10.0.0.0/8')

        c0 = net.addController(name='c0',
                            controller=RemoteController,
                            ip='127.0.0.1',
                            protocol='tcp',
                            port=6653)

        info('*** Add switches\n')
        s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
        s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
        s3 = net.addSwitch('s3', cls=OVSKernelSwitch)

        info('*** Add cars\n')
        car_count = self.config["cars"]["count"]
        cars = []
        for id in range(car_count):
            car = net.addCar(f'car{id + 1}', wlans=2, 
                             encrypt=['wpa2', ''], range=162)
            cars.append(car)

        info('*** Add APs\n')
        aps = []
        for ap_cfg in self.config["aps"]:
            ap = net.addAccessPoint(
                'e' + ap_cfg["id"],
                cls=OVSKernelAP,
                ssid=f"e{ap_cfg['id']}-ssid",
                mode='g',
                mac=f'00:00:00:00:00:0{ap_cfg["id"]}',
                channel=ap_cfg["channel"],
                position=ap_cfg["position"],
                range=200,
                protocols='OpenFlow13'
            )
            aps.append(ap)

        info("*** Configuring Propagation Model\n")
        net.setPropagationModel(model="logDistance", exp=2.8)

        info("*** Configuring wifi nodes\n")
        net.configureWifiNodes()

        # Mesh Link
        for car in cars:
            net.addLink(car, intf=car.wintfs[1].name,
                        cls=adhoc, ssid='adhocNet', channel=5, 
                        proto='olsrd')

        info('*** Add wired links\n')
        net.addLink(s1, s2)
        net.addLink(s2, s3)
        net.addLink(s1, aps[0])
        net.addLink(s2, aps[1])
        net.addLink(s3, aps[2])
        net.addLink(s3, aps[3])

        net.useExternalProgram(program=sumo, port=8813,
                               config_file=self.config["sumoConfig"],
                               extra_params=["--start", "--delay", "1000"],
                               clients=1, exec_order=0)

        for id, car in enumerate(cars):
            car.setIP(f'10.0.0.{id + 1}/24', intf=car.wintfs[0].name)
            car.setIP(f'10.0.1.{id + 1}/24', intf=car.wintfs[1].name)
            #car.wintfs[0].setMAC(f'02:00:00:00:{(id + 1):02x}:01')
            #car.wintfs[1].setMAC(f'02:00:00:00:{(id + 1):02x}:02')

        net.addNAT().configDefault()
        
        if self.config.get("telemetry", {}).get("enabled", False):
            net.telemetry(
                nodes=cars + aps,
                data_type='position',
                min_x=self.config["telemetry"]["min_x"],
                min_y=self.config["telemetry"]["min_y"],
                max_x=self.config["telemetry"]["max_x"],
                max_y=self.config["telemetry"]["max_y"]
            )

        info('*** Starting network\n')
        net.build()

        info('*** Starting controllers\n')
        for controller in net.controllers:
            controller.start()

        info('*** Starting switches/APs\n')
        s1.start([c0])
        s2.start([c0])
        s3.start([c0])
        for ap in aps:
            ap.start([c0])

        info('*** Post configure nodes\n')

        CLI(net)
        net.stop()
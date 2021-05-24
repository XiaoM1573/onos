#!/usr/bin/python

from mininet.node import Host
from mininet.topo import Topo
from stratum import StratumBmv2Switch

CPU_PORT = 255


class IPv4Host(Host):
    """Host that can be configured with an IPv4 gateway (default route).
    """

    def config(self, mac=None, ip=None, defaultRoute=None, lo='up', gw=None,
               **_params):
        super(IPv4Host, self).config(mac, ip, defaultRoute, lo, **_params)
        self.cmd('ip -4 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -6 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -4 link set up %s' % self.defaultIntf())
        self.cmd('ip -4 addr add %s dev %s' % (ip, self.defaultIntf()))
        if gw:
            self.cmd('ip -4 route add default via %s' % gw)
        # Disable offload
        for attr in ["rx", "tx", "sg"]:
            cmd = "/sbin/ethtool --offload %s %s off" % (
                self.defaultIntf(), attr)
            self.cmd(cmd)

        def updateIP():
            return ip.split('/')[0]

        self.defaultIntf().updateIP = updateIP


class SimpleTopo(Topo):

    def __init__(self, *args, **kwargs):
        Topo.__init__(self, *args, **kwargs)

        # Leaves
        # gRPC port 50001 - 50006
        s1 = self.addSwitch('s1', cls=StratumBmv2Switch, cpuport=CPU_PORT)
        s2 = self.addSwitch('s2', cls=StratumBmv2Switch, cpuport=CPU_PORT)
        s3 = self.addSwitch('s3', cls=StratumBmv2Switch, cpuport=CPU_PORT)
        s4 = self.addSwitch('s4', cls=StratumBmv2Switch, cpuport=CPU_PORT)
        s5 = self.addSwitch('s5', cls=StratumBmv2Switch, cpuport=CPU_PORT)
        s6 = self.addSwitch('s6', cls=StratumBmv2Switch, cpuport=CPU_PORT)

        # Switch Links
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s4)
        self.addLink(s2, s5)
        self.addLink(s3, s4)
        self.addLink(s3, s5)
        self.addLink(s4, s6)
        self.addLink(s5, s6)

        # Host h1a, h1b attached to Switch S1
        h1a = self.addHost('h1a', cls=IPv4Host, mac="00:00:00:00:00:1A",
                           ip='172.16.1.1/24', gw='172.16.1.254')
        h1b = self.addHost('h1b', cls=IPv4Host, mac="00:00:00:00:00:1B",
                           ip='172.16.1.2/24', gw='172.16.1.254')

        # Host h6a, h6b attached to Switch S6
        h6a = self.addHost('h6a', cls=IPv4Host, mac="00:00:00:00:00:6A",
                           ip='172.16.6.1/24', gw='172.16.6.254')
        h6b = self.addHost('h6b', cls=IPv4Host, mac="00:00:00:00:00:6B",
                           ip='172.16.6.2/24', gw='172.16.6.254')

        self.addLink(h1a, s1)
        self.addLink(h1b, s1)
        self.addLink(h6a, s6)
        self.addLink(h6b, s6)


topos = {'simple_topo': (lambda: SimpleTopo())}
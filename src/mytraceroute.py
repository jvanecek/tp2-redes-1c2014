#! /usr/bin/python

import unicodedata
import urllib
import json
import sys
import numpy
from math import *
from scapy.all import *

class Hop:
    hop_num = 0
    routers = []
    rtt_medio = 0.0
    rtt_min = 0.0
    rtt_max = 0.0
    zrtt = 0.0
    distinguido = 0

    def __init__(self, ttl):
        self.routers = []
        self.hop_num = ttl

    def add_ip(self, ip):
        if ip not in self.routers:
            self.routers.append( ip )

class TR:
    hops = []

    def request(self, host, ttl=30, timeout=1):
        cur_time = time.time()
        resp = sr(IP(dst=host, ttl=ttl) / ICMP(), timeout=timeout)
        rtt = (time.time() - cur_time)*1000
        resp += (rtt, )

        with open('log.txt', 'a') as f:
            f.write("%s\t%s\t%s\n" % (host, ttl, rtt) )
            f.closed

        return resp

    # manda packages paquetes por ttl a host, y devuelve una lista de Hop
    def send(self, host, timeout=1, packages=4, umbral=0.5):
        self.hops = []
        ttl = 1

        ya_termino = False
        while not ya_termino: 
            hop = Hop(ttl)

            for i in range(0, packages):
                ans, unans, rtt = self.request(host, ttl, timeout)

                if len(ans.res) > 0:
                    hop.add_ip( ans.res[0][1].src )
                    
                    hop.rtt_medio += rtt / packages
                    hop.rtt_min = rtt if i==0 else min(hop.rtt_min, rtt)
                    hop.rtt_max = rtt if i==0 else max(hop.rtt_max, rtt)

                    if ans.res[0][1].type == 0: # checking for ICMP echo-reply
                        ya_termino = True

                # no contesto nadie
                else:   
                    hop.add_ip( "?" )

            self.hops.append( hop )
            ttl += 1

        rtts = [ hop.rtt_medio for hop in self.hops ]
        rtt_promedio = numpy.mean( rtts )
        rtt_desvio = numpy.std( rtts )

        for i in range(0,len(rtts)): 
            self.hops[i].zrtt = (rtts[i] - rtt_promedio)/rtt_desvio
            self.hops[i].distinguido = (self.hops[i].zrtt > umbral)

        return self.hops

    def send_c_scapy(self, host):
        return traceroute([host], maxttl=20, retry=-2)

    # para las direcciones privadas o mal formadas devuelve (None, None).
    def get_location(self, ip):
        jresp = urllib.urlopen("http://api.hostip.info/get_json.php?ip=%s&position=true" % ip).read()
        response = json.loads(jresp.encode("ascii", "ignore"))
        return (response['lat'], response['lng'])

    # devuelve un arreglo de los hops que se pudieron geolocalizar
    def get_path(self):
        path = []
        for ip in self.hops.values():
            lat, lng = self.get_location(ip)
            if lat != None and lng != None:
                path.append((ip, float(lat), float(lng)))

        return path
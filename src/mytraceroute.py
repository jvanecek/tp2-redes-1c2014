#! /usr/bin/python

import unicodedata
import urllib
import json
import sys
from math import *
from scapy.all import *

class TR:
    hops = {}
    rtt_medio = {}
    rtt_min = {}
    rtt_max = {}
    zrtt = {}

    def request(self, host, ttl=30, timeout=1):
        cur_time = time.time()
        resp = sr(IP(dst=host, ttl=ttl) / ICMP(), timeout=timeout)
        rtt = (time.time() - cur_time)*1000
        resp += (rtt, )

        with open('log.txt', 'a') as f:
            f.write("%s\t%s\t%s\n" % (host, ttl, rtt) )
            f.closed

        return resp

    # manda packages paquetes por ttl a host, y devuelve una tupla: (hops, times, mins, maxs, zrtt) donde: 
    #  - hops = arreglo de hops hasta host
    #  - times = arreglo de los promedios de los rtt por salto
    #  - mins = arreglo de los minimos rtt por salto
    #  - maxs = arreglo de los maximos rtt por salto
    #  - zrtt = arreglo de los valores z de los rtt por salto
    def send(self, host, timeout=1, packages=4):
        self.hops = {}
        self.rtt_medio = {}
        ttl = 1
        
        ya_termino = False
        while not ya_termino:

            self.rtt_medio[ttl] = 0
            self.rtt_min[ttl] = 0
            self.rtt_max[ttl] = 0

            for i in range(0, packages):
                ans, unans, rtt = self.request(host, ttl, timeout)

                # hubo respuesta
                if len(ans.res) > 0:  
                    hop_ip = ans.res[0][1].src # storing the src ip from ICMP message

                    self.rtt_medio[ttl] += rtt / packages
                    self.rtt_min[ttl] = rtt if i==0 else min(self.rtt_min[ttl], rtt)
                    self.rtt_max[ttl] = rtt if i==0 else max(self.rtt_max[ttl], rtt)

                    if ans.res[0][1].type == 0: # checking for ICMP echo-reply
                        ya_termino = True

                # no contesto nadie
                else:   
                    hop_ip = "?"

                if not self.hops.has_key(ttl): self.hops[ttl] = []
                if not hop_ip in self.hops[ttl]: self.hops[ttl].append(hop_ip)

            ttl += 1

        return (self.hops, self.rtt_medio, self.rtt_min, self.rtt_max, self.zrtt)

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
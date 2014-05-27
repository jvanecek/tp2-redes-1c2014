#! /usr/bin/python

import unicodedata
import urllib
import json
import sys
import numpy
from bs4 import BeautifulSoup

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
    pais = "S/D"
    ciudad = "S/D"
    lat = 0.0
    lng = 0.0

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
            f.write("%s,%s,%s\n" % (host, ttl, rtt) )
            f.closed

        return resp

    # manda packages paquetes por ttl a host, y devuelve una lista de Hop
    def send(self, host, timeout=1, packages=4, umbral=0.5, localizacion=False, api=2):
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

        if localizacion: 
            self.get_localizaciones(api)

        return self.hops

    def fetch_data(self, ip, api):
        urls = [
            "http://api.hostip.info/get_json.php?ip=%s&position=true",
            "http://freegeoip.net/json/%s",
            "http://www.geoiptool.com/es/?IP=%s"
        ];
        
        html = urllib.urlopen( urls[api] % ip).read()
        if api == 0:
            resp = json.loads(html.encode("ascii", "ignore"))
            
            print resp 

            pais = resp['country_name']
            ciudad = resp['city']
            lat = float(unicode(resp['lat'])) if resp['lat'] != None else 0.0
            lng = float(unicode(resp['lng'])) if resp['lng'] != None else 0.0

        elif api == 1:
            resp = json.loads(html.encode("ascii", "ignore"))
            
            print resp 

            pais = resp['country_name']
            ciudad = resp['city']
            lat = float(unicode(resp['latitude'])) 
            lng = float(unicode(resp['longitude']))

        elif api == 2:
            soup = BeautifulSoup(html)

            tables = soup.findAll("table")
            if( len(tables) > 6 ):
                tds = tables[6].findAll("td")
                data = [d.get_text() for d in tds]

                print data

                pais = data[5]
                ciudad = data[11]
                lng = float(unicode(data[17])) if data[17] != '' else 0.0
                lat = float(unicode(data[19])) if data[19] != '' else 0.0

        return (pais, ciudad, lat, lng)

    # para las direcciones privadas o mal formadas devuelve (None, None).
    def get_localizacion(self, hop, api):
        ips = hop.routers

        if "?" in ips: 
            ips.remove("?")

        if len(ips) > 0:
            ip = ips[0] # agarro el primer ip que veo, ?vale la pena ubicar todos los routers?

            pais, ciudad, lat, lng = self.fetch_data(ip, api)

            hop.pais = pais
            hop.ciudad = ciudad
            hop.lat = lat
            hop.lng = lng


    # devuelve un arreglo de los hops que se pudieron geolocalizar
    def get_localizaciones(self, api):
        for hop in self.hops:
            self.get_localizacion(hop, api)

    def save_to_file(self, file):
        with open('%s' % (file), 'w') as f:
            f.write("hop,ips,cant_ips,time,min_times,max_times,zrtt,distinguido,pais,ciudad,lat lng\n")
        
            for hop in self.hops:         
                f.write("%s,[%s],%d,%.4f,%.4f,%.4f,%.4f,%d,%s,%s,%.4f %.4f\n" % 
                    (hop.hop_num, 
                    ";".join(hop.routers), 
                    len(hop.routers), 
                    hop.rtt_medio, 
                    hop.rtt_min, 
                    hop.rtt_max, 
                    hop.zrtt,
                    hop.distinguido,
                    hop.pais, 
                    hop.ciudad,
                    hop.lat,
                    hop.lng)
                )
            f.closed
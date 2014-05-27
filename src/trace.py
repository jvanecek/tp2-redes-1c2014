#! /usr/bin/python

import json
from datetime import datetime
from math import sqrt
from mytraceroute import * 

def main(pkt, umbral, localizacion, api):
    hosts = {
        "www.ubc.ca"       : "canada_%s_api%d.csv",
        "www.msu.ru"       : "rusia_%s_api%d.csv",
        "www.cuhk.edu.hk"  : "china_%s_api%d.csv",
        "www.nus.edu.ws"   : "samoa_%s_api%d.csv",
        #"web.up.ac.za"     : "safrica_%s_api%d.csv"
    }

    #hosts = { "www.google.com" : "google.csv"}

    for host in hosts.keys():
        arch = hosts[host] % (datetime.now().strftime("%y%m%d%H%M"), api)
        print "Comienzo de traceroute a: "+host
        print "Hora: " + str(time.time())
        print "Se guarda en: " + arch

        tr = TR()
        tr.send(host=host, packages=pkt, umbral=umbral, localizacion=localizacion, api=api)
        tr.save_to_file(arch)
        
        print "Terminado traceroute a: "+host

if __name__ == "__main__":
    pkt = 4 if not len(sys.argv) > 1 else int(sys.argv[1])
    umbral = 0.5 if not len(sys.argv) > 2 else float(sys.argv[2])
    localizacion = False if not len(sys.argv) > 3 else True
    api = 2 if not len(sys.argv) > 4 else int(sys.argv[4])    

    main(pkt, umbral, localizacion, api)

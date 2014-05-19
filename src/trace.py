#! /usr/bin/python

import json
from math import sqrt
from mytraceroute import * 

def print_hops_list( file, hops ):
    with open('%s' % (file), 'w') as f:
        f.write("hop\tips\tcant_ips\ttime\tmin_times\tmax_times\tzrtt\tdistinguido\n")
    
        for hop in hops:         
            f.write("%s\t[%s]\t%s\t%.4f\t%.4f\t%.4f\t%.4f\t%d\n" % 
                (hop.hop_num, 
                ",".join(hop.routers), 
                str(len(hop.routers)), 
                hop.rtt_medio, 
                hop.rtt_min, 
                hop.rtt_max, 
                hop.zrtt,
                hop.distinguido)
            )
        f.closed

def main(i):
    hosts = {
        "www.ubc.ca"       : str(i) +"_canada.txt",
        "www.msu.ru"       : str(i) +"_rusia.txt",
        "www.cuhk.edu.hk"  : str(i) +"_china.txt"
    }

    #hosts = { "www.google.com" : "google.txt"}

    for host in hosts.keys():
        arch=hosts[host]
        print "Comienzo de traceroute a: "+host
        print "Hora: " + str(time.time())
        print "Se guarda en: " + arch

        hops = TR().send(host=host, packages=3, umbral=0.5)
        print_hops_list(arch, hops)
        
        print "Terminado traceroute a: "+host

if __name__ == "__main__":
    main(sys.argv[1])

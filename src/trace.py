#! /usr/bin/python

import json
from math import sqrt
from mytraceroute import * 

def print_hops(file, hops, times, mins, maxs, zrtt):
    with open('%s' % (file), 'w') as f:
        f.write("hop\tips\ttime\tcant_ips\tmin_times\tmax_times\tzrtt\n")
        for i in hops.keys():
            if type(hops[i]) is list:
                f.write("%s\t[%s]" % (i, ",".join(hops[i])))
            else:
                f.write("%s\t%s" % (i, hops[i]))
            f.write("\t%.4f\t%s\t%.4f\t%.4f\t%.4f\n" % (times[i], str(len(hops[i])), mins[i], maxs[i], zrtt[i]))
        f.closed

def main(i):
    hosts = {
        "www.ubc.ca"       : str(i) +"_canada.txt",
        "www.msu.ru"       : str(i) +"_rusia.txt",
        "www.cuhk.edu.hk"  : str(i) +"_china.txt"
    }

    hosts = { "www.google.com" : "google.txt" }

    for host in hosts.keys():
        arch=hosts[host]
        print "Comienzo de traceroute a: "+host
        print "Hora: " + str(time.time())
        print "Se guarda en: " + arch

        hops, times, mins, maxs, zrtt = TR().send(host=host, packages=3)

        print_hops(arch, hops, times, mins, maxs, zrtt)
        print "Terminado traceroute a: "+host

if __name__ == "__main__":
    main(sys.argv[1])

#! /usr/bin/python

from mytraceroute import Hop
from iplocator import *
import numpy as np
import matplotlib.pyplot as plt

def parse_archivo(archivo):
	hops_parseados = []
	f = open(archivo)
	lines = f.readlines()
	f.close()

	hops = lines[1:]

	i = 1
	for hop_info in hops:
		hop_data = hop_info.split(",")
		hop_num = int(hop_data[0])

		hop = Hop(hop_num)
		
		hop.routers = hop_data[1].replace("[", "").replace("]", "").split(";")
		hop.rtt_medio = float(hop_data[3])
		hop.rtt_min = float(hop_data[4])
		hop.rtt_max = float(hop_data[5])
		hop.zrtt = float(hop_data[6])
		hop.distinguido = int(hop_data[7])
		hop.pais = hop_data[8]
		hop.ciudad = hop_data[9]

		lat_lng = hop_data[10].split(" ")
		hop.lat = float(lat_lng[0])
		hop.lng = float(lat_lng[1])

		hops_parseados.append( hop )
	return hops_parseados

def zrtt(archivo): 
	hops = parse_archivo(archivo)

	ttl = [hop.hop_num for hop in hops if hop.rtt_medio > 0]
	rtt = [hop.rtt_medio for hop in hops if hop.rtt_medio > 0]
	# para graficar con el rtt parcial
	# for i in range(1, len(rtt)):
	# 	rtt[i] = rtt[i] - rtt[i-1]
	zrtt= [hop.zrtt for hop in hops if hop.rtt_medio > 0]

	fig = plt.figure()
	rtt_fig = fig.add_subplot(111)
	zrtt_fig = rtt_fig.twinx()

	rtt_fig.set_xlabel('ttl')
	rtt_fig.set_ylabel('ms (rtt)')
	zrtt_fig.set_ylabel('ms (zrtt)')

	line1, = rtt_fig.plot(ttl, rtt)
	line2, = zrtt_fig.plot(ttl, zrtt)
	rtt_fig.legend([line1, line2], ['rtt', 'zrtt'])

	plt.show()

def rtt_promedio_dia(archivos):

	legends = []
	for archivo in archivos:
		hora = archivo.split("_")[1][6:8]
		legends.append(hora + " hs")
		hops = parse_archivo(archivo)
		
		ttl = [hop.hop_num for hop in hops]
		rtt = [hop.rtt_medio for hop in hops]
		plt.plot(ttl, rtt)

	plt.xlabel('TTL')
	plt.ylabel('RTT')
	plt.legend(legends,loc=2)
	plt.show()

def main():
	archivos = [
		'canada_1405270138_api2.csv',
		'canada_1405270239_api2.csv',
		'canada_1405270339_api2.csv',
		'china_1405270139_api2.csv',
		'china_1405270239_api2.csv',
		'china_1405270339_api2.csv',
		'rusia_1405270137_api2.csv',
		'rusia_1405270237_api2.csv',
		'rusia_1405270337_api2.csv',
		'samoa_1405270138_api2.csv',
		'samoa_1405270238_api2.csv',
		'samoa_1405270338_api2.csv'
	]
	zrtt(archivos[9])
	#rtt_promedio_dia(archivos[9:12])
	return

if __name__ == "__main__":
	main()
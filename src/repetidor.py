#! /usr/bin/python

import sched
import time
from trace import * 

scheduler = sched.scheduler(time.time, time.sleep)

now = time.time()

for i in range(0, 12):
	print "encolo para dentro de " + str(i) + " horas"
	temp = now+3600*i																		#3600 representa una hora
	scheduler.enterabs(temp, 1, main, (i+8,))

scheduler.run()

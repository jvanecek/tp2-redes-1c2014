#! /usr/bin/python

import sched
import time
from trace import * 

scheduler = sched.scheduler(time.time, time.sleep)

now = time.time()

for i in range(0, 1):
	print "encolo para dentro de " + str(i) + " horas"
	temp = now+3600*i								#3600 representa una hora
	scheduler.enterabs(temp, 1, main, (4,0.5,True,2))

scheduler.run()

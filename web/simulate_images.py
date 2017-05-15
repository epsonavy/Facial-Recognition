import os
import time

#This was for testing purposes.
for x in range(0, 1000):
	f = open('./realtime/epso__realtime__' + str(x) + '.png', 'w')	
	f.close()
	time.sleep(0.25)
	

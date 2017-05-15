import sys
from twisted.python import log
from twisted.internet import reactor, ssl
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory, listenWS
import os
import time
import threading
from collections import deque
import socket
from subprocess import Popen, PIPE
from datetime import datetime
log.startLogging(sys.stdout)

file_queue = deque()
active = True

process_threads = []
socket_dictionary = {}
count = 0
request_semaphore = threading.Semaphore(0)

contextFactory = ssl.DefaultOpenSSLContextFactory('/etc/nginx/ssl/nginx.key', '/etc/nginx/ssl/nginx.crt')

#Server client protocol defines functions for connection, closing, sending a message and sending an image.
class MyServerProtocol(WebSocketServerProtocol):
	def onConnect(self, request):
		global socket_dictionary
		print "A client has connected!"
	def onClose(self, wasClean, code, reason):
		1
	def onMessage(self, payload, isBinary):
		global count
		#payload becomes the jpg
		count = count + 1
		#f = open('/usr/share/nginx/html/static/__realtime__' + str(count) + ".png", "w")
		f = open("./realtime_processing/__realtime__" + str(count) + ".png", "w")
		f.write(payload)
		f.close()
		link = process_file("./realtime_processing/__realtime__" + str(count) + ".png")
		self.sendMessage(link, isBinary)
		#self.sendMessage("https://52.53.243.111/static/__realtime__" + str(count) + ".png", isBinary)

	@classmethod
	def sendImageLink(self,  token, link):
		global socket_dictionary, factory
		print "Image was processed. Sending now"
		try:
			client = socket_dictionary[token]
			if not client == None:
				reactor.callFromThread(factory.protocol.sendMessage, client, link)
		except Exception as e :
			print "Error ocurred: " + str(e)
			pass

#Spawn a thread and put it in the queue
class ProcessThread(threading.Thread):
	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID
	def run(self):
		global file_queue, request_semaphore
		while active:
			request_semaphore.acquire()
			if file_queue:
				path = file_queue.pop()
				print "Thread #" + str(self.threadID) + " is now processing " + path
				process_file(path)
				print "Thread #" + str(self.threadID) + " is finished processing."


		
		
class DeleteThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		# Need to implement a list with -tr to get the oldest image and unlink it
		#os.unlink
		1

	# processes a file for realtime face detection
def process_file(path):
	global socket_dictionary
	print "Currently processing file " + path
	filename = path.replace('./realtime_processing/', '')
	#path = ./realtime_processing/epso__realtime__fdsaCKzKNfdsKNfsfdsKFDN.png

	#Run matt's script
	#Move that finished file into /usr/share/html/static
	nginx_path = 'https://54.215.215.32/static/' + filename
	nginx_system_path = '/usr/share/nginx/html/static/' + filename

	token = filename.split('__realtime__')
	token = token[0]
	#Waits until matt's script is finished
	tstart = datetime.now()
	Popen(["python", "../pipeline/Faceline_Realtime.py", "-f", "-i", path, "-o", nginx_system_path]).wait()
	#os.system("python ../pipeline/Faceline_Realtime.py -f -i " + path + " -o " + nginx_system_path)
	tend = datetime.now()
	print tend - tstart
	print "File from " + path
	print "File should be moved to " + nginx_system_path
	return nginx_path	

#adds a file to the file queue
def add_file(path):
	global file_queue, request_semaphore
	file_queue.append(path)
	request_semaphore.release()

#processes a thread
for x in range(0, 2):
	processThread = ProcessThread(x)
	processThread.start()
	process_threads.append(processThread)
	
deleteThread = DeleteThread()
deleteThread.start()

factory = WebSocketServerFactory(u"wss://0.0.0.0:6654")
factory.protocol = MyServerProtocol
reactor.listenSSL(6654, factory, contextFactory)
reactor.run()




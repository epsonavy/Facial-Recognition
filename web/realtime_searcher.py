import sys
from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory
import os
import time
import threading
from collections import deque
import socket
from subprocess import Popen, PIPE
log.startLogging(sys.stdout)

file_queue = deque()
active = True

process_threads = []
socket_dictionary = {}

request_semaphore = threading.Semaphore(0)

class MyServerProtocol(WebSocketServerProtocol):
	def onConnect(self, request):
		global socket_dictionary
		socket_dictionary[request.protocols[0]] = request
	def onClose(self, wasClean, code, reason):
		1
	def onMessage(self, payload, isBinary):
		1
	def sendImageLink(self, token, link):
		global socket_dictionary
		client = socket_dictionary[token]
		if not client == None:
			reactor.callFromThread(self.sendMessage, client, link)
factory = WebSocketServerFactory()
factory.protocol = MyServerProtocol
reactor.listenTCP(6654, factory)
reactor.run()


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
		
		

			
def process_file(path):
	global socket_dictionary
	filename = path.replace('./realtime_processing/', '')
	#path = ./realtime_processing/epso__realtime__fdsaCKzKNfdsKNfsfdsKFDN.png

	#Run matt's script
	#Move that finished file into /usr/share/html/static
	nginx_path = 'http://52.53.243.111/static/' + filename
	nginx_system_path = '/usr/share/nginx/html/static/' + filename

	token = filename.split('__realtime__')
	token = token[0]
	#Waits until matt's script is finished
	Popen(["python", "../pipeline/Faceline.py", "-i", path, "-o", nginx_system_path]).wait() 

	MyServerProtocol.sendImageLink(token, nginx_path)
	

def add_file(path):
	global file_queue, request_semaphore
	file_queue.append(path)
	request_semaphore.release()
	
for x in range(0, 1):
	processThread = ProcessThread(x)
	processThread.start()
	process_threads.append(processThread)
	
deleteThread = DeleteThread()
deleteThread.start()


while active:
	for root, subFolders, files in os.walk('./realtime'):
		for file in files:
			if file.endswith('.png') or file.endswith('.jpg'):
				os.rename('./realtime/' + file, './realtime_processing/' + file)
				file_queue.append('./realtime_processing/' + file)
				request_semaphore.release()
	
	time.sleep(0.05)




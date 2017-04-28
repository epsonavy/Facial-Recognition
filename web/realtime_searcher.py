import sys
from twisted.python import log
from twisted.internet import reactor, ssl
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory, listenWS
import os
from random import randint
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

contextFactory = ssl.DefaultOpenSSLContextFactory('/etc/nginx/ssl/nginx.key', '/etc/nginx/ssl/nginx.crt')

class MyServerProtocol(WebSocketServerProtocol):
	def onConnect(self, request):
		global socket_dictionary
		socket_dictionary[request.protocols[0]] = request
		print "A client has connected!"
	def onClose(self, wasClean, code, reason):
		1
	def onMessage(self, payload, isBinary):
		1
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


class AcceptThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	
	def run(self):
		global socket, socket_dictionary
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.bind(('127.0.0.1', 6653))
		server_socket.listen(5)
		while active:
			(socket, address) = server_socket.accept()
			#WE NEED TO HANDLE THE WEBSOCKET PROTOCOL HERE
			#http://yz.mit.edu/wp/web-sockets-tutorial-with-simple-python-server/
			token = socket.recv(1024)
			token = token.replace('\n','') #Get rid of dem new lines
			token = token.replace('\r','')
			print "Added socket with token " + token
			socket_dictionary[token] = socket	
			readThread = ReadThread(socket)
			readThread.start()
			print "Socket is connected!"

class ReadThread(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.socket = socket
	def run(self):
		1

		
class DeleteThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		# Need to implement a list with -tr to get the oldest image and unlink it
		#os.unlink
		1
		
		

			
def process_file(path):
	global socket_dictionary
	print "Currently processing file " + path
	filename = path.replace('./realtime_processing/', '')
	#path = ./realtime_processing/epso__realtime__fdsaCKzKNfdsKNfsfdsKFDN.png

	#Run matt's script
	#Move that finished file into /usr/share/html/static
	nginx_path = 'http://52.53.243.111/static/' + filename
	nginx_system_path = '/usr/share/nginx/html/static/' + filename

	token = filename.split('__realtime__')
	token = token[0]
	#Waits until matt's script is finished

	Popen(["python", "../pipeline/Faceline_Realtime.py", "-f", "-i", path, "-o", nginx_system_path]).wait() 
	print "File from " + path
	print "File should be moved to " + nginx_system_path
	MyServerProtocol.sendImageLink(token, nginx_path)


def add_file(path):
	global file_queue, request_semaphore
	file_queue.append(path)
	request_semaphore.release()
	
for x in range(0, 2):
	processThread = ProcessThread(x)
	processThread.start()
	process_threads.append(processThread)
	
deleteThread = DeleteThread()
deleteThread.start()

factory = WebSocketServerFactory(u"wss://0.0.0.0:6654")

class FactoryThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		global contextFactory, factory
		factory.protocol = MyServerProtocol
		reactor.listenSSL(6654, factory, contextFactory)
		reactor.run(installSignalHandlers=False)

factoryThread = FactoryThread()
factoryThread.start()


while active:
	for root, subFolders, files in os.walk('./realtime'):
		for file in files:
			if file.endswith('.png') or file.endswith('.jpg'):
				print "Found an image. Ready to process"
				os.rename('./realtime/' + file, './realtime_processing/' + file)
				file_queue.append('./realtime_processing/' + file)
				request_semaphore.release()
	




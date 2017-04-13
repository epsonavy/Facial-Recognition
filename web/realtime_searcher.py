import os
import time
import threading
from collections import deque
import socket

file_queue = deque()
active = True

process_threads = []
socket_dictionary = {}

request_semaphore = threading.Semaphore(0)

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
		server_socket.bind(('127.0.0.1', 6654))
		server_socket.listen(5)
		while active:
			(socket, address) = server_socket.accept()
			token = socket.recv(1024)
			socket_dictionary[token] = socket	
			socket_dictionary[token].sendall('Added your token ' + token + ' to watch list')
			readThread = ReadThread(socket)
			readThread.start()
			print "Socket is connected!"

class ReadThread(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.socket = socket
	def run(self):
		1
		
		
		
		

			
def process_file(path):
	global socket_dictionary
	os.rename('./realtime/' + path, './realtime_processing/' + path)
	new_path = './realtime_processing/' + path

	#Run matt's script
	#Move that finished file into /usr/share/html/static
	nginx_path = 'https://openface.me/static/' + path
	token = path.split('_')
	token = token[0]

	socket_dictionary[token].sendall(nginx_path)

	

def add_file(path):
	global file_queue, request_semaphore
	file_queue.append(path)
	request_semaphore.release()
	
for x in range(0, 1):
	processThread = ProcessThread(x)
	processThread.start()
	process_threads.append(processThread)
	
acceptThread = AcceptThread()
acceptThread.start()


while 1:
	for root, subFolders, files in os.walk('./realtime'):
		for file in files:
			if file.endswith('.png'):
				process_file(file)
	
	time.sleep(0.05)




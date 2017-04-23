import os
from random import randint
import time
import threading
from collections import deque
import socket
from subprocess import Popen, PIPE

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
	filename = path.replace('./realtime_processing/', '')
	#path = ./realtime_processing/epso__realtime__fdsaCKzKNfdsKNfsfdsKFDN.png

	#Run matt's script
	#Move that finished file into /usr/share/html/static
	nginx_path = 'https://openface.me/static/' + filename
	nginx_system_path = '/usr/share/nginx/html/static/' + filename

	token = filename.split('__realtime__')
	token = token[0]
	#Waits until matt's script is finished
	#Popen(["python", "../pipeline/Faceline.py", "-i", path, "-o", nginx_system_path]).wait()
	time.sleep(randint(0,1))
	socket_dictionary[token].sendall(nginx_path + '\n')
	

def add_file(path):
	global file_queue, request_semaphore
	file_queue.append(path)
	request_semaphore.release()
	
for x in range(0, 2):
	processThread = ProcessThread(x)
	processThread.start()
	process_threads.append(processThread)
	
acceptThread = AcceptThread()
acceptThread.start()

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




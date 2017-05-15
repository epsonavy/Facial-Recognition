import socket
from packet import PacketType, Packet, RegisterPacket, LoadPacket, Header
import threading
import time
import os
import multiprocessing
from collections import deque
import datetime 
import math
import subprocess
from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory
from shutil import copyfile

import functools
import paramiko

alive = False
process_queue = deque()
process_semaphore = threading.Semaphore(0)
peer_servers = []
peer_paramiko = {}
#These are parallel arrays
packet_queue = deque()
packet_semaphore = threading.Semaphore(0)
peer_count = -1

#Format of images, size(PNG > BMP > JPG)
image_format = "png"
chunk_duration = 5.0

#pem key
pem_key = paramiko.RSAKey.from_private_key_file("/home/ubuntu/key/Distributed.pem")



class AllowAnythingPolicy(paramiko.MissingHostKeyPolicy):
	def missing_host_key(self, client, hostname, key):
		return


def my_callback(filename, bytes_so_far, bytes_total):
    print 'Transfer of %r is at %d/%d bytes (%.1f%%)' % (
        filename, bytes_so_far, bytes_total, 100. * bytes_so_far / bytes_total)

#Websocket server
#WebSocketServerProtocol)
class MyServerProtocol(WebSocketServerProtocol):
	#def onConnect(self, request):
	#	print "A client has connected!"
	#def onClose(self, wasClean, code, reason):
	#	1
	def onConnect(self, request):
		print "A client has connected!"
	def onMessage(self, payload, isBinary):
		print "ID received was " + payload
		self.factory.addId(self, payload)
		self.factory.sendMessageWebSocket(payload, "Peter is gay");
		self.factory.sendMessageWebSocket(payload, str(determine_split('./uploading/' + payload +'.mp4', 5.0)))
		MeowThread(payload).start()
	def onClose(self, wasClean, code, reason):
		1
	#def onMessage(self, payload, isBinary):
		#Receive 0 then look for 0.mp4 to process
	#	print payload
	#	try:
	#		process(id)
	#	except Exception as e:
	#		print "Error occurred when receiving a message from client " + str(e)

class MyServerFactory(WebSocketServerFactory):
	def __init__(self, *args, **kwargs):
		super(MyServerFactory, self).__init__(*args, **kwargs)
		self.clients = {}
	def addId(self, client, id):
		self.clients[id]  = client
		print "Added client to ID!"
	def sendMessageWebSocket(self, id, payload):
		print "Attempting to send client message"
		c = self.clients[id]
		if not c is None:
			print "Sending message"
			c.sendMessage(payload)
	

class ProcessRequest:
	def __init__(self, offset, duration, index, id):
		self.offset = offset #-ss 00:25
		self.duration = duration #-t 00:01
		self.index = index #0-29
		self.id = id #12394e982348923

class ProcessThread(threading.Thread):
	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID
		print "Thread #" + str(threadID) + " has started!"
	def run(self):
		global alive, image_format
		while alive:
			process_semaphore.acquire()
			if process_queue:
				request = process_queue.popleft()
				movie_file = './processing/' + str(request.id) + '/movie.mp4'
				ffmpeg_out = './processing/' + str(request.id) + '/' + str(request.index) + '/' + "%d." + image_format
				split_directory = './processing/' + str(request.id) + '/' + str(request.index) + '/'
				#1-24.png

				offset = request.offset #-ss flag for ffmpeg
				duration = request.duration #-t flag for ffmpeg
				#DO FFMPEG SPLIT


				outstream = open(os.devnull, 'w')
				ffmpegBreak = subprocess.Popen(["ffmpeg", "-ss", offset] + ["-t", duration] + ["-i", movie_file, ffmpeg_out], stdout=outstream, stderr=subprocess.STDOUT)
				ffmpegBreak.wait()

				print (request.index)
				#Once done splitting here

				send_available(request.id, request.index, split_directory)
		
class PacketThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		global alive, packet_queue, packet_semaphore, factory
		while alive:
			packet_semaphore.acquire()
			if packet_queue:
				packet = packet_queue.popleft()

				if type(packet) is RegisterPacket:
					#Handle register pqacket here
					print "Handling register packet"
				elif type(packet) is LoadPacket:
					os.rename('/home/ubuntu/dvp/distributed/processing/' + str(packet.id) + '/completed/' + str(packet.index) + '_final.mp4', '/usr/share/nginx/html/static/' + str(packet.id) + '_' + str(packet.index) + '.mp4')
					factory.sendMessageWebSocket(str(packet.id), 'http://54.193.119.113/static/' + str(packet.id) + '_' + str(packet.index) + '.mp4')


class MeowThread(threading.Thread):
	def __init__(self, payload):
		threading.Thread.__init__(self)
		self.payload = payload
	def run(self):
		process(self.payload)
def add_file(path):
	1
	#Remove and move somewhere else
	#Then add to the fucking queue

class AcceptThread(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.socket = socket
	def run(self):
		global alive, peer_servers, peer_paramiko, pem_key
		print "Server is ready to accept peer connections."
		while alive:
			(new_socket, address) = self.socket.accept()
			print ("the ip address is: " + str(address[0]))

			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(AllowAnythingPolicy())
			client.connect(address[0], username = 'ubuntu', pkey = pem_key)
			peer_paramiko[new_socket] = client
			print (peer_paramiko)

			peer_servers.append(new_socket)
			print "Peer server has connected!"
			ReceiveThread(new_socket).start()


class ReceiveThread(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.socket = socket
		self.alive = True
	def run(self):
		global packet_queue, packet_semaphore, peer_paramiko, peer_servers

		while self.alive:
			headerBytes = self.socket.recv(8)
			if headerBytes == '':
				self.alive = False

			header = Header()
			header.unpack(headerBytes)
			print "Received a packet!"

			packetBytes = self.socket.recv(header.size)
			if packetBytes == '':
				self.alive = False

			if header.type == PacketType.Register.value:
				print "Found a register packet!"
				packet = RegisterPacket()
				packet.unpack(packetBytes)
				packet_queue.append(packet)
			
			elif header.type == PacketType.Load.value:
				packet = LoadPacket()
				packet.unpack(packetBytes)
				packet_queue.append(packet)
			
			packet_semaphore.release()
			print "Packet has been added to packet queue"
		peer_servers.remove(self.socket)
		peer_paramiko.pop(self.socket)
		print "There are now " + str(len(peer_servers)) + " connections"
		print "There are now " + str(len(peer_paramiko)) + " paramiko connections"
def determine_split(path, chunk_duration):
	#Given a path determine how many splits are there. For example 0:30 with 1 second split is 30 splits
	#Ffprobe
	video_length = subprocess.check_output(['ffprobe', '-i', path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")])

	chunks = math.floor(float(video_length)) / chunk_duration
	print ("split movie into: " + str(chunks) + " chunks")
	return  int(math.ceil(chunks))

def process(id):
	global process_queue, process_semaphore, image_format
	print "Processing " + str(id) + ".mp4"
	#Move /uploading/0.mp4 to /processing/0/0.mp4
	if not os.path.exists('./processing/' + str(id)):
		os.mkdir('./processing/' + str(id))
	if not os.path.exists('./processing/' + str(id) + '/completed'):
		os.mkdir('./processing/' + str(id) + '/completed') #Making the completed directory. Movies will come back here SCP'd in directly.
	movie_file = './processing/' + str(id) + '/movie.mp4'
	print './uploading/' + str(id) + '.mp4'
	#os.rename('./uploading/' + str(id) + '.mp4', movie_file)
	copyfile('./uploading/' + str(id) + '.mp4', movie_file)

	start = datetime.datetime.now()


	global chunk_duration
	start_time = "00:00:00"

	default_time = datetime.datetime.strptime("00:00:00", '%H:%M:%S')
	convert_time =  default_time + datetime.timedelta(0, int(chunk_duration))
	duration = convert_time.strftime('%H:%M:%S')


	print ('\t\t' + " processing start");
	for x in range(0, determine_split(movie_file, chunk_duration)):

		os.mkdir('./processing/' + str(id) + '/' + str(x))
		process_queue.append(ProcessRequest(start_time, duration, x, id))
		process_semaphore.release() #Means starting at offset x to 1

		temp_time = datetime.datetime.strptime(start_time, '%H:%M:%S')
		temp_time = temp_time + datetime.timedelta(0, int(chunk_duration))
		start_time = temp_time.strftime('%H:%M:%S')

	
	while (not os.path.exists('./processing/' + str(id) + '/' + str(23) + '/1.' + image_format)):
		end = datetime.datetime.now()
	print ('\t\t' + " splitting finished at: " + str(end - start))

def send_available(id, index, path):
	global peer_count, peer_servers, peer_paramiko
	#Given a path like ./processing/0/0/
	#Send all files in that path to a server
	if len(peer_servers) == 0:
		return None
	peer_count = peer_count + 1

	if peer_count >= len(peer_servers):
		peer_count = 0
	client = peer_paramiko.get(peer_servers[peer_count])

	dest_path = '/home/ubuntu/dvp/distributed/received_images/' + str(id) + '/' + str(index) + '/'
	print ('dest: ' + dest_path)
	stdin, stdout, stderr = client.exec_command('mkdir -p ' + dest_path)
	stdout=stdout.readlines()
	print(stdout)
	stdin.close()
	sftp = client.open_sftp()
	print('/home/ubuntu/dvp/distributed/processing/'  + str(id) + '/' + str(index) + '/')
	start_path = '/home/ubuntu/dvp/distributed/processing/'  + str(id) + '/' + str(index) + '/'
	for root, directories, filenames in os.walk(path):
		for filename in filenames:
			callback_for_filename = functools.partial(my_callback, filename)
			print("the filename is: " + start_path +  str(filename))
			sftp.put(start_path+filename, dest_path + filename, callback=callback_for_filename)
	#client.close()

	#paramiko
	#send all files in path
	#print "Walking path " + path
	#if not os.path.exists('./received_images/' + str(id)):
	#	os.mkdir('./received_images/' + str(id))
	#if not os.path.exists('./received_images/' + str(id) + '/' + str(index)):
	#	os.mkdir('./received_images/' + str(id) + '/' + str(index))
	#for root, directories, filenames in os.walk(path):
	#	for filename in filenames:
	#		#debugging purposes
	#		#14949494940920_0_1.bmp
	#		#print("A: " + './processing/' + str(id) + '/' + str(index) + '/' + filename)
	#		#print("B: " + './received_images/' + str(index) +'/' + filename)
	#		os.rename('./processing/' + str(id) + '/' + str(index) + '/' + filename, './received_images/' + str(id) + '/' + str(index) + '/' +filename)



	loadHeader = Header()
	loadHeader.type = PacketType.Load

	loadPacket = LoadPacket()
	loadPacket.id = id
	loadPacket.index = index

	loadHeader.size = len(loadPacket.pack())

	print "Sending Load Packet to Peer Server #" + str(peer_count) + " with id " + str(id) + " and index: " + str(index)
	peer_servers[peer_count].sendall(loadHeader.pack())
	peer_servers[peer_count].sendall(loadPacket.pack())




alive = True
master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
master_socket.bind(('0.0.0.0', 27015))
master_socket.listen(0)

AcceptThread(master_socket).start()
PacketThread().start()

pu_count = multiprocessing.cpu_count()
#Leave one out for server and other shit
print "Starting Process Threads..."
for x in range(0, 1):
	ProcessThread(x).start()

time.sleep(10)
#process("1494544527034")
factory = MyServerFactory(u"ws://0.0.0.0:6654")
factory.protocol = MyServerProtocol

reactor.listenTCP(6654, factory)
reactor.run()

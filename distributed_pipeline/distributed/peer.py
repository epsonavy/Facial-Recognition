import socket
import threading
import os, inspect
import time
import subprocess
from collections import deque
from packet import Packet, PacketType, Header, RegisterPacket, LoadPacket

import glob
from datetime import datetime
import dlib
import cv2
import sys
import numpy as np

import paramiko


packet_queue = deque()
process_queue = deque()
packet_semaphore = threading.Semaphore(0)
process_semaphore = threading.Semaphore(0)
alive = True

#image_
image_format = "png"

#dlib library
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./shape_predictor_68_face_landmarks.dat') #directory for shape_predictor_68_face_landmarks.dat

#resize the image 
image_ratio = 0.6

#ip address of main directory
dire_address =  "54.193.119.113"

#paramiko
pem_key = paramiko.RSAKey.from_private_key_file("/home/ubuntu/key/Distributed.pem")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname = dire_address, username = 'ubuntu', pkey = pem_key)	
#sftp = client.open_sftp()

def in_rect(r, p):
    return p[0] > r[0] and p[1] > r[1] and p[0] < r[2] and p[1] < r[3] 

def ScanFrames (input_path, output_path, index, id):
	global image_format, client, peer_socket
	sftp = client.open_sftp()
	g = glob.glob(input_path + "*.png")
	print "ScanFrames starts!!!!"
	for i, fn in enumerate(g):
		print ("Handling frame " + str(i) + ":")
		tstart = datetime.now()
		HandleFrame(fn, output_path)
		tend = datetime.now()
		print("Finished handling frame " + str(tend - tstart))
	outstream = open(os.devnull, 'w')
	midPath = input_path + "%d.png"
	start = datetime.now()
	print (midPath)
	print ("building begin!!")
	ffmpegBuild = subprocess.Popen(["ffmpeg", "-i", midPath, output_path + str(index) + "_final.mp4"], stdout=outstream, stderr=subprocess.STDOUT)# Run FFMPEG to rebake the video
	ffmpegBuild.wait()

	#paramiko
	sftp.put(output_path + str(index) + "_final.mp4", output_path + str(index) + "_final.mp4")


	end = datetime.now()
	print ("building completed in :" + str(end-start))
	print "ScanFrames ends!!"
	loadHeader = Header()
	loadHeader.type = PacketType.Load
	loadPacket = LoadPacket()
	loadPacket.id = id
	loadPacket.index = index
	loadHeader.size = len(loadPacket.pack())
	
	peer_socket.sendall(loadHeader.pack())
	peer_socket.sendall(loadPacket.pack())	

	cleanUpImages(input_path, output_path)

def HandleFrame(fn, output_path):

	print "HandleFrame starts!!!!"
	img = cv2.imread(fn, 1)
	ptsList, breadthList = detectFrame(img)
	markFrame(fn, img, ptsList, breadthList)
	pupilData = getPupilData(fn) #IPC to get pupil data
	markPupil(img, pupilData, breadthList)

	cv2.imwrite(fn, img)
	print "HandleFrame ends!!!!!"


def detectFrame(img):
	global detector, predictor, image_ratio
	print "detectFrame starts!!!!"
	image = cv2.resize(img, (0,0), fx=image_ratio, fy=image_ratio)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	detections = detector(gray, 1)# type(detections) == dlib.rectangles

	ptsList = []
	breadthList = []

	for i, d in enumerate(detections):# type(d) == dlib.rectangle
		print("\t\tBeginning prediction (detection " + str(i) + ")")
		tstart = datetime.now()
		shape = predictor(gray, d)# type(shape) == dlib.full_object_detection

		pts = []
		for p in shape.parts():
			if p.x > 0 and p.y >0:
                #pts.append((p.x, p.y))
				pts.append((p.x/image_ratio, p.y/image_ratio))
		ptsList.append(pts)
		breadthList.append(np.sqrt(d.width() ** 2 + d.height() ** 2)) #this is a list of magnitudes of the hypotenuse (so called breadth) of the face detection
		tend = datetime.now()
		print("\t\t" + str(tend - tstart))
	print ("detectFrame ends!!!!")
	return ptsList, breadthList

def markFrame(fn, img, ptsList, breadthList):
	#if raw_input("Overwrite " + fn + " Y/N?") == "Y":
		print("\t\tBeginning Delauney drawing algorithm")
		tstart = datetime.now()
	
		i = 0
		for pts in ptsList:
			bounds = (0, 0, img.shape[1], img.shape[0])
			subdiv = cv2.Subdiv2D(bounds)
			for p in pts:
				subdiv.insert(p)
			tris = subdiv.getTriangleList();
			for t in tris:
				pt1 = (t[0], t[1])
				pt2 = (t[2], t[3])
				pt3 = (t[4], t[5])

				if in_rect(bounds, pt1) and in_rect(bounds, pt2) and in_rect(bounds, pt3):
					cv2.line(img, pt1, pt2, (0, 255, 0), int(breadthList[i] * 1/100), 8, 0) #tried using cv2.CV_AA
					cv2.line(img, pt2, pt3, (0, 255, 0), int(breadthList[i] * 1/100), 8, 0)
					cv2.line(img, pt3, pt1, (0, 255, 0), int(breadthList[i] * 1/100), 8, 0)
		i+=1 #something weird may happen
		tend = datetime.now()
		print("\t\t" + str(tend - tstart))
	#else:
	#	print("Permission denied. (mark Frame)")

def getPupilData(input_path):
	print("\t\tsubprocessing pupil data")
	tstart = datetime.now()
	eyeLine = subprocess.Popen(["./eyeLine", "-d", input_path], stdout=subprocess.PIPE, shell=True)
	eyeLine.wait()
	eyeLineStdout = eyeLine.communicate()[0]

	spaceIndexing = eyeLineStdout.split(" ")
	pupilData = []

	if len(spaceIndexing) % 5 == 0:				#it parsed appropriately
		spaceIndexing = spaceIndexing[:len(spaceIndexing)-1] 	#remove newlines elements from parsing, NOT FINISHED, ONLY HANDLES ONE SET ATM... LAZINESS
		for i, sp in enumerate(spaceIndexing):
			if i & 1 == 0: #every other one (think c: step+=2)
				pupilData.append((int(sp), int(spaceIndexing[i+1])))
	else:
		pupilData.append((-1, -1)) #dummy data necessary for drawing appropriate scaled pupils later
    
	tend = datetime.now()
	print("\t\t" + str(tend - tstart))
	return pupilData


def markPupil(img, pupilData, breadthList):
	print("\t\tDrawing pupils to image.")
	#if raw_input("Overwrite " + fn + " Y/N?") == "Y":
	tstart = datetime.now()
	i = 0
	for pupil in pupilData:
		if pupil != (-1, -1):
			pupilArray = np.array(pupil, np.int32).reshape((-1, 1, 2))
			cv2.polylines(img, pupilArray, True, (0, 0, 255/(i+1)), int(breadthList[i/2] * 3/100))
			cv2.polylines(img, pupilArray, True, (255/(i+1), 0, 0), int(breadthList[i/2] * 1/100))
			i += 1
	tend = datetime.now()
	print("\t\t" + str(tend - tstart))
	#else:
		#print("Permission denied. (mark Pupil")

def cleanUpImages(input_path, output_path):
	global image_format
	for f in glob.glob(input_path[:input_path.rfind(".")] + "*.png"):
		os.remove(f)
	for f in glob.glob(output_path[:output_path.rfind(".")] + "*.png"):
		os.remove(f)
	for f in glob.glob(output_path[:output_path.rfind(".")] + "*.mp4"):
		os.remove(f)


class PacketThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		global process_semaphore, packet_semaphore, process_queue, packet_queue
		while alive:
			print "Waiting for a packet.."
			packet_semaphore.acquire()
			print "Received a packet!"
			if packet_queue:
				packet = packet_queue.popleft()
				print "Received a packet of type " + str(type(packet))
				#Public infomraiton
				if type(packet) is RegisterPacket:
					1
				elif type(packet) is LoadPacket:
					print "Added load packet to process queue with id " + str(packet.id) + " index: " + str(packet.index)
					process_queue.append(ProcessRequest(packet.index, packet.id))
					process_semaphore.release()



class ProcessThread(threading.Thread):
	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID
		print "Thread #" + str(threadID) + " has started!"
	def run(self):
		global process_semaphore, process_queue
		while alive:
			print "Waiting for process semaphore.."
			process_semaphore.acquire()
			print "Acquired process semaphore"
			if process_queue:
				print "Found something in process_queue"
				request = process_queue.popleft()
				input_path = './received_images/' + str(request.id) + "/" + str(request.index) +"/"
				output_path = '/home/ubuntu/dvp/distributed/processing/'+ str(request.id) + '/completed' + "/"
				print ("the id is : " + str(request.id) + "the index is : " + str(request.index))
				print (input_path)
				print (output_path)
				if not os.path.exists(output_path):
					os.makedirs(output_path)
				ScanFrames(input_path, output_path, request.index, request.id)


class ProcessRequest:
	def __init__(self, index, id):
		self.index = index #0-29
		self.id = id #12394e982348923


class ReceiveThread(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.socket = socket
		self.alive = True
	def run(self):
		global packet_queue, packet_semaphore, peer_socket
		while self.alive:
			headerBytes = self.socket.recv(8)
			if headerBytes == '':
				self.alive = False
			print "Received header"
			header = Header()
			header.unpack(headerBytes)
			
			packetBytes = self.socket.recv(header.size)
			if packetBytes == '':
				self.alive = False
			print "Rceived Packet"
			if header.type == PacketType.Register.value:
				packet = RegisterPacket()
				packet.unpack(packetBytes)
				packet_queue.append(packet)
			elif header.type == PacketType.Load.value:
				print "Received a load packet, adding to packet queue"
				packet = LoadPacket()
				packet.unpack(packetBytes)
				packet_queue.append(packet)
				print len(packet_queue)

			packet_semaphore.release()

		 #Wait 5 seconds before reconnecting again
		hasNotEstablished = True

		while hasNotEstablished:
			time.sleep(5)
			print "Attempting to reconnect"
			peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				peer_socket.connect(('54.193.119.113', 27015))
				initialHeader = Header()
				initialHeader.type = PacketType.Register

				registerPacket = RegisterPacket()
				registerPacket.id = 0

				initialHeader.size = len(str(registerPacket.pack()))
				print initialHeader.size
				print len(str(registerPacket.pack()))
				print len(str(initialHeader.pack()))


				peer_socket.sendall(initialHeader.pack())
				peer_socket.sendall(registerPacket.pack())
				ReceiveThread(peer_socket).start()
				hasNotEstablished = False
			except Exception as e:
				print "Error occurred while connecting " + str(e)

hasNotEstablished = True

while hasNotEstablished:
	peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		peer_socket.connect(('54.193.119.113', 27015))
		initialHeader = Header()
		initialHeader.type = PacketType.Register

		registerPacket = RegisterPacket()
		registerPacket.id = 0

		initialHeader.size = len(str(registerPacket.pack()))
		print initialHeader.size
		print len(str(registerPacket.pack()))
		print len(str(initialHeader.pack()))


		peer_socket.sendall(initialHeader.pack())
		peer_socket.sendall(registerPacket.pack())
		ReceiveThread(peer_socket).start()
		hasNotEstablished = False
	except Exception as e:
		print "Error occurred while connecting " + str(e)

PacketThread().start()
ProcessThread(0).start()


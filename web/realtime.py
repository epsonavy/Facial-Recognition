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
import sys        # For argument handling
import datetime
import os, inspect  # For path handling, file deletion
from datetime import datetime
import dlib      # For facial recognition (neural network)

import glob      # For file path handling

import subprocess   # For running FFMPEG

import cv2        # image input/output, dependency to be refactored with OpenCV

import numpy as np  # For array handling

import scipy.misc


log.startLogging(sys.stdout)

file_queue = deque()
active = True

process_threads = []
socket_dictionary = {}
count = 0
request_semaphore = threading.Semaphore(0)
predictor_path = "../pipeline/shape_predictor_68_face_landmarks.dat"
contextFactory = ssl.DefaultOpenSSLContextFactory('/etc/nginx/ssl/nginx.key', '/etc/nginx/ssl/nginx.crt')

detector = dlib.get_frontal_face_detector()

predictor = dlib.shape_predictor(predictor_path)

'''
To-Do:
Parallel Processing
Eye tracking
'''

lazy_output_file = None
global_script_start = datetime.now()
def displayHelp():

	print(" Available Arguments\tDefault Arguments")

	print(" -h\tAccess the help menu (--help)")

	print(" -p\tPath of the Dlib predictor\t" + run_dir + "/shape_predictor_68_face_landmarks.dat")

	print(" -f\tProcess only a single frame\tFalse")

	print(" -d\tDraw Mode (Dot, Line, Delauney)\tDot")

	print(" -ss\tStart time of input file\t00:00.00")

	print(" -t\tDuration of final video\t\t00:01.00")

	print(" -i\tInput file path\t\t\t" + input_path)

	print(" -o\tOutput file path\t\tNamed as input + .mp4 unless specified")

	print(" -w\tWait before mutating frame\tFalse")

	print(" Sample shell input:\t\t\tpython Faceline.py -ss 00:30 -t 00:02 -i /home/hew/desktop/F/Fash.divx")



def in_rect(r, p):

	return p[0] > r[0] and p[1] > r[1] and p[0] < r[2] and p[1] < r[3] 

def data_uri_to_cv2_img(uri):
	encoded_data = uri.split(',')[1]
	nparr = np.fromstring(encoded_data.decode('base64'), np.uint8)
	img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
	return img

def markImg(fn, detector, predictor, draw_mode, output_path):					   # THIS FUNCTION MUTATES FILES
	global lazy_output_file, global_script_start
	print "Base encoding time"
	tstart = datetime.now()
	content_file = open(fn, 'r')
	img = data_uri_to_cv2_img(content_file.read())					
	content_file.close() 
	tend = datetime.now()
	print tend - tstart
	# load image with file name

	#win.clear_overlay()
	#win.set_image(img)
	print "Processing image now"
	print "Detection time"
	tstart = datetime.now()
	detections = detector(img, 1)						   # type(detections) == dlib.rectangles
	tend = datetime.now()
	print tend - tstart

	print "Algorithm"
	tstart = datetime.now()
	for d in detections:									# type(d) == dlib.rectangle

		shape = predictor(img, d)						   # type(shape) == dlib.full_object_detection

		pts = []

		for p in shape.parts():

			pts.append((p.x, p.y))

		ptsArray = np.array(pts, np.int32)

		ptsArray = ptsArray.reshape((-1, 1, 2))



		if draw_mode == "dot":

			cv2.polylines(img, ptsArray, True, (0, 0, 255))	# mark image with OpenCV

		elif draw_mode == "line":

			cv2.polylines(img, [ptsArray], True, (0, 0, 255))	# mark image with OpenCV

		elif draw_mode == "delauney":

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

					cv2.line(img, pt1, pt2, (0, 0, 255), 1, 8, 0) #tried using cv2.CV_AA

					cv2.line(img, pt2, pt3, (0, 0, 255), 1, 8, 0)

					cv2.line(img, pt3, pt1, (0, 0, 255), 1, 8, 0)


	cv2.imwrite(output_path, img)									#overwrite the image
	tend = datetime.now()
	print tend - tstart
	end_me = datetime.now()
	print "This is when it stopped"
	print end_me - global_script_start

#Server client goodies
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
		
		

#processes a file for realtime face detection	
def process_file(path):
	global socket_dictionary, detector, predictor
	print "Currently processing file " + path
	filename = path.replace('./realtime_processing/', '')
	#path = ./realtime_processing/epso__realtime__fdsaCKzKNfdsKNfsfdsKFDN.png

	#Run matt's script
	#Move that finished file into /usr/share/html/static
	nginx_path = 'https://54.67.30.141/static/' + filename
	nginx_system_path = '/usr/share/nginx/html/static/' + filename

	token = filename.split('__realtime__')
	token = token[0]
	#Waits until matt's script is finished
	tstart = datetime.now()
	markImg(path, detector, predictor, "dot", nginx_system_path)
	#os.system("python ../pipeline/Faceline_Realtime.py -f -i " + path + " -o " + nginx_system_path)
	tend = datetime.now()
	print tend - tstart
	print "File from " + path
	print "File should be moved to " + nginx_system_path
	return nginx_path	

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
factory.protocol = MyServerProtocol
reactor.listenSSL(6654, factory, contextFactory)
reactor.run()




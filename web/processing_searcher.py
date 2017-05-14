import sys
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

import glob      # For file path handling

import subprocess   # For running FFMPEG


import numpy as np  # For array handling

import psycopg2



conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='student'")

file_queue = deque()
active = True

process_threads = []
socket_dictionary = {}
count = 0
request_semaphore = threading.Semaphore(0)


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
		
# remove status file
def removeStatus(username):
    try:
        os.remove("status/" + username + ".status")
    except OSError:
        pass

			
def process_file(path):
	global socket_dictionary, detector, predictor, count, conn
	#os.system("python ../pipeline/Faceline_Realtime.py -f -i " + path + " -o " + nginx_system_path)
	count = count + 1	
	output_path = path.replace('./processing/', '')
	true_filename = output_path.replace('.mp4', '') + '.mp4'
	filename = output_path.replace('.mp4', '') + str(count) + '.mp4'

	relative_path =  'public/videos/' + filename
	username = output_path.replace('.mp4', '')
	print "The username is " +  username
	print "Relative path " + relative_path
	print "Filename is " + filename
	output_path = '/Facial-Recognition/web/public/videos/' + filename
	print "-i " + path
	print "-o " + output_path

	Popen(['python', '../pipeline/Faceline.py', '-l', '-i', '/Facial-Recognition/web/processing/' + true_filename, '-o', output_path, '-v']).wait()
	print "python ../pipeline/Faceline.py -l -i /Facial-Recognition/web/processing/" + true_filename + " -o " + output_path + " -v"
	with open('vProcessing.json', 'r') as myfile:
		data = myfile.read().replace('\n', '')
	cur = conn.cursor()
	cur.execute("INSERT INTO user_videos(path, username, v_processing) values('" + relative_path + "', '" + username + "', '" + data + "');" )
	conn.commit()
	print "INSERT INTO user_videos(path, username) values('" + relative_path + "', '" + username + "');"
	os.unlink(path)
	print "Inserted video into database. Now ready to view"
	#Write into database now
	removeStatus(username)

	
for x in range(0, 2):
	processThread = ProcessThread(x)
	processThread.start()
	process_threads.append(processThread)
	
while active:
	for root, dirnames, filenames in os.walk('./processing'):
		for filename in filenames:
			if filename.endswith(".mp4"):
				print "Added file " + filename + " to processing queue"
				process_file('./processing/' + filename)
	time.sleep(1)

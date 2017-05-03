import sys          # For argument handling
import os, inspect  # For path handling, file deletion
import dlib         # For facial recognition (neural network)
import glob         # For file path handling
import subprocess   # For running FFMPEG
import cv2          # image input/output
import numpy as np  # For array handling, line scaling

'''
TO HOOK INTO THE DATABASE (POSTGRES)
1. filename -> meta-data + frames
   meta-data -> face datapoints (for each frame)
2. video ID -> meta data -> eye datapoints (for each frame)
3. video ID -> meta data -> Delauney tri images (w/o overwrite)
'''

'''
To-Do:
Head Pos: Yaw, Pitch, Roll
write eye tracking coords to db
'''

def displayHelp():
    print(" Available Arguments\t\t\tDefault Arguments")
    print(" -h\tAccess the help menu (--help)")
    print(" -l\tlose original frames(overwrite)\tFalse")
    print(" -p\tPath of the Dlib predictor\t" + run_dir + "/shape_predictor_68_face_landmarks.dat")
    print(" -f\tProcess only a single frame\tFalse")
    print(" -ss\tStart time of input file\t00:00.00")
    print(" -t\tDuration of final video\t\t00:01.00")
    print(" -i\tInput file path\t\t\t" + input_path)
    print(" -o\tOutput file path\t\tInput file path + \"_final.mp4\"")
    print(" -v\tVerbose\t\t\t\tFalse")
    print(" -w\tWait before mutating frame\tFalse")
    print(" Sample shell input:\t\t\tpython Faceline.py -l -ss 00:30 -t 00:01 -i /home/hew/Desktop/F/Fash.divx")

def in_rect(r, p):
    return p[0] > r[0] and p[1] > r[1] and p[0] < r[2] and p[1] < r[3] 

def markFrame(img, ptsList, wait_at_frame):
    if(not wait_at_frame) or raw_input("Overwrite " + fn + " Y/N?") == "Y":
        for i, pts in enumerate(ptsList):
	    if i & 1 == 0:
		ptsArray = np.array(pts, np.int32).reshape((-1, 1, 2))
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
			cv2.line(img, pt1, pt2, (0, 255, 0), int(np.sqrt(ptsList[i+1][0] ** 2 + ptsList[i+1][1] ** 2) * 1/100), 8, 0) #tried using cv2.CV_AA
                        cv2.line(img, pt2, pt3, (0, 255, 0), int(np.sqrt(ptsList[i+1][0] ** 2 + ptsList[i+1][1] ** 2) * 1/100), 8, 0)
                        cv2.line(img, pt3, pt1, (0, 255, 0), int(np.sqrt(ptsList[i+1][0] ** 2 + ptsList[i+1][1] ** 2) * 1/100), 8, 0)
    else:
        print("Permission denied.")

def markPupil(img, ptsList, wait_at_frame):
    if(not wait_at_frame) or raw_input("Overwrite " + fn + " Y/N?") == "Y":
        for i, pts in enumerate(ptsList):
            if i & 1 == 0:
	        ptsArray = np.array(pts, np.int32).reshape((-1, 1, 2))
		cv2.polylines(img, ptsArray, True, (0, 0, 255), int(np.sqrt(ptsList[i+1][0] ** 2 + ptsList[i+1][1] ** 2) * 3/100))
                cv2.polylines(img, ptsArray, True, (255, 0, 0), int(np.sqrt(ptsList[i+1][0] ** 2 + ptsList[i+1][1] ** 2) * 1/100))
    else:
	print("Permission denied.")


def detectFrame(img, detector, predictor): # returns a list of lists of points
    ptsList = []
    print("Beginning detection.")
    detections = detector(img, 1)# type(detections) == dlib.rectangles
    for i, d in enumerate(detections):# type(d) == dlib.rectangle
        print("Beginning prediction for detection " + str(i))
        shape = predictor(img, d)# type(shape) == dlib.full_object_detection

        pts = []
        for p in shape.parts():
            pts.append((p.x, p.y))
        ptsList.append(pts)
	ptsList.append((d.width(), d.height()))

    return ptsList

def getMetadata(input_path):
    ffprobe = subprocess.Popen(["ffprobe", "-show_streams", input_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ffprobe.wait()
    metadata = ffprobe.communicate()[0]

    metaWidth = metadata[metadata.find("width="):metadata.find("\n", metadata.find("width="))]
    metaHeight = metadata[metadata.find("height="):metadata.find("\n", metadata.find("height="))]
    metaAvgRate = metadata[metadata.find("avg_frame_rate="):metadata.find("\n", metadata.find("avg_frame_rate="))]
    metaFrameNumb = metadata[metadata.find("nb_frames="):metadata.find("\n", metadata.find("nb_frames="))]
    
    return [metaWidth, metaHeight, metaAvgRate, metaFrameNumb]	

def getPupilData(input_path):
    eyeLine = subprocess.Popen(["./eyeLine", "-d", input_path], stdout=subprocess.PIPE)
    eyeLine.wait()
    eyeLineStdout = eyeLine.communicate()[0]

    spaceIndexing = eyeLineStdout.split(" ")
    spaceIndexing = spaceIndexing[:len(spaceIndexing)-1]

    pupilData = []

    for i, pupilCoord in enumerate(spaceIndexing):
        if i & 1 == 0 and pupilCoord != "Face":
            print "Is this face and a string?: " + pupilCoord
            pupilData.append((int(pupilCoord), int(spaceIndexing[i+1])))
    return pupilData 

def handleFrame(input_path, detector, predictor, wait_at_frame):
    img = cv2.imread(input_path, 1)
    ptsList = detectFrame(img, detector, predictor)

    #write ptsList to JSON
    #write JSON to DB
	
    pupilData = getPupilData(input_path) #IPC to get pupil data
    if len(pupilData) > 0:
        for i, pl in enumerate(ptsList):
            if i & 1 == 0:
	        ptsList[i].append(pupilData[i/2])

    #write pupil data to DB
	
    markFrame(img, ptsList, wait_at_frame)
    if len(ptsList) >= 1:
        markPupil(img, [pupilData, ptsList[1]], wait_at_frame)
    cv2.imwrite(((input_path[:input_path.rfind(".")] + "_final.png") if newCopy else input_path), img) 
    return img #for the sake of the single frame option (needed metadata)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Error: Too few arguments supplied.")
        exit()
    elif len(sys.argv) > 14:
        print("Error: Too many arguments supplied.")
        exit()

    run_dir = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
    predictor_path = run_dir + "/shape_predictor_68_face_landmarks.dat"
    newCopy = True
    single_frame = False
    start_time = "00:00"
    duration = "00:01"
    input_path = ""
    output_path = ""
    verbose = False
    wait_at_frame = False

    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        displayHelp()
        exit()

    for index, arg in enumerate(sys.argv):
        if arg == "-l":
            newCopy = False
        elif arg == "-p":
            predictor_path = sys.argv[index+1]
        elif arg == "-f":
            single_frame = True
        elif arg == "-ss":
            start_time = sys.argv[index+1]
        elif arg == "-t":
            duration = sys.argv[index+1]
        elif arg == "-i":
            input_path = sys.argv[index+1]
            if output_path == "":
                output_path = input_path[:input_path.rfind(".")] + "_final.mp4"
        elif arg == "-o":
            output_path = sys.argv[index+1]
        elif arg == "-v":
            verbose = True
        elif arg == "-w":
            wait_at_frame = True

    if input_path == "":
        print("Please enter an input file")
        exit()

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)

    outstream = (None if verbose else open(os.devnull, 'w')) #for redirecting output to nothing as desired

    if single_frame:
	img = handleFrame(input_path, detector, predictor, wait_at_frame)
        print("Image " + input_path + ": Width - " + str(img.shape[0]) + ", Height - " + str(img.shape[1]))


    else:
	metadata = getMetadata(input_path)
	for d in metadata:
	    print(d)
	#write metadata to DB
        
        midPath = input_path[:input_path.rfind(".")] + "%d.png"
        ffmpegBreak = subprocess.Popen(["ffmpeg","-i", input_path, midPath], stdout=outstream, stderr=subprocess.STDOUT) # Run FFMPEG, using pngs
	ffmpegBreak.wait()

        g = glob.glob(input_path[:input_path.rfind(".")] + "*.png")
        for i, fn in enumerate(g):
                print("Image " + str(i) + ":")
		handleFrame(fn, detector, predictor, wait_at_frame)

        if newCopy:
            midPath = midPath[:midPath.rfind(".")] + "_final.png"
        
	ffmpegBuild = subprocess.Popen(["ffmpeg", "-i", midPath, output_path], stdout=outstream, stderr=subprocess.STDOUT)# Run FFMPEG to rebake the video
        ffmpegBuild.wait()

	if newCopy:
            for f in glob.glob(input_path[:input_path.rfind(".")] + "*_final.png"):
                os.remove(f)
        else:
            for f in glob.glob(input_path[:input_path.rfind(".")] + "*.png"):
                os.remove(f)
    print("Execution Complete.")

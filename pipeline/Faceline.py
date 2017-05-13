import sys          # For argument handling
import datetime
from datetime import datetime
import os, inspect  # For path handling, file deletion
import dlib         # For facial recognition (neural network)
import glob         # For file path handling
import subprocess   # For running FFMPEG
import cv2          # image input/output
import numpy as np  # For array handling, line scaling
import json
import psycopg2

'''
To-Do:
Parallel Processing
Head Pos: Yaw, Pitch, Roll
realtime independent of filesystem
database calls
'''

global_script_start = datetime.now() 
URI_Handling = False

glbJson = {}
glbJsonFcount = 0
glbJsonPcount = 0
glbJsonPYRcount = 0

#Prints the CLI help menu
def displayHelp():
    print(" Available Arguments\t\t\tDefault Arguments")
    print(" -h\tAccess the help menu (--help)")
    print(" -uri\thandle URI images (thanks Kevin/Pei)")
    print(" -l\tlose original frames(overwrite)\tFalse")
    print(" -r\trealtime (don't track pupils)\tFalse")
    print(" -p\tPath of the Dlib predictor\t" + run_dir + "/shape_predictor_68_face_landmarks.dat")
    print(" -f\tProcess only a single frame\tFalse")
    print(" -ss\tStart time of input file\t00:00.00")
    print(" -t\tDuration of final video\t\t00:01.00")
    print(" -i\tInput file path\t\t\t" + input_path)
    print(" -o\tOutput file path\t\tInput file path + \"_final.mp4\"")
    print(" -v\tVerbose\t\t\t\tFalse")
    print(" -w\tWait before mutating frame\tFalse")
    print(" Sample shell input:\t\t\tpython Faceline.py -l -ss 00:30 -t 00:01 -i /home/hew/Desktop/F/Fash.divx")

#Returns boolean representing whether point 1 or point two is within the points of rectangle r
def in_rect(r, p):
    return p[0] > r[0] and p[1] > r[1] and p[0] < r[2] and p[1] < r[3] 

#Takes URI of data location and converts it to a cv2 image.
def data_uri_to_cv2_img(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(encoded_data.decode('base64'), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def findPitch(pts, verbose):
    print("\t\t\tCalculating Pitch") #compare magnitudes of vectors 0-1(16-15) with 7-8(9-8)

    #chin calculations
    leftChin = pts[7]
    centerChin = pts[8]
    rightChin = pts[9]

    leftChinEdge = [centerChin[0] - leftChin[0], centerChin[1] - leftChin[1]]
    leftChinMag = np.sqrt(leftChinEdge[0]**2 + leftChinEdge[1]**2)

    rightChinEdge = [rightChin[0] - centerChin[0], rightChin[1] - centerChin[1]]
    rightChinMag = np.sqrt(rightChinEdge[0]**2 + rightChinEdge[1]**2)

    #edge calculations
    leftPt = pts[0]
    leftPt2 = pts[1]
    leftEdge = [leftPt[0] - leftPt2[0], leftPt[1] - leftPt2[1]]
    leftEdgeMag = np.sqrt(leftEdge[0]**2 + leftEdge[1]**2)
    
    rightPt = pts[16]
    rightPt2 = pts[15]
    rightEdge = [rightPt[0] - rightPt2[0], rightPt[1] - rightPt2[1]]
    rightEdgeMag = np.sqrt(rightEdge[0]**2 + rightEdge[1]**2)

    #average the symmetrical magnitudes for redundant safety (avoid contamination by yaw or roll)
    edgeMag = (leftEdgeMag + rightEdgeMag) / 2
    chinMag = (leftChinMag + rightChinMag) / 2

    pitch = chinMag / edgeMag #similar (near 1) means level, large ratio means large pitch, unfortunately relative only
    pitch *= 180 / np.pi #pretend this is degrees
    return pitch

def findYaw(pts, verbose):
    print("\t\t\tCalculating yaw")
    leftPt = pts[0]
    leftTear = pts[39]
    rightPt = pts[16]
    rightTear = pts[42]

    leftSpan = [leftTear[0] - leftPt[0], leftTear[1] - leftPt[1]]
    rightSpan = [rightPt[0] - rightTear[0], rightPt[1] - rightTear[1]]

    leftSpanMag = np.sqrt(leftSpan[0]**2 + leftSpan[1]**2)
    rightSpanMag = np.sqrt(rightSpan[0]**2 + rightSpan[1]**2)
            
    deltaSpanMag = leftSpanMag - rightSpanMag
    avgSpanMag = (leftSpanMag + rightSpanMag) / 2
    yaw = deltaSpanMag / avgSpanMag # 0 is dead-on, -1 is looking left, 1 is looking right, supposedly
    yaw *= 180 / np.pi

    if verbose:
        print("\t\t\tLeft Point is " + str(leftPt))
        print("\t\t\tLeft tearduct is " + str(leftTear))
        print("\t\t\tRight Point is " + str(rightPt))
        print("\t\t\tRight tearduct is " + str(rightTear))
        print("\t\t\tLeft span is " + str(leftSpan))
        print("\t\t\tRight span is " + str(rightSpan))
        print("\t\t\tLeft span magnitude is " + str(leftSpanMag))
        print("\t\t\tRight span magnitude is " + str(rightSpanMag))
        print("\t\t\tDelta span magnitude is " + str(deltaSpanMag))
        print("\t\t\tAverage span magnitude is " + str(avgSpanMag))
        print("\t\t\tYaw is " + str(yaw))
    
    return yaw

def findRoll(pts, verbose):
    print("\t\t\tCalculating Roll")
    leftCorner = pts[36]
    rightCorner = pts[45]
    noseBridge = pts[28]

    leftDiag = [leftCorner[0] - noseBridge[0], leftCorner[1] - noseBridge[1]]
    rightDiag = [rightCorner[0] - noseBridge[0], rightCorner[1] - rightCorner[1]]

    leftRads = np.arctan(float(leftDiag[1])/leftDiag[0])
    rightRads = np.arctan(float(rightDiag[1])/rightDiag[0])
    rollRads = leftRads - rightRads
    roll = rollRads * 180 / np.pi   
        
    if verbose:
        print("\t\t\tLeft corner is " + str(leftCorner))
        print("\t\t\tRight corner is " + str(rightCorner))
        print("\t\t\tNose bridge is " + str(noseBridge))
        print("\t\t\tLeft diagonal is " + str(leftDiag))
        print("\t\t\tRight diagonal is " + str(rightDiag))
        print("\t\t\tLeft angle is " + str(leftRads) + " Rads")
        print("\t\t\tRight angle is "+ str(rightRads) + " Rads")
        print("\t\t\tRoll is " + str(roll))

    return roll

def approximatePYR(ptsList, verbose):
    global glbJson, glbJsonPYRcount
    print("\tBeginning PYR calculations")
    tstart = datetime.now()
    pitchList = []
    yawList = []
    rollList = []

    if ptsList[0][0] == (-1, -1):
        print("\t\t(No detection)")
    else:
        for i, pts in enumerate(ptsList):

            print("\t\tFor detection " + str(i))
            pitch = findPitch(pts, verbose)
            pitchList.append(pitch)

            yaw = findYaw(pts, verbose)
            yawList.append(yaw)
            
            roll = findRoll(pts, verbose)
            rollList.append(roll)
        
        glbJson["PYR " + str(glbJsonPYRcount)] = [pitchList, yawList, rollList]
        glbJsonPYRcount += 1
    tend = datetime.now()
    print("\t\t\t" + str(tend - tstart))
    return pitchList, yawList, rollList

# Takes in an image, list of points,
# breadthList which is a list of all of the hypotenuses, and a frame to wait at,
# Draws Delaunay triangles across points within the
# Bounded area. Achieved by subdividing and then drawing lines for each tri
# using OpenCV Delaunay triangle algorithm succeeded by cv2 line drawing.
def markFrame(img, ptsList, breadthList, pitchList, yawList, rollList, wait_at_frame):
    if(not wait_at_frame) or raw_input("Overwrite " + fn + " Y/N?") == "Y":
        print("\tBeginning Delauney drawing")
        tstart = datetime.now()
        if ptsList[0] == [(-1, -1)]:
            print("\t\tNaught to mark")
        else:
            i = 0
            for pts in ptsList:
                cv2.putText(img, "Pitch: " + str(pitchList[i]) + " Deg", (0, img.shape[0]-75), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(img, "Yaw: " + str(yawList[i]) + " Deg", (0, img.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(img, "Roll: " + str(rollList[i]) + " Deg", (0, img.shape[0]-25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
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
                i+=1
        tend = datetime.now()
        print("\t\t" + str(tend - tstart))
    else:
        print("Permission denied.")

#Draws Lines related to pupils on an input image,
#at points pupil data across hypotenuses in breadthList, waits a given frame.
def markPupil(img, pupilData, breadthList, wait_at_frame):
    print("\tBeginning pupil marking")
    if (not wait_at_frame) or raw_input("Overwrite " + fn + " Y/N?") == "Y":
        tstart = datetime.now()
        if pupilData[0] != (-1, -1):
            i = 0
            for pupil in pupilData:
                pupilArray = np.array(pupil, np.int32).reshape((-1, 1, 2))
                cv2.polylines(img, pupilArray, True, (0, 0, 255/(i+1)), int(breadthList[i/2] * 3/100))
            i += 1
        else:
            print("\t\tNo pupils to mark")
        tend = datetime.now()
        print("\t\t" + str(tend - tstart))
    else:
        print("Permission denied.")

#Takes an image, detector and predictor and returns a list of lists of points and a list of hypotenuses
def detectFrame(img, detector, predictor):
    print("\tBeginning detection")
    tstart = datetime.now()
    detections = detector(img, 1)# type(detections) == dlib.rectangles
    tend = datetime.now()
    print("\t\t" + str(tend - tstart))

    ptsList = []
    breadthList = []

    if(len(detections) == 0):
        print("\t\t(No detection)")
        ptsList.append([(-1,-1)]) #dummy detection for pupils
        breadthList.append(0) #zero breadth for pupils
    else:
        for i, d in enumerate(detections):# type(d) == dlib.rectangle
            print("\tBeginning prediction (detection " + str(i) + ")")
            tstart = datetime.now()
            shape = predictor(img, d)# type(shape) == dlib.full_object_detection

            pts = []
            for p in shape.parts():
                tx = p.x
                ty = p.y
                if tx >= img.shape[1]:
                    tx = img.shape[1] - 1
                elif tx < 0:
                    tx = 0
                if ty >= img.shape[0]:
                    ty = img.shape[0] - 1
                elif ty < 0:
                    ty = 0
                pts.append((tx, ty))
            ptsList.append(pts)

            breadthList.append(np.sqrt(d.width() ** 2 + d.height() ** 2)) #this is a list of magnitudes of the hypotenuse (so called breadth) of the face detection
    tend = datetime.now()
    print("\t\t" + str(tend - tstart))

    return ptsList, breadthList

#Magic function that takes an input path and uses FFprobe to check for metadata including
#width, height, average frame rate and number of frames for a video and returns it in a list.
def getMetadata(input_path):
    ffprobe = subprocess.Popen(["ffprobe", "-show_streams", input_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ffprobe.wait()
    metadata = ffprobe.communicate()[0]

    mtw = metadata[metadata.find("width="):metadata.find("\n", metadata.find("width="))]
    mth = metadata[metadata.find("height="):metadata.find("\n", metadata.find("height="))]
    mar = metadata[metadata.find("r_frame_rate="):metadata.find("\n", metadata.find("r_frame_rate="))]
    mfn = metadata[metadata.find("nb_frames="):metadata.find("\n", metadata.find("nb_frames="))]

    return {mtw[:mtw.find("=")] : mtw[mtw.find("=")+1:], mth[:mth.find("=")] : mth[mth.find("=")+1:], mar[:mar.find("=")] : mar[mar.find("=")+1:], mfn[:mfn.find("=")] : mfn[mfn.find("=")+1:]} 

#Returns a list of pupil data acquired using eyeLine, a modified version of Tristan Hume's eyeLike
def getPupilData(input_path):
    print("\tBeginning pupil subprocess")
    tstart = datetime.now()
    eyeLine = subprocess.Popen(["./eyeLine", "-d", input_path], stdout=subprocess.PIPE)
    eyeLine.wait()
    eyeLineStdout = eyeLine.communicate()[0]

    spaceIndexing = eyeLineStdout.split(" ")
    pupilData = []

    if len(spaceIndexing) % 5 == 0:             #it parsed appropriately
        spaceIndexing = spaceIndexing[:len(spaceIndexing)-1]    #remove newlines elements from parsing, NOT FINISHED, ONLY HANDLES ONE SET ATM... LAZINESS
        for i, sp in enumerate(spaceIndexing):
            if i & 1 == 0: #every other one (think c: step+=2)
                pupilData.append((int(sp), int(spaceIndexing[i+1])))

    else:
        pupilData.append((-1, -1)) #dummy data necessary for drawing appropriate scaled pupils later

    tend = datetime.now()
    print("\t\t" + str(tend - tstart))
    return pupilData

#Does frame processing such as calling mark frame and mark pupil
def handleFrame(input_path, detector, predictor, verbose, wait_at_frame, newCopy):
    global global_script_start, glbJson, glbJsonFcount, glbJsonPcount
    tstart = datetime.now()
    if URI_Handling:
        print("\tURI encoding time")
        content_file = open(fn, 'r')
        img = data_uri_to_cv2_img(content_file.read())
        content_file.close()
        tend = datetime.now()
        print("\t\t" + str(tend - tstart))
    else:
        img = cv2.imread(input_path, 1)

    ptsList, breadthList = detectFrame(img, detector, predictor)
    glbJson['Landmarks ' + str(glbJsonFcount)] = ptsList
    glbJsonFcount += 1

    pitchList, yawList, rollList = approximatePYR(ptsList, verbose)

    markFrame(img, ptsList, breadthList, pitchList, yawList, rollList, wait_at_frame)

    if not realTime:
        pupilData = getPupilData(input_path) #IPC to get pupil data
        glbJson['Pupils ' + str(glbJsonPcount)] = pupilData
        glbJsonPcount += 1

        markPupil(img, pupilData, breadthList, wait_at_frame)

    cv2.imwrite(((input_path[:input_path.rfind(".")] + "_final.png") if newCopy else input_path), img) 
    tend = datetime.now()
    print("\t\t" + str(tend - tstart)) 
    return img #for the sake of the single frame option (needed metadata)

def handleVideo(input_path, detector, predictor, verbose, wait_at_frame, start_time, duration, output_path, newCopy):
    ("Gathering metadata")
    tstart = datetime.now()

    metadata = getMetadata(input_path)
    for d in metadata:
        print(metadata[d])
    glbJson['Meta'] = metadata

    tend = datetime.now()
    noExtesion = input_path[:input_path.rfind(".")]
    username = noExtesion[noExtesion.rfind("/") + 1:]
    print("Finished gathering at " + str(tend - tstart) + "\n")
    writeStatus(username, "Finished gathering metadata at " + str(tend - tstart) + "\n")

    midPath = input_path[:input_path.rfind(".")] + "%d.png"
    print("Breaking into frames")
    writeStatus(username, "Breaking into frames...\n")
    tstart = datetime.now()
    ffmpegBreak = subprocess.Popen(["ffmpeg", "-ss", start_time] + (["-t", duration] if duration != "-1" else []) + ["-i", input_path, "-y", midPath], stdout=outstream, stderr=subprocess.STDOUT) # Run FFMPEG, using pngs
    ffmpegBreak.wait()
    tend = datetime.now()
    print("Finished breaking at " + str(tend - tstart) + "\n")
    writeStatus(username, "Finished breaking at " + str(tend - tstart) + "\n")

    g = glob.glob(input_path[:input_path.rfind(".")] + "*.png")
    for i, fn in enumerate(g):
        print("Frame " + str(i) + ":")
        tstart = datetime.now()
        writeStatus(username, "Detecting frame " + str(i) + "\n") 
        handleFrame(fn, detector, predictor, verbose, wait_at_frame, newCopy)
    tend = datetime.now()
    print("\t" + str(tend - tstart))

    if newCopy:
        midPath = midPath[:midPath.rfind(".")] + "_final.png"

    print("\nRebuilding video")
    writeStatus(username, "Rebuilding video...\n")
    tstart = datetime.now()
    ffmpegBuild = subprocess.Popen(["ffmpeg", "-framerate", metadata["r_frame_rate"], "-i", midPath, "-y", output_path], stdout=outstream, stderr=subprocess.STDOUT)# Run FFMPEG to rebake the video
    ffmpegBuild.wait()
    tend = datetime.now()
    print("Finished rebuilding at " + str(tend - tstart))
    writeStatus(username, "Finished rebuilding at " + str(tend - tstart) + "\n")
    if newCopy:
        for f in glob.glob(input_path[:input_path.rfind(".")] + "*_final.png"):
            os.remove(f)
    else:
        for f in glob.glob(input_path[:input_path.rfind(".")] + "*.png"):
            os.remove(f)
    end = datetime.now()
    with open("vProcessing.json", 'w') as outfile:
        json.dump(glbJson, outfile)

    #cur = conn.cursor()
    #cur.execute("INSERT INTO user_videos(path, username) values('" + relative_path + "', '" + username + "');" )
    #conn.commit()

# output status to file
def writeStatus(username, str):
    with open("../web/status/" + username + ".status", 'a') as myfile:
        myfile.write(str);

# main, handles args, potential arguments are: --help (displays help), -uri (enables uri handling), -l (newcopy), -r (realtime), 
# -p (predictor), -f (single frame)
# -ss (start time), -t (duration), -i (input path), -o (output path)
if __name__ == "__main__":

    global_script_start = datetime.now()

    if len(sys.argv) < 2:
        print("Error: Too few arguments supplied.")
        exit(1)

    elif len(sys.argv) > 14:
        print("Error: Too many arguments supplied.")
        exit(1)

    run_dir = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
    predictor_path = run_dir + "/shape_predictor_68_face_landmarks.dat"
    newCopy = True
    realTime = False
    single_frame = False
    start_time = "00:00"
    duration = "-1"
    input_path = ""
    output_path = ""
    verbose = False
    wait_at_frame = False

    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        displayHelp()
        exit(0)

    for index, arg in enumerate(sys.argv):
        if arg == "-uri":
            URI_Handling = True 
        elif arg == "-l":
            newCopy = False
        elif arg == "-r":
            realTime = True
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
        elif arg == "-o":
            output_path = sys.argv[index+1]
        elif arg == "-v":
            verbose = True
        elif arg == "-w":
            wait_at_frame = True
    
    if input_path == "":
        print("Please enter an input file")
        exit(1)
    if output_path == "":
        output_path = input_path[:input_path.rfind(".")] + "_final.mp4"

    #conn = psycopg2.connect(dbname="postgres", user="postgres", password="student", host="localhost")

    print("Calling DLib")
    tpeter = datetime.now()
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)
    tgay = datetime.now()
    print("\t" + str(tgay - tpeter)) #WTF

    outstream = (None if verbose else open(os.devnull, 'w')) #for redirecting output to nothing as desired

    if single_frame:
        print("")
        img = handleFrame(input_path, detector, predictor, verbose, wait_at_frame, newCopy)
        print("Image " + input_path + ": Width - " + str(img.shape[0]) + ", Height - " + str(img.shape[1])) #write to DB?
    else:
        print("")
        handleVideo(input_path, detector, predictor, verbose, wait_at_frame, start_time, duration, output_path, newCopy)

    end = datetime.now()
    print("\nExecution complete at " + str(end - global_script_start))

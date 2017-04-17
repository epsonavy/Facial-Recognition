import sys          # For argument handling

import os, inspect  # For path handling, file deletion

import dlib         # For facial recognition (neural network)

import glob         # For file path handling

import subprocess   # For running FFMPEG

import cv2          # image input/output

import numpy as np  # For array handling



'''

TO HOOK INTO THE DATABASE (POSTGRES)

1. filename -> meta-data + frames

   meta-data -> face datapoints (for each frame)

2. video ID -> meta data -> eye datapoints (for each frame)

3. video ID -> meta data -> Delauney tri images (w/o overwrite)

'''



'''

To-Do:

Head Pos: Yaw, Pitch, Roll - not sure how to do this without OpenFace, will ask Rob/Petr

write eye tracking coords to db - waiting for Tristan/Rob



Parallel Processing - need to hear about data base

anime faces - kudo can look into this

'''



def displayHelp():

    print(" Available Arguments\tDefault Arguments")

    print(" -h\tAccess the help menu (--help)")

    print(" -l\tlose original frames(overwrite)\tFalse")

    print(" -p\tPath of the Dlib predictor\t" + run_dir + "/shape_predictor_68_face_landmarks.dat")

    print(" -f\tProcess only a single frame\tFalse")

    print(" -d\tDraw Mode (Dot, Line, Delauney)\tDot")

    print(" -ss\tStart time of input file\t00:00.00")

    print(" -t\tDuration of final video\t\t00:01.00")

    print(" -i\tInput file path\t\t\t" + input_path)

    print(" -o\tOutput file path\t\tNamed as input + _final.mp4 unless specified")

    print(" -v\tVerbose\t\t\tFalse")

    print(" -w\tWait before mutating frame\tFalse")

    print(" Sample shell input:\t\t\tpython Faceline.py -l -ss 00:30 -t 00:01 -i /home/hew/Desktop/F/Fash.divx")



def in_rect(r, p):

    return p[0] > r[0] and p[1] > r[1] and p[0] < r[2] and p[1] < r[3] 



def markImg(img, detector, predictor, draw_mode):   # THIS FUNCTION MUTATES FILES

    #win.clear_overlay()

    #win.set_image(img)

    detections = detector(img, 1)                           # type(detections) == dlib.rectangles

    for i, d in enumerate(detections):                                    # type(d) == dlib.rectangle

        print(" Face Detection " + str(i) + " points:")

        shape = predictor(img, d)                           # type(shape) == dlib.full_object_detection



        pts = []

        for p in shape.parts():

            pts.append((p.x, p.y))

        

        print("  " + str(pts))

        ptsArray = np.array(pts, np.int32)

        ptsArray = ptsArray.reshape((-1, 1, 2))



        if draw_mode == "dot":

            cv2.polylines(img, ptsArray, True, (0, 0, 255))    # mark image with OpenCV

        elif draw_mode == "line":

            cv2.polylines(img, [ptsArray], True, (0, 0, 255))    # mark image with OpenCV

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

    draw_mode = "dot"

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

        elif arg == "-d":

            draw_mode = sys.argv[index+1]

        elif arg == "-ss":

            start_time = sys.argv[index+1]

        elif arg == "-t":

            duration = sys.argv[index+1]

        elif arg == "-i":

            input_path = sys.argv[index+1]

            if output_path == "":

                output_path = input_path[:input_path.rfind(".")] + "_final"+ ".mp4"

        elif arg == "-o":

            output_path = sys.argv[index+1]

        elif arg == "-v":

            verbose = True

        elif arg == "-w":

            wait_at_frame = True



    if input_path == "":

        print("Please enter an input file")

        exit()



    # video_dir = os.path.dirname(input_path), formerly used glob.glob(os.path.join(video_dir, "*.png"))

    detector = dlib.get_frontal_face_detector()

    predictor = dlib.shape_predictor(predictor_path)



    outstream = (None if verbose else open(os.devnull, 'w')) #for redirecting output to nothing as desired



    if single_frame:

        if (not wait_at_frame) or raw_input("Overwrite " + fn + " Y/N?") == "Y":

            img = cv2.imread(input_path, 1)                                                                         # load image with file name

            print("Image " + str(i) + ": Width - " + str(img.shape[0]) + ", Height - " + str(img.shape[1]))

            markImg(img, detector, predictor, draw_mode)

            cv2.imwrite(((input_path[:input_path.rfind(".")] + "_final.png") if newCopy else input_path), img)

        else:

            print("Permission denied.")

    else:

        metadataProc = subprocess.check_output(["ffprobe", "-show_streams", input_path], stderr=subprocess.STDOUT)

        metaWidth = metadataProc[metadataProc.find("width="):metadataProc.find("\n", metadataProc.find("width="))]

        metaHeight = metadataProc[metadataProc.find("height="):metadataProc.find("\n", metadataProc.find("height="))]

        metaAvgRate = metadataProc[metadataProc.find("avg_frame_rate="):metadataProc.find("\n", metadataProc.find("avg_frame_rate="))]

        metaFrameNumb = metadataProc[metadataProc.find("nb_frames="):metadataProc.find("\n", metadataProc.find("nb_frames="))]

        print(metaWidth)

        print(metaHeight)

        print(metaAvgRate)

        print(metaFrameNumb)



        midPath = input_path[:input_path.rfind(".")] + "%d.png"

        subprocess.call(["ffmpeg", "-ss", start_time, "-t", duration, "-i", input_path, midPath], stdout=outstream, stderr=subprocess.STDOUT) # Run FFMPEG, using pngs



        #win = dlib.image_window()

        g = glob.glob(input_path[:input_path.rfind(".")] + "*.png")

        for i, fn in enumerate(g):                                                                              # iterate over all images

            if (not wait_at_frame) or raw_input("Overwrite " + fn + " Y/N?") == "Y":

                print("Image " + str(i) + ":")

                img = cv2.imread(fn, 1)

                markImg(img, detector, predictor, draw_mode)

                cv2.imwrite(((fn[:fn.rfind(".")] + "_final.png") if newCopy else fn), img)

            else:

                print("Permission denied.")

        if newCopy:

            midPath = midPath[:midPath.rfind(".")] + "_final.png"

        subprocess.call(["ffmpeg", "-i", midPath, output_path], stdout=outstream, stderr=subprocess.STDOUT)# Run FFMPEG to rebake the video

        if newCopy:

            for f in glob.glob(input_path[:input_path.rfind(".")] + "*_final.png"):

                os.remove(f)

        else:

            for f in glob.glob(input_path[:input_path.rfind(".")] + "*.png"):

                os.remove(f)

    print("Execution Complete.")
#include <opencv2/objdetect/objdetect.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

#include <iostream>
#include <queue>
#include <stdio.h>
#include <math.h>
#include <string>

#include "constants.h"
#include "findEyeCenter.h"
#include "findEyeCorner.h"


/** Constants **/


/** Function Headers */
void detect( cv::Mat frame );

/** Global variables */
//-- Note, either copy these two files from opencv/data/haarscascades to your current folder, or change these locations
cv::CascadeClassifier face_cascade;
cv::RNG rng(12345);

/**
 * @function main
 */
int main( int argc, const char** argv ) {

	std::vector<std::string> args(argv, argc + argv);
	std::vector<std::string>::iterator argi;

	//Load the cascades
	cv::String face_cascade_name;
	if(args[1].compare("-h") == 0){std::cout << std::endl << "Takes a series of pngs from stdin  and returns the coordinates of pupils detected in a human face." << std::endl << "The first argument is the filepath to cascade file (xml) and the following are are number of pngs" << std::endl << std::endl << "Sample use:" << std::endl << "eyeLine ./haarcascade_frontalface_alt.xml ./Matt.png ./Pei.png ./Kevin.png ./Andrew.png" << std::endl << "(This is the default filepath by using '-d' as arg1)" << std::endl << std::endl << "Original source by Tristan Hume. Modified by Matthew Binning." << std::endl; return 0;}
	if(args[1].compare("-d") == 0) face_cascade_name = "./haarcascade_frontalface_alt.xml";
	else if(args[1].substr(args[1].size()-4).compare(".xml") != 0){std::cout << std::endl << "Usage: cascade_filepath [image.png...]" << std::endl; return -1;}
	else face_cascade_name = args[1];

	if( !face_cascade.load( face_cascade_name ) ){ printf("Face cascade corrupt.\n"); return -1; };

	createCornerKernels();

	for(argi = args.begin()+2; argi < args.end(); argi++)
	{
		if((*argi).substr((*argi).size()-4).compare(".png") == 0)
		{
			cv::Mat frame = cv::imread(*argi, 1);
			if(!frame.empty()) detect(frame);
			else
			{
				printf("Image corrupt or empty.");
				break;
			}

		}
	}
	releaseCornerKernels();
	return 0;
}

std::vector<cv::Point> eyesFromFace(cv::Mat frame_gray, cv::Rect face) {
	cv::Mat faceROI = frame_gray(face);
	cv::Mat debugFace = faceROI;

	if (kSmoothFaceImage) {
		double sigma = kSmoothFaceFactor * face.width;
		GaussianBlur( faceROI, faceROI, cv::Size( 0, 0 ), sigma);
	}
	//-- Find eye regions and draw them
	int eye_region_width = face.width * (kEyePercentWidth/100.0);
	int eye_region_height = face.width * (kEyePercentHeight/100.0);
	int eye_region_top = face.height * (kEyePercentTop/100.0);

	cv::Rect leftEyeRegion(face.width*(kEyePercentSide/100.0), eye_region_top,eye_region_width,eye_region_height);
	cv::Rect rightEyeRegion(face.width - eye_region_width - face.width*(kEyePercentSide/100.0), eye_region_top,eye_region_width,eye_region_height);

	//-- Find Eye Centers
	cv::Point leftPupil = findEyeCenter(faceROI,leftEyeRegion,"Left Eye");
	cv::Point rightPupil = findEyeCenter(faceROI,rightEyeRegion,"Right Eye");
	// get corner regions
	cv::Rect leftRightCornerRegion(leftEyeRegion);
	leftRightCornerRegion.width -= leftPupil.x;
	leftRightCornerRegion.x += leftPupil.x;
	leftRightCornerRegion.height /= 2;
	leftRightCornerRegion.y += leftRightCornerRegion.height / 2;
	cv::Rect leftLeftCornerRegion(leftEyeRegion);
	leftLeftCornerRegion.width = leftPupil.x;
	leftLeftCornerRegion.height /= 2;
	leftLeftCornerRegion.y += leftLeftCornerRegion.height / 2;
	cv::Rect rightLeftCornerRegion(rightEyeRegion);
	rightLeftCornerRegion.width = rightPupil.x;
	rightLeftCornerRegion.height /= 2;
	rightLeftCornerRegion.y += rightLeftCornerRegion.height / 2;
	cv::Rect rightRightCornerRegion(rightEyeRegion);
	rightRightCornerRegion.width -= rightPupil.x;
	rightRightCornerRegion.x += rightPupil.x;
	rightRightCornerRegion.height /= 2;
	rightRightCornerRegion.y += rightRightCornerRegion.height / 2;
	// change eye centers to face coordinates
	rightPupil.x += rightEyeRegion.x;
	rightPupil.y += rightEyeRegion.y;
	leftPupil.x += leftEyeRegion.x;
	leftPupil.y += leftEyeRegion.y;

	//-- Find Eye Corners
	if (kEnableEyeCorner) {
		cv::Point2f leftRightCorner = findEyeCorner(faceROI(leftRightCornerRegion), true, false);
		leftRightCorner.x += leftRightCornerRegion.x;
		leftRightCorner.y += leftRightCornerRegion.y;
		cv::Point2f leftLeftCorner = findEyeCorner(faceROI(leftLeftCornerRegion), true, true);
		leftLeftCorner.x += leftLeftCornerRegion.x;
		leftLeftCorner.y += leftLeftCornerRegion.y;
		cv::Point2f rightLeftCorner = findEyeCorner(faceROI(rightLeftCornerRegion), false, true);
		rightLeftCorner.x += rightLeftCornerRegion.x;
		rightLeftCorner.y += rightLeftCornerRegion.y;
		cv::Point2f rightRightCorner = findEyeCorner(faceROI(rightRightCornerRegion), false, false);
		rightRightCorner.x += rightRightCornerRegion.x;
		rightRightCorner.y += rightRightCornerRegion.y;
	}

	std::vector<cv::Point> eyesLR;
	eyesLR.push_back(leftPupil);
	eyesLR.push_back(rightPupil);
	return eyesLR;
}

/**
 * @function detect
 */
void detect(cv::Mat frame){
	std::vector<cv::Rect> faces;

	std::vector<cv::Mat> rgbChannels(3);
	cv::split(frame, rgbChannels);
	cv::Mat frame_gray = rgbChannels[2];

	//-- Detect faces
	face_cascade.detectMultiScale( frame_gray, faces, 1.1, 2, 0|CV_HAAR_SCALE_IMAGE|CV_HAAR_FIND_BIGGEST_OBJECT, cv::Size(150, 150) );

	for(int i = 0; i < faces.size(); i++){
		std::vector<cv::Point> eyesLR = eyesFromFace(frame_gray, faces[i]);
		//change eye centers to image coordinates
		eyesLR[0].x += faces[i].x;
		eyesLR[1].x += faces[i].x;
		eyesLR[0].y += faces[i].y;
		eyesLR[1].y += faces[i].y;
		std::cout << eyesLR[0].x << " " << eyesLR[0].y << " " << eyesLR[1].x << " " << eyesLR[1].y << " "; 
	}
	std::cout << std::endl;
}

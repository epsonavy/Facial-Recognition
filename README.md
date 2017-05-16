# Facial-Recognition

## Demo screenshot

![Image of Demo](https://github.com/epsonavy/Facial-Recognition/blob/master/demo.png)

## Systems:

* Frontend: Utilizes Node.js, HTML5, CSS3, Javascript with JADE view engine and Express, to offer a user friendly frontend for login and and user interaction. The goal for the users was to have a good user experience for video upload, and also to allow them to view real time, processed video straight from their webcam. 
* Backend Server: Nginx and distributed computing networked capabilities utilizing AWS and allows for real time video processing when combined with the video processing system.
* PostgreSQL Server: First normal form due to simplicity in design. It only contained a user table and a video table for each video which has a foreign key associated with username. The video table contains information on filepath of a video file and a json with all of its information.
* Video Processing: FFMPEG, OpenCV, dlib and EyeLike, combined with delaunay’s triangle algorithm breaks a video into component frames, scrapes metadata and adds 68 points with meshed lines. It also bounds the eyes and tracks the pupil locations which are then written to the database.

## Challenges

* Utilizing OpenCV and dlib for face recognition and point detection
* To draw and connect points using the Delaunay triangle algorithm
* Implementing a multi-server architecture
* Real time video processing
* Staying on schedule
* Choosing between quality and speed of processing
* Keeping large operations fast (such as FFMPEG un-stitching and restitching of frames)
* To repurpose multiple existing codebases into a different use
* Ensuring frequent meetings amongst busy schedules
* Yaw, Pitch and Roll detection
* Getting frames into and out of EyeLike

## Install dependencies: Extract project directory, you also may need to install

OpenCV
Cmake
FFMPEG
Dlib
Python 2.x
Numpy
PostgreSQL
JQuery
Video.js
Moment.js
Connect-multiparty
express
express-session
Jade
pg-promise

# The MIT License (MIT)

Copyright (c) [2017] [Andrew Levon Ajemian, Matthew Evan Binning, Pei Lian Liu, Long Trinh]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


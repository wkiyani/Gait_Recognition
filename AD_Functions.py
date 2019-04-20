# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 18:04:12 2019

@author: Asif Towheed
"""

import os
import numpy as np
from PIL import Image
from scipy.fftpack import dct

from skimage import io
import matplotlib.pyplot as plt
from sklearn import svm
import pyrealsense2 as rs
import cv2
from PIL import Image
from PIL import ImageDraw


PATH = os.getcwd().replace('\\','/')
PATH_AD = PATH + '/AD'
SUBJECTNAME = ""
SUBJECTPATH = ""
FINALORIGINALPATH = ""
FINALDIFFPATH = ""
INDEX = None

width, height = (640, 480)

IMAGELIST = []
NUMPYLIST = []
ACC_DIFF_IMG = np.zeros([height, width], dtype=np.uint8)
FEATUREVEC = []
KILLTHREAD = False
STATUSBOOL = False
STATUSARR = []

print(PATH)
print(PATH_AD)

################################################################################
## BEGIN TRAINING FOR NEW SUBJECT --> CREATE A DIRECTORY WITH THEIR NAME
################################################################################
def AD_Begin(subjectname):
    
    global SUBJECTNAME, SUBJECTPATH
    SUBJECTNAME = subjectname
    
    print(SUBJECTNAME)
    print(PATH_AD)
    SUBJECTPATH = PATH_AD + '/' + SUBJECTNAME
    print(PATH_AD + '/' + SUBJECTNAME)
    
    try:
        os.mkdir(SUBJECTPATH)
    except OSError:
        print('Error in creation of directory')
    else:
        print('Successfully created directory')
##-------------------------------------------------------------------------------
        
        
        

def detect2(imagearr, depth, clipdist):
    """
    print (len(imagearr))   # 480 = number of rows (column-wise)
    for x in imagearr:      # row-wise interation
        print(x)            # each pixel in a row (column-wise)
        print(x.size)
        #print(y)
    """
    imagearr

    for y in range(480):
        for x in range(640):
            dist = depth.get_distance(x,y)
            
            if 0 < dist and dist < clipdist:
                imagearr[y][x] = 255

    return imagearr

    





################################################################################
## GET THE WALK --> SAVE THE ORIGINAL FRAMES
################################################################################
def AD_GetWalk(index):
    global INDEX, SUBJECTPATH, STATUSBOOL, STATUSARR
    INDEX = index
    try:
        print('trying1')
        global FINALORIGINALPATH
        print('trying2')
        FINALORIGINALPATH = SUBJECTPATH + '/WALK' + str(INDEX) + "/ORIGINAL"
        print('trying3')
        os.makedirs(FINALORIGINALPATH)
        print('trying4')
    except OSError:
        print('Error in creation of directory')
    else:
        print('Successfully created directory')
    
    # Capture the images and store them in 'newSubject/WALK(index)/ORIGINAL
    
    print("Started")
    
    getframe = False
    
    #################################################################################
    # Create a pipeline
    pipeline = rs.pipeline()
    
    #Create a config and configure the pipeline to stream
    #  different resolutions of color and depth streams
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    
    # Start streaming
    profile = pipeline.start(config)
    #################################################################################
    
    
    # Getting the depth sensor's depth scale (see rs-align example for explanation)
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()
    print("Depth Scale is: " , depth_scale)
    
    # We will be removing the background of objects more than
    #  clipping_distance_in_meters meters away
    clipping_distance_in_meters = 3 #5.5 meter optimum for gait recognition
    clipping_distance = clipping_distance_in_meters / depth_scale
    
    # Create an align object
    # rs.align allows us to perform alignment of depth frames to others frames
    # The "align_to" is the stream type to which we plan to align depth frames.
    align_to = rs.stream.color
    align = rs.align(align_to)
    
    # Streaming loop
    try:
        imnumber = 0
        while True:
            # Get frameset of color and depth
            frames = pipeline.wait_for_frames()
            # frames.get_depth_frame() is a 640x360 depth image
            
            # Align the depth frame to color frame
            aligned_frames = align.process(frames)
            
            # Get aligned frames
            aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
            color_frame = aligned_frames.get_color_frame()
            
            # Validate that both frames are valid
            if not aligned_depth_frame or not color_frame:
                continue
            
            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            
            # Remove background - Set pixels further than clipping_distance to grey
            grey_color = 0
            depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
            bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)
            
            gray = cv2.cvtColor(bg_removed, cv2.COLOR_BGR2GRAY) # We do some colour transformations.
            #depthwhite = detect2(gray, aligned_depth_frame, clipping_distance*depth_scale) # We get the output of our detect function.
            
            im = Image.fromarray(gray)
            #im = Image.fromarray(depthwhite)
            imnumber += 1
            im.save(FINALORIGINALPATH + '/' + "{}.jpeg".format(imnumber))
            cv2.imshow('Align Example', gray)
            #cv2.imshow('Align Example', depthwhite)
            print('KT', str(KILLTHREAD))
            k = cv2.waitKey(1)
            if k & 0xFF == ord("q") or KILLTHREAD: # Exit condition
                cv2.destroyAllWindows()
                break
    finally:
        pipeline.stop()


##-------------------------------------------------------------------------------






################################################################################
## GET AN INDIVIDUAL DIFFERENCE IMAGE
################################################################################
def AD_FindDiff(im1, im2, n):
    global ACC_DIFF_IMG
    IND_DIFF_IMG = np.zeros([height, width], dtype=np.uint8) # to store the individual differences
    sumofdiff = 0
    
    for w in range(width):
        for h in range(height):
            absdiff = abs(int(im1[h,w]) - int(im2[h,w]))
            #print("PRINTING", int(im1[h,w]))
            if absdiff < 30:
                absdiff = 0
            sumofdiff += absdiff
            IND_DIFF_IMG[h,w] = absdiff
    
    newthresh = sumofdiff/(width*height)
    
    for w in range(width):
        for h in range(height):
            if IND_DIFF_IMG[h,w] < newthresh:
                IND_DIFF_IMG[h,w] = 0
            else:
                ACC_DIFF_IMG[h,w] += 10
    print("SAVING")
    newimage = Image.fromarray(IND_DIFF_IMG)
    newimage.save(FINALDIFFPATH + "/IND-IMAGE-{}.jpeg".format(n))
    STATUSARR.append(n)

##-------------------------------------------------------------------------------







################################################################################
## GET THE DIFFERENCES --> SAVE THE INDIVIDUAL DIFFERENCE IMAGES
################################################################################
def AD_GenerateDiffs():

    try:
        global FINALDIFFPATH
        FINALDIFFPATH = SUBJECTPATH + '/WALK' + str(INDEX) + "/DIFFERENCES"
        os.mkdir(FINALDIFFPATH)
    except OSError:
        print('Error in creation of directory')
    else:
        print('Successfully created directory')    

    print('---------EXTRACTING IMAGES INTO AN ARRAY--------------------------------------------')
    
    global IMAGELIST, NUMPYLIST
    IMAGELIST = []
    NUMPYLIST = []

    for filename in os.listdir(FINALORIGINALPATH):
        print(filename)
        openedImage = Image.open(FINALORIGINALPATH + '/' + str(filename)).convert("L")
        IMAGELIST.append(openedImage)
        NUMPYLIST.append(np.array(openedImage))
        
    global STATUSBOOL
    STATUSBOOL = True
            
    for i in range(len(NUMPYLIST) - 1):
        print(i, 'called')
        AD_FindDiff(NUMPYLIST[i], NUMPYLIST[i+1], i)



#    print('---------FOR FOLDERS --------------------------------------------')
#    for filename in os.listdir(PATH):
#        if not os.path.isfile(filename):
#            print(filename)
#        
#    print('---------FOR FILES --------------------------------------------')
#    for filename in os.listdir(PATH):
#        if os.path.isfile(filename):
#            print(filename)
##-------------------------------------------------------------------------------

    
    



    

################################################################################
## GET THE FEATURE VECTOR --> PRODUCE THE DCT IMAGE
################################################################################
def AD_GetStatus():
    global IMAGELIST, NUMPYLIST, STATUSBOOL, FINALDIFFPATH, STATUSARR
    
    if not STATUSBOOL:
        return 0
    else:
        len(STATUSARR)/(len(IMAGELIST)-1) * 20
        return int(len(STATUSARR)/(len(IMAGELIST)-1) * 20)
##-------------------------------------------------------------------------------

    
    



    
    
################################################################################
## GET THE FEATURE VECTOR --> PRODUCE THE DCT IMAGE
################################################################################
def AD_GetDCT():
    global ACC_DIFF_IMG, FEATUREVEC

    DCT_Image = dct( dct( ACC_DIFF_IMG, axis=0), axis=1)

    for i in range(10):
        for j in range(10):
            FEATUREVEC.append(DCT_Image[i][j])

##-------------------------------------------------------------------------------

    
    



    
    
################################################################################
## GET THE FEATURE VECTOR --> PRODUCE THE DCT IMAGE
################################################################################
def TerminateCapture():
    global KILLTHREAD
    KILLTHREAD = True
##-------------------------------------------------------------------------------

    
    



    
    
################################################################################
## GET THE DIFFERENCES --> SAVE THE INDIVIDUAL DIFFERENCE IMAGES
################################################################################
def AD_RESET():
    global PATH, PATH_AD, SUBJECTNAME, SUBJECTPATH, FINALORIGINALPATH, FINALDIFFPATH, INDEX, IND_DIFF_IMG, ACC_DIFF_IMG, FEATUREVEC, KILLTHREAD
    PATH = os.getcwd().replace('\\','/')
    PATH_AD = PATH + '/AD'
    SUBJECTNAME = ""
    SUBJECTPATH = ""
    FINALORIGINALPATH = ""
    FINALDIFFPATH = ""
    INDEX = None
        
    IND_DIFF_IMG = np.zeros([height, width], dtype=np.uint8) # to store the individual differences
    ACC_DIFF_IMG = np.zeros([height, width], dtype=np.uint8)
    FEATUREVEC = []
    KILLTHREAD = False
    print('RESET CALLED', str(KILLTHREAD))
##-------------------------------------------------------------------------------
################################################################################
## GET THE DIFFERENCES --> SAVE THE INDIVIDUAL DIFFERENCE IMAGES
################################################################################
def MID_AD_RESET():
    global PATH, PATH_AD, SUBJECTNAME, SUBJECTPATH, FINALORIGINALPATH, FINALDIFFPATH, INDEX, IND_DIFF_IMG, ACC_DIFF_IMG, FEATUREVEC, KILLTHREAD, STATUSBOOL, STATUSARR

    FEATUREVEC = []
    KILLTHREAD = False
    STATUSBOOL = False
    STATUSARR = []

    print('MID-RESET CALLED', str(KILLTHREAD))
##-------------------------------------------------------------------------------

    
    
    
    
#AD_Begin('Hello')

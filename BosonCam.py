#!/usr/bin/env python3

from flirpy.camera.boson import Boson
import time
import os
import matplotlib.pyplot as plt
import numpy as np
from playsound import playsound

class BosonCam:
    #Time values in seconds
    MIN_TOTTIME = 60
    MAX_TOTTIME = 7200
    
    MIN_INTTIME = 5
    MAX_INTTIME = 600
    
    def __init__(self):
        pass
    
    def image_capture(self):
        '''
        Captures an image using a connected FLIR Boson camera. 
        Must be a Boson camera core.
        
        args:
            None
            
        Raises:
            None
            
        Returns:
            Image stored as an array.
        '''
        
        camera = Boson()
        image = camera.grab()
        camera.close()
        return image

#Focal Temp Function
    def focal_temp_capture(self):
        '''
        Captures the focal plane temperature of a connected
        Radiometric FLIR Boson Camera. Must be a Boson
        camera core.
        
        args:
            None
            
        Raises:
            None
            
        Returns:
            Focal Plane Temperature as a float
        '''
        
        camera = Boson()
        focal_temp = camera.get_fpa_temperature()
        camera.close()
        return focal_temp
    
    def interval_capture(self, totalTime=120 , intervalTime=30 , workDir=os.getcwd() ):
        
        '''
        Captures images from a FLIR Boson camera at a specified time interval for a specified amount of time.
        Saves the images to a default work directory or specified directory
        
        args:
            totalTime (int) must be within 60 and 7200 seconds.
            intervalTime (int) must be within 5 and 600 seconds.
            workDir (str) must be a valid, working directory.
            
        Default args:
            Runs for 120 seconds, taking images at 30 second intervals. Working directory is current directory.
            
        Raises:
            Value Error if interval time either exceeds limit or does not meet minimum.
            Value Error if total time either exceeds limit or does not meet minimum.
            Value Error if interval time is greater than total time.
            OS Error if working directory is invalid.
        '''
        
        self.totalTime = totalTime
        self.intervalTime = intervalTime
        self.workDir = workDir
        t = 0
        start=time.time()
        
        #Checking path and time validity
        if(os.path.isdir(workDir) == False):
            raise OSError("Invalid Directory entered. Please enter a valid working directory.")
        if(totalTime > self.MAX_TOTTIME or totalTime < self.MIN_TOTTIME):
            raise ValueError("Invalid total run time entered. Maximum running time is 7200 seconds. Minimum running time is 60 seconds.")
        if(intervalTime > self.MAX_INTTIME or intervalTime < self.MIN_INTTIME):
            raise ValueError("Invalid interval time entered. Maximum interval time is 600 seconds. Minimum interval time is 5 seconds.")
        if(intervalTime > totalTime):
            raise ValueError("Interval Time cannot be greater than Total Time.")
        
        '''
        Takes images at the specified interval and time and saves the images. A folder is created for 
        local date in working or specified directory.
        '''
        
        #File path convention, created outside the loop, once. Additonally, starts a timer
        today = time.localtime()
        month, year, day, hour, minute = today.tm_mon, today.tm_year, today.tm_mday, today.tm_hour, today.tm_min
        path = workDir + '\\' + str(month) + '_' + str(day) + '_' + str(year) + '_'+ str(hour) + '_' + str(minute) + '\\'
        os.mkdir(path)
        t_val = []
        tempr_val = []
        np.set_printoptions(suppress=True) 
        
        
        while(True):
            
            #Image Capture
            pic = self.image_capture()
            
            #Naming and save path convention
            fileName = 'FLIRIM' + '_' + str(t) + '.png'
            savePath = path + fileName + '.png'
            
            #Constructing and saving the image
            plt.axis('off')
            plt.imshow(pic)
            plt.imsave(savePath, pic)
            
            
            #Focal Plane Temperature 
            tempr = self.focal_temp_capture()
            t_val.append(t)
            tempr_val.append(tempr)
                        
            
            #Creating the interval capture and break statement
            t += intervalTime
            if(t > totalTime):
                break
            time.sleep(intervalTime)
        
        t_v_tempr=np.array([t_val, tempr_val])
        fileName = "Time_Vs_Temperature.txt"
        savePath = path + "\\" + fileName
        np.savetxt(savePath, t_v_tempr, delimiter = ',', fmt='%f')
        end = time.time()
        imageNum = os.listdir(path)
        imageNum = len(imageNum)
        runTime = end - start
        playsound('success.MP3')
        print("Image capture complete." , str(imageNum) + " Photos saved to " + path , "Total Time Elapsed: " + str(runTime) + " Seconds" , sep= "\n")


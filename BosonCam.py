#!/usr/bin/env python3
'''
BosonCam 
Version 3
8/22/2022
Created by Marissa Klein, Wellesley College 2022
Intended use is controlling a FLIR Boson 640 and a thermal calibrator to test the infrared camera for BeaverCube2
'''
from flirpy.camera.boson import Boson
import time
import os
import matplotlib.pyplot as plt
import numpy as np
from playsound import playsound
import serial as s
import pandas as pd

class BosonCam:
    #Time values in seconds
    MIN_TOTTIME = 60
    MAX_TOTTIME = 7200
    
    MIN_INTTIME = 5
    MAX_INTTIME = 600
    
    def __init__(self):
        pass
    
    #Basic Image Capture
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
    
    #Interval Image Capture and Serial Line Capture
    def interval_capture(self, totalTime=120 , intervalTime=30 , workDir=os.getcwd(), serPortCap = True, serPort=""):
        
        '''
        Captures images from a FLIR Boson camera at a specified time interval for a specified amount of time.
        Saves the images to a default work directory or specified directory
        
        args:
            totalTime (int) must be within 60 and 7200 seconds.
            intervalTime (int) must be within 5 and 600 seconds.
            workDir (str) must be a valid, working directory.
            serPortCap (bool) True by default
            serPort (str) is the serial port.
            
        Default args:
            Runs for 120 seconds, taking images at 30 second intervals. Working directory is current directory. Serial
            port capture is true.
            
        Raises:
            Value Error if interval time either exceeds limit or does not meet minimum.
            Value Error if total time either exceeds limit or does not meet minimum.
            Value Error if interval time is greater than total time.
            OS Error if working directory is invalid.
            Runtime Error if no serial port is given and one is expected.
            Type Error if serial port is not a string.
        '''
        
        self.totalTime = totalTime
        self.intervalTime = intervalTime
        self.workDir = workDir
        self.serPort = serPort
        self.serPortCap = serPortCap
        t = 0
        start=time.time()
        
        #Error Handling
        if(os.path.isdir(workDir) == False):
            raise OSError("Invalid Directory entered. Please enter a valid working directory.")
        if(totalTime > self.MAX_TOTTIME or totalTime < self.MIN_TOTTIME):
            raise ValueError("Invalid total run time entered. Maximum running time is 7200 seconds. Minimum running time is 60 seconds.")
        if(intervalTime > self.MAX_INTTIME or intervalTime < self.MIN_INTTIME):
            raise ValueError("Invalid interval time entered. Maximum interval time is 600 seconds. Minimum interval time is 5 seconds.")
        if(intervalTime > totalTime):
            raise ValueError("Interval Time cannot be greater than Total Time.")
        if(serPortCap == True and serPort == ""):
            raise RuntimeError("No serial port given when expected.")
        if(serPortCap == True and isinstance(serPort,str) == False):
            raise TypeError("Given serial port must be a string.")
        
        '''
        Takes images at the specified interval and time and saves the images. A folder is created for 
        local date in working or specified directory.
        '''
        
        #File path convention, created outside the loop, once. Additonally, starts a timer
        today = time.localtime()
        month, year, day, hour, minute = today.tm_mon, today.tm_year, today.tm_mday, today.tm_hour, today.tm_min
        path = workDir + '\\' + str(month) + '_' + str(day) + '_' + str(year) + '_'+ str(hour) + '_' + str(minute) + '\\'
        os.mkdir(path)
        
        #Important Instantiations
        elapsed_time =[]
        target_tempr = []
        it_num = []
        central_tempr = []
        back_tempr = []
        ring_tempr = []
        t_val = []
        tempr_val = []
        np.set_printoptions(suppress = True) 
        
        
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
            
            if(serPortCap == True):
                #Capture the Serial port, baud rate 19200, times out after two minutes
                ser = s.Serial(serPort,19200,timeout=120)
                buffer = ser.readline() #Clears the line in process
                real_line = ser.readline()
                ser.close()
                
                if(real_line == ''):
                    print("Failure due to serial port error.")
                    break
                
                real_line = real_line.decode("utf-8")
                
                #Values
                el_t = real_line[0:8] #Time Elapsed
                elapsed_time.append(el_t)
                
                tar_t = real_line[24:28] #Target Temp
                target_tempr.append(tar_t)
                
                itn = real_line[34:38] #Iteration Number
                it_num.append(itn)
                
                cen_t = real_line[39:45] #Central Target Temp
                central_tempr.append(cen_t)
                
                b_t = real_line[62:68] #Back Heatsink Temp
                back_tempr.append(b_t)
                
                ring_t = real_line[75:81] #Ring Temp
                ring_tempr.append(ring_t)
            
            #Creating the interval capture and break statement
            t += intervalTime
            if(t > totalTime):
                break
            time.sleep(intervalTime)
        
        #Focal Plane Temperature Reading
        t_v_tempr=np.array([t_val, tempr_val])
        fileName = "Time_Vs_FocalTemp.txt"
        savePath = path + "\\" + fileName
        np.savetxt(savePath, t_v_tempr, delimiter = ',', fmt='%f')
        
        if(serPortCap == True):
            #Serial Port Readings
            data = {"Elapsed Time" : elapsed_time,
                    "Recorded T_Val" : t_val,
                    "Set Target Temperature" : target_tempr,
                    "Number of iterations" : it_num,
                    "Central Target Temperature" : central_tempr,
                    "Back Heatsink Temperature" : back_tempr,
                    "Ring Temperature" : ring_tempr}
            
            df = pd.DataFrame(data)
            fileNameCSV = str(month) + "_" + str(day) + "_Serial_Data.csv"
            savePathcsv = path + "\\" + fileNameCSV
            df.to_csv(savePathcsv)
        
        #End Values and Sign Off
        end = time.time()
        imageNum = os.listdir(path)
        imageNum = len(imageNum)
        runTime = end - start
        runTime = int(runTime)
        playsound('success.mp3')
        print("Image capture complete." , str(imageNum) + " Photos saved to " + path , "Total Time Elapsed: " + str(runTime) + " Seconds" , sep= "\n")
        final_playback = "Image capture complete." , str(imageNum) + " Photos saved to " + path , "Total Time Elapsed: " + str(runTime) + " Seconds" 
        return final_playback
    
    
    def serialRead(self,serPort):
        '''

        Parameters
        ----------
        serPort : String
            Designated serial port of the device.

        Returns
        -------
        Dataframe
            DESCRIPTION.
            
        Raises RuntimeError if the serial line is blank.

        '''
        self.serPort = serPort
        
        elapsed_time =[]
        target_tempr = []
        it_num = []
        central_tempr = []
        back_tempr = []
        ring_tempr = []
        
        #Capture the Serial port, baud rate 19200, times out after two minutes
        ser = s.Serial(serPort,19200,timeout=120)
        buffer = ser.readline() #Clears the line in progess
        real_line = ser.readline()
        ser.close()
        
        if(real_line == ''):
            raise RuntimeError
            #Serial Line error
            
        
        real_line = real_line.decode("utf-8")
        
        #Values
        el_t = real_line[0:8] #Time Elapsed
        elapsed_time.append(el_t)
        
        tar_t = real_line[24:28] #Target Temp
        target_tempr.append(tar_t)
        
        itn = real_line[34:38] #Iteration Number
        it_num.append(itn)
        
        cen_t = real_line[39:45] #Central Target Temp
        central_tempr.append(cen_t)
        
        b_t = real_line[62:68] #Back Heatsink Temp
        back_tempr.append(b_t)
        
        ring_t = real_line[75:81] #Ring Temp
        ring_tempr.append(ring_t)
        
        data = {"Elapsed Time" : elapsed_time,
                "Set Target Temperature" : target_tempr,
                "Number of iterations" : it_num,
                "Central Target Temperature" : central_tempr,
                "Back Heatsink Temperature" : back_tempr,
                "Ring Temperature" : ring_tempr}
        
        df = pd.DataFrame(data)
        return df
        
            

How to use the BosonCam Python Class
BosonCam V1

Introduction:
BosonCam is a Python class created for controlling a FLIR Boson 640 and a thermal calibrator build by Paul Fucile at WHOI. The purpose of the calibrator
is to get thermal resolution for the infrared camera that will be aboard the CubeSat, BeaverCube2, by STAR lab at MIT. The class controls the camera and
reads data from the serial port on the calibrator. 

Requirements:
Python 3.x and the following packages
Flirpy, time, os, matplotlib, numpy, serial, pandas, and playsound
Currently untested for macOS and Linux

Functions:
1) __init__(self)
Allows the class to be called.

2) image_capture(self)
Uses Flirpy to take a picture .

3) focal_temp_capture(self)
Uses Flirpy to get focal plane temperature of the camera.

3) interval_capture(self, totalTime, intervalTime, workDir, serPort)
Captures images at a given interval.
- totalTime (int) total time for taking images. Max value 7200 seconds, min value 60 seconds. Default of 120 seconds.
- intervalTime (int) time interval for taking images (Ex: images to be taken every 30 seconds). Max value 600 seconds, min value 5 seconds. Default of 30 seconds.
- workDir (str) directory for images and files to be saved. Defaults to current working directory.
- serPort (str) serial port the calibrator is plugged into. Has no default.
=> Errors are thrown if min/max conditions are violated or the working directory does not exist.

interval_capture does the following:
- Creates a folder within the working directory with the date and time of when the function first starts. All images and files are saved to this folder.
- Takes images at a specified interval and saves the images with the naming convention of FLIRM_(t_val)
- Logs the focal plane temperature during every loop and then outputs the temperature versus t_value as a text file
- Logs the serial monitor during every loop, pulling the temperatures of the calibrator, and outputs all of the values as a CSV. The corresponding t value is
also included so images can be correlated to the data.
	=> Note: This format can be easily toggled as pandas is very flexible for outputs.
- Plays a chime at the end of the function to alert that it is finished (current tone is the Super Metroid Item Get sound)
- Prints the following information to console: Number of images captured, path to the new folder created, and total time elapsed.

Tutorial:
The function intended for main use is interval_capture. The other two functions can be called but are primarily created for use within interval_capture.

Example one: Default
cam = BosonCam()
cam.interval_capture(serPort = "COM6")

This captures images for 120 seconds at 30 second intervals. These values are the default settings. The working directory is whatever the current directory is.
The serial port must always be specified, as there is no default value.

Example two:
cam = BosonCam()
cam.interval_capture(300,30,'C:\ThisLab\WorkingDir',serPort='COM6')

This captures images for 300 seconds at 30 second intervals. The working directory has been set as 'C:\ThisLab\WorkingDir' and the serial port in use is
designated as COM6.

Example three:
cam = BosonCam()
cam.interval_capture(7300,60,serPort='COM6')

This will throw a value error. The maximum allowed value for total time run in 7200 seconds and this exceeds that.

Example four:
cam = BosonCam()
cam.interval_capture(60,2,serPort='COM6')

This will throw a value error. The minimum interval capture allowed is 5 second intervals and this does not meet the threshold.

Setup:
Download BosonCam.py and success.MP3 to the same place (eg: C:\ThisLab\CameraCal\Code). BosonCam can be run in a python terminal with the commands then typed
into the terminal or it can be imported to another python program for use there.



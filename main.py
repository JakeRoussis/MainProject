import RPi.GPIO as GPIO
import time
import requests
import os

# Set-up pins
GPIO.setmode(GPIO.BCM)
pirPin = 2
GPIO.setup(pirPin, GPIO.IN)

# Establish lists and other variables
homeList = ["Jake", "John"]
deviceList = ["192.168.1.133", "192.168.1.138"]
isHome = []
notHome = []
imageCounter = 1
outputString = ""

# Check if motion is detected
def checkMotion():
    if(GPIO.input(pirPin) == 1):
        print("Debug: Motion detected")
        return 1;
    else:
        return 0;

# Check who is home
def checkHome():
    for i,val in enumerate(deviceList):
        response = os.system("ping -c 1 " + val)
        if(response == 0):
            isHome.append(homeList[i])
        else:
            notHome.append(homeList[i])

# Capture an image and save it to the Surveillance directory
def takePicture():
    global imageCounter
    operationString = ("sudo fswebcam -r 1920x1080 -S 10 Surveillance/Capture{}.jpg").format(imageCounter)
    os.system(operationString)
    imageCounter += 1

# Debugging function
def printOutput():
   for i in isHome:
       print("Debug: " + i + " is home!")
   for i in notHome:
       print("Debug: " + i + " is NOT home!")

# Clear list of who is and isn't home (Prevent duplicate push notification)
def clearList():
    isHome.clear()
    notHome.clear()

# Concatenate IFTT output string
def createOutputString():
    global outputString
    for i in isHome:
        outputString += " " + i
    if not outputString:
        r = requests.post('https://maker.ifttt.com/trigger/motion_detected/with/key/d05UjYXesLzPgrucAbKOJA', params={"value1":"Nobody is home!", "value2":"none", "value3":"none"})
    else:
        r = requests.post('https://maker.ifttt.com/trigger/motion_detected/with/key/d05UjYXesLzPgrucAbKOJA', params={"value1":outputString, "value2":"none", "value3":"none"})
    outputString = ""

try:
    while True:
        if(checkMotion() == 1):
            takePicture()
            time.sleep(0.5)
            checkHome()
            createOutputString()
            printOutput()
            clearList()
            print("Debug: Home check finished!")
        time.sleep(1)

except KeyboardInterrupt:
    print(" Quit")
    # Clear GPIO
    GPIO.cleanup()

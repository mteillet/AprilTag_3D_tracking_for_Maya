import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.OpenMaya as py
import unicodedata
import math
import getpass
import os
import subprocess


####    Copyright 2019 TEILLET Martin - Licensed under the Apache License, Version 2.0 (the "License");
####    you may not use this file except in compliance with the License. You may obtain a copy of the License at:
####   http://www.apache.org/licenses/LICENSE-2.0



def main():
    
    windowWidth = 300
    window = cmds.window( title="April Tracking to Maya", iconName='Apr_Track', widthHeight=(windowWidth, 300) )
    ####            Header          ####
    cmds.rowColumnLayout( numberOfColumns=1, columnWidth=[(1, windowWidth)])
    cmds.text( label = "April Tag Tracking for maya", font = "boldLabelFont", backgroundColor = [0.290, 0.705, 0.909], enableBackground = True, height = 80)
    

    ####            Insert path to images sequence and create 00_focalLengthEstimation.bat         ####
    cmds.separator()
    cmds.text( label = "Path to the images folder:", height = 30)
    cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 30), (2, 270)] )
    cmds.iconTextButton( style='iconAndTextVertical',align='right',command='updateFocEstimation(updateFolderPath())', image1='fileOpen.xpm', height=20 )
    (cmds.textField('PickDirectory', editable = False))

    cmds.separator(height = 10 )
    cmds.separator(height = 10 )

    ####            Converting the 00_focalLengthEstimation.bat to the .txt output          ####
    cmds.separator(style = "none" )
    cmds.button(label = "Auto tracking", command= 'lensAllEstimations()', height=20 )

    cmds.separator(style = "none", height = 20 )
    cmds.separator(style = "none", height = 20 )

    ####            Ask for the lens and the camera sensor size before running           ####
    cmds.separator(style = "none" )
    cmds.button(label = "Manual settings", command = 'inputLensCensorSize()')
    
    cmds.separator( height = 40 )
    cmds.separator( height = 40 )
    
    ####                Convert tracking data to the actual camera              ####
    cmds.separator(style = "none" )
    cmds.button(label = "Track Camera", command = 'AprilTrack_Solver()')

    cmds.setParent( '..' )
    cmds.showWindow( window ) 


# Function registering the images' directory path and removing useless characters
def updateFolderPath():
    realProject = cmds.workspace( q=True, rootDirectory=True )
    print(realProject)
    chosenFileList = cmds.fileDialog2(fm=3, ds=1, cap="Open", ff='Directory' ,okc="Select directory", hfe=0)
    chosenFileString = str(chosenFileList)
    chosenFileString = (chosenFileString[3:])
    chosenFileString = (chosenFileString[:-2])
    print (chosenFileString)
    cmds.textField('PickDirectory', edit=1, text=chosenFileString)
    cmds.workspace( realProject, o=True )
    return (chosenFileString)

def inputLensCensorSize():
    resultLens = cmds.promptDialog( title = "Focal Length in mm", message = "Input the focal lenght of you cam (mm). If you cancel the value will default to a 35mm", button = ['OK', 'Cancel'], defaultButton = 'OK', cancelButton = 'Cancel', dismissString = 'Cancel')
    if resultLens == 'OK':
        lensMM =  cmds.promptDialog(query=True, text=True)
    else:
        lensMM = 35
    
    resultSensor = cmds.promptDialog( title = "Censor Size", message = "Input the sensor size of the camera. If you cancel the value will default to 35mm (full frame)", button = ['OK', 'Cancel'], defaultButton = 'OK', cancelButton = 'Cancel', dismissString = 'Cancel')
    if resultSensor == 'OK':
        sensor =  cmds.promptDialog(query=True, text=True)
    else:
        sensor = 35
    
    print (lensMM)
    print (sensor)

def lensAllEstimations():
    runFocEstim()
    getLensMMFunctions()

# April Track creates bat for camera px estimation
def updateFocEstimation(chosenFileString):
    # Check if the directory path has been selected
    print (chosenFileString)
    if chosenFileString is None:
        cmds.error( "You need to set the directory path" )
    else:
        #Get the current project Path
        projectPath = cmds.workspace( q=True, rootDirectory=True )

        #Create a folder where we can create the tracking tools
        dataPath =  projectPath + "cache/AprilTag_Tracking"
        dataPath = (dataPath.replace("/", "\\"))
        try :
            os.mkdir(dataPath)
        except OSError as error:
            print("folder already exists")

        #Getting the username and setting the path to AprilTools
        username = getpass.getuser()
        AprilToolsExePath = "C:\\Users\\" + (username) + "\\Documents\\maya\\scripts\\AprilTools-master\\bin\\apriltools.exe"
        print(AprilToolsExePath)

        

        #Create a file that will run the focal-length estimation
        createFocEstim = dataPath + "\\00_focalLengthEstimation.bat"
        modFocEstim= open(createFocEstim, "w+")

        #Changing the choseFileStringSyntax to the correct one
        chosenFileString = chosenFileString.replace("/", "\\")

        #Writing the destination for the .txt file
        writeFocEstim = dataPath + "\\estimFocalLength.txt"

        string = AprilToolsExePath + ' --path "' + chosenFileString + '" --estimate-focal-length > ' + writeFocEstim + " \\n"
        modFocEstim.write(str(string))

        execFocEstim = createFocEstim.replace('\\', '\\\\')
        print(execFocEstim)
        
        # Write the path to the footage in a file
        createFootageFile = dataPath + "\\.currentFootagePath.txt"
        pathFootageFile = open(createFootageFile, "w+")
        pathFootageFile.write(str(chosenFileString))

        
# Run the bat to create the .txt containing the camera px estimated data
def runFocEstim():
    # Recreating the variable to the 00_focalLengthEstimation.bat
    projectPath = cmds.workspace( q=True, rootDirectory=True )
    dataPath =  projectPath + "cache/AprilTag_Tracking/00_focalLengthEstimation.bat"
    dataPath = dataPath.replace("/", "\\\\")
    
    # Running the actual bat file
    os.system(dataPath)        

# Getting the camera real lens from the pixel length
def getLensMMFunctions():
    getLensMM()
    runLensMM()

def getLensMM():
    projectPath = cmds.workspace( q=True, rootDirectory=True )
    dataPath =  projectPath + "cache/AprilTag_Tracking/estimFocalLength.txt"
    # Opening the newly created.txt file 
    with open (dataPath, "r") as focLenTxt:
        data=focLenTxt.readlines()
    # Getting the line containing the px Lens value
    mmPxLineIndex = (len(data)-1)
    mmPxLine = (data[mmPxLineIndex])

    mmPxSplit = (mmPxLine.split("--focal-length-pixels "))
    mmPxSplit = (mmPxSplit[1].split(' --tag-size'))
    mmPxValue = float(mmPxSplit[0])

    print(mmPxValue)

    #Opening the file containing the path to the footage path
    dataPath2 = projectPath + "cache/AprilTag_Tracking/.currentFootagePath.txt"
    with open (dataPath2, "r") as footagePathTxt:
        data = footagePathTxt.readlines()
    footagePath = str(data[0])

    # Creating the 01_realfocalLengthMM.bat
    realFocPath = projectPath + "cache/AprilTag_Tracking/01_realfocalLengthMM.bat"
    username = getpass.getuser()
    AprilToolsExePath = "C:\\Users\\" + (username) + "\\Documents\\maya\\scripts\\AprilTools-master\\bin\\apriltools.exe"
    
    ####    STILL NEED TO PROMP THE USER FOR THE TAG SQUARE SIZE    ####
    result = cmds.promptDialog( title = "Size of the April Tag", message = "Input the size of the April Tag in cm. If you cancel the value will default to an A4 printed tag Value", button = ['OK', 'Cancel'], defaultButton = 'OK', cancelButton = 'Cancel', dismissString = 'Cancel')
    if result == 'OK':
        tagSize =  cmds.promptDialog(query=True, text=True)
    else:
        tagSize = 17
        
    tagSize = float(tagSize) * 1000

    string = str(AprilToolsExePath) + ' --path "' + str(footagePath) + '" --focal-length-pixels ' + str(mmPxValue) + ' --tag-size ' + str(tagSize)
    modFocMM= open(realFocPath, "w+")
    modFocMM.write(str(string))
    
    runLensMM()

def runLensMM():
    # Recreating the variable to the 00_focalLengthEstimation.bat
    projectPath = cmds.workspace( q=True, rootDirectory=True )
    dataPath =  projectPath + "cache/AprilTag_Tracking/01_realfocalLengthMM.bat"
    dataPath = dataPath.replace("/", "\\\\")
    
    # Running the actual bat file
    os.system(dataPath)        
    

# Application of the track.txt file to an actual maya camera
def AprilTrack_Solver():
    #Creating the camera
    cmds.camera(n="April_Track_Cam_1")

    #Creating the groundplane locator
    cmds.spaceLocator( p=(0, 0, 0), n="GroundOrientation_AprilCAM" )
    
    #Creating the reference matrix locator
    cmds.spaceLocator( p=(0, 0, 0), n="referenceMatrix" )

    #Get the current path to images
    projectPath = cmds.workspace( q=True, rootDirectory=True )
    dataPath2 = projectPath + "cache/AprilTag_Tracking/.currentFootagePath.txt"
    with open (dataPath2, "r") as footagePathTxt:
        data = footagePathTxt.readlines()
    footagePath = str(data[0]) + "\\track.txt"

    #Reading the lines from the track file
    with open(footagePath) as trackList:
        trackList = [line.rstrip('\n') for line in open(footagePath)]


    # Setting Camera Focal Length
    focal = trackList[0].split(",")

    #The sublist container is composed of lists of lists, which are indexed by Frame, rotX, rotY, rotZ, locX, locY, locZ
    #The index of the sublist 1 is representing the frame 0
    current = 0
    sublistsContainer = []
    for i in trackList:
        sublistsContainer.insert(current, trackList[current].split(","))
        current += 1
    
    current = 0

    
    #Setting the Camera's focal length
    cmds.setAttr("April_Track_Cam_1Shape1.focalLength", float(focal[0]))
    
    
    #Going to the first Frame and setting the frame counter (current)
    cmds.currentTime(current)
    


    ###     Test printing some values
    #print(trackList[1])
    #print (sublistsContainer[1][1])
    #test = float(sublistsContainer[1][1]) 


    #Loop to set the position and rotation of the camera

    for i in trackList:

        ####               Rotations
        # Inverting the indexes for the X and Z rotations
        rotZ = (-float(sublistsContainer[current][1])) * 180 / math.pi
        rotY = (-float(sublistsContainer[current][2])) * 180 / math.pi
        rotX = float(sublistsContainer[current][3]) * 180 / math.pi
        cmds.setAttr("referenceMatrix.rotateX", rotX)
        cmds.setAttr("referenceMatrix.rotateY", rotY)
        cmds.setAttr("referenceMatrix.rotateZ", rotZ)
        #cmds.move(float(line[4]), float(line[5]), float(line[6]))
        
        ####                Locations
        locX = float(sublistsContainer[current][4])
        locY = (-float(sublistsContainer[current][5]))
        locZ = (-float(sublistsContainer[current][6]))
        cmds.setAttr("referenceMatrix.translateX", locX)
        cmds.setAttr("referenceMatrix.translateY", locY)
        cmds.setAttr("referenceMatrix.translateZ", locZ)

        cmds.setKeyframe()
        current += 1
        cmds.currentTime(current)

    
    # Inverse the Locator's matrix and pass it to the camera
    cmds.createNode( 'inverseMatrix', n='MatrixInversion' )
    cmds.createNode( 'decomposeMatrix', n='MatrixDecomposition' )
    cmds.connectAttr ( 'referenceMatrix.matrix', 'MatrixInversion.inputMatrix')
    cmds.connectAttr ( 'MatrixInversion.outputMatrix', 'MatrixDecomposition.inputMatrix')
    cmds.connectAttr ( 'MatrixDecomposition.outputTranslate', 'April_Track_Cam_1.translate')
    cmds.connectAttr ( 'MatrixDecomposition.outputRotate', 'April_Track_Cam_1.rotate')

    #Parenting the camera to the ground locator and orienting it for the ground to be flate on Y axis
    cmds.parent( 'April_Track_Cam_1', 'GroundOrientation_AprilCAM')
    cmds.setAttr ("GroundOrientation_AprilCAM.rotateX", -90)

    #Baking the Matrix and ground orientation informations to the camera's animation curves
    timeLimit = current - 1
    cmds.bakeResults( 'April_Track_Cam_1.translate', t=(1,timeLimit), sb=1,  simulation=True  )
    cmds.bakeResults( 'April_Track_Cam_1.rotate', t=(1,timeLimit), sb=1,  simulation=True  )

    #Delete the inversed Matrix locator as it is no longer needed (anim has been baked)
    cmds.delete("referenceMatrix")

if __name__ == '__main__':
    main()

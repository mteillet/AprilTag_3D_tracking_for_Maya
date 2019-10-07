# AprilTag_3D_tracking_for_Maya

3D tracking with a single click in Maya

 Marker-based 3D tracking for maya using the AprilTags technology from the University of Michigan (https://april.eecs.umich.edu/software/apriltag.html)

 Also using the cmd interpreter made by thegoodhen on his AprilTools repository (https://github.com/thegoodhen/AprilTools) 


# How to use it

The AprilTools-master folder needs to be in your documents maya scripts folder.

C:\Users\USERNAME\Documents\maya\scripts

It is imperative to set your Maya project for the script to work.


Video link : https://www.youtube.com/watch?v=6u-DLy3HaP4&feature=youtu.be


You need to load the script April_Tracker_Maya_v01_01.py from Maya's script editor (you can save it to a shelf if you want to)

On launch, a new window opens. 

1st, click on the folder icon, and go to the folder containing the images you want to track.

2nd, if you know your camera lens' focal length and the camera's sensor size, click on the "Manual settings" button. You will be ask to input these values. If you don't know these values, click on "Auto Tracking" and the software will try to estimate them for you. You will also be asked in both cases, to input the size of the april tracker you were using when shooting. If you don't know this value, you can put a random one, and scale the camera later to fit your needs.

3rd, click on "Track Camera" in order to apply the tracking data generated directly to a new Maya camera. The focal length will also be modified automatically to fit your input or the software estimations, depending on the method you had chosen.

Don't forget to change your render resolution to the original footage for the track to be optimal. You can load the footage on an image plane as image sequence to check the quality of the tracking.

That's it !

![](/.imgs/.gifs/April_Tracker_Maya_Demo2.gif)

![](/.imgs/.gifs/April_Tracker_Maya_Demo.gif)
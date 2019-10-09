---
output: github_document
---


#Model world definition and creation

#Summary

The "model world" forms the basis of the three-dimensional environment used to perform the atmospheric correction for complex camera and terrain configurations. It is created using the [Blender](https://www.blender.org/) rendering software and facilitates the correct interpretation of:

1. Three-dimensional surface geometry
2. Camera intrinsic (e.g. focal length) and extrinsic (location, rotation) parameters

In this tutorial, a model world will be created for the [real world camera image example](tutorials/Real-world-images). The tutorial has been tested using Blender v2.80.

#Geometry

##Import

The sample geometry data is found [here](README_files/geometry). In a new Blender session:
- Delete all existing objects (camera, cube, etc)
- Load [IMU_sample_geometry.obj](README_files/geometry/IMU_sample_geometry.obj) in Blender

##Examine

You will be presented with the following GUI. The colours represent the different surface types (orientation and material). Pan around the scene with the mouse and holding down the middle mouse button.
![BlenderGUI_read3Dmodel](README_files/figure-misc/BlenderGUI_1.PNG)


#Camera

##New Camera

Insert a new "camera" into the scene.
 Shift + "a" -> "Camera"
 
##Extrinsic parameters

Select the the camera (click on it, top right in "scene collection") and press 
  n
then you will see the location and rotation XYZ "transform" parameters window.
Modify these 6 parameters to all be 0 and the camera will be located at X=0,Y=0,Z=0 world coordinates, with rotation of 0 across 3D vector elements X,Y,Z. Press
  Crtl + Numpad0
to view the geometry through the camera viewport.
![BlenderGUI_cameraViewport](README_files/figure-misc/BlenderGUI_2.PNG)




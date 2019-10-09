# Summary

The "model world" forms the basis of the three-dimensional (3D) environment used to perform the atmospheric correction for complex camera and terrain configurations. It is created using the [Blender](https://www.blender.org/) rendering software and facilitates the correct interpretation of:

1. 3D surface geometry
2. Camera intrinsic (e.g. focal length) and extrinsic (location, rotation) parameters

In this tutorial, a model world will be created for the [real world camera image example](../Real-world-images). The tutorial has been tested using Blender v2.80.

# Geometry

## Import

The sample geometry data is found [here](README_files/geometry). In a new Blender session:

1. Delete all existing objects (camera, cube, etc)
2. Import [IMU_sample_geometry.obj](README_files/geometry/IMU_sample_geometry.obj)

## Examine

You will be presented with the following GUI. The colours represent the different surface types (orientation and material). Pan around the scene with the mouse and holding down the middle mouse button.
![BlenderGUI_read3Dmodel](README_files/figure-misc/BlenderGUI_1.PNG)


# Camera

## New Camera

Insert a new "camera" into the scene.

```
Shift + "a" -> "Camera"
```

## Extrinsic parameters

Select the the camera (click on it, top right in "scene collection"), press *n*, then you will see the location and rotation XYZ "transform" parameters window.

Modify these 6 parameters to all be 0 and the camera will be located at X=Y=Z=0 world coordinates and 3D vector elements. Press

```
Crtl + Numpad0
```

to view the newly altered geometry through the camera viewport to give the following GUI, where the camera is looking directly downwards onto the scene. The center of teh camrea (camera axis) intersects the X=Y=0 corner of the 3D model.
![BlenderGUI_cameraViewport](README_files/figure-misc/BlenderGUI_2.PNG)

## Intrinsic values

After selecting the camera in the scene collection window, navigate the icons in the [red circle](BlenderGUI_read3Dmodel) to set:

* **Number of pixels** The tab with the printer icon ('Output').
* **Field of view** The tab with the green film camera icon ('Object data').



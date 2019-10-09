
# DART-atmos-corr

A place for code and tutorials for atmospheric correction of longwave
infrared camera imagery using the [Discrete Anisotropic Radiative
Transfer (DART)](http://www.cesbio.ups-tlse.fr/us/dart.html) model.

This repository is being constantly updated with [tutorials](tutorials)
and [code](code) to give readers of Morrison *et al.* (2019) (in press)
a hands-on guide to performing atmospheric and emissivity corrections
for longwave infrared camera imagery across complex terrain.

![DARTscene3D\_London\_Islington](readme/DARTscene3D_London_Islington.PNG)
*DART “Scene 3D” view of central London area (430 m x 430 m) used for
testing of DART atmospheric correction.*

A software package has been developed to work with DART outputs: [daRt
for the R programming language](https://github.com/willmorrison1/daRt)
and complements the atmospheric correction processing and analysis. daRt
methods are being developed to simplify the atmospheric correction
process.

## Summary of atmospheric correction routine

1.  [**Real world
    images**](https://github.com/willmorrison1/DART-atmos-corr/tree/master/tutorials/London/DARTsimulation).
    Defines the types of ‘real world’ images that are suitable for
    correction using this technique
2.  [**Model
    world**](https://github.com/willmorrison1/DART-atmos-corr/tree/master/tutorials/London/DARTsimulation).
    Configure a three-dimensional model world to faciliate the
    correction.
3.  [**Create multi line of sight
    image**](https://github.com/willmorrison1/DART-atmos-corr/tree/master/tutorials/London/DARTsimulation).
    Optional. Create multi line of sight (MLOS) image with per-pixel
    path lengths between the surface and camera.
4.  [**DART atmosphere
    simulation**](https://github.com/willmorrison1/DART-atmos-corr/tree/master/tutorials/London/DARTsimulation).
    Configure and run DART for simulation of atmospheric effects.
5.  [**DART image
    post-processing**](https://github.com/willmorrison1/DART-atmos-corr/tree/master/tutorials/London/DARTsimulation).
    Optional. Process the MLOS image mask with the DART-processed
    images.
6.  [**Band calculation and
    correction**](https://github.com/willmorrison1/DART-atmos-corr/tree/master/tutorials/London/DARTsimulation).
    Correct the real world images using the simulated images.
7.  [**Image
    analysis**](https://github.com/willmorrison1/DART-atmos-corr/tree/master/tutorials/London/DARTsimulation).
    Perform some simple analysis on processed images.

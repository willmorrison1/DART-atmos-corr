# Summary 

This tutorial outlines the configuration of the DART model for creation of atmospheric emission and transmissivity of the air between surfaces and a camera, throught the perspective of a [model world](../Model-world) camera.

# DART model configuration

The DART simulation template can be found [here](README_files/DART-simulation) and has been tested using hte version shown in the input files xml headers. The settings that should be changed are:

- Advanced mode:
    - cell size 
    - sub-cells
    - sub-faces (per sub-cell)
- Flux tracking parameters:
    - number and width of bands
    - number and type of cameras
- Atmosphere:
    - height of earth scene (with air)
    - Define water vapor parameters at a point 
    - altitude
    - pressure
    - temperature
    - RH
    - distance to calculate reference cross-section

## Import 3D model

Import the 3D model. This tutorial uses the one from the [model world](../Model-world) section. When importing, position the 3D model in the middle (horizontally) of the DART scene.

## DART camera - location coordinates

For a model world camera with XYZ location:

```
X[mw] = -28.553
Y[mw] = -27.9681
Z[mw] =  87.1
```

with the world coordinate origin in the center of the scene, the comparable DART camera coordinates are:

```
X[dart] = (max(Y[dart]) / 2) + Y[mw]
Y[dart] = (max(X[dart]) / 2) + X[mw]
Z[dart] =  Z[mw]
```
This is becuase the DART world coordinate origin is in the "top left" and the X and Y axes are opposite to that of Blender. For the [model world](../Model-world) camera example, this requires the following calculation:


```r
Xdart_max <- Ydart_max <- 300
Xmw <- -28.553
Ymw <- -27.9681
Xdart <- (Xdart_max / 2) + Ymw
Ydart <- (Ydart_max / 2) + Xmw
```
which gives the following DART coordinates:


```r
print(Xdart)
```

```
## [1] 122.0319
```

```r
print(Ydart)
```

```
## [1] 121.447
```

## DART camera - rotation vector

### Inside scene camera

The DART camera rotation can be directly translated from the [model world](../Model-world) Blender coordinates when using the "inside scene" camera. 

### Frame camera

When using a camera that is located above the tallest model world surface, the camera is above the model world and the "frame camera" should be used. With the Blender rotation order as XZY, set the DART frame camera rotation order to XZY. The Blender camera rotation vector (X[mw]... etc) is related to DART frame camera rotation by: 

```
X[dart] = X[mw]
Y[dart] = Z[mw]
Z[dart] = -Y[mw]
```

# Read DART data

This section outlines the output data that we are interested in: spectral transmittance and radiance for the air between the surface and camera, as seen through the perspective of the [real world](../Real-world-images) camera. The reading of data is done using the [daRt](https://github.com/willmorrison1/daRt) package.


```r
library(daRt)
library(dplyr)
library(ggplot2)
simDir <- "README_files/DART-simulation/dart-atmos-corr"

sF_trans <- daRt::simulationFilter(product = "images", bands = integer(), iters = "ITERX", 
                                   imageTypes = c("camera_transmittance"), typeNums = "",
                                   variables = "Tapp")
sF_tapp <- sF_trans
imageTypes(sF_tapp) <- "camera"
typeNums(sF_tapp) <- "1_Fluid"

simData_transAtm <- daRt::getData(x = simDir, sF = sF_trans)
simData_tappAtm <- daRt::getData(x = simDir, sF = sF_tapp)
simData_radAtm <- daRt::tappToRadiance(simData_tappAtm)

transDF <- as.data.frame(simData_transAtm)
transDF$value[transDF$value == 0] <- NA
radDF <- as.data.frame(simData_radAtm)
radDF$value[radDF$value == 0] <- NA
```

Now plot the data. Plot all raw images.

```r
plotThemes <- theme(
  axis.text = element_blank(),
  axis.title = element_blank(),
  axis.ticks = element_blank(), 
  panel.spacing = unit(0.1, "lines"),
  strip.text = element_text(size = 5, margin = margin(0, 0, 0, 0)),
  strip.background = element_rect(fill = "white", margin(0, 0, 0, 0)),
  aspect.ratio = 120 / 160
)

ggplot(transDF) +
  geom_raster(aes(x = x, y = y, fill = value)) +
  facet_wrap(~ band, ncol = 7) +
  theme_bw() +
  plotThemes +
  coord_flip() +
  scale_x_reverse(expand = c(0, 0)) +
  scale_y_continuous(expand = c(0, 0)) +
  ggtitle("Atmospheric spectral transmittance")
```

![](README_files/figure-gfm/unnamed-chunk-5-1.png)<!-- -->

```r
ggplot(radDF) +
  geom_raster(aes(x = x, y = y, fill = value)) +
  facet_wrap(~ band, ncol = 7) +
  theme_bw() +
  plotThemes +
  coord_flip() +
  scale_x_reverse(expand = c(0, 0)) +
  scale_y_continuous(expand = c(0, 0)) +
  ggtitle("Atmospheric spectral radiance")
```

![](README_files/figure-gfm/unnamed-chunk-5-2.png)<!-- -->

Now do some simple aggregation of the data and plot the median transmittance (line) and 5th -> 9th percentile (shading) across all pixels.

```r
transDFsummary <- transDF %>%
  dplyr::group_by(band, imgType, imageNo, simName) %>%
  dplyr::summarise(minValue = quantile(value, 0.05, na.rm = TRUE),
                   medValue = median(value, na.rm = TRUE),
                   maxValue = quantile(value, 0.95, na.rm = TRUE))

ggplot(transDFsummary %>% dplyr::left_join(wavelengths(simData_radAtm))) +
  geom_ribbon(aes(x = lambdamid, ymin = minValue, ymax = maxValue), fill = "grey") +
  geom_line(aes(x = lambdamid, y = medValue), size = 0.65) +
  xlab(expression(wavelength~"("*mu*m*")")) +
  ylab("Transmittance") + 
  theme_bw()
```

![](README_files/figure-gfm/unnamed-chunk-6-1.png)<!-- -->


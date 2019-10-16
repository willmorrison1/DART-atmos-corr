# Summary 

This section demonstrates methods for correcting [real world](../Real-world-images) thermal images using [DART simulation](../DART-simulation) results. 


```r
library(daRt)
library(dplyr)
library(ggplot2)
simDir <- "../../tutorials/DART-simulation/README_files/DART-simulation/dart-atmos-corr"

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
radDF <- as.data.frame(simData_radAtm)
```



Band calculation trapezoidal approximation:

$$\int_{\lambda=1}^{\lambda=n} d\lambda~L_\lambda R_\lambda\approx
\sum_{i=1}^n \frac{1}{2} 
\times(\lambda_{max_{i}}-\lambda_{min_{i}}) 
\times (L_{\lambda_{i}}R_{min_{i}} + 
L_{\lambda_{i}}R_{mid_{i}}) + 
(L_{\lambda_{i}}R_{mid_{i}} + 
L_{\lambda_{i}}R_{max_{i}})$$


Define the real world observations. This should be a data frame which has information that can relate to the model world observations. Namely, the pixels (x, y), brightness temperature (value), the image type (imgType) and DART image number that models its perspective (imageNo). This way, each model world camera is matched to the correct real world camera.

Todo: make formal `Thermograph` class to check validity and enable relevant methods e.g. spectralRadiance(tapp, simData[opt], lambda[opt]). 

```r
DFobs <- expand.grid(x = unique(transDF$x), y = unique(transDF$y), value = 300, imgType = "camera", imageNo = 251)
```

The user should also have a spectral response function that spans the [DART simulation](../DART-simulation) bands. It can be sparsely/heterogeneously populated with data and it is linearly interpolated to exactly match the required bands.


```r
SRF_raw <- data.frame("lambda" = seq(5, 20, by = 1e-2), "value" = seq(1, 1, length.out = length(seq(5, 20, by = 1e-2))))
```

WIP. Tapp to spectral radiance


```r
LcamSpectral <- thermographToSpectralRadiance(thermograph = DFobs, simData = simData_radAtm)
```

WIP. Perform band calculation. 
- Add trapezoidal integration equation. 
- Tidy up inputs to bandRadiance_surf()? e.g. 
    - LCam_spectralBrick can be a Thermograph() type object and thermographToSpectralRadiance() can be internal. 
    - simData_transAtm and simData_radAtm combined?


```r
bandRadDF <- bandRadiance_surf(LCam_spectralBrick = LcamSpectral, 
                               simData_transAtm = simData_transAtm, 
                               simData_radAtm = simData_radAtm, 
                               SRF_raw = SRF_raw)
```


```r
ggplot(bandRadDF %>% filter(between(bandValue, 130, 150))) +
  geom_raster(aes(x = x, y = y, fill = bandValue)) +
  theme_bw() +
  coord_flip() +
  scale_x_reverse() +
  ggtitle("Surface-leaving band radiance")
```

![](README_files/figure-markdown_github/unnamed-chunk-8-1.png)

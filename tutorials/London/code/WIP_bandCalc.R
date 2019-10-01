library(daRt)
#WIP integration of "offline" integration of dart images - for band calculation of atmospheric correction

simulationDir <- "man/data/cesbio"

sF <- simulationFilter(product = "images", bands = c("BAND0", "BAND1"))
#placeholder for observations
obsData <- daRt::getData(x = simulationDir, sF = sF)

dataDF <- obsData@data %>% dplyr::filter(iter == "ITER1", imageNo == 1)
#placeholder values for integration
dataDF$lambdaMin <- 8
dataDF$lambdaMax <- 8.5
dataDF$lambdaMid <- 8.25
dataDF$lambdaMin[dataDF$band == "BAND1"] <- 8.5
dataDF$lambdaMax[dataDF$band == "BAND1"] <- 9
dataDF$lambdaMid[dataDF$band == "BAND1"] <- 8.25
dataDF$lambdaMid[dataDF$band == "BAND1"] <- 8.75
#transmittance images
#in practice this will use e.g. product(sF) <- "transmittance" [sic]
transmittanceDF <- dataDF
#atmosphere radiance images
#in practice this will use e.g. typeNum(sF) <- "fluid" [sic]
latmDF <- dataDF
#SRF
SRF <- dataDF

SRF$value <- 1
dataDF <- dataDF %>%
    dplyr::mutate(deltaLambda = lambdaMax - lambdaMin)
#trapezoidal integration
#get integrals for LHS of SRF - for each band
LHS <- dataDF$value * SRF$lambdaMid + dataDF$value * SRF$lambdaMid
#get integrals for RHS of SRF - for each band
RHS <- dataDF$value * SRF$lambdaMid + dataDF$value * SRF$lambdaMax
integral <- (LHS + RHS) * dataDF$deltaLambda * 0.5
dataDF$integral <- integral
dataDF_out <- dataDF %>%
    dplyr::group_by(x, y, iter, imageNo, VZ, VZ, simName) %>%
    dplyr::summarise(bandValue = sum(value))


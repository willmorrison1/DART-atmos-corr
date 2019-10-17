.planck <- function(lam, Temp){
  #lam is wavelenght in microns
  #Temp is temperature in Kelvin
  
  #boltzmann constant m^2 kg s^-2 K^-1
  k <- 1.38064852e-23
  #planck constant m^2 kg s^-1
  h <- 6.62607004e-34
  #speed of light m s^-1
  cc <- 299792458
  
  
  lam <- lam * 1e-6
  specRad <- (((2 * h) * (cc^2))/((lam^5) * (exp((h * cc) / (lam * k * Temp)) - 1))) * 1e-6
  
  return(specRad)
  
}

.normalise <- function(x) {
  minVal <- min(x, na.rm = TRUE)
  maxVal <- max(x, na.rm = TRUE)
  if (minVal == maxVal) {
    return(x)
  } else {
    return((x - minVal) / (maxVal - minVal))
  }
}

SRFinterp <- function(SRF_raw, simData, sigFig = 4) {
  
  require(dplyr)
  require(imputeTS)
  wavelengthVals <- wavelengths(simData)
  SRF_raw <- SRF_raw %>%
    dplyr::filter(between(lambda, min(wavelengthVals$lambdamin), 
                          max(wavelengthVals$lambdamax)))
  if (nrow(SRF_raw) == 0) stop("SRF outside bandwidth")
  SRF_raw$value <- .normalise(SRF_raw$value)
  minMaxVals <- data.frame(lambda = c(max(wavelengthVals$lambdamin) - 0.01,
                                      max(wavelengthVals$lambdamin) + 0.01,
                                      0, 100),
                           value = c(0, 0, 0, 0))
  SRF_raw <- rbind(SRF_raw, minMaxVals)
  SRF_raw <- SRF_raw[order(SRF_raw$lambda),]
  
  lambdaCols <- c("lambdamin", "lambdamid", "lambdamax", "equivalentWavelength")
  
  wavelengthVals[, lambdaCols] <- round(wavelengthVals[, lambdaCols], sigFig)
  SRF_raw_edited <- SRF_raw %>%
    dplyr::mutate(lambda = round(lambda, sigFig)) %>%
    dplyr::filter(!duplicated(lambda))
  minMaxPer <- sapply(wavelengthVals[, lambdaCols], function(x) 
    c(min(x, na.rm = TRUE), max(x, na.rm = TRUE)))
  minMaxAll <- apply(minMaxPer, 1, function(x) 
    c(min(x, na.rm = TRUE), max(x, na.rm = TRUE)))
  lambdaOUTall <- seq(minMaxAll[, 1][1], minMaxAll[, 2][2], by = 1 * 10^-(sigFig))
  dfOUT <- data.frame(lambda = lambdaOUTall) %>%
    dplyr::mutate(lambda = round(lambda, sigFig)) %>%
    dplyr::filter(!duplicated(lambda))
  lambdaDF <- dfOUT %>% 
    dplyr::left_join(SRF_raw_edited, by = "lambda") %>%
    dplyr::mutate(value = imputeTS::na_interpolation(value))
  wavelengthOut <- wavelengthVals
  for (lambdaCol in lambdaCols) {
    lambdaDFout <- lambdaDF
    colnames(lambdaDFout) <- c(lambdaCol, paste0(lambdaCol, "_SRF"))
    wavelengthOut <- wavelengthOut %>%
      dplyr::left_join(lambdaDFout, by = lambdaCol)
  }
  wavelengthOutDF <- dplyr::bind_cols(wavelengthOut)
  
  return(wavelengthOutDF)
}

thermographToSpectralRadiance <- function(thermograph, simData) {
  
  require(dplyr)
  
  wavelengthVals <- wavelengths(simData)
  
  wavelengthDF <- expand.grid(
    x = unique(thermograph$x), 
    y = unique(thermograph$y),
    band = unique(wavelengthVals$band)) %>%
    dplyr::left_join(wavelengthVals, by = "band")
  
  spectralRadDF <- wavelengthDF %>%
    dplyr::left_join(thermograph, by = c("x", "y")) %>%
    dplyr::mutate(value = .planck(lam = equivalentWavelength, Temp = value))
  
  return(spectralRadDF)
}

bandRadiance_surf <- function(LCam_spectralBrick, simData_transAtm, simData_radAtm, SRF_raw) {
  
  SRF <- SRFinterp(SRF_raw, simData_transAtm)
  
  Lcam_attenuated <- LCam_spectralBrick %>% 
    dplyr::left_join(as.data.frame(simData_transAtm) %>% 
                       dplyr::rename(tau = value), 
                     by = c("x", "y", "band", "simName", "imgType", "imageNo")) %>%
    dplyr::mutate(value = value / tau) %>%
    dplyr::select(-tau)
  
  Latm_attenuated <- as.data.frame(simData_radAtm) %>% 
    dplyr::left_join(SRF %>% 
                       dplyr::select(-c(
                         lambdamin_SRF, 
                         lambdamid_SRF, 
                         lambdamax_SRF, 
                         equivalentWavelength_SRF)), 
                     by = c("band", "simName")) %>%
    dplyr::left_join(as.data.frame(simData_transAtm) %>% 
                       dplyr::rename(tau = value), 
                     by = c("x", "y", "band", "variable", "iter", "typeNum", 
                            "imgType", "imageNo", "VZ", "VA", "simName", "transmittance")) %>%
    dplyr::mutate(value = value / tau) %>%
    dplyr::select(-tau)
  
  Lcam_bandRad <- getBandRadiance(spectralDF = Lcam_attenuated, 
                                  SRF = SRF)
  Latm_bandRad <- getBandRadiance(spectralDF = Latm_attenuated, 
                                  SRF = SRF)
  
  OUTdf <- Lcam_bandRad %>%
    dplyr::left_join(
      Latm_bandRad %>%
        dplyr::mutate(bandValue_Latm = bandValue) %>%
        dplyr::select(-bandValue),
      by = c("x", "y", "iter", "imgType", "imageNo", "VZ", "VA", "typeNum", "simName")) %>%
    dplyr::mutate(bandValue = bandValue - bandValue_Latm)
  
  return(OUTdf)
}


getBandRadiance <- function(spectralDF, SRF) {
  
  SRFbandvals <- SRF %>% 
    dplyr::select(-c(lambdamin, lambdamid, lambdamax, equivalentWavelength))
  
  spectralDFintegrals <- spectralDF %>%
    dplyr::left_join(SRFbandvals, 
                     by = c("band", "simName")) %>%
    dplyr::mutate(deltaLambda = (lambdamax - lambdamin) * 0.5,
                  LHS = value * lambdamin_SRF + value * lambdamid_SRF,
                  RHS = value * lambdamid_SRF + value * lambdamax_SRF,
                  integral = (LHS + RHS) * deltaLambda * 0.5) %>%
    dplyr::group_by(x, y, iter, typeNum, imgType, imageNo, VZ, VA, simName) %>%
    dplyr::summarise(bandValue = sum(integral, na.rm = TRUE))
  
  return(spectralDFintegrals)
}

.planck_inverse <- function(lam, specRad){
  c1 <- 1.191042e8
  c2 <- 1.4387752e4
  
  return(c2 / 
           (lam * log(c1 / (lam^5 * specRad) + 1)))
  
}

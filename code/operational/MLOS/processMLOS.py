# -*- coding: utf-8 -*-
'''
@author: TIANGANG YIN
'''
# module load python/canopy-1.7.2

import sqlite3
import os
import sys
import gdal
import numpy as np
import math
from scipy.interpolate import RegularGridInterpolator
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import argparse
import scipy.io
from simulationPropertiesTree import *

Cplanck1 = 1.19104402394075e-016  # =2.h.c2 (W/m2)
Cplanck2 = 0.0143876876890208  # =hc/k (m.K)


def readDARTImage(f_name, size_modified):
    ifHeadSucceed = False;
    with open(f_name + '.mpr') as fp:
        for line in fp:
            tmp = line.rstrip().split('=');
            if len(tmp) > 1 and tmp[0] == 'Size':
                sizeDartImage = np.array([int(tmpStr) for tmpStr in tmp[1].split(' ')]);
                ifHeadSucceed = True;
    if ifHeadSucceed:
        data = np.reshape(np.fromfile(f_name + '.mp#', '=f8'), sizeDartImage);
        marginDiff = [int(tmp) for tmp in (sizeDartImage - size_modified) / 2];
        return data[marginDiff[0]:marginDiff[0] + size_modified[0], marginDiff[1]:marginDiff[1] + size_modified[1]]
    else:
        print 'Error! The header file is not succesfully read.';
        quit();


def radiance2temp(rad, wl_m):
    return 1 / wl_m * Cplanck2 / math.log(Cplanck1 / math.pow(wl_m, 5.0) / rad / 1e6 + 1.0);


def radiance2temp_simp(rad, p1, p2):  # p1 = 1 / wl_m * Cplanck2; p2 = Cplanck1 / math.pow(wl_m, 5.0)
    return p1 / math.log(p2 / rad / 1e6 + 1.0);


def temp2radiance(wl_m, temp):
    return Cplanck1 / math.pow(wl_m, 5.0) / (math.exp(Cplanck2 / wl_m / temp) - 1.0) / 1E6;


def temp2radiance_simp(temp, p2, p3):  # p2 = Cplanck1 / math.pow(wl_m, 5.0); p3=Cplanck2 / wl_m
    return p2 / (math.exp(p3 / temp) - 1.0) / 1E6;


def getMoleculesPerCubicMeterFromTemperatureAndRH(T, RH):
    pressure_saturation_H2O = 6.112 * math.exp((17.62 * (T - 273.15)) / (243.12 + T - 273.15));
    pressure_H2O = RH / 100 * pressure_saturation_H2O;
    density_g_per_m3 = pressure_H2O * 216.67 / T;
    return density_g_per_m3 / 18.0 * 6.02214129e23;


def findBoundInd(col, inp):
    valueFound = False;
    for i in range(len(col) - 1):
        if inp >= min(col[i], col[i + 1]) and inp <= max(col[i], col[i + 1]):
            valueFound = True;
            return [col[i], col[i + 1]];
    if not valueFound:
        print('ERROR: Interpolation parameter not found!!!');
        quit()


# def dict_factory(cursor, row):
#     d = {}
#     for idx, col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d

class H2ODatabase:
    _connexionDB = None
    _cursorDB = None
    _pathToDB = None

    def __init__(self, path2DBfile):
        try:
            self.openConnexion(path2DBfile)
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]

    def openConnexion(self, pathToDB):
        if (self._connexionDB == None):
            if os.path.isfile(pathToDB):
                self._pathToDB = pathToDB
                self._connexionDB = sqlite3.connect(self._pathToDB)
                self._connexionDB.row_factory = sqlite3.Row
                #
                self._cursorDB = self._connexionDB.cursor()
                self._cursorDB.execute("PRAGMA temp_store=MEMORY")
                self._cursorDB.execute("PRAGMA main.page_size = 4096")
                self._cursorDB.execute("PRAGMA main.cache_size=10000")
                # If you need to lock the database for write inside (on multithreading env.)
                # self._CursorSpecularDB.execute("PRAGMA main.locking_mode=EXCLUSIVE")
                self._cursorDB.execute("PRAGMA main.synchronous=NORMAL")
                self._cursorDB.execute("PRAGMA main.journal_mode=OFF")
                self._cursorDB.execute("PRAGMA main.cache_size=5000")
            else:
                print pathToDB, ": no such file"
                sys.exit()
        else:
            print "Warning : You try to connect into an existing connection."

    def closeConnexion(self):
        # If you make an update (insert/remove data, create table, etc...), commit the changes !
        # self._connexionDB.commit();
        # Close the la connexion
        self._cursorDB.close()

    def execute(self, simulationPath, distanceFilePath, controlFile, outputPath):

        tree_phase = ET.parse(simulationPath + 'input/phase.xml')
        root_phase = tree_phase.getroot()
        wls = [float(child.attrib['meanLambda']) for child in root_phase[0][2][2]]

        simulationPropertiesTree = SimulationProperties(simulationPath + 'output/simulation.properties.txt')
        root_simulationPropertiesTree = simulationPropertiesTree.getroot()
        root_simulationPropertiesTree_waterVapor = root_simulationPropertiesTree.find('atmosphere/waterVapor')

        # tree_atmosphere = ET.parse(simulationPath + 'input/atmosphere.xml')
        # root_atmosphere = tree_atmosphere.getroot()
        # h2oAttr = root_atmosphere[0][0][1][0][0][0]
        # h2oAttr = root_atmosphere[0][0][0][0][0][0]

        # pressure = float(h2oAttr.attrib['pressure']);
        # temperature = float(h2oAttr.attrib['temp']);
        # relhumidity = float(h2oAttr.attrib['rh']);
        # refDist = float(h2oAttr.attrib['dist']);
        pressure = float(root_simulationPropertiesTree_waterVapor.find('meanPressure').attrib['value'])
        temperature = float(root_simulationPropertiesTree_waterVapor.find('meanTemp').attrib['value'])
        relhumidity = float(root_simulationPropertiesTree_waterVapor.find('meanRh').attrib['value'])
        refDist = float(root_simulationPropertiesTree_waterVapor.find('meanDistance').attrib['value'])

        moleculesPerCubicMeter = getMoleculesPerCubicMeterFromTemperatureAndRH(temperature, relhumidity);

        # print 'pressure', pressure, 'temperature', temperature, 'relhumidity', relhumidity, 'refDist', refDist, 'moleculesPerCubicMeter', moleculesPerCubicMeter

        queryDist = "   SELECT distance FROM Distance";
        self._cursorDB.execute(queryDist);
        listDist = self._cursorDB.fetchall();
        listDist = np.reshape(listDist, (len(listDist)), 1);
        # print 'listDist:', listDist

        queryPressure = "   SELECT pressure FROM Pressure";
        self._cursorDB.execute(queryPressure);
        listPressure = self._cursorDB.fetchall();
        listPressure = np.reshape(listPressure, (len(listPressure)), 1);
        # print 'listPressure:', listPressure

        queryTemp = "   SELECT temperature FROM Temperature";
        self._cursorDB.execute(queryTemp);
        listTemp = self._cursorDB.fetchall();
        listTemp = np.reshape(listTemp, (len(listTemp)), 1);
        # print 'listTemp:', listTemp

        queryRH = "   SELECT rh FROM RelHumidity";
        self._cursorDB.execute(queryRH);
        listRH = self._cursorDB.fetchall();
        listRH = np.reshape(listRH, (len(listRH)), 1);
        # print 'listRH:', listRH

        queryWL = "   SELECT wavelength FROM Wavelength";
        self._cursorDB.execute(queryWL);
        listWL = self._cursorDB.fetchall();
        listWL = np.reshape(listWL, (len(listWL)), 1);
        # print 'listWL:', listWL

        pressureBoundValues = findBoundInd(listPressure, pressure);
        temperatureBoundValues = findBoundInd(listTemp, temperature);
        relhumidityBoundValues = findBoundInd(listRH, relhumidity);

        dimInterpData = (
        len(listDist), len(pressureBoundValues), len(temperatureBoundValues), len(relhumidityBoundValues), len(listWL));

        # print 'dimInterpData', dimInterpData
        # print pressureBoundValues, temperatureBoundValues, relhumidityBoundValues;

        # It's a string.
        query = "   SELECT CS.croSec \
                    FROM CrossSection CS \
                    INNER JOIN Pressure P ON P.id = CS.idPres \
                    INNER JOIN Temperature T ON T.id = CS.idTemp \
                    INNER JOIN RelHumidity RH ON RH.id = CS.idRH \
                    WHERE P.pressure  in (?,?) \
                    AND T.temperature in (?,?) \
                    AND RH.rh in (?,?) "

        self._cursorDB.execute(query, [pressureBoundValues[0], pressureBoundValues[1], temperatureBoundValues[0],
                                       temperatureBoundValues[1], relhumidityBoundValues[0],
                                       relhumidityBoundValues[1]]);
        data_lut = np.reshape(np.array(self._cursorDB.fetchall()), dimInterpData);

        # print listDist, pressureBoundValues[::-1], temperatureBoundValues, relhumidityBoundValues
        #         Pressure MUST be reversed to have the regular grid interpolator working.
        interpolating_function_5d = RegularGridInterpolator(
            (listDist, pressureBoundValues[::-1], temperatureBoundValues, relhumidityBoundValues, listWL),
            data_lut[:, ::-1, :, :, :]);

        #         Reduce number of dimensions for the interpolator
        arrayWL, arrayDist = np.meshgrid(listWL, listDist);
        tmpIntputInterp = [[dist, pressure, temperature, relhumidity, wl] for dist, wl in
                           zip(arrayDist.ravel(), arrayWL.ravel())];
        intepolartor_2d_values = np.reshape(interpolating_function_5d(tmpIntputInterp), (len(listDist), len(listWL)));
        interpolating_function_2d = RegularGridInterpolator((listDist, listWL), intepolartor_2d_values);

        with open(controlFile) as fp:
            for line in fp:
                tmp = line.rstrip().split(' ');
                if len(tmp) == 2:
                    imageFile = tmp[0];
                    distFile = distanceFilePath + tmp[1] + '.tif';
                    # print 'Processing image file...', imageFile,

                    ds = gdal.Open(distFile)
                    distArray = np.array(ds.ReadAsArray())
                    shape_distArray = np.shape(distArray);

                    resultPathRadiance = [];
                    resultTransmittance = [];

                    for i in range(len(wls)):
                        # print '.',
                        # Reading the input images files
                        imageRadiance = simulationPath + 'output/1_Fluid/' + 'BAND' + str(
                            i) + '/Tapp/ORDER1/IMAGES_DART/' + imageFile;
                        # print imageRadiance
                        data_temperature = readDARTImage(imageRadiance, shape_distArray);
                        newRadiance = np.zeros(np.shape(data_temperature));
                        newTemperature = np.zeros(np.shape(data_temperature));
                        imageTrans = simulationPath + 'output/BAND' + str(
                            i) + '/Tapp/ORDER1/IMAGES_DART/Transmittance/' + imageFile;
                        dataTrans = readDARTImage(imageTrans, shape_distArray);

                        wl_um = wls[i];
                        wl_nm = wl_um * 1000;
                        wl_m = wl_um / 1e6;
                        # Making a image of reference optical depth
                        refEcoef = interpolating_function_2d([refDist, wl_nm]) * moleculesPerCubicMeter;
                        fakeDepthMap = distArray * refEcoef;

                        # compute the reference radiance as if the path is totally absorbed.
                        p1 = 1 / wl_m * Cplanck2;
                        p2 = Cplanck1 / math.pow(wl_m, 5.0);
                        p3 = Cplanck2 / wl_m;
                        refRadiance = temp2radiance_simp(temperature, p2, p3);
                        # print 'refRadiance', refRadiance

                        # Making a image of reference optical depth
                        calcEcoefhMap = np.reshape(
                            interpolating_function_2d([[tmp_dist, wl_nm] for tmp_dist in distArray.ravel()]),
                            shape_distArray) * moleculesPerCubicMeter;
                        calcDepthhMap = np.multiply(calcEcoefhMap, distArray)
                        dataTrans_before = np.copy(dataTrans);

                        # Correction for Transmittance
                        for i in range(shape_distArray[0]):
                            for j in range(shape_distArray[1]):
                                # For transmittance
                                if dataTrans[i, j] > 0:
                                    tmp_Depth_Diff = math.log(dataTrans[i, j]) + fakeDepthMap[i, j];
                                    if tmp_Depth_Diff > 0:
                                        tmp_Depth_Diff = 0;
                                    dataTrans[i, j] = math.exp(tmp_Depth_Diff - calcDepthhMap[i, j]);
                                else:
                                    dataTrans[i, j] = math.exp(-calcDepthhMap[i, j]);

                                # For radiance
                                if data_temperature[i, j] > 0:
                                    rad_value = temp2radiance_simp(data_temperature[i, j], p2, p3);
                                    old_emis = math.fabs(rad_value / refRadiance);
                                    tmp_1_minus_emis = 1 - old_emis if 1 - old_emis > 0 else 0;
                                    new_emis = 1;
                                    if tmp_1_minus_emis > 0:
                                        tmp_Depth_Diff = math.log(tmp_1_minus_emis) + fakeDepthMap[i, j] - \
                                                         calcDepthhMap[i, j];
                                        if tmp_Depth_Diff > 0:
                                            new_emis = 1 - math.exp(-calcDepthhMap[i, j]);
                                        else:
                                            new_emis = 1 - math.exp(tmp_Depth_Diff);
                                    else:
                                        new_emis = 1 - math.exp(-calcDepthhMap[i, j]);
                                    newRadiance[i, j] = new_emis * refRadiance;
                                    newTemperature[i, j] = radiance2temp_simp(newRadiance[i, j], p1, p2);
                        resultPathRadiance.append(newRadiance);
                        resultTransmittance.append(dataTrans);

                        #                        plt.imshow(distArray);
                        #                        plt.show()
                        #                        plt.imshow(calcDepthhMap - fakeDepthMap);
                        #                        plt.show()
                        #                        plt.imshow(dataTrans-dataTrans_before);
                        #                        plt.show()
                        #                        plt.imshow(newTemperature);
                        #                        plt.show()
                        #                        plt.imshow(data_temperature);
                        #                        plt.show()

                        # print 'End';
                scipy.io.savemat(outputPath + imageFile,
                                 dict(resultPathRadiance=resultPathRadiance, resultTransmittance=resultTransmittance))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='processMLOS.py script converts the 1st order fluid path radiance and transmittance images from Single-line into Multi-line distances specified for TIR camera')

    parser.add_argument('databaseFile', type=str, help='H2O database file')
    parser.add_argument('simulationPath', type=str, help='Path of the DART simulation')
    parser.add_argument('distanceFilePath', type=str, help='Path of distance files')
    parser.add_argument('controlFile', type=str, help='File that specified the map of distance file into camera file')
    parser.add_argument('outputPath', type=str, help='Path of output files')

    args = parser.parse_args()

    if args.databaseFile:
        print('Database File:      ' + args.databaseFile)

    if args.simulationPath:
        print('Simulation Path:    ' + args.simulationPath)

    if args.distanceFilePath:
        print('Distance File Path: ' + args.distanceFilePath)

    if args.controlFile:
        print('Control File:       ' + args.controlFile)

    if args.outputPath:
        print('Output Path:        ' + args.outputPath)

    database = H2ODatabase(args.databaseFile)
    database.execute(args.simulationPath, args.distanceFilePath, args.controlFile, args.outputPath)
    database.closeConnexion()
    print 'Finished'

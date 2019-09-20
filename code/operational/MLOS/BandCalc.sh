#!/bin/bash
#put this in DART subdir: tools/linux/

#use the below line to load various modules if using compute cluster
#module load python3.5

##arguments
#sim name
simulationName=$1
#SRF file name NOT incl. dir. file should exist in $DART_HOME/database/SensorSpectralFunction/
SRFfilename=$2
#T or F
doBandCalc=$3
#TIF or ENVI or [empty] to not run export
doExport=$4


## Set up the environnement variables
curpath="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
rcfile=`cat "${curpath}/../../config.ini"`
if [ -f $rcfile ]
then
        source $rcfile
else
        echo "'$rcfile': no such file in $(curpath)"
#       exit 1
fi

function fileExists {
               if [ -f $1 ]
then
        echo "* $1 exists"
else
        echo "* $1 not found!"
        exit 1
fi
}

function dirExists {
               if [ -d $1 ]
then
        echo "* $1 exists"
else
        echo "* $1 not found!"
        exit 1
fi
}

echo

#formulate directories
SRFfull=$DART_HOME/database/SensorSpectralFunction/$SRFfilename
pythonToolsDir=$DART_HOME/bin/python_script/BandTools
fullSimName=$DART_LOCAL/simulations/$simulationName

#check files/paths exists
fileExists $SRFfull
dirExists $pythonToolsDir
dirExists $fullSimName

##clean old data
#Exported images (bricks)
exportImgDir=$fullSimName/ExportedImage
if [ -d $exportImgDir ]
then
        echo "* cleaning data in $exportImgDir"
        rm -rf $exportImgDir
fi
#Broadband images (single integrated images with SRF considered)
broadbandImageDir=$fullSimName/BroadBand
if [ -d $broadbandImageDir ]
then
        echo "* cleaning data in $broadbandImageDir"
        rm -rf $broadbandImageDir
fi

#cd to python tools dir
cd $pythonToolsDir
if [[ $doBandcalc -eq "T" ]]
then
        echo
        #do broadband calc
        fullBroadbandCmd="python3.5 Broadband.py -sequencer 0 -simulation $fullSimName -sensitivity $SRFfull"
        echo "* running Broadband.py"
        echo "* $fullBroadbandCmd"
        echo
        echo $fullBroadbandCmd
        $fullBroadbandCmd
        echo
fi

scenespectraCmd="SceneSpectra.py -sequencer 0 -simulation $fullSimName -image_format $doExport"

#if not exporting, then finish
if [[ $doExport -eq "ENVI" || $doExport -eq "TIF" ]]
then
        echo
        #do export image
        echo "* running ExportImage.py"
        echo "* Exporting as $doExport format"
        echo
        fullExportImageCmd="python3.5 ExportImage.py -sequencer 0 -simulation $fullSimName -processingImage - -image_format $doExport"
        echo $fullExportImageCmd
        $fullExportImageCmd

        echo
fi

#go back to prior directory
cd $curpath

exit 0

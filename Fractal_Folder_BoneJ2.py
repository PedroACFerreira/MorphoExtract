#################################
#			MORPHOEXTRACT		#
###############################################################################################################################################################################################################
# READ CAREFULLY BEFORE USING
# The purpose of this script is to automatically extract a set of measures from .tif or .ims single planes or stacks created in Bitplane Imaris. It was originally create to evaluate microglia morphology.
#
# This script was tested for Bitplane Imaris versions above 7.4. .ims files generated in prior versions might not work. 
#
# IMPORTANT: If you are running this script on multiple files with more than one color channel, make sure all the channels are in the same order for all images!
#
# Available morphological parameters to select from:
#		Fractal Dimension - Measure of complexity derived from box-counting methodology. Uses BoneJ algorithm - http://bonej.org/fractal
#		Convex Hull - smallest bounding polygon - ConvexHull3D plugin - https://imagej.nih.gov/ij/plugins/3d-convex-hull/index.html
#		Solidity - Area or Volume /Convex Hull - ConvexHull3D plugin - https://imagej.nih.gov/ij/plugins/3d-convex-hull/index.html
#
# Created by Pedro Ferreira @ https://github.com/PedroACFerreira
# If used for publication purposes, please cite as: 

# Ferreira, P (2019) Automated ImageJ script for morphological parameters extraction from microscopy images. https://github.com/PedroACFerreira/MorphoExtract

# Also cite the authors of the plugins mentioned above!
################################################################################################################################################################################################################


#@ String (visibility=MESSAGE, value="-------------------------------------------------------------------Folder Settings--------------------------------------------------------------", required=false) msg1
#@ File    (label = "Input directory", style = "directory") srcFile
#@ String  (label = "File extension", value=".ims") ext
#@ String  (label = "File name contains", value = "") containString
#@ String (visibility=MESSAGE, value="-------------------------------------------------------------------Image Settings--------------------------------------------------------------", required=false) msg2
#@ Boolean (label = "Are the images a z-stack (3D)?", value = true) Dimension
#@ Boolean (label = "Compress and analyze in 2D anyway?", value = false) CompressDim
#@ Integer (label = "Number of channels? ", value = "3", min=1, stepSize=1) TChannel
#@ Integer (label = "Channel to analyze? ", value = "1", stepSize=1) DChannel
#@ String (visibility=MESSAGE, value="(make sure all images have the same number of channels in the same order)", required=false) msg4
#@ String (visibility=MESSAGE, value="(negative   <<Channel to analyze>>   values will count backwards from last channel)", required=false) msg5
#@ String (visibility=MESSAGE, value="----------------------------------------------------Choose parameters to be calculated-----------------------------------------------", required=false) msg3
#@ Boolean (label = "Fractal Dimension", value = true) Fractal
#@ Boolean (label = "Convex Hull (Area/Volume)", value = true) ConvVolume
#@ Boolean (label = "Solidity (2D/3D)", value = true) Solidity
#@ String (visibility=MESSAGE, value="----------------------------------------------------------------Logging Settings------------------------------------------------------------", required=false) msg3
#@ Boolean (label = "Generate log with list of files processed?", value = false, description = 'Will generate a .csv file with a row for each file, logging total time, as well as the time taken to run time consuming functions.') NamesLog
#@ Boolean (label = "Log average and total run times?", value = false, description = 'Will generate a .txt file describing total images processed, run time, as well as average run time per image.') TimesLog
#@CommandService cs

import csv
import os
from ij import IJ, ImagePlus
from ij import WindowManager as WM 
from ij.gui import GenericDialog
import sys
import time

ZProjectTimerList = []
FractalTimerList = []
TotalTimeList =[]

def run():

	###Get path and create results folder

  srcDir = srcFile.getAbsolutePath()
  dstDir = srcDir + '\\Results'

  Selection = [Dimension, CompressDim, Fractal, ConvVolume, Solidity]
  Measures = ['Fractal Dimension', 'Convex Hull', 'Solidity']
  Params = []
  counter1 = -1
  
  for i in Selection[2:]:
  	counter1 += 1
  	if i:
  		if Selection[0] and not Selection[1]:
  			Params.append(Measures[counter1] + ' (3D)')
  		else:
  			Params.append(Measures[counter1] + ' (2D)')

  if not os.path.isdir(dstDir):
  	os.mkdir(dstDir)
  for i in Params:
  	if not os.path.isdir(dstDir + '\\' + i):
  		os.mkdir(dstDir + '\\' + i)

  ###Get Fractal Dimension parameters

  if Fractal:
	gui = GenericDialog("Fractal Dimension Parameters")
	gui.addMessage("Select parameters for BoneJ Fractal Dimension:")
	gui.addNumericField("Starting Box Size (pixels)", 128, 0)
	gui.addNumericField("Smallest Box Size (pixels)", 1, 0)
	gui.addNumericField("Scale Factor", 2, 0)
	gui.addNumericField("Translations", 0, 0)
	gui.addMessage("WARNING: Higher number of translations\n increase calculation time considerably!")
	gui.showDialog()
	if gui.wasOKed():
		if gui.wasOKed():
			try:
			    startBoxSize = int(gui.getNextNumber()) 
			    smallestBoxSize = int(gui.getNextNumber())
			    scaleFactor = int(gui.getNextNumber())
			    translations = int(gui.getNextNumber())
			    FracParam = [startBoxSize,smallestBoxSize,scaleFactor,translations]
			except:
				quit()
	elif gui.wasCanceled():
		quit()
		
  ##########   Iterate function through folder, create list with all filenames ran

  NameList = []
  for root, directories, filenames in os.walk(srcDir):
    filenames.sort();
    for filename in filenames:
      # Check for file extension
      if not filename.endswith(ext):
        continue
      # Check for file name pattern
      if containString not in filename:
        continue
      NameList.append(filename)
      process(srcDir, dstDir, filename, Selection, FracParam, TChannel, DChannel)

  #############   Logging   ################
	
  if NamesLog:
    header = ('File ID', 'Total Time (s)', "3D Project Time (s)", 'Fractal Time (s)')

    #Create zip with all relevant logs depending on params
    if Dimension and not CompressDim:
        if Fractal:
    		LogTuples = zip(NameList,TotalTimeList,ZProjectTimerList,FractalTimerList)
        else:
    		LogTuples = zip(NameList,TotalTimeList,ZProjectTimerList)
    else:
        if Fractal:
            LogTuples = zip(NameList,TotalTimeList,FractalTimerList)
        else:
    	    LogTuples = zip(NameList,TotalTimeList)
    	
    LogCsv = open(dstDir +  "\\Log.csv","w+")
    LogWriter = csv.writer(LogCsv, delimiter=';', lineterminator='\n')
    LogWriter.writerow(header)
    for i in LogTuples:
    	LogWriter.writerow(i)
    LogCsv.close()
    
  if TimesLog:
    LogTxt = open(dstDir +  "\\Log.txt","w+")
    LogTxt.write("Script processed {} images in a total of {}s (average {}s per image).".format(len(TotalTimeList),round(sum(TotalTimeList),2),round(sum(TotalTimeList)/len(TotalTimeList),2)))
    if Dimension and not CompressDim:
		LogTxt.write("\n3D Projection took on average {}s.".format(round((sum(ZProjectTimerList) / len(ZProjectTimerList)),2)))
    if Fractal:
		LogTxt.write("\nFractal Box Counting took on average {}s.".format(round(sum(FractalTimerList) / len(FractalTimerList),2)))
    LogTxt.close()

	###Finish and print time log
  print("Script processed {} images in a total of {}s (average {}s per image).".format(len(TotalTimeList),round(sum(TotalTimeList),2),round(sum(TotalTimeList)/len(TotalTimeList),2)))
  if Dimension and not CompressDim:
  	print("\n3D Projection took on average {}s.".format(round(sum(ZProjectTimerList) / len(ZProjectTimerList),2)))
  if Fractal:
	print("\nFractal Box Counting took on average {}s.".format(round(sum(FractalTimerList) / len(FractalTimerList),2)))
    

####################################################################        Processing code          ##################################################################################

def process(srcDir, dstDir, fileName, Selection, FracParam, TChannel, DChannel):

  global ZProjectTimerList
  global FractalTimerList
  global TotalTimeList
  
  ###Define function to select adequate windows based on channel params
  
  def windows_selector():
	  windows = WM.getImageTitles()
	  if TChannel in (0,1):
	  	IJ.selectWindow(windows[0])
	  elif DChannel > TChannel:
	  	IJ.selectWindow(windows[-1])
	  elif DChannel < 0:
	  	IJ.selectWindow(windows[DChannel])
	  else:
	  	IJ.selectWindow(windows[DChannel-1])

  ###Define function to close results windows
  	  	
  def close_res_win():
  	reswin = WM.getNonImageTitles()
  	for i in range(0,len(reswin)):
  		IJ.selectWindow(reswin[i])
  		IJ.run('Close')


  ###Function start
  
  print "Processing:"
  start = time.time()
  # Opening the image
  print "Open image file", fileName
  IJ.run("Bio-Formats Windowless Importer", "open=" + srcDir + "\\" + fileName)

  # Split Channels and select correct one based on params

  IJ.run("Split Channels");
  windows_selector()
  
  IJ.run("Measure Convex Volume...")
  IJ.saveAs("Results", dstDir + "\\Convex Hull (3D)\\" + "Hull_" + fileName.split(".")[0] + ".txt" )
  IJ.run("Clear Results")
  close_res_win() #Close results windows

  
  ###3D project image stack

  ProjectTimer = time.time()
  windows_selector()
  IJ.run("3D Project...", "projection=[Brightest Point] axis=Y-Axis slice=0.60 initial=0 total=360 rotation=10 lower=1 upper=255 opacity=0 surface=100 interior=50 interpolate")
  IJ.run("Make Binary", "method=Mean background=Default calculate black")
  ProjectTimerEnd = time.time() - ProjectTimer
  ZProjectTimerList.append(ProjectTimerEnd)


  FractalTimer = time.time()
  wrapper = cs.run("org.bonej.wrapperPlugins.FractalDimensionWrapper", True, ["startBoxSize", FracParam[0], "smallestBoxSize", FracParam[1], "scaleFactor", FracParam[2], "translations", FracParam[3], "translationInfo", False, "autoParam", False, "showPoints", False])
  wrapperInstance = wrapper.get()
  Results = wrapperInstance.getOutput("resultsTable")
  FractalTimerEnd = time.time() - FractalTimer
  FractalTimerList.append(ProjectTimerEnd)

  data = ""
  fractalcsv = open(dstDir + "\\Fractal Dimension (3D)\\Fractal_"+ fileName + ".csv","w+")
  fractalWriter = csv.writer(fractalcsv, delimiter=';')
  for i in Results:
    data = data + i

  fractalWriter.writerow([str(data[0]) + ";" + str(data[1])])
  fractalcsv.close()
  
  IJ.run("Clear BoneJ results")
  
  close_res_win()

  windows = WM.getImageTitles()
  for i in range(0,(len(windows))):
  	IJ.selectWindow(windows[i])
  	IJ.run("Close")
  	
  end = time.time() - start
  TotalTimeList.append(end)

  
run()

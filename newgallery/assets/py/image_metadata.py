import os
import subprocess
from os import listdir

mainPath = "C:\\Users\\SerGo\\Dropbox\\webStuff\\PhotoWeb\\photowebgithub\\newgallery\\images\\fulls"
outputPath = "C:\\Users\SerGo\\Dropbox\\webStuff\\PhotoWeb\\photowebgithub\\newgallery\\assets\\js"

folderNames = [name for name in os.listdir(mainPath) if os.path.isdir(os.path.join(mainPath, name))]

# folderNames = os.listdir(mainPath)

fileNames = []

metadataNames = ["ExposureTime","Date","FocalLength","ExposureTime","Aperture","ISO"]

# Literal output from the exiftool metadata extractor
metadataNamesOutput = ["Exposure Time","File Creation Date/Time","Focal Length","Exposure Time","Aperture","ISO"]

picInFolder = []
count=0;

for folder in folderNames:
	path = mainPath + "\\" + folder
	for file in os.listdir(path):
		if file.endswith(".jpg"):
			fileNames.append([folder,file])
			count+=1
	picInFolder.append(count)
	count=0

dic = {}
countFolder = 0
countPhoto = 0

# print(picInFolder)

for i in range(0,len(fileNames)):
	print(fileNames[i])

for folder in folderNames:
	print("----------------------------")
	print("---- FOLDER: " + folder)
	print("----------------------------")
	path = outputPath + "\\" + folder + "photonames.js"
	file = open(path,"w")
	file.write("var photo = [ \n ")
	for index in range(0,picInFolder[countFolder]):
		# print(countPhoto,index,picInFolder[countFolder])
		command = "exiftool " + mainPath + "\\" + folder + "\\" + fileNames[countPhoto][1]
		metadata = os.popen(command).readlines()
		for names in metadataNamesOutput:
			for data in metadata:
				dic["name"] = fileNames[countPhoto][1][:-4]
				if data[:len(names)] == metadataNamesOutput[0]: # Exposure time
					dic["ExposureTime"] = data.split(":",1)[1][:-1][1:]
				elif data[:len(names)] == metadataNamesOutput[1]: # Date
					dic["Date"] = data.split(":",1)[1][:-1][1:][:-15]
				elif data[:len(names)] == metadataNamesOutput[2]: # Focal Length
					dic["FocalLength"] = data.split(":",1)[1][:-32][1:]
				elif data[:len(names)] == metadataNamesOutput[3]: # Exposure Time
					dic["ExposureTime"] = data.split(":",1)[1][:-1][1:]
				elif data[:len(names)] == metadataNamesOutput[4]: # Aperture
					dic["Aperture"] = "F" + data.split(":",1)[1][:-1][1:]
				elif data[:len(names)] == metadataNamesOutput[5]: # ISO
					dic["ISO"] = data.split(":",1)[1][:-1][1:]
		print(dic)
		file.write(str(dic))
		file.write(",")
		file.write("\n")
		countPhoto+=1
	file.write("]")
	file.close()
	countFolder+=1
	

#Note: 
# Copy the fulls folder with the large photos two times and rename the folders with:
# thumbs and thumbsBlurry
# The script will load each photo in those two folders, reduce and replace each.

import PIL
from PIL import Image

import os
import subprocess
from os import listdir

mainPath = "C:\\Users\\SerGo\\Dropbox\\webStuff\\Photoweb\\photowebgithub\\newgallery\\images"

folderNames = [name for name in os.listdir(mainPath + "\\fulls") if os.path.isdir(os.path.join(mainPath + "\\fulls", name))]

fileNames = []

# thumbnail size
thumbWidth = 640
thumbHeight = 480

def black_bg_square(img):
	"return a white-background-color image having the img in exact center"
	img_w, img_h = img.size
	size = (int(img_h/0.75), int(img_h))
	background = Image.new('RGB', size, (0,0,0))
	bg_w, bg_h = background.size
	offset = (int((bg_w - img_w) / 2), int((bg_h - img_h) / 2))
	background.paste(img, offset)
	return background

# check if it is a portrait photo

for folder in folderNames:
	path = mainPath + "\\fulls\\" + folder
	for file in os.listdir(path):
		if file.endswith(".jpg"):
			img = Image.open(path + "\\" + file)
			width, height = img.size
			if height > width:
			
				print(file + ' is a portrait photo')

				addBackground = black_bg_square(img)
				addBackground.thumbnail((thumbWidth,thumbHeight))
				addBackground.save(mainPath + "\\thumbs\\" + folder + "\\" + file)
			else:
				img.thumbnail((thumbWidth,thumbHeight))
				img.save(mainPath + "\\thumbs\\" + folder + "\\" + file)

				
for folder in folderNames:
	path = mainPath + "\\thumbs\\" + folder
	for file in os.listdir(path):
		img = Image.open(path + "\\" + file)
		img.thumbnail((thumbWidth/10,thumbHeight/10))
		img.save(mainPath + "\\thumbsBlurry\\" + folder + "\\" + file)
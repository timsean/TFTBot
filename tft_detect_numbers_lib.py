## import os, subprocess
import pyautogui
import psutil
import time
from PIL import Image, ImageOps
import pytesseract
import win32gui
import xml.dom.minidom
import matplotlib.pyplot as plt

import cv2
from os import listdir
from os.path import isfile, join
from matplotlib import pyplot as plt
import numpy as np
import math as m

from skimage.measure import label, regionprops, regionprops_table

def get_current_money(frame,template):
	total_money = 0

	height = frame.shape[0]
	width = frame.shape[1]

	h1 = int(np.floor(0.8135 * height))
	h2 = int(np.floor(0.8403 * height))

	w1 = int(np.floor(0.4514 * width))
	w2 = int(np.floor(0.4766 * width))

	## if reading frames from game, include buffer from edges of window	
	debug = 0
	if debug == 0:
		h1 = h1 +10;
		h2 = h2 +10;
		w1 = w1 -10;
		w2 = w2 -10;


	## binarize image and label islands
	gray = frame
	money = gray[ h1:h2 , w1:w2] 
	ret, bin_img = cv2.threshold(money,128,255,cv2.THRESH_BINARY)
	label_img = label(bin_img)
	regions = regionprops(label_img)


	# initializations
	digit_loc = []
	digits = []
	found = 0
	for props in regions:
		if found < 2:

			# acquire each island from bounding box. pad array for match template
			y0,x0 = props.centroid
			minr, minc, maxr, maxc = props.bbox
			cropped = bin_img[minr:maxr, minc:maxc]
			cropped = np.pad(cropped,10,'constant',constant_values = (0))

			# find matches from digits 0-9
			match = []
			for number in range(10):
				method = cv2.TM_CCOEFF_NORMED
				num_image = template[number]
				res = cv2.matchTemplate(cropped,num_image,method)
				match.append(np.amax(res))

			# minimum threshold, just in case there is noise
			threshold = 0.6
			if np.amax(match) > threshold:
				digit_loc.append(x0)		
				digits.append(np.argmax(match))
				found += 1

	# at most 2 digit number
	if found == 1:
		total_money = digits[0]
	elif found > 1:
		if digit_loc[0] < digit_loc[1]:
			total_money = digits[0]*10 + digits[1]
		else:
			total_money = digits[1]*10 + digits[0]

	return total_money


def get_current_stage(frame,template,location):

	height = frame.shape[0]
	width = frame.shape[1]

	h1 = int(np.floor(0.0001 * height));
	h2 = int(np.floor(0.0347 * height));
	
	if location == 0:
		# stage 1
		w1 = int(np.floor(0.4323 * width));
		w2 = int(np.floor(0.4597 * width));
	else:
		# for stages 2 to end
		w1 = int(np.floor(0.4023 * width));
		w2 = int(np.floor(0.4297 * width));

	## if reading frames from game, include buffer from edges of window	
	debug = 0
	if debug == 0:
		h1 = h1 +30;
		h2 = h2 +30;
		w1 = w1 -20;
		w2 = w2 -20;	


	## binarize image and label islands
	gray = frame
	money = gray[ h1:h2 , w1:w2] 
	ret, bin_img = cv2.threshold(money,100,255,cv2.THRESH_BINARY)
	label_img = label(bin_img)
	regions = regionprops(label_img)

	# initializations
	digit_loc = []
	digits = []
	found = 0
	for props in regions:
		if found < 2:
			# acquire each island from bounding box. pad array for match template
			y0,x0 = props.centroid
			minr, minc, maxr, maxc = props.bbox
			cropped = bin_img[minr:maxr, minc:maxc]
			cropped = np.pad(cropped,10,'constant',constant_values = (0))

			# find matches from digits 1-7
			match = []
			for number in range(7):
				method = cv2.TM_CCOEFF_NORMED
				num_image = template[number]
				res = cv2.matchTemplate(cropped,num_image,method)
				match.append(np.amax(res))

			# minimum threshold, just in case there is noise, in this case the hyphen in stage
			threshold = 0.6
			if np.amax(match) > threshold:
				digit_loc.append(x0)		
				digits.append(np.argmax(match)+1)
				found += 1

	# default case
	stage_str = ''

	# just in case they are swapped, create stage string		
	if found > 1:
		if digit_loc[0] < digit_loc[1]:
			stage_str = str(digits[0]) + '-' + str(digits[1])
		else:
			stage_str = str(digits[1]) + '-' + str(digits[0])

	return stage_str


def get_money_template():
	# read template images for money digits
	template = []
	for number in range(10):
		tmp = cv2.cvtColor(cv2.imread(f'money_images/{number}.png'), cv2.COLOR_BGR2GRAY)  
		template.append(tmp)

	return template

def get_stage_template():
	# read template images for stage digits 
	template = []
	for number in range(7):
		tmp = cv2.cvtColor(cv2.imread(f'stage_images/{number+1}.png'), cv2.COLOR_BGR2GRAY)  
		template.append(tmp)

	return template	

## start reading video

####  not calling because its now a library for main
# videopath = 'C:/Users/kjj34/Desktop/TFTBot kevin'
# videopath = 'C:/Users/kjj34/Videos/League of Legends'
# vidname = 'League of Legends 2020.09.08 - 17.35.48.02.mp4'

# cap = cv2.VideoCapture(videopath + '/' + vidname)

# fps =int(cap.get(5)); 
# totalframe = int(cap.get(7))
# width = int(cap.get(3))
# height = int(cap.get(4))

# minute = 15;
# second = 30;
# timestamp = (minute*60 + second)*fps

# # intialization
# oldstage = '' 
# money_template = get_money_template();
# stage_template = get_stage_template();
# stage_loc = 0; # start looking location for stage 1

# while True:
# 	# get frame
# 	cap.set(1,timestamp)
# 	ret, frame = cap.read()
# 	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# 	plt.imshow(frame)
# 	plt.show()

# 	# read money
# 	current_money = get_current_money(frame,money_template);

# 	# read stage
# 	stage = get_current_stage(frame,stage_template,stage_loc);

# 	# if stage not found, probably on stage 2 or later now
# 	if not stage:
# 		stage_loc = 1
# 		stage = get_current_stage(frame,stage_template,stage_loc);

	
# 	if stage == oldstage:
# 		print('no change')
# 	else:
# 		print('new stage')
# 		oldstage = stage
# 		print(stage)
# 		print(current_money)

# 		# tmp_sec = timestamp/60
# 		# tmp_min = m.floor(tmp_sec/60)
# 		# tmp_sec = tmp_sec % 60
# 		# print(str(tmp_min) + ':' + str(int(tmp_sec)))	

# 	# plt.imshow(frame)
# 	# plt.show()

# 	timestamp = timestamp + 60*fps
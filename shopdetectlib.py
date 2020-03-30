
import cv2
from os import listdir
from os.path import isfile, join
import numpy as np


def get_champ_database(train_dir):
	# input: string containing directory for training images. 
	# output: database of descriptors for each image. 

	train_set = [f for f in listdir(train_dir) if isfile(join(train_dir, f))]
	orb = cv2.ORB_create()
	database = [];
	for i in range(len(train_set)):
		tmp_image = cv2.imread(train_dir + '/' + train_set[i],0)
		kp, des = orb.detectAndCompute(tmp_image,None)
		database.append(des)

	return database

def get_champ_database(train_dir):
	# input: string containing directory for training images. 
	# output: database of descriptors for each image. 

	train_set = [f for f in listdir(train_dir) if isfile(join(train_dir, f))]
	orb = cv2.ORB_create()
	database = [];
	for i in range(len(train_set)):
		tmp_image = cv2.imread(train_dir + '/' + train_set[i],0)
		kp, des = orb.detectAndCompute(tmp_image,None)
		database.append(des)

	return database


def score_champ_in_shop(image , database):
	# input: image of a single slot in the store
	# output: array of length database containing values from 0 to 1, indcating how close of a match

	orb = cv2.ORB_create()
	score = np.zeros(1)
	kp2, des_test = orb.detectAndCompute(image,None)
	if des_test is not None:
		score = np.zeros(len(database))
		num_list = len(des_test);
		for j in range(len(database)):
			bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
			matches = bf.match(des_test,database[j])
			if num_list > 100:
				score[j] = len(matches)/num_list;
	return score

def classify_champ(score, train_dir):
	# input: score, the output from score_champ_in_shop(), as well as training directory
	# output: string containing name of prediction. threshold can be edited here

	train_set = [f for f in listdir(train_dir) if isfile(join(train_dir, f))]
	best_score = max(score)
	if best_score > 0.4:
		predict = train_set[np.argmax(score)];
		predict = predict[:-4]
	else:
		predict = 'error'

	return predict


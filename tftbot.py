# Dependencies: PyAutoGUI, psutil, pywin32, PIL, pytesseract (google's OCR package)
import os, subprocess
import pyautogui
import psutil
import time
from PIL import Image, ImageOps
import pytesseract
import win32gui
import xml.dom.minidom

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

import cv2
from os import listdir
from os.path import isfile, join
from matplotlib import pyplot as plt
import numpy as np
import shopdetectlib as sd

## import my files
import tft_detect_numbers_lib as dn
import math

pyautogui.FAILSAFE= False
client_x = 0
client_y = 0
client_w = 0
client_h = 0
game_x = 0
game_y = 0
game_w = 0
game_h = 0

# Define cursor locations
cursor_play = (9.5, 5.5)
cursor_tft = (68.5, 28.9)
cursor_confirm = (42, 96)
cursor_find_match = (42, 95)
cursor_accept_match = (50, 77)
cursor_close_notif = (50, 94)
cursor_surrender = (45, 47)
cursor_level_up = (19, 90)
check_notif_pixel = (1, 99)
pet_home = (23, 63)


# Rounds
rounds_list = [\
	['c', 'm', 'm', 'm'],\
	['p', 'p', 'p', 'c', 'p', 'p', 'm'],\
	['p', 'p', 'p', 'c', 'p', 'p', 'm'],\
	['p', 'p', 'p', 'c', 'p', 'p', 'm'],\
	['p', 'p', 'p', 'c', 'p', 'p', 'm'],\
	['p', 'p', 'p', 'c', 'p', 'p', 'm'],\
	['p', 'p', 'p', 'c', 'p', 'p', 'm']]

champ_list = []


# Prepare for Shop Detection
train_dir = 'champ_shop_images'
database = sd.get_champ_database(train_dir)

def grab_client_screen():
	global client_x, client_y, client_w, client_h
	leagueWnd = win32gui.FindWindow(None, 'League of Legends')
	rect = win32gui.GetWindowRect(leagueWnd)
	client_x = rect[0]
	client_y = rect[1]
	client_w = rect[2] - client_x
	client_h = rect[3] - client_y
	screen_raw = pyautogui.screenshot()
	screen_cropped = screen_raw.crop(rect)
	return screen_cropped

def update_game_location():
	global game_x, game_y, game_w, game_h
	leagueWnd = win32gui.FindWindow(None, 'League of Legends (TM) Client')
	rect = win32gui.GetWindowRect(leagueWnd)
	game_x = rect[0]
	game_y = rect[1]
	game_w = rect[2] - game_x
	game_h = rect[3] - game_y

def grab_game_screen():
	global game_x, game_y, game_w, game_h
	update_game_location()
	screen_raw = pyautogui.screenshot()
	screen_cropped = screen_raw.crop((game_x, game_y, game_x+game_w, game_y+game_h))
	return screen_cropped

def crop_screen(screen, ul, br):
	w, h = screen.size
	return screen.crop((ul[0]*0.01*w, ul[1]*0.01*h, br[0]*0.01*w, br[1]*0.01*h))

def compute_global_coord_client(loc_x, loc_y):
	# Computes the global coordinate of mouse clicks for CLIENT window
	# loc_x and loc_y are integers from 0 to 100 representing percentage 
	# across the window
	global client_x, client_y, client_w, client_h
	glob_x = int(client_x + client_w*loc_x*0.01)
	glob_y = int(client_y + client_h*loc_y*0.01)
	return glob_x, glob_y

def compute_global_coord_game(loc_x, loc_y):
	# Computes the global coordinate of mouse clicks for GAME window
	# loc_x and loc_y are integers from 0 to 100 representing percentage 
	# across the window
	global game_x, game_y, game_w, game_h
	glob_x = int(game_x + game_w*loc_x*0.01)
	glob_y = int(game_y + game_h*loc_y*0.01)
	return glob_x, glob_y

def play_again():
	# Click the play again button (same location as find match)
	global cursor_find_match
	glob_x, glob_y = compute_global_coord_client(cursor_find_match[0], cursor_find_match[1])
	pyautogui.click(x=glob_x, y=glob_y, clicks=1, interval=0, button='left')
	print('Playing again')
	time.sleep(5)

def close_notif():
	# Click the play again button (same location as find match)
	global cursor_close_notif
	glob_x, glob_y = compute_global_coord_client(cursor_close_notif[0], cursor_close_notif[1])
	pyautogui.click(x=glob_x, y=glob_y, clicks=1, interval=0, button='left')
	print('Closing notif')
	time.sleep(5)

def find_accept_match():
	# Spam the accept match button until the actual game starts
	global cursor_accept_match, cursor_find_match
	glob_x, glob_y = compute_global_coord_client(cursor_find_match[0], cursor_find_match[1])
	pyautogui.click(x=glob_x, y=glob_y, clicks=1, interval=0, button='left')
	print('Finding match')
	start_queue_time = time.time()
	match_not_found = True

	restarted = False

	while(match_not_found):
		glob_x, glob_y = compute_global_coord_client(cursor_accept_match[0], cursor_accept_match[1])
		pyautogui.click(x=glob_x, y=glob_y, clicks=1, interval=0, button='left')
		time.sleep(1)
		match_not_found = not checkIfProcessRunning('League of Legends')
		glob_x, glob_y = compute_global_coord_client(cursor_find_match[0], cursor_find_match[1])
		pyautogui.click(x=glob_x, y=glob_y, clicks=1, interval=0, button='left')
		time.sleep(0.5)
		if time.time() - start_queue_time > 300:
			if not restarted:
				restart_client()
				start_queue_time = time.time()
				restarted = True
			else:
				restart_client_and_click()
				start_queue_time = time.time()
				restarted = False

	print('Match accepted')
	time.sleep(7)

def restart_client():
	global cursor_play, cursor_tft, cursor_confirm
	os.system("taskkill /f /im  LeagueClient.exe")
	time.sleep(5)
	subprocess.Popen(["C:/Riot Games/League of Legends/LeagueClient.exe"])
	while not checkIfProcessRunning('LeagueClient.exe'):
		time.sleep(1)
	print('League client restarted')
	time.sleep(30)
	grab_client_screen()

def restart_client_and_click():
	global cursor_play, cursor_tft, cursor_confirm
	os.system("taskkill /f /im  LeagueClient.exe")
	time.sleep(5)
	subprocess.Popen(["C:/Riot Games/League of Legends/LeagueClient.exe"])
	while not checkIfProcessRunning('LeagueClient.exe'):
		time.sleep(1)
	print('League client restarted')
	time.sleep(30)
	grab_client_screen()
	glob_x, glob_y = compute_global_coord_client(cursor_play[0], cursor_play[1])
	pyautogui.click(x=glob_x, y=glob_y, clicks=1, interval=0, button='left')
	time.sleep(1)
	glob_x, glob_y = compute_global_coord_client(cursor_tft[0], cursor_tft[1])
	pyautogui.click(x=glob_x, y=glob_y, clicks=1, interval=0, button='left')
	time.sleep(1)
	glob_x, glob_y = compute_global_coord_client(cursor_confirm[0], cursor_confirm[1])
	pyautogui.click(x=glob_x, y=glob_y, clicks=1, interval=0, button='left')
	time.sleep(1)


def surrender():
	# Forfeit
	global cursor_surrender
	update_game_location()
	pyautogui.press('enter')
	pyautogui.press('/')
	pyautogui.press('f')
	pyautogui.press('f')
	pyautogui.press('enter')
	time.sleep(0.5)
	glob_x, glob_y = compute_global_coord_game(cursor_surrender[0], cursor_surrender[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.05)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(20)

def check_match_loaded():
	# Check if the match is loaded
	global game_w, game_h
	color_check_loc1 = (99.4, 12.25)
	rgb = (22,32,33)
	match_not_loaded = True
	while(match_not_loaded):
		game_scr = grab_game_screen()
		game_scr_pixels = game_scr.load()
		color1 = game_scr_pixels[int(color_check_loc1[0]*game_w*0.01), int(color_check_loc1[1]*game_h*0.01)]
		color1_diff = (color1[0] - rgb[0])**2 + (color1[1] - rgb[1])**2 + (color1[2] - rgb[2])**2
		if (color1_diff < 300):
			match_not_loaded = False
		time.sleep(1)
	print('Match loaded')

def check_notif():
	global check_notif_pixel
	rgb = (1,5,10)
	time.sleep(5)
	client_scr = grab_client_screen()
	client_scr_pixels = client_scr.load()
	color1 = client_scr_pixels[int(check_notif_pixel[0]*client_w*0.01), int(check_notif_pixel[1]*client_h*0.01)]
	color1_diff = (color1[0] - rgb[0])**2 + (color1[1] - rgb[1])**2 + (color1[2] - rgb[2])**2
	return color1_diff < 150

def level_up():
	global cursor_level_up
	update_game_location()
	glob_x, glob_y = compute_global_coord_game(cursor_level_up[0], cursor_level_up[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.05)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(0.1)

def full_level_up():
	for i in range(0,10):
		level_up()

def buy_champ():
	global pet_home
	champ1 = (30, 90)
	champ2 = (41, 90)
	champ3 = (52, 90)
	champ4 = (63, 90)
	champ5 = (74, 90)

	glob_x, glob_y = compute_global_coord_game(champ1[0], champ1[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.05)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(0.25)

	glob_x, glob_y = compute_global_coord_game(champ2[0], champ2[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.05)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(0.25)

	glob_x, glob_y = compute_global_coord_game(champ3[0], champ3[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.05)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(0.25)

	glob_x, glob_y = compute_global_coord_game(champ4[0], champ4[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.05)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(0.25)

	glob_x, glob_y = compute_global_coord_game(champ5[0], champ5[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.05)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(0.25)

	# glob_x, glob_y = compute_global_coord_game(pet_home[0], pet_home[1])
	# pyautogui.click(x=glob_x, y=glob_y, clicks=5, interval=0.1, button='right')

def random_move():
	# List of locations to move pet to
	# First tuple is home
	locations = [(1000, 850),\
		(2245, 850),\
		(2245, 670),\
		(1140, 670),\
		(1140, 490),\
		(2245, 490)]
	for loc in locations:
		pyautogui.click(x=loc[0], y=loc[1], clicks=5, interval=0.1, button='right')
		time.sleep(4)
	pyautogui.click(x=pet_home[0], y=pet_home[1], clicks=5, interval=0.1, button='right')

def check_gold():
	crop_ul = (45,82)
	crop_br = (48,84.3)
	game_scr = grab_game_screen()
	game_scr = ImageOps.invert(game_scr.convert('L'))
	gold_crop = crop_screen(game_scr, crop_ul, crop_br)
	w, h = gold_crop.size
	gold_crop = gold_crop.resize((w*3, h*3))
	gold_text = pytesseract.image_to_string(gold_crop, config='--psm 13 -c tessedit_char_whitelist=0123456789 ')
	return gold_text

def check_planning():
	crop_ul = (46,17)
	crop_br = (54,21.5)
	game_scr = grab_game_screen()
	plan_crop = crop_screen(game_scr, crop_ul, crop_br)
	w, h = plan_crop.size
	plan_crop = plan_crop.resize((w, h))
	plan_text = pytesseract.image_to_string(plan_crop)
	# print(plan_text)
	return plan_text == 'Planning'

def get_round(name):
	crop_ul = (40.1,3.15)
	crop_br = (42.4,5.25)
	game_scr = grab_game_screen()
	game_scr = ImageOps.invert(game_scr.convert('L'))
	round_crop = crop_screen(game_scr, crop_ul, crop_br)
	w, h = round_crop.size
	round_crop = round_crop.resize((w*5, h*5))
	round_text = pytesseract.image_to_string(round_crop)
	#round_crop.save('images\\' + str(name) + '_' + round_text + '.png', 'png')
	if len(round_text) >= 3:
		round_num = round_text[0]
		match_num = round_text[2]
		return round_num, match_num
	else:
		return 0, 0

def get_champ_list():
	global champ_list
	doc = xml.dom.minidom.parse('tftinfo.xml')
	names = doc.getElementsByTagName('name')
	champ_list = [name.firstChild.data for name in names]

def detect_champ_name(name_img):
	global champ_list
	scaler = 2
	w, h = name_img.size
	name_crop = name_img.resize((w*scaler, h*scaler))
	detected_name = pytesseract.image_to_string(name_crop)
	while detected_name not in champ_list:
		if scaler == 6:
			name_crop.save('images\\error.png', 'png')
			return 'ERR'
		scaler = scaler + 1
		name_crop = name_img.resize((w*scaler, h*scaler))
		detected_name = pytesseract.image_to_string(name_crop)
	print(scaler)
	return detected_name

def get_store_champs():
	game_scr = grab_game_screen()
	# game_scr = ImageOps.invert(game_scr.convert('L'))
	game_scr = cv2.cvtColor(np.array(game_scr), cv2.COLOR_BGR2GRAY)

	height = game_scr.shape[0]
	width = game_scr.shape[1]

	shop_loc_h = np.floor(np.dot([0.8542, 1] , height));
	shop_loc_w = np.floor(np.dot([0.2461,0.7734] , width )) 
	shop_div = np.ceil(np.linspace(shop_loc_w[0],shop_loc_w[1],6))
	shop_space = int(shop_div[1] - shop_div[0])

	champ_store = ''
	for k in range(5):
		h1 = int(shop_loc_h[0])
		h2 = int(shop_loc_h[1])
		w1 = int(shop_div[k])
		slot = game_scr[ h1:h2 , w1:(w1 + shop_space)]
		score = sd.score_champ_in_shop(slot , database)
		predict = sd.classify_champ(score,train_dir)
		champ_store = champ_store + predict + f' {max(score):.2f} '
	return champ_store

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

def check_exitnow(frame):
	
	# initialize for clicking exit now
	cursor_exit_now = (46,50)
	glob_x, glob_y = compute_global_coord_game(cursor_exit_now[0], cursor_exit_now[1])
	found = 0 

	# template of exit now
	exitnow = cv2.cvtColor(cv2.imread(f'exitnow.png'), cv2.COLOR_BGR2GRAY) 

	# check area of where exit now is
	height = frame.shape[0]
	width = frame.shape[1]

	h1 = int(np.floor(0.4720 * height));
	h2 = int(np.floor(0.5192 * height));
	
	w1 = int(np.floor(0.3550 * width));
	w2 = int(np.floor(0.4900 * width));

	## if reading frames from game, include buffer from edges of window	
	debug = 0
	if debug == 0:
		h1 = h1 +30;
		h2 = h2 +30;

	gray = frame
	exit_area = gray[ h1:h2 , w1:w2]
	exit_area=  np.pad(exit_area,10,'constant',constant_values = (0))

	# compare 
	method = cv2.TM_CCOEFF_NORMED
	res = cv2.matchTemplate(exit_area,exitnow,method)
	confidence = np.amax(res)
	threshold = 0.3
	if confidence > threshold:
		print('Exiting now...')
		pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
		time.sleep(0.05)
		pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
		time.sleep(0.25)
		found = 1
		
	return found

###################################################################################################
########################################## MAIN ###################################################
###################################################################################################

time.sleep(2)
while True:

	### find game
	grab_client_screen()
	find_accept_match()
	check_match_loaded()
	start_time = time.time()

	### play game

	# intialization
	oldstage = '' 
	old_money = -1
	current_money = 0
	money_template = dn.get_money_template();
	stage_template = dn.get_stage_template();
	stage_loc = 0; # start looking location for stage 1

	while True:
		# get frame
		frame = grab_game_screen()
		frame = cv2.cvtColor(np.array(frame), cv2.COLOR_BGR2GRAY)		

		# read stage
		stage = dn.get_current_stage(frame,stage_template,stage_loc);

		# if stage not found, probably on stage 2 or later now
		if stage == '' and stage_loc == 0:
			stage_loc = 1
			stage = dn.get_current_stage(frame,stage_template,stage_loc);
		elif stage == '' and stage_loc == 1:
			stage = '0-0'
			
		stage_parta = int(stage[0])
		stage_partb = int(stage[2])


		## read money on non stage carousels
		if stage_parta == 1:
			if stage_partb > 2:
				current_money = dn.get_current_money(frame,money_template);

		else:
			if stage_partb != 4:
				current_money = dn.get_current_money(frame,money_template);


		# display if there is change in money
		if current_money != old_money:
			old_money = current_money
			print('gold:' + str(current_money))


		# if new stage, do stuff
		if stage != oldstage:
			# replace old stage
			oldstage = stage

			# display stage
			print('new stage: ' + stage)

			# buy champs except on stage x-4, for x>=2, and not 1-1.
			stage_parta = int(stage[0])
			stage_partb = int(stage[2])

			if stage_parta == 1:
				if stage_partb > 2:
					print("Buying Champions:")
					buy_champ()

					frame = grab_game_screen()
					frame = cv2.cvtColor(np.array(frame), cv2.COLOR_BGR2GRAY)	
					current_money = dn.get_current_money(frame,money_template);

			else:
				if stage_partb != 4:
					print("Buying Champions:")
					buy_champ()

					frame = grab_game_screen()
					frame = cv2.cvtColor(np.array(frame), cv2.COLOR_BGR2GRAY)	
					current_money = dn.get_current_money(frame,money_template);

			# display gold again if new amount of money
			if current_money != old_money:
				old_money = current_money
				print('gold:' + str(current_money))		

			# if greater than 50 gold, level up but dont get less than 50
			if current_money >= 50:
				num_levelup = int((current_money-50)/4)

				print("Leveling down to ~50 gold:")
				for i in range(0,num_levelup):
					level_up()



			# at stage 4-1, all in level.
			if stage == '4-2' or stage == '4-5' or stage == '5-1':
				num_levelup = int(current_money/4)

				print("Leveling down all the way:")
				for i in range(0,num_levelup):
					level_up()
		# else, dont do anything.


		# end stage. leave loop and surrender 
		if stage == '5-4':
			time.sleep(5)
			break

		# check if died. leave if died
		died = check_exitnow(frame)
		if  died == 1:
			break 

		# frame refresh rate. can increase time to decrease amount of processing	
		time.sleep(1)	
			
	# Surrender if 5-1.
	if died == 0:
		print('Surrendering...')
		surrender()

	# restart Game
	print('Checking Notifications...')
	while check_notif():
		grab_client_screen()
		close_notif()
	play_again()


	

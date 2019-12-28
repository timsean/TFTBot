# Dependencies: PyAutoGUI, psutil, pywin32, PIL, pytesseract (google's OCR package)
import pyautogui
import psutil
import time
from PIL import Image
import pytesseract
import win32gui

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

client_x = 0
client_y = 0
client_w = 0
client_h = 0
game_x = 0
game_y = 0
game_w = 0
game_h = 0

# Define cursor locations
cursor_find_match = (42, 95)
cursor_accept_match = (50, 77)
cursor_close_notif = (50, 94)
cursor_surrender = (45, 58.25)
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

def find_match():
	# Click the find match button
	global cursor_find_match
	glob_x, glob_y = compute_global_coord_client(cursor_find_match[0], cursor_find_match[1])
	pyautogui.click(x=glob_x, y=glob_y, clicks=1, interval=0, button='left')
	print('Finding match')

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

def accept_match():
	# Spam the accept match button until the actual game starts
	global cursor_accept_match
	glob_x, glob_y = compute_global_coord_client(cursor_accept_match[0], cursor_accept_match[1])
	match_not_found = True
	while(match_not_found):
		pyautogui.click(x=glob_x, y=glob_y, clicks=1, interval=0, button='left')
		time.sleep(1)
		match_not_found = not checkIfProcessRunning('League of Legends')
	print('Match accepted')
	time.sleep(7)

def surrender():
	# Forfeit
	global cursor_surrender
	pyautogui.press('enter')
	pyautogui.press('/')
	pyautogui.press('f')
	pyautogui.press('f')
	pyautogui.press('enter')
	time.sleep(0.5)
	glob_x, glob_y = compute_global_coord_game(cursor_surrender[0], cursor_surrender[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.3)
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
	glob_x, glob_y = compute_global_coord_game(cursor_level_up[0], cursor_level_up[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.1)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(0.3)

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
	time.sleep(0.3)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(0.5)

	glob_x, glob_y = compute_global_coord_game(champ2[0], champ2[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.3)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(0.5)

	glob_x, glob_y = compute_global_coord_game(champ3[0], champ3[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.3)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(0.5)

	glob_x, glob_y = compute_global_coord_game(champ4[0], champ4[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.3)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(0.5)

	glob_x, glob_y = compute_global_coord_game(champ5[0], champ5[1])
	pyautogui.mouseDown(x=glob_x, y=glob_y, button='left')
	time.sleep(0.3)
	pyautogui.mouseUp(x=glob_x, y=glob_y, button='left')
	time.sleep(0.5)

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
	gold_crop = crop_screen(game_scr, crop_ul, crop_br)
	w, h = gold_crop.size
	gold_crop = gold_crop.resize((w*3, h*3))
	gold_text = pytesseract.image_to_string(gold_crop, config='--psm 13 -c tessedit_char_whitelist=01234567890 ')
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
	round_crop = crop_screen(game_scr, crop_ul, crop_br)
	w, h = round_crop.size
	round_crop = round_crop.resize((w*5, h*5))
	round_text = pytesseract.image_to_string(round_crop)
	round_crop.save(str(name) + '_' + round_text + '.png', 'png')
	if len(round_text) >= 3:
		round_num = round_text[0]
		match_num = round_text[2]
		return round_num, match_num
	else:
		return 0, 0

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

time.sleep(2)
while True:
	planning_done = False
	stage = 0
	grab_client_screen()
	find_match()
	accept_match()
	check_match_loaded()
	start_time = time.time()
	while True:
		time.sleep(0.5)
		if not check_planning() and planning_done:
			planning_done = False
			print('Planning done')
		if check_planning() and not planning_done:
			print('Planning start: buying champs')
			print(get_round(stage))
			buy_champ()
			planning_done = True
			stage = stage + 1
			if (stage == 7):
				time.sleep(1)
				level_up()
				print('Leveled up at stage 7')
			if (stage == 10 or stage == 13):
				time.sleep(1)
				full_level_up()
				print('Leveled up at stage 10/12')
			print(stage)
			time.sleep(10)
		current_time = time.time()
		elapsed_time = current_time-start_time
		if elapsed_time > 600:
			print('Time:')
			print(elapsed_time/60)
		if (elapsed_time >= 1260):
			break
	surrender()
	while check_notif():
		close_notif()
	play_again()


#random_move()



# TODO:
# Game time
# Detecting planning phase and game phase
# Gold detection
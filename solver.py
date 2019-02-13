from PIL import Image
import pytesseract
import subprocess
import itertools
import time
import sys
import img


#SETUPS
#read all words from dict
dictionary = open('dict.txt', 'r')
real_words = dictionary.readlines()

#Factors to align coord systems (apparently they're different...) may not work for all.
xf = 0.2636
yf = 0.542

#Data for where to tap for a certain letter.
mapx = {6:[540, 750, 750, 540, 330, 330], 7:[540, 740, 780, 650, 430, 300, 340]}
mapy = {6:[1360, 1480, 1720, 1830, 1720, 1480], 7:[1340, 1440, 1650, 1820, 1820, 1650, 1440]}

#Gets real words from a scrambled string.
def get_real_words(scrambled, nothrees):
	res = []
	perms = []
	for i in range(3+nothrees, len(scrambled)+1): #generate possibilites from length 3 to length of scrambled
		tryer = [''.join(i) for i in itertools.permutations(scrambled, i)]
		for i in tryer:
			if i not in perms: #only \n for Windows, running in Ubuntu app you must append \r\n...
				perms.append(i)
	perms.sort()
	#print perms
	for i in range(len(real_words)):
		if len(perms) == 0:
			break
		while real_words[i].strip('\n') >= perms[0]:
			if real_words[i].strip('\n') == perms[0]:
				res.append(perms[0])
			del perms[0]
			if len(perms) == 0:
				break
	return res

#ADB stuff
#NOTE: Multi-touch is not supported or needed here.
#NOTE: make sure you have adb.exe in PATH

#Communicates a *shell* command via ADB
def do(command):
	process = subprocess.Popen('adb shell', shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
	process.communicate(command)
	return

#String for an ADB event beginning a screen press
finger_down = "sendevent dev/input/event2 3 57 0\nsendevent dev/input/event2 1 330 1\nsendevent dev/input/event2 1 325 1\n"

#String for an ADB event releasing a screen press
finger_up = "sendevent dev/input/event2 3 57 -1\nsendevent dev/input/event2 1 330 0\nsendevent dev/input/event2 1 325 0\nsendevent dev/input/event2 0 0 0\n"

#Returns string for an ADB event directing it to move the touch to (x, y). Press should already be down at this point.
def move_to(x, y):
	global xf, yf
	return "sendevent dev/input/event2 3 53 {}\nsendevent dev/input/event2 3 54 {}\nsendevent dev/input/event2 0 0 0\n".format(str(int(x/xf)), str(int(y/yf)))

#Taps the screen at (x, y). Could be done with adb input tap instead... whatever.
def tap(x, y):
	payload = finger_down + move_to(x, y) + finger_up
	do(payload)

#Starts at a point, then goes through each (x_i, y_i) in xpts[] and ypts[]. 
def draw(xpts, ypts):
	payload = finger_down
	for i in range(len(xpts)):
		payload += move_to(xpts[i], ypts[i])
	payload += finger_up
	payload += "sleep 0.15\n" #Puts a small space between each draw, so we don't accidentally go too fast and skip. (has happened...)
	do(payload)

#Presses the screen at (x, y); press Enter on the keyboard to release.
def longpress(x, y):
	payload = finger_down
	payload += move_to(x, y)
	do(payload)
	raw_input("Paused. Press Enter to continue")
	do(finger_up)

#Returns an Image object of the current screen, also stores it in fn.png.
def getscreen(fn):
	process = subprocess.Popen('adb shell', shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
	process.communicate("screencap /sdcard/{}".format(fn))
	process = subprocess.Popen('adb pull /sdcard/{}'.format(fn), shell = False, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
	process.communicate()
	return Image.open(fn)

#Draws all the real words to the screen. numletters = 6 or 7, orig = original scrambled string (used to account for repeating letters)
def draw_words(wordlist, numletters, orig):
	for word in wordlist:
		tempword = orig
		dqx = []
		dqy = []
		for letter in word:
			dqx.append(mapx[numletters][tempword.find(letter)])
			dqy.append(mapy[numletters][tempword.find(letter)])
			tempword = tempword[:tempword.find(letter)] + '_' + tempword[tempword.find(letter)+1:]
		draw(dqx, dqy)

#Tries to get to the next level OR pack. Exits the program if fail; most likely the program didn't solve the level...
def next_level():
	tap(0,0)
	time.sleep(10)
	test = getscreen("next.png").crop((350,1520,720,1650))
	#test.save("nextleveldebug.png")
	if "LEVEL" in pytesseract.image_to_string(img.clean(test)):
		tap(540, 1590)
		return
	else:
		time.sleep(10)
		test = getscreen("next.png").crop((350, 1520, 720, 1650))
		if "LEVEL" in pytesseract.image_to_string(img.clean(test)):
			tap(540, 1590)
		else:
			print "Failed to press next level."
			sys.exit(-2)

#Solve a level, with manual input.
if __name__ == "__main__":
	data = raw_input("Letters: ")
	nothr = raw_input("3 letter restriction? (Y = 1, N = 0) ")
	print "Unscrambling"
	words = get_real_words(data, int(nothr))
	print "Done unscrambling"
	print words
	print "Drawing"
	draw_words(words, len(data), data)
	print "Done drawing"
	print "Trying to press next level/pack"
	next_level()

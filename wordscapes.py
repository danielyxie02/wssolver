from PIL import Image
import subprocess
import argparse
import solver
import time
import img
import sys

def main():
	print "---NEW LEVEL-----------------------"

	#Get the level's screencap
	start = time.time()
	levelscreen = solver.getscreen("screen.png")
	print "Got screen in {}".format(str(time.time() - start))

	#Determine useful image data
	start = time.time()
	num = img.sixseven(levelscreen)
	no3 = img.nothree(levelscreen)
	data = img.getsquares(levelscreen, num)
	letters = img.tessread(data)
	print "Number of letters: {}".format(str(num))
	print "No 3 restriction: {}".format(str(no3))
	print "String: {}".format(letters)
	print "Determined image data in {}".format(str(time.time() - start))

	#Unscramble
	print "Unscrambling"
	start = time.time()
	words = solver.get_real_words(letters, no3)
	print words
	print "Unscrambled in {}".format(str(time.time() - start))

	#Draw 
	print "Drawing"
	start = time.time()
	solver.draw_words(words, len(letters), letters)
	print "Done drawing"
	print "Drew answers in {}".format(str(time.time() - start))

	#Go to the next level, or fail...
	solver.next_level()
	time.sleep(2)

if __name__ == "__main__":
	solver.tap(0,0) #Get rid of any lines left over from previous runs
	while True:
		main()
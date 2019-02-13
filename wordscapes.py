from PIL import Image
import subprocess
import solver
import time
import img
import sys

def main():
	masterstart = time.time()

	#Get the level's screencap
	start = time.time()
	levelscreen = solver.getscreen("screen.png")
	end = time.time()
	print "Got screen in {}".format(str(end - start))

	#Determine useful image data
	start = time.time()
	num = img.sixseven(levelscreen)
	no3 = img.nothree(levelscreen)
	data = img.getsquares(levelscreen, num)
	letters = img.tessread(data)
	print "Number of letters: {}".format(str(num))
	print "No 3 restriction: {}".format(str(no3))
	print "String: {}".format(letters)
	end = time.time()
	print "Determined image data in {}".format(str(end - start))

	#Unscramble
	print "Unscrambling"
	start = time.time()
	words = solver.get_real_words(letters, no3)
	end = time.time()
	print words
	print "Unscrambled in {}".format(str(end - start))

	#Draw 
	print "Drawing"
	start = time.time()
	solver.draw_words(words, len(letters), letters)
	print "Done drawing"
	end = time.time()
	print "Drew answers in {}".format(str(end - start))

	#Go to the next level, or fail...
	solver.next_level()
	time.sleep(3)
	main()

if __name__ == "__main__":
	main()

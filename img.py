from PIL import Image
import pytesseract
import solver
import string
import numpy
import sys

#Data to crop letter-bounding rectangles.
left = {6:[480, 685, 685, 480, 275, 275], 		7:[465, 675, 740, 590, 375, 240, 285]}
up = {6:[1280, 1415, 1600, 1775, 1600, 1415], 	7:[1240, 1345, 1560, 1730, 1730, 1560, 1385]}
right = {6:[600, 810, 810, 600, 395, 395], 		7:[615, 805, 840, 710, 485, 350, 395]}
down = {6:[1420, 1535, 1780, 1900, 1780, 1535], 7:[1400, 1500, 1710, 1880, 1880, 1710, 1490]}

#Checks if 3 letter words are allowed.
def nothree(img):
	img = img.crop((135, 1880, 200, 1950))
	template = Image.open("no3template.png")
	score = 0
	for y in range(img.size[1]):
		for x in range(img.size[0]):
			a = img.getpixel((x, y))
			b = template.getpixel((x, y))
			if tuple(numpy.subtract(b, (5,5,5,5))) <= a <= tuple(numpy.add(b, (5,5,5,5))):
				score += 1
	if score > 3100:
		return 1
	else:
		return 0

#Determines whether there are 6 or 7 letters used in the level by taking a small chunk near the bottom of the letter circle. 
#If there is a letter, it's 6; if not, 7 (the bottom letters in a 7 config are to the left and right of the bottom letter of a 6 config)
def sixseven(img):
	img = img.crop((480, 1775, 600, 1900))
	w, h = img.size
	blackcnt = 0
	whitecnt = 0
	for y in range(h):
		for x in range(w):
			r, g, b, a = img.getpixel((x, y))
			if r == 0 and g == 0 and b == 0:
				blackcnt += 1
			elif r == 0xff and g == 0xff and b == 0xff:
				whitecnt += 1
	blackprop = blackcnt * 1.0 / (h * w)
	whiteprop = whitecnt * 1.0 / (h * w)
	if blackprop > 0.15 or whiteprop > 0.15:
		return 6
	else:
		return 7

#Returns a list with 6/7 Image objects; each is a region containing a letter.
def getsquares(img, mode):
	crops = []
	for i in range(mode):
		crops.append(img.crop((left[mode][i], up[mode][i], right[mode][i], down[mode][i])))
	return crops

#For a letter-containing rectangle, try to "clean" it such that the letter stands out. Helps OCR read.
#This suffers if the background is too light/dark. Oops.
def clean(img):
	res = Image.new("RGB", img.size)
	w, h = res.size
	for y in range(h):
		for x in range(w):
			r,g,b,a = img.getpixel((x, y))
			if r==0 and g==0 and b==0:
				res.putpixel((x, y), 0)
			elif r==0xff and g==0xff and b==0xff:
				res.putpixel((x, y), 0)
			else:
				res.putpixel((x, y), 0xffffff)
	res.resize((w*10,h*10))
	return res

#Use tesseract to read from the letter-containing rectangles
def tessread(crops):
	res = ""
	x = 0
	goofslist = ['|','[','/','1','\xa9','@','7']
	goofs = {'i':['|', '[', '/', '1'], 'o':[u'\xa9'], 'q':['@'], 'f':['7']}
	for i in crops:
		clean(i).save("tmp{}.png".format(x), dpi = (300, 300)) #can use these img files for debugging
		x += 1
		t1 = pytesseract.image_to_string(clean(i), config = "--psm 10")
		t2 = pytesseract.image_to_string(clean(i), config = "--psm 13")
		read = t1
		if t1 == "" or t1[0] not in string.lowercase and t1[0] not in string.uppercase and t1[0] not in goofslist and t1 not in goofslist:
			read = t2
		#Account for Tesseract goofs. (i = |, q = @, etc.)
		normal = 1
		for key in goofs:
			if read[0] in goofs[key] or read in goofs[key]:
				res += key
				normal = 0
				break
		if normal:
			if read == "VV": #one more small edgecase
				res += 'w'
			else:
				res += read[0].lower()
	return res

#Gets # of letters, 3-restrict, and letters for a screenshot of an entire level. 
#Screenshot file must be supplied through command line.
if __name__ == "__main__":
	raw = Image.open(sys.argv[1])
	num = sixseven(raw)
	no3 = nothree(raw)
	test = getsquares(raw, num)
	print "Number of letters: " + str(num)
	print "No 3: " + str(no3)
	print "String: " + tessread(test)
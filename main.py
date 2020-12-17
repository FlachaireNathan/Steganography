#!/usr/bin/env python3

import lib.png as png
import argparse


# Build the argument parser with argparse
parser = argparse.ArgumentParser()
parser.add_argument("imagefile", help="image file path")
parser.add_argument("-w", "--write", help="Write hidden text in the png file", action="store_true")
parser.add_argument("-r", "--read", help="Read hidden text in image", action="store_true")
parser.add_argument("-f", "--file", help="Read text from file, need to specify the filename", type=str)
parser.add_argument("-t", "--text", help="Read text from text in argument from command line, need to specify the text", type=str)
args = parser.parse_args()



# Verify errors in commands
if (args.write and args.read):
	print("ERROR : Cannot read and write at the same time, choose only 1 option")
	exit()

if (args.text and args.file):
	print("ERROR : Cannot read text from argument and file, choose only 1 option")
	exit()


# Open image and extract data
print("Opening Image, file path: ", args.imagefile)
image = open(args.imagefile)
reader = png.Reader(filename = args.imagefile)
#r = png.Reader(file=args.imagefile)
w, h, pixels, metadata = reader.read_flat()

# Print useful information about the image
print("Image Width : ", w)
print("Image Height : ", h)
print(metadata)

textToEncode = ""

if (args.write):
	print("Write mode activated")

	# Get the text to encode
	if (args.file):
		print("Text will be extracted from the file : ", args.file)
		textfile = open(args.file)
		textToEncode = textfile.read()
	elif (args.text):
		print("Text will be extracted from the argument : ")
		textToEncode = args.text
	else:
		print("No text given, input it there : ")
		textToEncode = input()

	textToEncode += chr(3) # add the end of text symbol to know when to stop reading the text

	# Check if the text can be entirely encrypted in the image( not too long), if not it exit the programm
	if (metadata["alpha"] == True):
		if (len(pixels) < len(textToEncode)*8):
			print("ERROR : Text to encore is too long for the image given.")
			exit()
	elif(metadata["alpha"] == False):
		if len(pixels) - (len(pixels)/9) < len(textToEncode)*8:
			print("ERROR : Text to encore is too long for the image given.")
			exit()
	
	pixelIndex = 0 # Will be incremented in the loop to go trough all pixels of the image
	# Loop that will encrypt each character of the text in the image
	for c in textToEncode:
		bString = f'{ord(c):08b}'
		for b in bString:
			if (int(b) % 2) == 0:
				if (pixels[pixelIndex] % 2) == 0:
					pass
				else:
					pixels[pixelIndex] = pixels[pixelIndex]-1
			else:
				if (pixels[pixelIndex] % 2) == 0:
					pixels[pixelIndex] = pixels[pixelIndex]+1
				else:
					pass
			pixelIndex += 1
		# we need to account the non presence of the alpha canal by skipping 1 rgb code each 3 pixels (or after encrypted 8 bits)
		if (metadata["alpha"] == False):
			pixelIndex += 1

	# Save the image as output.png
	output = open('output.png', "wb")
	if "physical" in metadata:
		metadata.pop("physical")
	writer = png.Writer(w, h, **metadata)
	writer.write_array(output, pixels)
	output.close()


else:
	print("Read mode activated")

	text = "" # store the text read
	b = "" # store byte to convert into char 
	i = 0 # index of list of pixel code
	loop = True

	while(loop == True):
		# construct the bytes
		if (pixels[i] % 2) == 0:
			b += "0"
		else:
			b += "1"
		if (len(b) == 8): # if byte is complete
			# check if end of file, if yes, stop the loop else convert it into char
			if (int(b, 2) == 3):
				loop = False
			else:
				text += (chr(int(b, 2)))
				b = ""
				# if alpha, we need to skip 1 bit
				if (metadata["alpha"] == False):
					i += 1
		i += 1

	# print result
	print("\nText : \n")
	print(text)




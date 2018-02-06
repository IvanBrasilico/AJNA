# -*- coding: utf-8 -*-
''' Exemplo do site pyimagesearc de uso do tesseract OCR
'''
import argparse
from PIL import Image
from PIL import ImageFilter
import pytesseract

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, 
                default="none", help="type of preprocessing to be done")
args = vars(ap.parse_args())

# load the example image and convert it to grayscale
image = Image.open(args["image"]).convert('L') 

# check to see if we should apply thresholding to preprocess the image
if args["preprocess"] == "blur":
    image = image.filter(ImageFilter.BLUR)

# load the image as a PIL/Pillow image, apply OCR, and then delete
# the temporary file
text = pytesseract.image_to_string(image)
print(text)


from difflib import SequenceMatcher
import re
from wand.image import Image
from wand.color import Color
import os
#goes through a list and detects simular text

# import the necessary packages for pyessract
from PIL import Image
import pytesseract
import argparse
import os
import cv2

print(SequenceMatcher(None, "hello", "hello").ratio())
casesstart = [' 22nd international congress', "\s*[0-9]*\s*.[0-9]*\s*introduction"]
casesend = ["keywords:\s*(\w*\s*[,;]*)*."]
text = " panel data, production frontier, time varying, random effects, fixed effects. 1. introduction  carter and zhang (1994), wu (1995), kalirajan et al. (1996), mao and koo (1997), li and rozelle (2000), yao et al. (2001) and zhang (2002) have investigated agricultural production efficiency with sample periods preceding the high profile eighth five-year period. this paper estimates production efficiency in china™s agricultural sector with a panel data set comprising 30 provinces for the seven year period 1991-1997, which encompasses the eighth five-year period. a panel data model based on the cobb-douglas production function is used to represent the production frontier and to compute technical efficiency at the provincial level. individual effects are tested to determine if pooled estimation is preferred to unpooled (panel) estimation. the test confirms significant differences between the provinces, and hence warrants panel data estimation. both fixed and random effects models are estimated, with provincial technical inefficiency specified as province-specific intercept terms for the former, and regression disturbances for latter. although the random effects model is rejected in favour of the fixed effects model, the latter did not produce estimates with correct signs, and is rejected on economic grounds. using the random effects model, production efficiency has increased for fast and steady economic growth in china during the 1990s attracted much international attention, with the real gdp annual growth rate from 1991 to 1997 averaging over 10%. the first half of the 1990s, namely 1991-1995, was china™s eighth five-year plan. economic development during the eighth five-year period is widely seen as the most successful in prc history, during which the government increased its support for agriculture: government expenditure on agriculture accounted for 8.8% of the total, an increase of 0.4% compared with the seventh five-year period, and state bank loans to agriculture also rose from 144.9 billion yuan in 1992 to 357.2 billion yuan in 1996 in real terms. with scarce resources, economic growth depends on production efficiency improvements to achieve sustainability. as china is the world™s second largest foreign capital recipient, foreign capital plays an increasingly important role in investment. if economic growth is fuelled by investment, then an exodus or a shortage of foreign capital will render growth unsustainable. however, if growth is propelled by improvements in production efficiency, it is more likely to be sustained and to withstand reductions in production input."


for case in casesstart:
    match = re.search(case,text)
    if match:
        print(text[:match.start()])

for case in casesend:
    match = re.search(case,text)
    if match:
        print(text[match.start():match.end()-1])


'''
with Image(filename=os.path.dirname(os.path.abspath(__file__))+"/downloads/-MODSIM01-Vol 1-Abdul.pdf", resolution=300) as img:
    with img.convert('png') as converted:
        converted.save(filename='page.png')
'''

##=========== https://www.pyimagesearch.com/2017/07/10/using-tesseract-ocr-python/

imagepath = "page-0.png"
preprocess = "blur" #thresh or blur
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
	help="type of preprocessing to be done")

# load the example image and convert it to grayscale
image = cv2.imread(imagepath)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# check to see if we should apply thresholding to preprocess the
# image
if preprocess == "thresh":
    gray = cv2.threshold(gray, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# make a check to see if median blurring should be done to remove
# noise
elif preprocess == "blur":
    gray = cv2.medianBlur(gray, 3)

# write the grayscale image to disk as a temporary file so we can
# apply OCR to it
filename = "{}.png".format(os.getpid())
cv2.imwrite(filename, gray)

# load the image as a PIL/Pillow image, apply OCR, and then delete
# the temporary file
text = pytesseract.image_to_string(Image.open(filename))
os.remove(filename)
print(text)

# show the output images
cv2.imshow("Image", image)
cv2.imshow("Output", gray)
cv2.waitKey(0)

for filename in os.listdir(os.path.dirname(os.path.abspath(__file__))+"/"):
    print(filename)
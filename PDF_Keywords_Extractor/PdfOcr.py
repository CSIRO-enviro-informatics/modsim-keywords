from wand.image import Image as wandImage
from wand.color import Color
import os

# import the necessary packages for pyessract
from PIL import Image as PilImage
import pytesseract
import argparse
import os
import cv2
import PyPDF2
import io


#this tool converts pdf to text and extracts keywords
class keywordpdftotext():

    def imagetotext(self,imagepath):

        if imagepath not in os.listdir():
            return ""
        #- uses code example from https://www.pyimagesearch.com/2017/07/10/using-tesseract-ocr-python/
        #- to extract text from images

        preprocess = "blur"  # thresh or blur
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
        text = pytesseract.image_to_string(PilImage.open(filename))
        os.remove(filename)
        os.remove(imagepath)
        return text

    def pdftoimage(self, pdfpath):

        pdf = PyPDF2.PdfFileReader(open(pdfpath, "rb"))
        newpdf = PyPDF2.PdfFileWriter()
        if pdf.getNumPages() > 0:
            newpdf.addPage(pdf.getPage(0))
            pdf_bytes = io.BytesIO()
            newpdf.write(pdf_bytes)
            pdf_bytes.seek(0)


        #- this function uses wand to change pdf to images
        try:
            with wandImage(file=pdf_bytes,resolution=400) as img:
                with img.convert('png') as converted:
                    converted.save(filename='tempimg.png')
        except:
            print("error")

    def gettext(self, pdfpath):
        #-uses ocr to return pdf text
        self.pdftoimage(pdfpath)
        return self.imagetotext("tempimg.png")

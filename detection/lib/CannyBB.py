import cv2
import numpy
import ImageROI
#Based on http://www.danvk.org/2015/01/07/finding-blocks-of-text-in-an-image-using-python-opencv-and-numpy.html

#Class for detecting ROIs using Canny Image Detection

class CannyDetector:
	def __init__(self):
		pass
	def CannyBoxes(img):
                '''
                Given an image as a numpy array (PIL or opencv image) 
                find ROIs using Canny Image Detection
                Returns a list of ImageROI objects denoting ROIs found.
                '''
		#white if px >225 or near px that is >225. Black if below 200
                img = cv2.bilateralFilter(img,9,75,75)
                img=cv2.Canny(img,150,225)
                img = cv2.medianBlur(img,3)
                for i in range(1,7):
                        ker=cv2.getStructuringElement(cv2.MORPH_RECT,(i,i))
                        img=cv2.dilate(img,ker,i)
                        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, ker)
                        
                ret,thresh=cv2.threshold(img,127,255,cv2.THRESH_BINARY)
                        
                im2 ,countours, hr = cv2.findContours (img,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                areas=[]
                canvas = numpy.zeros(img.shape)
                for cntr in countours :
	                x,y,w,h=cv2.boundingRect(cntr)
                        areas.append(ImageROI(x,y,w,h,None,None,None))
                return areas
        def CannySimple(img):
                ''' 
                Takes an image and returns basic bounding boxes
                with simple countour based merge.
                '''
                preproc=self.CannyBoxes(img)
                final=ImageROI.CountourMerge(preproc)
                return final

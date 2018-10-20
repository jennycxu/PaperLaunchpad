import numpy as np
import cv2

# Documentation 
# https://docs.opencv.org/3.3.1/d4/d73/tutorial_py_contours_begin.html
# https://docs.opencv.org/3.3.1/d4/d73/tutorial_py_contours_begin.html
# https://docs.opencv.org/3.3.1/d6/d6e/group__imgproc__draw.html#ga746c0625f1781f1ffc9056259103edbc

img = cv2.imread('daniel3.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
 
ret,thresh = cv2.threshold(gray,127,255,1)
 
newimg,contours,h = cv2.findContours(gray,1,cv2.CHAIN_APPROX_SIMPLE)
# ContourApproximationModes CHAIN_APPROX_SIMPLE only stores 4 of these points
 
for cnt in contours:
    approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
    if len(approx)==5:
        print( "pentagon")
        cv2.drawContours(img,[cnt],0,255,-1)
    elif len(approx)==3:
        print( "tri")
        cv2.drawContours(img,[cnt],0,(0,255,0),-1)
    elif len(approx)==4:
        print( "square")
        cv2.drawContours(img,[cnt],0,(0,0,255),0)
        print(approx)
        img = cv2.rectangle(img,(approx[0][0][0],approx[0][0][1]),(approx[2][0][0],approx[2][0][1]),(0,255,0),3)
    elif len(approx) == 9:
        print( "half circ")
        cv2.drawContours(img,[cnt],0,(255,255,0),-1)
    elif len(approx) > 15:
        print( "circle")
        cv2.drawContours(img,[cnt],0,(0,255,255),-1)
 
cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows()

import numpy as np
import cv2
from boundingpoly import BoundingPoly

# Documentation 
# https://docs.opencv.org/3.3.1/d4/d73/tutorial_py_contours_begin.html
# https://docs.opencv.org/3.3.1/d4/d73/tutorial_py_contours_begin.html
# https://docs.opencv.org/3.3.1/d6/d6e/group__imgproc__draw.html#ga746c0625f1781f1ffc9056259103edbc

img = cv2.imread('daniel4.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
 
ret,thresh = cv2.threshold(gray,127,255,1)
 
newimg,contours,h = cv2.findContours(gray,1,cv2.CHAIN_APPROX_SIMPLE)
# ContourApproximationModes CHAIN_APPROX_SIMPLE only stores 4 of these points
 
bounding_boxes = [] 

for cnt in contours:
    approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
    if len(approx)==5:
        pass
       # print( "pentagon")
       #cv2.drawContours(img,[cnt],0,255,-1)
    elif len(approx)==3:
        pass
        #print( "tri")
        #cv2.drawContours(img,[cnt],0,(0,255,0),-1)
    elif len(approx)==4:
        #print( "square")
        #cv2.drawContours(img,[cnt],0,(0,0,255),0)
        #print(approx)
        #img = cv2.rectangle(img,(approx[0][0][0],approx[0][0][1]),(approx[2][0][0],approx[2][0][1]),(0,255,0),3)
        #img = cv2.polylines(img,approx,True,(0,255,255))
        points = []
        tuple_points = []
        for i in range(len(approx)):
            x,y = approx[i][0]
            points.append([x,y])
            tuple_points.append((x,y))
        poly = BoundingPoly(tuple_points)

        is_duplicate = False
        for i in range(len(bounding_boxes)):
            if(bounding_boxes[i].equals(poly)):
                is_duplicate = True
        if(is_duplicate is False):
            bounding_boxes.append(poly)
            # only print if large enough
            if(poly.is_valid_size()):
                pts = np.array([points], np.int32)
                pts = pts.reshape((-1,1,2))

                # figuring out valid touch area 
                top_left = poly.get_valid_shape()[0]
                bottom_right = poly.get_valid_shape()[3]

                # https://docs.opencv.org/3.1.0/d6/d6e/group__imgproc__draw.html#ga07d2f74cadcf8e305e810ce8eed13bc9
                img = cv2.rectangle(img,top_left,bottom_right,(0,255,0),-1)
                img = cv2.polylines(img,[pts],True,(0,255,255),6)
                for point in tuple_points:
                    radius = 10
                    img = cv2.circle(img,point, radius, (0,0,255), -1)
    elif len(approx) == 9:
        pass
        #print( "half circ")
        #cv2.drawContours(img,[cnt],0,(255,255,0),-1)
    elif len(approx) > 15:
        pass
       #print( "circle")
        #cv2.drawContours(img,[cnt],0,(0,255,255),-1)


cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows()


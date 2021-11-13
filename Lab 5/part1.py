import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math

################################
wCam, hCam = 640, 480
################################
 
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
 
detector = htm.handDetector(detectionCon=0.7)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
 
        # coordinate for 5 fingers
        thumbX, thumbY = lmList[4][1], lmList[4][2] #thumb
        pointerX, pointerY = lmList[8][1], lmList[8][2] #pointer
        middleX, middleY = lmList[12][1], lmList[12][2]
        ringX, ringY = lmList[16][1], lmList[16][2]
        pinkyX, pinkyY = lmList[20][1], lmList[20][2]
  
        # draw circle at the end of each finger
        cv2.circle(img, (thumbX, thumbY), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (pointerX, pointerY), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (middleX, middleY), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (ringX, ringY), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (pinkyX, pinkyY), 15, (255, 0, 255), cv2.FILLED)

        # calculate the distances for condition
        len_calc = lambda x1,y1,x2,y2: math.hypot(x2 - x1, y2 - y1)
        thumb2ring = len_calc(thumbX,thumbY,ringX,ringY)
        thumb2pinky = len_calc(thumbX,thumbY,pinkyX,pinkyY)
        thumb2pointer = len_calc(thumbX,thumbY,pointerX,pointerY)
        thumb2middle = len_calc(thumbX,thumbY,middleX,middleY)
        pointer2middle = len_calc(pointerX,pointerY,middleX,middleY)

        print(thumb2ring, thumb2pinky, thumb2pointer, thumb2pointer, pointer2middle)

        # conditions for 'Yeah' gesture
        thumb_ring_pinky_close = thumb2ring < 80 and thumb2pinky < 80
        middle_pointer_away_from_thumb = thumb2pointer > 100 and thumb2middle > 100
        pointer_away_from_middle = pointer2middle > 50

        condition = thumb_ring_pinky_close and \
            middle_pointer_away_from_thumb and \
            pointer_away_from_middle

        if condition:
            cv2.putText(img, 'Yeah', (40, 90), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 255, 255), 3)

            # take a picture of current image
            cv2.imwrite('c1.png',img)
        
    # Get the frame per second
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)
 
    cv2.imshow("Img", img)
    cv2.waitKey(1)


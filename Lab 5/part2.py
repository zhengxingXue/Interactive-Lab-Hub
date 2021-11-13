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

COLOR = (204, 153, 102) # blue color

def rps(lmList, xloc):
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
        middle2ring = len_calc(middleX,middleY,ringX, ringY)

        # print(thumb2ring, thumb2pinky, thumb2pointer, thumb2pointer, pointer2middle)

        # conditions 
        thumb_ring_pinky_close = thumb2ring < 80 and thumb2pinky < 80
        pointer_middle_ring_close = pointer2middle < 80 and middle2ring < 80

        middle_pointer_away_from_thumb = thumb2pointer > 100 and thumb2middle > 100
        ring_pinky_away_from_thumb = thumb2ring > 100 and thumb2pinky > 100

        # condition for 'scissor' gesture
        scissors_condition = thumb_ring_pinky_close and middle_pointer_away_from_thumb 

        # condition for 'rock' gesture
        rock_condition = thumb_ring_pinky_close and pointer_middle_ring_close
        
        # condition for 'paper' gesture
        paper_condition = middle_pointer_away_from_thumb and ring_pinky_away_from_thumb

        if rock_condition:
            cv2.putText(img, 'rock', (xloc, 90), cv2.FONT_HERSHEY_COMPLEX,
                1, COLOR, 3)
            return 'rock'
        elif scissors_condition:
            cv2.putText(img, 'scissor', (xloc, 90), cv2.FONT_HERSHEY_COMPLEX,
                1, COLOR, 3)
            return 'scissor'
        elif paper_condition:
            cv2.putText(img, 'paper', (xloc, 90), cv2.FONT_HERSHEY_COMPLEX,
                1, COLOR, 3)
            return 'paper'
        return None

def show_result(msg, xloc=160):
    cv2.putText(img, msg, (xloc, 90), cv2.FONT_HERSHEY_COMPLEX,
                1, COLOR, 3)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    h = detector.results.multi_hand_landmarks
    if h and len(detector.results.multi_hand_landmarks) > 1:
        lmList0_ = detector.findPosition(img, handNo=0, draw=True)
        lmList1_ = detector.findPosition(img, handNo=1, draw=True)

        # decide which hand is on the left 
        lmList0 = lmList1_ if lmList0_[4][1] > lmList1_[4][1] else lmList0_
        lmList1 = lmList0_ if lmList0_[4][1] > lmList1_[4][1] else lmList1_

        g0 = rps(lmList0, xloc=40)
        g1 = rps(lmList1, xloc=200)

        if g0 and g1:
            if g0 == g1:
                show_result('=')
            elif g0 == "rock":
                show_result('>' if g1 == 'scissor' else '<')
            elif g0 == 'paper':
                show_result('>' if g1 == 'rock' else '<')
            elif g0 == 'scissor':
                show_result('>' if g1 == 'paper' else '<')  
        
    # Get the frame per second
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)
 
    cv2.imshow("Img", img)
    cv2.waitKey(1)


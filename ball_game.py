######
#Author: ECNU虾饺
######
import cv2
import imutils
import random
import math
import time

haar_face_cascade = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")
haar_upper_body_cascade = cv2.CascadeClassifier("data/haarcascade_upperbody.xml")


video_capture = cv2.VideoCapture(0)
video_width = video_capture.get(3)
video_height = video_capture.get(4)

ballx = 0
bally = 0
ball_size = 30
direction = 0 #<0: left ; >0: right
speed = 25
hint_time = 0

real_head = [0,0,0,0] #x,y,height,width
real_body = [0,0,0,0]

inform = ""

def new_round():
    global ballx,bally,direction,head_count,body_count
    ballx = random.randint(1,1000)
    bally = 0
    dirction = 0
    head_count = 0
    body_count = 0
    
    if ballx <= 300:
        direction = 1*random.randint(0,int(math.atan((1000-ballx)/video_height)/math.pi*180))
    elif ballx >= 800:
        direction = -1*random.randint(0,int(math.atan(ballx/video_height)/math.pi*180))
    else:
        if random.uniform(-1,1) >0:
            direction = 1*random.randint(0,int(math.atan((1000-ballx)/video_height)/math.pi*180))
        else:
            direction = -1*random.randint(0,int(math.atan(ballx/video_height)/math.pi*180))
    

def ball_control():
    global ballx, bally
    bally += speed
    ballx += speed * math.tan(direction / 180 * math.pi) * 1.1
    ballx = int(ballx)
    cv2.circle(frame, (ballx,bally), ball_size, (255, 0, 0), -1)

def check_status():
    global head_count, body_count,hint_time,inform

    if real_head[3] >= 150:
        inform = "too close!"
    
    if bally > video_height*1.2:
        new_round()

    if math.sqrt((ballx - real_head[0]) ** 2 + (bally - real_head[1]) ** 2) < (ball_size + real_head[2]) or \
       math.sqrt((ballx - real_head[0]) ** 2 + (bally - real_head[1]) ** 2) <  (ball_size + real_head[3]):
        #print(str(math.sqrt((ballx - real_head[0]) ** 2 + (bally - real_head[1]) ** 2))+ " " + str ((ball_size + real_head[2])) + " " + str(ball_size + real_head[3]))
        hint_time += 1
        new_round()
    

    cv2.putText(frame, str(hint_time) + " " + inform, (20,100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 2)
    inform = ""
    

while True:
    
    ret, frame = video_capture.read()
    frame = cv2.flip(frame, 1) #图像镜面翻转

    frame = imutils.resize(frame, width=1000) # resize original video for better viewing performance
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert video to grayscale
    
    face = haar_face_cascade.detectMultiScale(
        gray,
        scaleFactor = 1.1,
        minNeighbors = 5,
        minSize = (50, 100), # Min size for valid detection, changes according to video size or body size in the video.
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    upper_body = haar_upper_body_cascade.detectMultiScale(
        gray,
        scaleFactor = 1.1,
        minNeighbors = 5,
        minSize = (50, 100), # Min size for valid detection, changes according to video size or body size in the video.
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    # Draw a rectangle around the upper bodies
    for (x, y, w, h) in upper_body:
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1) # creates green color rectangle with a thickness size of 1
        #cv2.putText(frame, str(w), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 2) # creates green color text with text size of 3 & thickness size of 2
        real_body = [int(x + w/2),int(y + h/2),h,w]

    for (x, y, w, h) in face:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1) 
        #cv2.putText(frame, str(w), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 2)
        if real_head[0] == int(x + w/2) and real_head[1] == int(y + h/2):
            real_head = [0,0,h,w]
        real_head = [int(x + w/2),int(y + h/2),h,w]

    check_status()
    ball_control()

    cv2.imshow('press \'q\' to exit', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()

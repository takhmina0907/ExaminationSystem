import numpy as np
import cv2
import os.path
face_cascade = cv2.CascadeClassifier('../cascade/haarcascade_frontalface_alt2.xml')
def create_photo(id):
    cap = cv2.VideoCapture(0)

    while 1:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        print(faces)
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            image_item = "media/student/"+id+"/image.png"
            cv2.imwrite(image_item,roi_gray)
            return image_item
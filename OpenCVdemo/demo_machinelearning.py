import numpy as np
import cv2
import arg_parser as parse
from Source import Source
import os

def main():
    print "Appuyer sur la touche ECHAP pour quitter"

    VIDEO_SOURCE = "dataset\\street.mp4"

    args = parse.parser()
    if args.input:
        if args.input == "0":
            input_video = 0
        elif args.input == "1":
            input_video = 1
        else:
            input_video = args.input
    else:
        input_video = VIDEO_SOURCE
    
    video = Source(VIDEO_SOURCE)

    car_cascade = cv2.CascadeClassifier("dataset\\cascade_15_5024.xml")
    cv2.namedWindow('Demo machine learning (ECHAP pour quitter)', cv2.WINDOW_NORMAL) 
    cv2.resizeWindow('Demo machine learning (ECHAP pour quitter)', int(video.new_size[0]), int(video.new_size[1])+48)

    while(True):

        ret, frame = video.next_frame()

        if not ret:
            print('End of video')
            break

        key = cv2.waitKey(1)

        if key == 27:
            print("Exiting...")
            break   

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cars = car_cascade.detectMultiScale(gray, 1.5, 6)

        for x,y,w,h in cars:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

        cv2.imshow("Demo machine learning (ECHAP pour quitter)", frame)


    video.release()
    cv2.destroyAllWindows()
    print "bye."

if __name__ == "__main__":
    main()
import cv2
import numpy as np
import argparse

def show_video(args):
    # create a VideoCapture object and read from input file
    cap = cv2.VideoCapture(args.rtmp_mrl)

    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            # display the resulting frame
            cv2.imshow('Pull Frame',frame)
        else: 
            break

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.release()
    
    # Closes all the frames
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--rtmp_mrl', type=str, default='rtmp://127.0.0.1:1935/live/stream')

    args = parser.parse_args()

    show_video(args)
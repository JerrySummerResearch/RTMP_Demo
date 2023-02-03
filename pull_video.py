import cv2
import numpy as np
import argparse

def show_video(args):
    # create a VideoCapture object and read from input file
    # if the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture(args.rtmp_mrl)
    
    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")
        
    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:

            # Display the resulting frame
            cv2.imshow('Pull Frame',frame)
        # Break the loop
        else: 
            break

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    
    
    # When everything done, release the video capture object
    cap.release()
    
    # Closes all the frames
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--rtmp_mrl', type=str, default='rtmp://127.0.0.1:1935/live/stream')

    args = parser.parse_args()

    show_video(args)
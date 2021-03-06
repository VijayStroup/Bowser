"""lane.py is responsible for the lane detection part of Bowser and will
determine where the lanes are and also send signals to Bowser telling it
whether it should move left or right to stay within the lines.

"""

import os
import cv2
from PIL import ImageGrab
import numpy as np
from feed import Feed


if __name__ == '__main__':
    raw_feed = 'stream'

    if raw_feed[-3:] in ['jpg', 'mp4'] and not os.path.isfile(raw_feed):
        print('feed does not exist.')
        exit(-1)

    if raw_feed[-3:] == 'jpg': # image
        feed = Feed(raw_feed, 'image')
        feed.robo_vis()
        feed.show_lanes()
    elif raw_feed[-3:] == 'mp4': # video
        cap = cv2.VideoCapture(raw_feed)
        while(cap.isOpened()):
            _, frame = cap.read()
            feed = Feed(frame, 'video')
            feed.robo_vis()
            if feed.show_lanes() == -2: break
    elif raw_feed == 'stream': # stream
        """its getting the stream of desktop from inside wsl and not whats on my windows"""
        while True:
            screen = np.array(ImageGrab.grab(bbox=(0, 0, 800, 640)))
            cv2.imshow('', cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
    else: # camera
        pass

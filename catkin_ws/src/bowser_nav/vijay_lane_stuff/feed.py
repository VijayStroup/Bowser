"""feed.py contains a class Feed that is used for all the data feed transforms
in order for Bowser to see lane markings.

"""

import cv2
import numpy as np


class Feed:
    """Class that initializes an image and then preforms transforms on the
    image to make it desirable for lane detection.

    Parameters
    ----------
    image_path : string
        Path to the feed 

    Returns
    -------
    shows image
        if you call the show_image method, the image will be shown and wait for
        a keystroke to close.

    Notes
    -----
    To determine lanes, we first convert the feed to a single channel array,
    then determine the change in pixel value intensity to show an edge.

    Examples
    --------
    >>> import cv2, numpy as np
    >>> from feed import Feed
    >>> feed = Feed('image.jpg')
    >>> feed.robo_vis()
    >>> feed.show_lanes()

    Revisions
    ---------
    2020-10-15 Vijay Stroup created Feed class with show_image and to_grey
               methods.
    2020-10-16 Vijay Stroup created to_blur, to_canny, and roi methods.
    2020-10-19 Vijay Stroup created get_lanes and show_lanes methods.
    2020-10-20 Vijay Stroup created robo_vis method.

    """

    WHITE = (255, 255, 255)
    BLUE = (255, 0, 0)

    def __init__(self, image_path):
        self.image = cv2.imread(image_path)
        self.height, self.width, _ = self.image.shape
        self.image_copy = np.copy(self.image)
        self.lanes = None

    def to_grey(self):
        """Convert the image to grey scale so our color channel will only be 1
        with values ranging from 0 to 255 to make it faster and eaiser to
        determine change in intensity of pixel values.
        
        """

        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    def to_blur(self):
        """We use a Gaussian Blur to smoothen hard edges that could give us
        false positives on edges, but keep the very dramatic average change in
        pixel values we need to see the lane markings.
        
        """

        kernal = (5, 5)
        deviation = 0

        self.image = cv2.GaussianBlur(self.image, kernal, deviation)

    def to_canny(self):
        """Canny determines the relative intensity in pixel values within a
        particular region. The Canny function preforms a derivative with
        respect to x and y - f(x, y) to determine intensity with respect to
        adjacent pixels (the gradient).

        Notes
        -----
        The underlying function cv2.Canny() preforms a Gaussian Blur.
        
        """

        low_threshold = 50
        high_threshold = 150

        self.image = cv2.Canny(self.image, low_threshold, high_threshold)

    def roi(self):
        """The region of intrest allows us to only use part of the feed to
        preform manipulations on to improve effency. The region of intrest we
        care about for our cause is just the lane Bowser is in, not the other
        side of the lane or what is to it's far right or left.
        
        Notes
        -----
        We use bitwise & with our mask and feed to only pick out the white that
        is in both our mask and our feed.

        """

        mask = self.make_mask()

        self.image = cv2.bitwise_and(self.image, mask)

    def make_mask(self):
        """To make a mask we define an array of points on our feed, and then on
        our mask, we fill in the area of our mask by our points with white as
        to use bitwise & on our mask and feed.

        Returns
        -------
        mask: tuple
            a black image with the same dimensions as the feed with white only
            in our defined roi.
        
        """

        lower_left = (0, self.height)
        lower_right = (self.width, self.height)
        middle = (self.width / 2, self.height / 2)

        points = np.array([
            [lower_left, lower_right, middle]
        ], dtype=np.int32)

        mask = np.zeros_like(self.image)
        cv2.fillPoly(mask, points, self.WHITE)

        return mask

    def get_lanes(self):
        """The Hough Space will allow us to find intersectional points of the
        different slopes from the Canny edge finder that will allow us to find
        what might be a stright line.

        Notes
        -----
        The Hough Space is a 2D array with the rows being theata in raidans and
        rho as the columns.

        """

        rho = 2
        theata = np.pi / 180
        threshold = 100 # how many intersecting points must there to be
                        # considered a stright line
        lines = np.array([])
        minLineLength = 40 # any lines detected that are less than 40px are
                           # rejected
        maxLineGap = 35 # max distance two detected lines can be a part from
                        # each other and then combine

        self.lanes = cv2.HoughLinesP(
            self.image,
            rho,
            theata,
            threshold,
            lines,
            minLineLength,
            maxLineGap
        )

    def show_lanes(self):
        """Show lanes on feed.
        
        Notes
        -----
        When preforming cv2.addWeighted, it is the same thing as doing
        cv2.bitwise_or on the two images. The weighted just lets us see the
        lanes better as it will be more prominent.

        """

        lanes_image = np.zeros_like(self.image_copy)
        
        if self.lanes is not None:
            for lane in self.lanes:
                x1, y1, x2, y2 = lane.reshape(4)
                cv2.line(lanes_image, (x1, y1), (x2, y2), self.BLUE, 5)

        lanes_overlay = cv2.addWeighted(self.image_copy, .8, lanes_image, 1, 1)
        # lanes_overlay = cv2.bitwise_or(self.image_copy, lanes_image)

        print('Press a key to exit, don\'t press the x on the window!')
        cv2.imshow('', lanes_overlay)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def show_image(self):
        """Show image and wait for keystroke."""

        print('Press a key to exit, don\'t press the x on the window!')
        cv2.imshow('', self.image)
        cv2.waitKey()
        cv2.destroyAllWindows()
    
    def robo_vis(self):
        """Call other methods to transform feed for Bowser."""

        self.to_grey()
        self.to_blur()
        self.to_canny()
        self.roi()
        self.roi()
        self.get_lanes()

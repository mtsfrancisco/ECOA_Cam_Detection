import cv2

class VideoStream:
    def __init__(self, source=0):
        """
        Initializes the video stream.
        :param source: path to the video file or camera index (default is 0 for the default camera).
        """
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise ValueError("Não foi possível abrir o vídeo ou a câmera.")
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    def read(self):
        """
        Reads the next frame from the video or camera.
        :return: (ret, frame) where ret is True if the reading was successful and frame is the read image.
        """
        ret, frame = self.cap.read()
        if not ret:
            return ret, None
        return ret, frame
    
    def release(self):
        """
        Releases the video stream/camera.
        """
        self.cap.release()
        cv2.destroyAllWindows()
    
    def display(self, frame, window_name="Video Stream"):
        """
        Displays the frame in a window.
        :param frame: frame to be displayed.
        :param window_name: name of the display window.
        """
        cv2.imshow(window_name, frame)
    
    def get_frame_dimensions(self):
        """
        Gets the dimensions of the frame.
        :return: (width, height)
        """
        return self.width, self.height

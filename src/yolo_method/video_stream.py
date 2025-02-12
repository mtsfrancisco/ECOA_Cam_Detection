import cv2

class VideoStream:
    def __init__(self, source=0):
        """
        Initializes the video stream.
        :param source: Path to video file or camera index (default=0 for webcam).
        """
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise ValueError("Não foi possível abrir o vídeo ou a câmera.")

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def read(self):
        """ 
        Reads the next frame from the video or camera.
        :return: (ret, frame) where ret is True if successful, and frame is the image read.
        """
        ret, frame = self.cap.read()
        if not ret:
            return ret, None
        return ret, frame

    def release(self):
        """
        Releases the video/camera feature.
        """
        self.cap.release()
        cv2.destroyAllWindows()

    def get_frame_dimensions(self):
        """
        Returns the dimensions of the frame (width, height).
        """
        return self.width, self.height

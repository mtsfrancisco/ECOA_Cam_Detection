import cv2

class VideoStream:
    def __init__(self, source=0):
        """
        Inicializa o fluxo de vídeo.
        :param source: Caminho para arquivo de vídeo ou índice da câmera (default=0 para webcam).
        """
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise ValueError("Não foi possível abrir o vídeo ou a câmera.")

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def read(self):
        """ 
        Lê o próximo frame do vídeo ou da câmera.
        :return: (ret, frame) onde ret é True se bem-sucedido, e frame é a imagem lida.
        """
        ret, frame = self.cap.read()
        if not ret:
            return ret, None
        return ret, frame

    def release(self):
        """
        Libera o recurso de vídeo/câmera.
        """
        self.cap.release()
        cv2.destroyAllWindows()

    def get_frame_dimensions(self):
        """
        Retorna as dimensões do frame (largura, altura).
        """
        return self.width, self.height

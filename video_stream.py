import cv2

class VideoStream:
    def __init__(self, source=0):
        """
        Inicializa o stream de vídeo.
        :param source: caminho do arquivo de vídeo ou índice da câmera (padrão é 0 para a câmera padrão).
        """
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise ValueError("Não foi possível abrir o vídeo ou a câmera.")
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    def read(self):
        """
        Lê o próximo frame do vídeo ou da câmera.
        :return: (ret, frame) onde ret é True se a leitura foi bem-sucedida e frame é a imagem lida.
        """
        ret, frame = self.cap.read()
        if not ret:
            return ret, None
        return ret, frame
    
    def release(self):
        """
        Libera o stream de vídeo/câmera.
        """
        self.cap.release()
        cv2.destroyAllWindows()
    
    def display(self, frame, window_name="Video Stream"):
        """
        Exibe o frame em uma janela.
        :param frame: frame a ser exibido.
        :param window_name: nome da janela de exibição.
        """
        cv2.imshow(window_name, frame)
    
    def get_frame_dimensions(self):
        """
        Obtém as dimensões do frame.
        :return: (largura, altura)
        """
        return self.width, self.height

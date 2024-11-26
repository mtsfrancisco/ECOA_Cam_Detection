import cv2
import numpy as np

class QuadrilateralDrawer:
    def __init__(self):
        self.current_points = []  # Pontos do quadrilátero em criação
        self.area1 = []  # Área 1 - primeiros quadriláteros
        self.area2 = []  # Área 2 - segundos quadriláteros
        self.drawing = False  # Indica se estamos em modo interativo
        self.img = np.ones((500, 800, 3), dtype=np.uint8) * 255  # Imagem base

    def mouse_callback(self, event, x, y, flags, param):
        """Callback para eventos do mouse."""
        if event == cv2.EVENT_LBUTTONDOWN:  # Clique do botão esquerdo
            self.current_points.append((x, y))  # Adiciona o ponto clicado
            if len(self.current_points) == 4:  # Finaliza o quadrilátero após 4 pontos
                if len(self.area1) < 1:  # Se não houver quadrilátero em area1
                    self.area1.append(self.current_points.copy())
                else:  # Quando area1 estiver preenchida, preenche area2
                    self.area2.append(self.current_points.copy())
                self.current_points = []  # Reseta os pontos para o próximo quadrilátero
                self.drawing = False

        elif event == cv2.EVENT_MOUSEMOVE and len(self.current_points) > 0:  # Movimento do mouse
            self.drawing = True  # Ativa o modo interativo
            self.current_point = (x, y)  # Atualiza o ponto atual do mouse

    def run(self):
        """Método principal para executar o programa."""
        cv2.namedWindow("Quadrilateral Drawer")
        cv2.setMouseCallback("Quadrilateral Drawer", self.mouse_callback)

        while True:
            temp_img = self.img.copy()  # Cópia da imagem para desenho temporário

            # Desenhar os quadriláteros em área 1
            for quadrilateral in self.area1:
                for i in range(4):
                    cv2.line(temp_img, quadrilateral[i], quadrilateral[(i + 1) % 4], (0, 0, 255), 2)

            # Desenhar os quadriláteros em área 2
            for quadrilateral in self.area2:
                for i in range(4):
                    cv2.line(temp_img, quadrilateral[i], quadrilateral[(i + 1) % 4], (0, 255, 0), 2)

            # Desenhar os pontos fixos do quadrilátero em criação
            for point in self.current_points:
                cv2.circle(temp_img, point, 5, (0, 0, 255), -1)

            # Desenhar as linhas fixas do quadrilátero em criação
            if len(self.current_points) > 1:
                for i in range(len(self.current_points) - 1):
                    cv2.line(temp_img, self.current_points[i], self.current_points[i + 1], (0, 0, 255), 2)

            # Desenhar a linha interativa
            if self.drawing and len(self.current_points) < 4:
                cv2.line(temp_img, self.current_points[-1], self.current_point, (0, 255, 0), 2)
                if len(self.current_points) == 3:  # Linha do primeiro ao terceiro ponto enquanto desenha o quarto
                    cv2.line(temp_img, self.current_points[0], self.current_point, (0, 255, 0), 2)

            cv2.imshow("Quadrilateral Drawer", temp_img)

            # Sair ao pressionar a tecla ESC
            key = cv2.waitKey(1)
            if key == 27 or len(self.area1) == 1 and len(self.area2) == 1:  # Limite de dois quadriláteros
                break

        cv2.destroyAllWindows()

# Instancia e executa o programa
if __name__ == "__main__":
    drawer = QuadrilateralDrawer()
    drawer.run()
    print(drawer.area1)
    print(drawer.area2)



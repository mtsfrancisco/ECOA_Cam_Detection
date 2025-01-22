import cv2
import os

# Cria a pasta 'people' caso ela não exista
if not os.path.exists('people'):
    os.makedirs('people')

# Inicializa a captura de vídeo da webcam
cap = cv2.VideoCapture(0)

while True:
    # Captura o frame da webcam
    ret, frame = cap.read()

    # Se a captura for bem-sucedida
    if not ret:
        print("Falha ao capturar imagem")
        break

    # Exibe o frame na janela
    cv2.imshow('Webcam', frame)

    # Espera a tecla pressionada
    key = cv2.waitKey(1) & 0xFF

    # Se a tecla 'w' for pressionada, salva a imagem
    if key == ord('w'):
        # Define o nome da imagem com a data e hora
        image_filename = os.path.join('people', 'photo.jpg')
        cv2.imwrite(image_filename, frame)
        print(f'Imagem salva como {image_filename}')

    # Se a tecla 'q' for pressionada, sai do loop
    if key == ord('q'):
        break

# Libera a captura de vídeo e fecha todas as janelas
cap.release()
cv2.destroyAllWindows()

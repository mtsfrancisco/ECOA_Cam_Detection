document.getElementById('start-camera').addEventListener('click', function() {
    let cameraContainer = document.getElementById('camera-container');
    let imageUploadContainer = document.getElementById('image-upload-container');
    let startCameraButton = document.getElementById('start-camera');

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            document.getElementById('video').srcObject = stream;
            cameraContainer.style.display = 'block';
            imageUploadContainer.style.display = 'none'; // Esconde o upload de imagem
            startCameraButton.style.display = 'none'; // Esconde o botão de ativar câmera
        })
        .catch(function(error) {
            console.error('Erro ao acessar a webcam:', error);
        });
});

document.getElementById('capture').addEventListener('click', function() {
    let canvas = document.getElementById('canvas');
    let video = document.getElementById('video');
    let capturedImageInput = document.getElementById('captured-image');
    let captureMessage = document.getElementById('capture-message');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);

    let imageData = canvas.toDataURL('image/png');
    capturedImageInput.value = imageData; // Salva a imagem no campo oculto

    captureMessage.style.display = 'block'; // Exibe mensagem de sucesso
});

document.getElementById('cancel-webcam').addEventListener('click', function() {
    let cameraContainer = document.getElementById('camera-container');
    let imageUploadContainer = document.getElementById('image-upload-container');
    let startCameraButton = document.getElementById('start-camera');
    let video = document.getElementById('video');

    // Para a transmissão da câmera
    let stream = video.srcObject;
    let tracks = stream.getTracks();
    tracks.forEach(track => track.stop());

    video.srcObject = null;
    cameraContainer.style.display = 'none';
    imageUploadContainer.style.display = 'block'; // Reexibe o campo de upload de imagem
    startCameraButton.style.display = 'block'; // Reexibe o botão de ativar câmera
});
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

// Work in progress
function initVideoStreaming() {
    const img = document.createElement('img');
    img.id = 'img';
    img.src = "{% url 'camera_setup' %}"; // Replaces {{ url_for('video_feed') }}

    const canvas = document.createElement('canvas');
    canvas.id = 'canvas';
    canvas.width = 640;
    canvas.height = 480;

    document.body.appendChild(img);
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');

    function refreshCanvas(){
        ctx.drawImage(img, 0, 0);
    }

    window.setInterval(refreshCanvas, 50);
}

// Example usage: call after page loads or camera setup
window.addEventListener('DOMContentLoaded', () => {
    initVideoStreaming();
});
function initVideoStreaming() {
    const video = document.getElementById('video');
    video.src = "/users/video_feed/";
    video.play();
}

// Initialize video streaming on page load
window.addEventListener('DOMContentLoaded', () => {
    let cameraContainer = document.getElementById('camera-container');
    let imageUploadContainer = document.getElementById('image-upload-container');
    let startCameraButton = document.getElementById('start-camera');

    cameraContainer.style.display = 'block';
    if (imageUploadContainer) imageUploadContainer.style.display = 'none'; // Hide image upload
    if (startCameraButton) startCameraButton.style.display = 'none'; // Hide start camera button

    initVideoStreaming(); // Initialize video streaming
});
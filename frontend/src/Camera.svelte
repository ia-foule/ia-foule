<script>
import { onMount, onDestroy } from 'svelte';

export let deviceId;
export let nbPerson;
let video;
let socket;

console.log('start stream!');
const IMAGE_INTERVAL_MS = 1000;

const startCounting = (video, canvas, deviceId) => {
  const socket = new WebSocket('ws://localhost/api/video-browser');
  let intervalId;

  // Connection opened
  socket.addEventListener('open', function () {

    // Start reading video from device
    navigator.mediaDevices.getUserMedia({
      audio: false,
      video: {
        deviceId,
        width: { max: 640 },
        height: { max: 480 },
      },
    }).then(function (stream) {
      video.srcObject = stream;
      video.play().then(() => {
        // Adapt overlay canvas size to the video size
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Send an image in the WebSocket every 42 ms
        intervalId = setInterval(() => {
          // Create a virtual canvas to draw current video image
          const ctx = canvas.getContext('2d');
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          ctx.drawImage(video, 0, 0);

          // Convert it to JPEG and send it to the WebSocket
          canvas.toBlob((blob) => socket.send(blob), 'image/jpeg');
        }, IMAGE_INTERVAL_MS);
      });
    });
  });

  // Listen for messages
  socket.addEventListener('message', function (event) {
    nbPerson = event.data;
    console.log(nbPerson)
  });

  // Stop the interval and video reading on close
  socket.addEventListener('close', function () {
    window.clearInterval(intervalId);
    video.pause();
  });

  return socket;
};

onMount( () => {
  var canvas = document.createElement('canvas');
  // Close previous socket is there is one
  if (socket) {
    socket.close();
  }
  socket = startCounting(video, canvas, deviceId);
});

onDestroy( () => {
  socket.close();
  video.pause();
})
</script>

<div class="container">
  <div>
    <video
      bind:this={video}>
      <track kind="captions"/></video>
  </div>
</div>

<script>
import { onMount, onDestroy } from 'svelte';

export let deviceId;
export let nbPerson;
export let display;

export let density;
// boolean parameter to get bounding boxes from a detector
export let detection;
// boolean parameter to fuse detection and count model
export let fusion;

let video;
let socket;

console.log('start stream!');
const IMAGE_INTERVAL_MS = 42;

const startCounting = (video, deviceId) => {
  socket = new WebSocket('ws://localhost/api/video-browser');
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
        // Send an image in the WebSocket every 42 ms
        intervalId = setInterval(() => {
          // Create a virtual canvas to draw current video image
          display.drawFromVideo(video)

          // Convert it to JPEG and send it to the WebSocket
          display.toBlob((blob) => socket.send(blob), 'image/jpeg');

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
  // Close previous socket is there is one
  if (socket) {
    socket.close();
  }
  socket = startCounting(video, deviceId);
});

onDestroy( () => {
  socket.close();
  video.pause();
})
</script>

<div class="container">
  <div>
    <video
      width = 200
      bind:this={video}>
      <track kind="captions"/></video>
  </div>
</div>
<style>
video {
  object-fit:cover;
}
</style>

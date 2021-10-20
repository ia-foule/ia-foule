<script>
import { onMount, onDestroy } from 'svelte';

export let nbPerson;
export let canvas;
let video;
let socket;
var ctx = canvas.getContext("2d");
const PING_INTERVAL_MS = 1000; // Ping every 1 s


async function draw(url) {
    var img = new Image();
    //ctx.clearRect(0, 0, canvas.width, canvas.height) // clear canvas
    //ctx.drawImage(img, 0, 0, img.naturalWidth, img.naturalHeight);
    img.onload = function() {
      // get the scale
      var scale = Math.min(canvas.width / img.width, canvas.height / img.height);
      // get the top left position of the image
      var x = (canvas.width / 2) - (img.width / 2) * scale;
      var y = (canvas.height / 2) - (img.height / 2) * scale;
      ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
    };
    img.src = url;
}

const startCounting = () => {
  socket = new WebSocket('ws://localhost/api/video-server');
  let intervalId;
  // Connection opened
  socket.addEventListener('open', function () {
    intervalId = setInterval(() => {
      socket.send('ping');
    }, PING_INTERVAL_MS);
    });

    // Listen for messages
    socket.addEventListener('message', function (event) {
      console.log('ws message')
      if (event.data instanceof Blob) {
        draw(URL.createObjectURL( event.data ) )
        URL.revokeObjectURL(event.data)
        //img.src = URL.createObjectURL( new Blob( [ event.data ] ) );
      } else {
        nbPerson = event.data;
      }
    });

  // Stop the interval and video reading on close
  socket.addEventListener('close', function () {
    window.clearInterval(intervalId);
  });

  return socket;
};

onMount( () => {
  // Close previous socket is there is one
  if (socket) {
    socket.close();
  }
  socket = startCounting();
});

onDestroy( () => {
  socket.close();
})
</script>

<style>
video {
  object-fit:cover;
}
</style>

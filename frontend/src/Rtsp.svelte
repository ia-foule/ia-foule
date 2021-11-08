<script>
import { onMount, onDestroy } from 'svelte';

export let nbPerson;
export let display;
// boolean parameter to get crowd density
export let density;
let video;
let socket;
const PING_INTERVAL_MS = 1000; // Ping every 1 s

const startCounting = () => {
  socket = new WebSocket(`ws://localhost/api/video-server?density=${density}`);
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
        display.drawFromImg(URL.createObjectURL( event.data ))
        URL.revokeObjectURL(event.data)
        //img.src = URL.createObjectURL( new Blob( [ event.data ] ) );
      } else {
        if (event.data.length < 5) {
          nbPerson = event.data;
        } else {
          display.drawDensity('data:image/png;base64,' + event.data, nbPerson)
        }
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

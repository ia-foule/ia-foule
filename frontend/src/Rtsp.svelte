<script>
import { onMount, onDestroy } from 'svelte';

export let nbPerson;
export let display;
// boolean parameter to get crowd density
export let density;
export let detection;
export let fusion;
let video;
let socket;
const PING_INTERVAL_MS = 500; // Ping every 0.5s

const startCounting = () => {
  socket = new WebSocket(`ws://localhost/api/video-server?density=${density}&detection=${detection}&fusion=${fusion}`);
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
      } else {
        const result = JSON.parse(event.data)
        if (result.hasOwnProperty("nb_person")) {
          nbPerson = result.nb_person
        }
        if (density === true && result.hasOwnProperty("url")) {
          display.drawDensity('data:imasge/png;base64,' + result.url,
            result.nb_person_counted || result.nb_person)
        }
        if (detection === true  && result.hasOwnProperty("bboxes")) {
          display.drawBox(result.bboxes, result.width, result.height)
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

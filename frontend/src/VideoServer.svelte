<script>
  import { onMount, onDestroy } from 'svelte';
  console.log('VideoServer')
  export let nbPerson;
  export let display;
  var ctx = canvas.getContext("2d");


  let socket;
  let intervalId;
  const IMAGE_INTERVAL_MS = 1000; // Asks for 12 frames per seconds

onMount( async () => {
  socket = new WebSocket('ws://localhost/api/video-server');

  // Connection opened
  socket.addEventListener('open', function () {
    console.log("ws open");
        // Send an image in the WebSocket every 42 ms
    intervalId = setInterval(() => {
      // Convert it to JPEG and send it to the WebSocket
      //console.log("ask for new frame in frontend!");
       socket.send("frame");
    }, IMAGE_INTERVAL_MS);
    });
  // Listen for messages
  socket.addEventListener('message', function (event) {
    console.log('ws message')
    if (event.data instanceof Blob) {
      display.drawFromImg(URL.createObjectURL( event.data ))
      URL.revokeObjectURL(event.data)
      //img.src = URL.createObjectURL( new Blob( [ event.data ] ) );
    } else {
      nbPerson = event.data;
    }
  });

  // Stop the interval
  socket.addEventListener('close', function () {
    console.log('ws close')
    window.clearInterval(intervalId);
  });
});

onDestroy( () => {
  //socket.close();
  window.clearInterval(intervalId);
})
</script>

<style>
</style>

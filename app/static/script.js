const IMAGE_INTERVAL_MS = 84; // Asks for 12 frames per seconds

const drawFaceRectangles = (img, canvas, faces) => {
  const ctx = canvas.getContext('2d');
  ctx.width = img.width;
  ctx.height = img.height;
  ctx.beginPath();
  ctx.clearRect(0, 0, ctx.width, ctx.height);
  for (const [x, y, width, height] of faces.faces) {
    ctx.strokeStyle = "#49fb35";
    ctx.beginPath();
    ctx.rect(x, y, width, height);
    ctx.stroke();
  }
};

const startFaceDetection = (img, canvas, deviceId) => {
  const socket = new WebSocket('ws://localhost:7000/face-detection');
  //socket.binaryType = 'arraybuffer';
  let intervalId;

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
    const img = document.getElementById( "photo" );
    const canvas = document.getElementById('canvas');
    canvas.width = img.width;
    canvas.height = img.height;

    if (event.data instanceof Blob) {
      img.src = URL.createObjectURL( event.data ) ;
      URL.revokeObjectURL(event.data)
      //img.src = URL.createObjectURL( new Blob( [ event.data ] ) );
    } else {
        // json frame
        img.onload = drawFaceRectangles(img, canvas, JSON.parse(event.data));
    }
  });


  // Stop the interval and video reading on close
  socket.addEventListener('close', function () {
    window.clearInterval(intervalId);
  });

  return socket;
};

window.addEventListener('DOMContentLoaded', (event) => {
  const img = document.getElementById( "photo" );
  const canvas = document.getElementById('canvas');
  const cameraSelect = document.getElementById('camera-select');
  let socket;

  // List available cameras and fill select
  navigator.mediaDevices.enumerateDevices().then((devices) => {
    console.log(devices)
    for (const device of devices) {
      if (device.kind === 'videoinput' && device.deviceId) {
        const deviceOption = document.createElement('option');
        deviceOption.value = device.deviceId;
        deviceOption.innerText = device.label;
        cameraSelect.appendChild(deviceOption);
      }
    }
  });

  // Start face detection on the selected camera on submit
  document.getElementById('form-connect').addEventListener('submit', (event) => {
    console.log('ws submit')
    event.preventDefault();

    // Close previous socket is there is one
    if (socket) {
      socket.close();
    }

    const deviceId = cameraSelect.selectedOptions[0].value;
    socket = startFaceDetection(img, canvas, deviceId);
  });

});

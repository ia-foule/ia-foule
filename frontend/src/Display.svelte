<script>
  import { onMount, onDestroy } from 'svelte';

  export let density
  // Input Image
  let canvasI;
  let ctxI;

  // Density map
  let canvasD;
  let ctxD;

  onMount( () => {
    ctxI = canvasI.getContext("2d")
    ctxD = canvasD.getContext("2d")
    //drawDensity('https://upload.wikimedia.org/wikipedia/commons/b/b6/Felis_catus-cat_on_snow.jpg')
  });

  // Function to parse csv file to array, for density map.
  // TODO: backend return height and width to construct Uint8ClampedArray directly...
  function csvToArray (csv) {
      const rows = csv.split("\n");
      return rows.map(function (row) {
      	return row.split(",");
      });
  };

  async function  draw(url, ctx, canvas) {
    ctx.clearRect(0, 0, canvas.width, canvas.height) // clear canvas
    var img = new Image();
    img.onload = function() {
      // get the scale
      var scale = Math.min(canvas.width / img.width, canvas.height / img.height);
      // get the top left position of the image
      var dx = (canvas.width / 2) - (img.width / 2) * scale;
      var dy = (canvas.height / 2) - (img.height / 2) * scale;
      var dWidth = img.width * scale
      var dHeight = img.height * scale
      ctx.drawImage(img, dx, dy, dWidth, dHeight);
      // without scaling
      //ctxI.drawImage(img, 0, 0, img.width,    img.height,     // source rectangle
      //           0, 0, canvasI.width, canvasI.height); // destination rectangle
    };
    img.src = url;
  }

  export function drawInput(url) {
    draw(url, ctxI, canvasI)
  }

  export function drawDensity(density_map) {
    // density_map is an 2Darray
    density_map = csvToArray(density_map)
    var width = density_map[0].length
    var height = density_map.length
    console.log(width, height);
    console.log(density_map[0])
    var buffer = new Uint8ClampedArray(width * height * 4);
    for(var y = 0; y < height; y++) {
    for(var x = 0; x < width; x++) {
        var pos = (y * width + x) * 4; // position in buffer based on x and y
        buffer[pos  ] = density_map[y][x];           // some R value [0, 255]
        buffer[pos+1] = 0;           // some G value
        buffer[pos+2] = 0;           // some B value
        buffer[pos+3] = density_map[y][x] > 0 ? 255: 0;           // set alpha channel
        }
    }
    // Initialize a new ImageData object
    let imageData = new ImageData(buffer, width , height);
    var scale = Math.min(canvasD.width / width, canvasD.height / height);
    // get the top left position of the image
    var dx = (canvasD.width / 2) - (width / 2) * scale;
    var dy = (canvasD.height / 2) - (height / 2) * scale;
    var dirtyWidth = width * scale
    var dirtyHeight = height * scale
    ctxD.putImageData(imageData, dx, dy, dirtyWidth, dirtyHeight);

    //var dataUri = canvasD.toDataURL();
    //draw(dataUri, ctxD, canvasD)
  }

  export function adjust(dx, dy) {
    canvasI.width = dx;
    canvasI.height = dy;
    ctxI.filter = 'grayscale(1)'; // reduce dimension
  }
  // *** Wrappers of html methods to avoid to export it  ***

  // Wrapper of drawImage
  export function drawImage(video, dx=0, dy=0, dWidth=0, dHeight=0) {
    ctxI.drawImage(video, dx, dy, dWidth, dHeight);
  }

  // Wrapper of toBlob
  export function toBlob(callback, type) {
    return canvasI.toBlob(callback, type)
  }

</script>

<div style="position: relative;">
  <canvas class="image input" width="1000" height="600" bind:this={canvasI}/>
  <canvas class="image density" width="1000" height="600" bind:this={canvasD}/>
</div>

<style>
  .image {
    border: 1px solid #d3d3d3;
    object-fit: cover;
    width: 100%;
    height: auto;
    position: absolute;
    left: 0;
    top: 0;
  }

  .input {
    z-index: 0;
    background-color: black;
  }

  .density {
    z-index: 1;
    opacity:0.5;

    }

</style>

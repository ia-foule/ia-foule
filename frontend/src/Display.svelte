<script>
  import { onMount, onDestroy } from 'svelte';

  let canvas;
  let ctx;

  onMount( () => ctx = canvas.getContext("2d"));


  export async function drawInput(url) {
      ctx.clearRect(0, 0, canvas.width, canvas.height) // clear canvas
      var img = new Image();
      img.onload = function() {
        // get the scale
        var scale = Math.min(canvas.width / img.width, canvas.height / img.height);
        // get the top left position of the image
        var dx = (canvas.width / 2) - (img.width / 2) * scale;
        var dy = (canvas.height / 2) - (img.height / 2) * scale;
        var dWidth = img.width * scale
        var sWidth = img.height * scale
        ctx.drawImage(img, dx, dy, dWidth, sWidth);
        // without scaling
        //ctx.drawImage(img, 0, 0, img.width,    img.height,     // source rectangle
        //           0, 0, canvas.width, canvas.height); // destination rectangle
      };
      img.src = url;
  }

  export function adjust(dx, dy) {
    canvas.width = dx;
    canvas.height = dy;
    ctx.filter = 'grayscale(1)'; // reduce dimension
  }
  // *** Wrappers of html methods to avoid to export it  ***

  // Wrapper of drawImage
  export function drawImage(video, dx=0, dy=0, dWidth=0, dHeight=0) {
    ctx.drawImage(video, dx, dy, dWidth, dHeight);
  }

  // Wrapper of toBlob
  export function toBlob(callback, type) {
    return canvas.toBlob(callback, type)
  }
</script>

<canvas id="input-image" width="1000" height="600" bind:this={canvas}/>
<style>
  #input-image {
    border: 1px solid #d3d3d3;
    object-fit: cover;
    background-color: black;
    width: 100%;
    height: auto;
  }
</style>

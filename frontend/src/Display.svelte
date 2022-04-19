<script>
  import { onMount, onDestroy } from 'svelte';
  export let detection;
  export let density;
  $: console.log('density : ' + density);
  // Input Image
  let canvasI;
  let ctxI;

  // Density map
  let canvasD;
  let ctxD;

  // Bboxes
  let canvasB;
  let ctxB;

  onMount( () => {
    ctxI = canvasI.getContext("2d")
    ctxD = canvasD.getContext("2d")
    ctxB = canvasB.getContext("2d")
    // **** For debugging ****/
    //const bboxes = [{'x1': 74, 'y1': 89, 'x2': 181, 'y2': 308, 'class_name': 'accordion', 'confidence': 0.99},
    //              {'x1': 435, 'y1': 280, 'x2': 540, 'y2': 605, 'class_name': 'accordion', 'confidence': 0.97}]
    //drawBox(bboxes, 1000, 500)
    //drawDensity('https://upload.wikimedia.org/wikipedia/commons/b/b6/Felis_catus-cat_on_snow.jpg')
  });

  function computeScale(canvasW, canvasH, imgW, imgH) {
    // Compute a scale to make the html element (image or video) to fit in the
    // canvas
    var scale = Math.min(canvasW / imgW, canvasH / imgH);
    // get the top left position of the image
    var dx = (canvasW / 2) - (imgW / 2) * scale;
    var dy = (canvasH / 2) - (imgH / 2) * scale;
    var dWidth = imgW * scale
    var dHeight = imgH * scale
    return [dx, dy, dWidth, dHeight]
  }


  async function  draw(url, ctx, canvas, callback=()=>void 0) {
    var img = new Image();
    img.onload = function() {
      // get the scale
      let [dx, dy, dWidth, dHeight] = computeScale(canvas.width, canvas.height, img.width, img.height);
      ctx.drawImage(img, dx, dy, dWidth, dHeight);
      callback()
    };
    img.src = url;
  }
  export function cleanAllCanvas() {
    ctxI.clearRect(0, 0, canvasI.width, canvasI.height)
    ctxB.clearRect(0, 0, canvasB.width, canvasB.height)
    ctxD.clearRect(0, 0, canvasD.width, canvasD.height)
  }

  export function drawFromImg(url) {
    // Clear all canvas
    ctxI.clearRect(0, 0, canvasI.width, canvasI.height)
    ctxB.clearRect(0, 0, canvasB.width, canvasB.height)
    ctxD.clearRect(0, 0, canvasD.width, canvasD.height)
    draw(url, ctxI, canvasI)
  }

  export function drawFromVideo(video) {
    // Clear all canvas
    ctxI.clearRect(0, 0, canvasI.width, canvasI.height)
    ctxB.clearRect(0, 0, canvasB.width, canvasB.height)
    ctxD.clearRect(0, 0, canvasD.width, canvasD.height)
    let [dx, dy, dWidth, dHeight] = computeScale(canvasI.width, canvasI.height, video.videoWidth, video.videoHeight);
    ctxI.drawImage(video, dx, dy, dWidth, dHeight);
  }

  export function drawDensity(url, nbPerson) {
    ctxD.clearRect(0, 0, canvasD.width, canvasD.height)
    const callback = () => {
      ctxD.font = '35px serif';
      ctxD.fillStyle = "red";
      ctxD.fillText(nbPerson + (nbPerson <= 1 ? ' personne' : ' personnes'), 10, canvasD.height - 10);
    }
    draw(url, ctxD, canvasD, callback)
  }

  export function adjust(dx, dy) {
    canvasI.width = dx;
    canvasI.height = dy;
    ctxI.filter = 'grayscale(1)'; // reduce dimension
  }

  export function drawBox(bboxes, width, height) { // bboxes + image shape
    ctxB.clearRect(0, 0, canvasB.width, canvasB.height);
    var scale = Math.min(canvasB.width / width, canvasB.height / height);
    var dx = (canvasB.width / 2) - (width / 2) * scale;
    var dy = (canvasB.height / 2) - (height / 2) * scale;
    ctxB.strokeStyle = "green";
    ctxB.lineWidth = 5;

    bboxes.map(bbox => {
      var x = dx + bbox['x1'] * scale
      var y = dy + bbox['y1'] * scale
      var w = (bbox['x2'] - bbox['x1']) * scale
      var h = (bbox['y2'] - bbox['y1']) * scale
      ctxB.strokeRect(x, y, w, h);
    })
    ctxB.font = '35px serif';
    ctxB.fillStyle = "green";
    ctxB.fillText(bboxes.length + (bboxes.length <= 1 ? ' personne' : ' personnes'), 10, 50);
  }
  // *** Wrappers of html methods to avoid to export it  ***

  // Wrapper of toBlob
  export function toBlob(callback, type) {
    return canvasI.toBlob(callback, type)
  }

</script>

<div style="position: relative;">
  <canvas
    class="image input"
    width="1000" height="600"
    bind:this={canvasI}>
  </canvas>

  <canvas
    class="image density"
    width="1000" height="600"
    bind:this={canvasD}
    style="visibility: {density===true ? 'visible':'hidden'}">
  </canvas>

  <canvas
    class="image bbox"
    width="1000" height="600"
    bind:this={canvasB}
    style="visibility: {detection===true ? 'visible':'hidden'}">
  </canvas>

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
    opacity:1;
    }

  .bbox {
    z-index: 2;
    opacity:0.9;
    }
</style>

<script>
  import { onMount, onDestroy } from 'svelte';

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
    ctxB.clearRect(0, 0, canvasB.width, canvasB.height) // clear canvas
    ctxD.clearRect(0, 0, canvasD.width, canvasD.height) // clear canvas
    draw(url, ctxI, canvasI)
  }

  export function drawDensity(url) {
    draw(url, ctxD, canvasD)
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
    console.log(bboxes.length);
    ctxB.fillText(bboxes.length + ' person', 10, 50);
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
  <canvas class="image bbox" width="1000" height="600" bind:this={canvasB}/>
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

  .bbox {
    z-index: 2;
    opacity:0.9;
    }
</style>

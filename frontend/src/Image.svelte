<script>
  import { onMount } from 'svelte';
  console.log('Image')
  export let nbPerson;
  export let canvas
  let promise = new Promise(() => {})

  var ctx = canvas.getContext("2d");
  let url;


  async function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height) // clear canvas
      var img = new Image();
      img.onload = function() {
        // get the scale
        var scale = Math.min(canvas.width / img.width, canvas.height / img.height);
        // get the top left position of the image
        var x = (canvas.width / 2) - (img.width / 2) * scale;
        var y = (canvas.height / 2) - (img.height / 2) * scale;
        ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
        // without scaling
        //ctx.drawImage(img, 0, 0, img.width,    img.height,     // source rectangle
        //           0, 0, canvas.width, canvas.height); // destination rectangle
      };
      img.src = url;
  }


  const onUrlCopied = async () => {
    draw()
    let response = await fetch(`/api/prediction/?url=${url}`)
    let result = await response.json();
    nbPerson = result.nb_person
  }

  const onFileSelected = async (e) => {
    let image = e.target.files[0];
    let reader = new FileReader();
    reader.readAsDataURL(image);
    reader.onload = e => {
         url = e.target.result
         draw()
       };
   let data = new FormData()
   data.append('file', image)
   promise = predictOnImage(data);
  }

  // fetch function
  async function predictOnImage(data) {
    let response = await fetch(`/api/image/`, {
            method: "POST",
            body: data
          })
		if (response.ok) {
      let result = await response.json();
      nbPerson = result.nb_person
			return result;
		} else {
			throw new Error(response.statusText);
		}
	}

</script>


<input bind:value={url} placeholder="Coller une url"on:change={onUrlCopied}>
<input  type="file" accept=".jpg, .jpeg, .png" on:change={(e)=>onFileSelected(e)} >

{#await promise}
{:catch error}
  <p style="color: red">{error.message}</p>
{/await}

<style>
</style>

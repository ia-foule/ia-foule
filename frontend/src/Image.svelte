<script>
  import { onMount } from 'svelte';
  console.log('Image')
  export let nbPerson;
  export let canvas
  var ctx = canvas.getContext("2d");
  let url;


  async function draw() {
      var img = new Image(500,300);
      ctx.drawImage(img, 0, 0)//, img.naturalWidth, img.naturalHeight);
      img.onload = function() {
        ctx.drawImage(img, 0, 0);
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
   let response = await fetch(`/api/image/`, {
           method: "POST",
           body: data
         })
   let result = await response.json();
   nbPerson = result.nb_person
  }

  let response;

</script>


<input bind:value={url} placeholder="Coller une url"on:change={onUrlCopied}>
<input  type="file" accept=".jpg, .jpeg, .png" on:change={(e)=>onFileSelected(e)} >


<style>
</style>

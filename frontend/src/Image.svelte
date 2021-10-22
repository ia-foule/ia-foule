<script>
  import { onMount } from 'svelte';
  console.log('Image')
  export let nbPerson;
  export let display;
  let promise = new Promise(() => {})
  let url;

  const onUrlCopied = async () => {
    display.drawInput(url)
    let response = await fetch(`/api/prediction/?url=${url}`)
    // Suppose get the density map
    //ctx.globalAlpha = 0.0;
    //draw('https://upload.wikimedia.org/wikipedia/commons/b/b6/Felis_catus-cat_on_snow.jpg')
    let result = await response.json();
    nbPerson = result.nb_person
  }

  const onFileSelected = async (e) => {
    let image = e.target.files[0];
    let reader = new FileReader();
    reader.readAsDataURL(image);
    reader.onload = e => {
         url = e.target.result
         display.drawInput(url)
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

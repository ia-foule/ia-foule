<script>
  import { onMount } from 'svelte';
  // input image component
  export let display;
  // ouptut
  export let nbPerson;
  // boolean parameter to get crowd density
  export let density;
  // boolean parameter to get bounding boxes from a detector
  export let detection;
  // boolean parameter to fuse detection and count model
  export let fusion;

  let promise = new Promise(() => {})
  let url; //='https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Crowd_Tokyo.jpg/1280px-Crowd_Tokyo.jpg';

  const onUrlCopied = async () => {
    display.cleanAllCanvas()
    display.drawFromImg(url)
    let response = await fetch(`/api/prediction/?url=${url}&density=${density}&detection=${detection}&fusion=${fusion}`)
    let result = await response.json();
    nbPerson = result.nb_person
    if (density === true) {//&& ('density_map' in result) {
      //display.drawDensity(result.density_map)
      display.drawDensity('data:image/png;base64,' + result.url,
        result.nb_person_counted || result.nb_person)
    }
    if (detection === true) {//&& ('density_map' in result) {
      //display.drawDensity(result.density_map)
      display.drawBox(result.bboxes, result.width, result.height)
    }
  }

  const onFileSelected = async (e) => {
    display.cleanAllCanvas()
    let image = e.target.files[0];
    let reader = new FileReader();
    reader.readAsDataURL(image);
    reader.onload = e => {
         url = e.target.result
         display.drawFromImg(url)
       };
   let data = new FormData()
   data.append('file', image)
   promise = predictOnImage(data);
  }

  // fetch function
  async function predictOnImage(data) {
    let response = await fetch(`/api/image/?density=${density}&detection=${detection}&fusion=${fusion}`, {
            method: "POST",
            body: data
          })
		if (response.ok) {
      let result = await response.json();
      nbPerson = result.nb_person
      if (density === true) {
        display.drawDensity('data:image/png;base64,' + result.url,
          result.nb_person_counted || result.nb_person)
      }
      if (detection === true) {
        display.drawBox(result.bboxes, result.width, result.height)
      }
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

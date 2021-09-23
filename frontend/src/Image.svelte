<script>
  import { onMount } from 'svelte';
  console.log('Image')
  export let nbPerson;
  let url;

  const onUrlCopied = async () => {
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

{#if url !== undefined}
  <img src={url}/>
{/if}

<input bind:value={url} placeholder="Coller une url"on:change={onUrlCopied}>
<input  type="file" accept=".jpg, .jpeg, .png" on:change={(e)=>onFileSelected(e)} >


<style>
img {
  width:500;
  }
</style>

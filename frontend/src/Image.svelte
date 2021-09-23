<script>
import { onMount } from 'svelte';

export let url;
export let nbPerson;
let response;
onMount(async () => {
  response = await fetch(`/api/prediction/?url=${url}`).then(
    r => r.json()
  );
  nbPerson = response.nb_person
});

</script>

<img src={url}/>

<style>
img {
  width:500;
  }
</style>

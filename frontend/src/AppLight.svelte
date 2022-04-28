<script>

	import Rtsp from './Rtsp.svelte';

	import Display from './Display.svelte';

	let selected;
	let density=true; // If density map is needed
	let detection=false; // If detection bboxes is needed
	let fusion=false; // The model type

	let isSubmit=false;

	let nbPerson;

	let display; // the display component where result image is drawn
	function handleChange() {
		console.log(selected);
		isSubmit = false
		display.cleanAllCanvas()
	}

	async function handleSubmit() {
		isSubmit = !isSubmit
		console.log(isSubmit);

	}
</script>


<svelte:head>
	<title>Ia-foule</title>
</svelte:head>

<div class="wrapper">

<Rtsp bind:nbPerson={nbPerson} {display} {density} {detection} {fusion}/>

<main>
	{#if nbPerson !== undefined }
		<h2> {nbPerson} {nbPerson <= 1 ? 'personne' : 'personnes'}</h2>
	{/if}
	<Display bind:this={display} {density} {detection} writeCount={false}/>
</main>



</div>
<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 75%;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	/*------ Asides ------*/

	.wrapper {
	  display: flex;
	  flex-flow: row wrap;
	  font-weight: bold;
	  text-align: center;
	}

	.wrapper > * {
	  padding: 10px;
	  flex: 1 100%;
	}

	@media (min-width: 640px) {
   main    { flex: 3 0px; }
   main    { order: 1; }
  .footer  { order: 2; }
}
</style>

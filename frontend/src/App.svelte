<script>
	import Camera from './Camera.svelte';
	import Image from './Image.svelte';
	import Video from './Video.svelte';

	let options = [
	{ id: 1, text: `Video (Depuis le navigateur)`, needUrl: false, needFile:true, class: `Video` },
	// not implemented
	{ id: 2, text: `Video (Depuis le serveur)`, needUrl: true, needFile:false, class: `VideoServer` },
	{ id: 3, text: `Image (Depuis le navigateur)`, needUrl: true, needFile:true, class: `Image` },
	// not implemented
	{ id: 4, text: `Rtsp (Depuis le serveur)`, needUrl: false, needFile:false,class: `Rtsp` }
	];

	// Add video device of the client
	navigator.mediaDevices.enumerateDevices().then((devices) => {
		for (const device of devices) {
			if (device.kind === 'videoinput' && device.deviceId) {
				const option = { id: device.deviceId, text: device.label, needUrl: false,needFile:false, class: `Camera` }
				options = [...options, option];
			}
		}
	});

	let selected;

	let isSubmit=false;

	let nbPerson;

	let canvas; // the canvas where result image is drawn
	function handleChange() {
		console.log(selected);
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

<aside class="aside aside-1">
<form on:submit|preventDefault={handleSubmit}>
	<select bind:value={selected} on:change={handleChange}>
		{#each options as option}
			<option value={option}>
				{option.text}
			</option>
		{/each}
	</select>

	<button type=submit>
		Go
	</button>
</form>

{#if isSubmit === true }
	{#if selected.class === 'Image'}
		<Image bind:nbPerson={nbPerson} {canvas}/>
	{:else if selected.class === 'Camera' }
		<Camera deviceId={selected.id} bind:nbPerson={nbPerson}/>
	{:else if selected.class === 'Video' }
		<Video  bind:nbPerson={nbPerson}/>
	{/if}
{/if}
</aside>

<aside class="aside aside-2">
{#if nbPerson }
	<p> {nbPerson} personnes </p>
{/if}
</aside>

<main>
<canvas id="result-image" width="500" height="300" bind:this={canvas}/>
</main>
</div>
<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}



	img {
		width:500;
		}

	#result-image {
	}
	/*------ Asides ------*/

	.wrapper {
	  display: flex;
	  /*flex-flow: row wrap;*/
	  font-weight: bold;
	  text-align: center;
	}

	.wrapper > * {
	  padding: 10px;
	  flex: 1 100%;
	}
	.aside-1 {
	  background: white;
	}

	.aside-2 {
	  background: white;
	}
	@media (min-width: 640px) {
   main    { flex: 3 0px; }
  .aside-1 { order: 1; }
   main    { order: 2; }
  .aside-2 { order: 3; }
  .footer  { order: 4; }
}
</style>

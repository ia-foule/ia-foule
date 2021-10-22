<script>
	import Camera from './Camera.svelte';
	import Image from './Image.svelte';
	import Video from './Video.svelte';
	import VideoServer from './VideoServer.svelte';
	import Rtsp from './Rtsp.svelte';

	import Display from './Display.svelte';

	let options = [
	{ id: 1, text: `Video (Depuis le navigateur)`, class: `Video` },
	//{ id: 2, text: `Video (Depuis le serveur)`,  class: `VideoServer` },
	{ id: 2, text: `Image (Depuis le navigateur)`, class: `Image` },
	// not implemented
	{ id: 3, text: `Rtsp (Depuis le serveur)`, class: `Rtsp` }
	];

	// Add video device of the client
	navigator.mediaDevices.enumerateDevices().then((devices) => {
		for (const device of devices) {
			if (device.kind === 'videoinput' && device.deviceId) {
				const option = { id: device.deviceId, text: device.label, class: `Camera` }
				options = [...options, option];
			}
		}
	});

	let selected;

	let isSubmit=false;

	let nbPerson;

	let display; // the display where result image is drawn
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
		{@html isSubmit? "Stop" : "Go"}
	</button>
</form>

{#if isSubmit === true }
	{#if selected.class === 'Image'}
		<Image bind:nbPerson={nbPerson} {display}/>
	{:else if selected.class === 'Camera' }
		<Camera deviceId={selected.id} bind:nbPerson={nbPerson} {display}/>
	{:else if selected.class === 'Video' }
		<Video  bind:nbPerson={nbPerson} {display}/>
	{:else if selected.class === 'VideoServer' }
			<VideoServer bind:nbPerson={nbPerson} {display}/>
	{:else if selected.class === 'Rtsp' }
			<Rtsp bind:nbPerson={nbPerson} {display}/>
	{/if}

{/if}

{#if nbPerson }
	<p> {nbPerson} {nbPerson === "0" ? 'personne' : 'personnes'} </p>
{/if}

</aside>

<main>
	<Display bind:this={display} />
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
	.aside-1 {
	  background: white;
		max-width: 20%;
		min-width: 0;
	}

	.aside-2 {
	  background: white;
	}
	@media  (min-width: 640px) {
  .aside { flex: 1 0 0; }
}
	@media (min-width: 640px) {
   main    { flex: 3 0px; }
  .aside-1 { order: 1; }
   main    { order: 2; }
  .aside-2 { order: 3; }
  .footer  { order: 4; }
}
</style>

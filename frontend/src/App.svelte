<script>
	import Camera from './Camera.svelte';
	import Image from './Image.svelte';
	import Video2 from './Video2.svelte';

	let options = [
	{ id: 1, text: `Video`, needUrl: true, class: `Video` },
	{ id: 2, text: `Image`, needUrl: true, class: `Image` },
	{ id: 3, text: `Rtsp`, needUrl: false, class: `Rtsp` }
	];

	// Add video device of the client
	navigator.mediaDevices.enumerateDevices().then((devices) => {
		for (const device of devices) {
			if (device.kind === 'videoinput' && device.deviceId) {
				const option = { id: device.deviceId, text: device.label, needUrl: false, class: `Camera` }
				options = [...options, option];
			}
		}
	});

	let selected;
	let url='';
	let files;
	$: { if (files) {url = URL.createObjectURL(files[0])}}

	let isSubmit=false;

	let nbPerson;

	function handleChange() {
		console.log(selected);
		console.log(isSubmit);
	}

	async function handleSubmit() {
		isSubmit = !isSubmit
	}
</script>

<svelte:head>
	<title>Ia-foule</title>
</svelte:head>

<main>


<form on:submit|preventDefault={handleSubmit}>
	<select bind:value={selected} on:change={handleChange}>
		{#each options as option}
			<option value={option}>
				{option.text}
			</option>
		{/each}
	</select>

	{#if (selected !== undefined && selected.needUrl)}
		<label for="input">Depuis internet:</label>
		<input bind:value={url} placeholder="Coller une url">
		<label for="input">Depuis l'ordinateur:</label>
		<input type="file" id="input" accept="video/mp4, video/mov" bind:files>
		<button disabled={!url} type=submit>
			Submit
		</button>

	{:else}
	<button type=submit>
		Submit
	</button>
	{/if}
</form>

{#if isSubmit }
	{#if (url && selected.class === 'Image')}
		<Image {url} bind:nbPerson={nbPerson}/>
	{:else if selected.class === 'Camera' }
		<Camera deviceId={selected.id} bind:nbPerson={nbPerson}/>
	{:else if selected.class === 'Video' }
		<Video2 {url} file={files[0]} bind:nbPerson={nbPerson}/>
	{/if}
{/if}

{#if nbPerson }
	<p> {nbPerson} personnes </p>
{/if}

</main>

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

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}

	img {
		width:500;
		}
</style>

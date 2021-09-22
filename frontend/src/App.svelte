<script>
	import Webcam from './Webcam.svelte';
	import Image from './Image.svelte';

	let options = [
	{ id: 1, text: `Webcam`, needUrl: false },
	{ id: 2, text: `Video`, needUrl: true },
	{ id: 3, text: `Image`, needUrl: true },
	{ id: 4, text: `Rtsp`, needUrl: false }

	];
	let selected;
	let url='';
	let isSubmit=false;
	function handleChange() {
		console.log(selected);
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
		<input bind:value={url} placeholder="Coller une url">
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
	{#if (url && selected.text === 'Image')}
		<Image {url}/>

	{:else if selected.text === 'Webcam' }
		<Webcam/>
	{/if}
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

import AppLight from './AppLight.svelte';

const appLight = new AppLight({
	target: document.body,
	props: {
		name: 'world'
	}
});

export default appLight;

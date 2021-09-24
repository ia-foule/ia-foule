<script>
  export let nbPerson;
  export let canvas
  let files;
  let url;
  let video;
  let img;
  var scaleFactor = 0.25;
	// These values are bound to properties of the video
	let time = 0;
	let duration;
	let paused = true;

	let showControls = true;
	let showControlsTimeout;

	// Used to track time of last mouse down event
	let lastMouseDown;

	function handleMove(e) {
		// Make the controls visible, but fade out after
		// 2.5 seconds of inactivity
		clearTimeout(showControlsTimeout);
		showControlsTimeout = setTimeout(() => showControls = false, 2500);
		showControls = true;

		if (!duration) return; // video not loaded yet
		if (e.type !== 'touchmove' && !(e.buttons & 1)) return; // mouse not down

		const clientX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
		const { left, right } = this.getBoundingClientRect();
		time = duration * (clientX - left) / (right - left);
	}

	// we can't rely on the built-in click event, because it fires
	// after a drag — we have to listen for clicks ourselves
	function handleMousedown(e) {
		lastMouseDown = new Date();
	}

	function handleMouseup(e) {
		if (new Date() - lastMouseDown < 300) {
			if (paused) e.target.play();
			else e.target.pause();
		}
	}

  async function handlePause(e) {
    console.log(e)
    // TODO : try ->
    //https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/captureStream
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.filter = 'grayscale(1)'; // reduce dimension
    ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
    //img.src = canvas.toDataURL();
    let blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
    // blob image in RGBA
    let data = new FormData()
    data.append('file', blob)
    let response = await fetch(`/api/image/`, {
            method: "POST",
            body: data
          })
    let result = await response.json();
    nbPerson = result.nb_person
    console.log(nbPerson)
  }

  async function handlePlay(e) {
    console.log(e)
  }

	function format(seconds) {
		if (isNaN(seconds)) return '...';

		const minutes = Math.floor(seconds / 60);
		seconds = Math.floor(seconds % 60);
		if (seconds < 10) seconds = '0' + seconds;

		return `${minutes}:${seconds}`;
	}

  const onFileSelected = async (e) => {
    let image = e.target.files[0];
    let reader = new FileReader();
    reader.readAsDataURL(image);
    reader.onload = e => {
         url = e.target.result
       };
    }
</script>
<input  type="file" accept=".mp4" on:change={(e)=>onFileSelected(e)}  >

<div>
	<video
    bind:this={video}
    src={url}
		on:mousemove={handleMove}
		on:touchmove|preventDefault={handleMove}
		on:mousedown={handleMousedown}
		on:mouseup={handleMouseup}
		bind:currentTime={time}
    on:pause|preventDefault={handlePause}
    on:play|preventDefault={handlePlay}
		bind:duration
		bind:paused>
			<track kind="captions"/>
	</video>

	<div class="controls" style="opacity: {duration && showControls ? 1 : 0}">
		<progress value="{(time / duration) || 0}"/>

		<div class="info">
			<span class="time">{format(time)}</span>
			<span>click anywhere to {paused ? 'play' : 'pause'} / drag to seek</span>
			<span class="time">{format(duration)}</span>
		</div>
	</div>
  <img  bind:this={img} />

</div>

<style>
	div {
		position: relative;
	}

	.controls {
		position: absolute;
		top: 0;
		width: 100%;
		transition: opacity 1s;
	}

	.info {
		display: flex;
		width: 100%;
		justify-content: space-between;
	}

	span {
		padding: 0.2em 0.5em;
		color: white;
		text-shadow: 0 0 8px black;
		font-size: 1.4em;
		opacity: 0.7;
	}

	.time {
		width: 3em;
	}

	.time:last-child { text-align: right }

	progress {
		display: block;
		width: 100%;
		height: 10px;
		-webkit-appearance: none;
		appearance: none;
	}

	progress::-webkit-progress-bar {
		background-color: rgba(0,0,0,0.2);
	}

	progress::-webkit-progress-value {
		background-color: rgba(255,255,255,0.6);
	}

	video {
		width: 100%;
	}
</style>

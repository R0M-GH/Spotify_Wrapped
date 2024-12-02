let christmas = false; // Christmas mode
let highScore = 0;
let isOver = false;    // Game status
let points = 0;        // Tracks successful clicks
let missed = 0;        // Tracks missed clicks
let hits = 0;
let totalCircles = 0;
const size = 150;      // Initial size of each circle in pixels
const duration = 20000; // Duration in milliseconds (15 seconds)
const frequency = 666; // Frequency of circle appearance (every 1 second)
const play = document.getElementById('t-play'); // Start button element
const replay = document.getElementById('r-play'); // Replay button element
const fullplay = document.getElementById('play'); // Replay button element
const header = document.querySelector('.header'); // Header element to be hidden during gameplay
const container = document.getElementById('button-array'); // Container for the circles
const christmasSwitch = document.getElementById('christmas-switch'); // Christmas mode switch
const sco = document.getElementById('scores');
const options = document.getElementById('options');
let selectedMode = 'classic';
const sleigh = new Image(); // Create an image element
sleigh.src = '/static/Images/sleigh.png'; // Set the image source
sleigh.style.position = 'absolute';
sleigh.style.display = 'none';
document.body.appendChild(sleigh);
sleigh.style.top = '-50px'; // Always at the top of the screen

leftC = 50;

let circles = []; // Array to store references to circles
const shrinkAmount = 15; // Define how much each circle shrinks per interval
const shrinkIntervalDuration = 100; // Time between shrink intervals in milliseconds
let real_artist_names; // Array of top 50 artist names
let real_song_titles; // Array of top 50 track names
console.log("hi");

/**
 * Returns a random percentage string for positioning circles.
 * @returns {string} A random percentage string between 10% and 90%.
 */
function getRandomPercentage() {
	return 10 + (Math.random() * 80) + '%';
}

/**
 * Returns a random top position for a circle in percentage.
 * @returns {string} A random percentage string for top position.
 */
function getRandomTop() {
	return 10 + (Math.random() * 20) + '%';
}

/**
 * Updates the high score if the current points exceed it.
 */
function updateHighScore() {
	if (points > highScore) {
		highScore = points;
		document.querySelector('.h-score').textContent = `High Score: ${highScore}`;
	}
}

/**
 * Returns a random position based on the given axis (top or left).
 * @param {string} axis - The axis to calculate position for ('top' or 'left').
 * @returns {string} A random pixel position for the specified axis.
 */
function getRandomPosition(axis) {
	if (axis === 'top') {
		return Math.floor(Math.random() * window.innerHeight) + 'px'; // Vertical position based on viewport height
	} else if (axis === 'left') {
		return Math.floor(Math.random() * window.innerWidth) + 'px'; // Horizontal position based on viewport width
	}
}

/**
 * Retrieves the left coordinate for the circle positions.
 * @returns {string} The left position in 'px' format.
 */
function getLeftC() {
	leftC += 20 + (Math.random() * 200); // Increment by a random value between 0 and 49
	if (leftC + 80 > window.innerWidth) { // If the circle goes out of bounds
		leftC = 50; // Reset left position to 50px
	}
	return leftC + 'px'; // Return the position in 'px' format
}

/**
 * Updates the score display showing accuracy, hits, and points.
 */
function updateScoreDisplay() {
	const accuracyElement = document.querySelector('.accuracy');
	const hitElement = document.querySelector('.hit');
	const scoreElement = document.querySelector('.score');

	const accuracy = (hits / (hits + missed) * 100 || 0).toFixed(2);
	accuracyElement.textContent = `${accuracy}%`; // Display accuracy as percentage
	hitElement.textContent = `${hits} Hits`; // Display updated hits count
	scoreElement.textContent = `${points} Points`; // Display points
	updateHighScore();
}

/**
 * Handles the actions performed when a circle is clicked.
 * @param {boolean} isReal - Indicates if the clicked circle was real or not.
 */
function killButtons(isReal) {
	if (isReal) {
		points += 2;
	} else {
		points -= 1;
	}
	this.style.display = 'none'; // Hide the clicked circle
	hits += 1; // Increment hits count on successful click
	const sound = new Audio('/static/Images/laser-zap-90575.mp3');
	sound.play();// Play sound effect
	updateScoreDisplay(); // Update the score display
}

/**
 * Retrieves a random item (artist or song) from the respective lists.
 * @returns {Object} An object containing the name of the item and a boolean indicating if it's fake.
 */
function getRandomItem() {
	const realFake = Math.random();
	let arr;
	let fake = true;

	console.log(realFake);
	if (realFake < 0.25) {
		arr = fake_artist_names;
	} else if (realFake < 0.5) {
		arr = fake_song_titles;
	} else if (realFake < 0.75) {
		arr = real_artist_names;
		fake = false;
	} else {
		arr = real_song_titles;
		fake = false;
	}

	const randomIndex = Math.floor(Math.random() * arr.length);
	return {
		name: arr[randomIndex],
		isFake: fake // Indicates whether the name is fake or real
	};
}

/**
 * Initiates the process of creating circles for the game.
 */
function getRandomPosition(axis) {
	if (axis === 'top') {
		return Math.floor(Math.random() * window.innerHeight) + 'px'; // Vertical position based on viewport height
	} else if (axis === 'left') {
		return Math.floor(Math.random() * window.innerWidth) + 'px'; // Horizontal position based on viewport width
	}
}

/**
 * Initiates the process of creating circles for the game.
 */
function makeCircles() {
	// Reset game variables and UI elements
	points = 0;        // Tracks successful clicks
	missed = 0;        // Tracks missed clicks
	hits = 0;
	totalCircles = 0;
	header.style.display = 'none';
	options.style.display = 'none';
	fullplay.style.display = 'flex';
	isOver = false;

	// Clear previous circles if any
	circles = []; // Reset the circles array
	container.innerHTML = ""; // Clear previous circles from the container


	// Set up interval for creating circles
	setTimeout(function () {
		isOver = true;
	}, duration);

	const interval = setInterval(function () {
		if (isOver) {
			clearInterval(interval);
			header.style.display = 'flex';
			fullplay.style.display = 'none';
			options.style.display = 'flex';
			instructions.style.display = 'flex';
			sleigh.style.display = 'none';

			circles = []; // Reset the circles array
			container.innerHTML = ""; // Clear previous circles from the container
			createSleigh(10000);
			updateHighScore();
			sleigh.style.display = 'none';
			return;
		}

		// Create the circle element
		const circle = document.createElement('button'); // Create a button element for accessibility
		circle.className += 'circle';
		circle.style.width = `${size}px`;
		circle.style.height = `${size}px`;
		circle.style.position = 'absolute';
		const itemName = getRandomItem();
		circle.textContent = itemName.name;
		circle.style.color = 'white';
		circle.style.borderRadius = '50%'; // Make it circular
		circle.style.transition = 'width 0.1s, height 0.1s'; // Smooth transition for shrinking
		circle.style.fontSize = `${20}px`

		circle.addEventListener('click', function () {
			killButtons.call(this, true);
			shrinkCircle(this);
		});
		// Set behavior based on mode
		if (selectedMode === 'classic') {
			applyClassicMode(circle);
		} else if (selectedMode === 'bouncing') {
			applyBouncingMode(circle);
		} else if (selectedMode === 'shooting') {
			applyShootingMode(circle);
		} else if (selectedMode === 'gliding') {
			applyGlidingMode(circle);
		}
		circles.push(circle);
		container.appendChild(circle);
		totalCircles += 1;
	}, frequency);
}

/**
 * Applies the behavior for classic mode to a circle.
 * @param {HTMLElement} circle - The circle element to apply the classic mode.
 */
function applyClassicMode(circle) {
	sleigh.style.display = 'none';
	shrinkCircles();
	circle.style.top = getRandomPosition('top');
	circle.style.left = getRandomPosition('left');
}

/**
 * Applies the behavior for bouncing mode to a circle.
 * @param {HTMLElement} circle - The circle element to apply the bouncing mode.
 */
function applyBouncingMode(circle) {
	sleigh.style.display = 'none';
	enableBouncing(circle);
	circle.style.top = getRandomPosition('top');
	circle.style.left = getRandomPosition('left');
}

/**
 * Applies the behavior for shooting mode to a circle.
 * @param {HTMLElement} circle - The circle element to apply the shooting mode.
 */
function applyShootingMode(circle) {
	sleigh.style.display = 'none';
	circle.style.top = getRandomTop();
	circle.style.left = getRandomTop();
	enableShooting(circle);
}

/**
 * Applies the behavior for gliding mode to a circle.
 * @param {HTMLElement} circle - The circle element to apply the gliding mode.
 */
function applyGlidingMode(circle) {
	sleigh.style.display = 'flex';
	createGlidingBall(circle);
	circle.style.left = getLeftC();
	circle.style.top = '130px'; // Example top position for the circle
}

/**
 * Shrinks the size of a circle on each successful click.
 * @param {HTMLElement} circle - The circle element to shrink.
 */
function shrinkCircle(circle) {
	let currentWidth = parseInt(circle.style.width);
	let currentHeight = parseInt(circle.style.height);
	let currentFontSize = parseInt(window.getComputedStyle(circle).fontSize);

	// Decrease the width, height by 30 and font size by 4 each time
	currentWidth -= 30;
	currentHeight -= 30;
	currentFontSize -= 5;

	// Ensure the width and height do not go below zero
	if (currentWidth <= 0 || currentHeight <= 0 || currentFontSize <= 0) {
		circle.style.display = 'none';  // Hide the circle if it shrinks to 0
		missed += 1;  // Increment missed count
		updateScoreDisplay();  // Update score display
	} else {
		// Update the circle's size and font size
		circle.style.width = currentWidth + 'px';
		circle.style.height = currentHeight + 'px';
		circle.style.fontSize = currentFontSize + 'px';
	}
}
/**
 * Shrinks all circles in the circles array.
 */
function shrinkCircles() {
	circles.forEach(circle => {
		shrinkCircle(circle);
	});
}

/**
 * Starts the game and prepares the UI for play.
 */
function startPlay() {
	getData();
	console.log("start play!");
	points = 0;
	missed = 0;
	hits = 0;

	const accuracyElement = document.querySelector('.accuracy');
	const hitElement = document.querySelector('.hit');
	const scoreElement = document.querySelector('.score');
	accuracyElement.textContent = "0%";
	hitElement.textContent = "0 Hits";
	scoreElement.textContent = "0 Points";
	const scoresDiv = document.querySelector('.scores');

	makeCircles(); // Start making circles
}

play.addEventListener("click", function () {
	startPlay();
});

/**
 * Sets the selected game mode based on user interaction.
 */
document.querySelectorAll('.game-mode-option').forEach(option => {
	option.addEventListener('click', () => {
		// Uncheck all other options except the one that was clicked
		document.querySelectorAll('.game-mode-option').forEach(otherOption => {
			otherOption.checked = false;
		});
		// Set the clicked option to true
		option.checked = true;

		selectedMode = document.querySelector('.game-mode-option:checked').value;

		// Make decisions based on the selected mode
		if (selectedMode === 'classic') {
			console.log("Classic Mode selected - Regular speed, unlimited time");
			// Add code for Classic Mode here
		} else if (selectedMode === 'bouncing') {
			console.log("Timed Mode selected - 60 seconds to score as much as possible");
			// Add code for Timed Mode here
		} else if (selectedMode === 'shooting') {
			console.log("Hardcore Mode selected - Faster circles, limited time");
			// Add code for Hardcore Mode here
		} else if (selectedMode === 'shooting') {
			console.log("gliding");
			// Add code for Hardcore Mode here
		}
	});
});

/**
 * Enables shooting behavior for a circle.
 * @param {HTMLElement} circle - The circle element to enable shooting for.
 */
function enableShooting(circle) {
	let dx = (Math.random() + 0.2) * 3; // Random horizontal speed
	let dy = (Math.random() + 0.2) * 3; // Random vertical speed

	function moveCircle() {
		const rect = fullplay.getBoundingClientRect();
		const circleRect = circle.getBoundingClientRect();

		// Update position
		circle.style.left = `${circle.offsetLeft + dx}px`;
		circle.style.top = `${circle.offsetTop + dy}px`;

		requestAnimationFrame(moveCircle);
	}

	requestAnimationFrame(moveCircle);
}

let balls = [];  // To store all the balls on screen

/**
 * Enables bouncing behavior for a circle.
 * @param {HTMLElement} circle - The circle element to enable bouncing for.
 */
function enableBouncing(circle) {
	let dx, dy;

	// Generate initial random speeds with a wider range and avoid values between -1 and 1
	do {
		dx = (Math.random() - 0.5) * 6; // Speed range [-3, 3]
	} while (Math.abs(dx) < 1); // Ensure dx is not between -1 and 1

	do {
		dy = (Math.random() - 0.5) * 6; // Speed range [-3, 3]
	} while (Math.abs(dy) < 1); // Ensure dy is not between -1 and 1

	let speedIncreaseFactor = 1.05; // Speed increase factor after each bounce
	let maxSpeed = 5; // Max speed limit
	let deleteSpeedThreshold = 5; // Speed threshold for deletion
	let timeoutDuration = Math.random() * 2000 + 5000; // 3-5 seconds timeout

	const screenWidth = window.innerWidth;
	const screenHeight = window.innerHeight;
	let isOver = false; // Check if the game is over

	// Set initial random position within bounds
	circle.style.left = `${Math.random() * screenWidth}px`;
	circle.style.top = `${Math.random() * screenHeight}px`;

	// Add the circle to the list of active balls
	balls.push({circle, dx, dy});

	// Detect collision between two balls
	function checkCollisions() {
		balls.forEach((otherBall) => {
			if (otherBall === circle) return; // Skip self collision

			const otherRect = otherBall.circle.getBoundingClientRect();
			const circleRect = circle.getBoundingClientRect();

			// Calculate the distance between the centers of the two circles
			const distX = otherRect.left + otherRect.width / 2 - (circleRect.left + circleRect.width / 2);
			const distY = otherRect.top + otherRect.height / 2 - (circleRect.top + circleRect.height / 2);
			const distance = Math.sqrt(distX * distX + distY * distY);

			// If the circles are close enough (colliding)
			if (distance < (circleRect.width / 2 + otherRect.width / 2)) {
				// Calculate the angle of the collision
				const angle = Math.atan2(distY, distX);

				// Calculate the new velocities based on elastic collision formulas
				const speed1 = Math.sqrt(dx * dx + dy * dy);
				const speed2 = Math.sqrt(otherBall.dx * otherBall.dx + otherBall.dy * otherBall.dy);
				const direction1 = Math.atan2(dy, dx);
				const direction2 = Math.atan2(otherBall.dy, otherBall.dx);

				// Reflect velocities in the direction of the collision angle
				const newDx1 = speed2 * Math.cos(direction2 - angle);
				const newDy1 = speed2 * Math.sin(direction2 - angle);
				const newDx2 = speed1 * Math.cos(direction1 - angle);
				const newDy2 = speed1 * Math.sin(direction1 - angle);

				// Apply the new velocities to both balls
				dx = newDx1;
				dy = newDy1;
				otherBall.dx = newDx2;
				otherBall.dy = newDy2;

				// Adjust positions slightly to ensure they no longer overlap
				const overlap = (circleRect.width / 2 + otherRect.width / 2) - distance;
				const angleOfCollision = Math.atan2(distY, distX);
				circle.style.left = `${circle.offsetLeft - Math.cos(angleOfCollision) * overlap}px`;
				circle.style.top = `${circle.offsetTop - Math.sin(angleOfCollision) * overlap}px`;
				otherBall.circle.style.left = `${otherBall.circle.offsetLeft + Math.cos(angleOfCollision) * overlap}px`;
				otherBall.circle.style.top = `${otherBall.circle.offsetTop + Math.sin(angleOfCollision) * overlap}px`;
			}
		});
	}

	/**
	 * Moves the circle and checks for collisions.
	 */
	function moveCircle() {
		const circleRect = circle.getBoundingClientRect(); // Get circle boundaries

		// Update circle position
		circle.style.left = `${circle.offsetLeft + dx}px`;
		circle.style.top = `${circle.offsetTop + dy}px`;

		// Detect collisions with screen edges
		if (circleRect.left + dx < 0) {
			dx = Math.abs(dx); // Bounce off left edge
			increaseSpeed();
		} else if (circleRect.right + dx > screenWidth) {
			dx = -Math.abs(dx); // Bounce off right edge
			increaseSpeed();
		}

		if (circleRect.top + dy < 0) {
			dy = Math.abs(dy); // Bounce off top edge
			increaseSpeed();
		} else if (circleRect.bottom + dy > screenHeight) {
			dy = -Math.abs(dy); // Bounce off bottom edge
			increaseSpeed();
		}

		// Prevent ball from getting stuck in very low speed
		if (Math.abs(dx) < 0.5) dx = (Math.random() < 0.5 ? -1 : 1) * 1;
		if (Math.abs(dy) < 0.5) dy = (Math.random() < 0.5 ? -1 : 1) * 1;

		// Implement damping: slowly reduce the speed if the ball is not moving fast
		if (Math.abs(dx) < 1) dx *= 0.99; // Apply damping to slow speeds
		if (Math.abs(dy) < 1) dy *= 0.99;

		// Check for ball-to-ball collisions
		checkCollisions();

		// Request animation frame if the game is not over
		if (!isOver) {
			requestAnimationFrame(moveCircle);
		}
	}

	/**
	 * Function to increase speed after bouncing.
	 */
	// Function to increase speed after bouncing
	function increaseSpeed() {
		dx *= speedIncreaseFactor;
		dy *= speedIncreaseFactor;

		// Cap the speed
		dx = Math.min(dx, maxSpeed);
		dy = Math.min(dy, maxSpeed);

		// If speed exceeds threshold, remove the ball
		if (Math.abs(dx) >= deleteSpeedThreshold || Math.abs(dy) >= deleteSpeedThreshold) {
			circle.remove(); // Remove from DOM
			cancelAnimationFrame(moveCircle);
			circle.style.display = 'none';  // Hide the circle if it shrinks to 0
			missed += 1;  // Increment missed count
			updateScoreDisplay();  // Update score display
		}
	}

	// Set a timeout to remove the ball after 3-5 seconds
	setTimeout(() => {
		circle.remove(); // Remove ball after random time
		cancelAnimationFrame(moveCircle); // Stop the animation
	}, timeoutDuration);

	// Start the animation
	requestAnimationFrame(moveCircle);
}

/**
 * Creates the sleigh at a specific horizontal position.
 * @param {number} initialLeft - The initial horizontal position of the sleigh.
 */
// Function to create the sleigh at a specific horizontal position
function createSleigh(initialLeft) {
	sleigh.style.left = `${initialLeft}px`; // Initial horizontal position
}

/**
 * Creates and glides a ball along with the sleigh.
 * @param {HTMLElement} circle - The circle element to glide.
 */
// Function to create and glide a ball along with the sleigh
function createGlidingBall(circle) {
	let dy = 2 + (Math.random() * 3); // Set an initial downward speed


	function moveCircle() {
		// Update the circle's position
		circle.style.top = `${circle.offsetTop + dy}px`;

		// Update the sleigh's position to follow the circle horizontally
		sleigh.style.left = `${circle.offsetLeft}px`;

		// If the game is not over, continue moving the circle and sleigh
		if (!isOver) {
			requestAnimationFrame(moveCircle);
		}
	}

	// Start the motion
	requestAnimationFrame(moveCircle);
	if (isOver) {
		sleigh.style.display = 'none';
	}

}


const root = document.body; // Apply class to the <body> tag
// Toggle the class when the switch is toggled
/**
 * Toggles the Christmas theme and updates the fake artist/song lists.
 */
christmasSwitch.addEventListener('change', () => {
	const chioElement = document.getElementById('chio'); // Get the element with id 'chio'

	if (christmasSwitch.checked) {
		root.classList.add('christmas-theme');
		fake_artist_names = fake_christmas_artists;
		fake_song_titles = fake_christmas_songs;
		real_artist_names = real_christmas_artists;
		real_song_titles = real_christmas_songs;
		chioElement.style.display = "flex";
		sleigh.style.display = 'flex';

	} else {
		root.classList.remove('christmas-theme');
		chioElement.style.display = "none";   // Make it invisible
		sleigh.style.display = 'none';

		fake_artist_names = fake_artist_names;
		fake_song_titles = fake_song_titles;
		getData();
	}
});

fake_artist_names = [
	"EchoWave", "CrimsonFalls", "Starfire", "VelvetReign", "LunarVeil",
	"GhostLight", "Azure", "MysticEcho", "SolarWind", "NightVibe",
	"Zenith", "BlazeTrail", "PulseField", "LucidDream", "MidnightArc",
	"PhantomBeat", "GoldenEcho", "NeonBloom", "Prism", "SilentHorizon",
	"Wander", "SoundWave", "EchoValley", "SonicRush", "SilverMist",
	"OpalSky", "Spectral", "UrbanChill", "DesertPulse", "ShadowGlow",
	"Twilight", "MoonSage", "InfiniteRhythm", "Nocturne", "VioletFlare",
	"Obsidian", "EchoChase", "NeonOasis", "SunlitPath", "Jade",
	"CyanDream", "PhantomGroove", "Nostalgia", "ElectricSoul", "SolarRay",
	"Daybreak", "Stellar", "Myst", "StormValley", "EmeraldFlow",
	"LostEcho", "Moonlight", "RainShadow", "Eclipse", "SilverLight",
	"Skyline", "GhostFrost", "GoldenHour", "Aurora", "EchoFlow",
	"VelvetArc", "BlueMist", "StarChase", "Nightfall", "Sable",
	"Retro", "SonicTwist", "AshenGlow", "Sapphire", "CityPulse",
	"CrimsonSound", "LunaEcho", "WaveRun", "Ivory", "Blaze",
	"EchoShore", "Indigo", "PrismWave", "Cinder", "Dusk",
	"Serenity", "Lumen", "Harmony", "VaporRise", "EmberArc",
	"Lush", "Hollow", "Solace", "WhisperShade", "Drift",
	"Static", "SilverDust", "Boreal", "IronGlow", "SunRider",
	"Wildwood", "CloudCity", "Lotus", "NeonZen", "Sonnet"
]
//fake artist name pool
fake_song_titles = [
	"Stardust", "Whispered Dreams", "Lunar Glow", "Echoes of You", "Velvet Sky",
	"Sapphire Nights", "Sunrise Drift", "Neon Echo", "Silent Horizon", "Soul Fire",
	"Lost in Time", "Crimson Mist", "Forevermore", "Endless Rhythm", "Golden Hour",
	"Shadows Fade", "Beneath the Waves", "Falling Stars", "Infinite Roads", "Dreamcatcher",
	"Electric Storm", "Chasing Echoes", "Celestial Tide", "Midnight Waltz", "Phantom Light",
	"Opal Moon", "Twilight Daze", "Forgotten Roads", "Sundown", "Prism Heart",
	"Sacred Sands", "Vapor Trails", "Onyx Sky", "Afterglow", "Soul Drift",
	"Echo in Blue", "Hidden Realm", "Wanderlust", "Luminous", "Veil of Fire",
	"Into the Wild", "Bright Haze", "Pulse of Rain", "Reverie", "Burning Dreams",
	"Neon Pulse", "Mystic Dawn", "Faded Echo", "Last Serenade", "Oceans Apart",
	"Gravity", "Falling Away", "Boundless", "Night Shift", "Solitude",
	"Heartbreaker", "Storm Chaser", "Endless Night", "Midnight Gold", "Moonlight Shadow",
	"Hollow Sun", "Desert Rose", "Starborne", "Out of Reach", "Forever Fade",
	"Winter Glow", "Solstice", "Celestial Dance", "Into the Abyss", "First Light",
	"Wild Heart", "Mystic River", "Shadowplay", "Ember and Ash", "City Lights",
	"Dreamscape", "Flicker", "Iron Bloom", "Snowfall", "Ghost in the Wind",
	"Echo Fields", "Aurora", "Lost Souls", "Solar Drift", "End of the Line",
	"Faded Love", "Skyward Bound", "Endless Roads", "Nightwalk", "Solace",
	"Timeless", "Ocean Breeze", "Lost Horizon", "Silver Tide", "Burning Stars",
	"Forgotten Shores", "Ivory Skies", "Drifting", "Hidden Path", "Eclipse",
	"Electric Breeze", "Voyager", "Cold Fire", "Sunset Fade", "Last Whisper"
]
//fake song names pool
fake_christmas_artists = [
	"The Frosty Bells", "Holly & Mistletoe", "Snowflake Harmony", "Winter Whispers", "The Yuletide Quartet",
	"The North Pole Players", "Silver Bells Orchestra", "Evergreen Echoes", "St. Nick & Friends", "The Reindeer Swing",
	"Tinsel Tones", "The Cozy Chorale", "Noel Nightingale", "Silent Snowfall", "Snowy Sleigh",
	"Candlelight Choir", "The Warmth Singers", "Winter Waltz", "The Snowdrift Trio", "The Merry Minstrels",
	"Polar Carolers", "Frost & Ivy", "Peppermint Jam", "The Holly Harmony", "The Jingle Belles",
	"Fireside Trio", "Northern Lights Band", "Winterlight Voices", "The Mistletoes", "Sleigh Ride Rhapsody",
	"Winter Star Quartet", "The Jolly Gatherers", "Icicle Jazz", "Frosted Harmony", "The Fir Tree Troupe",
	"Snowdrop Symphony", "The Frost Fire Five", "Gingerbread Groove", "Yuletide Ensemble", "The Cozy Composers",
	"Snowfall Singers", "The Reindeer Rhythms", "Jingle All Stars", "The Starlit Sleigh", "Frosted Flutes",
	"The Winter Whistlers", "Snow Globe Serenade", "The Merry Carolers", "Glisten & Glow", "Crimson & Clove",
	"The Candlelight Carols", "Warm Wishes Quartet", "The Fir Tree Folk", "Winter Bells Band", "The Cozy Crew",
	"Chimney Choir", "The Jingle Tunes", "Noel Notes", "Frosted Stars", "The Winter Songbirds",
	"Caroling Compass", "Polar Lights", "Icicle Harmony", "Holly Days", "The Hearth Harmonics",
	"The Sugarplum Singers", "Evergreen Echos", "The Warmth Winders", "North Star Notes", "The Frosty Strummers",
	"Glisten & Glow", "Holiday Harmonies", "The Bells of Joy", "The Snow Angels", "Sleigh Song Serenade",
	"The Cheer Troupe", "The Bright Bells", "Crimson Choir", "Winter Frost Band", "Silent Snowscape",
	"Snowy Path", "The Mistletoe Melodies", "The Jolly Trio", "Noel Notes", "North Star",
	"Icicle Tunes", "The Evergreen Quartet", "Snowshoe Serenade", "Winter Glow", "The Hearth Singers",
	"The Peppermint Twists", "Polar Serenade", "Winter Spirit Band", "The Carol Keepers", "Snowstorm Singers",
	"The Silent Sleigh", "Noel Nights", "Winter Wonder Singers", "Icicle Serenade", "The Sparkling Singers"
]

fake_christmas_songs = [
	"Under the Mistletoe", "Frosted Dreams", "Silent Snow", "The Holly Days", "Glistening Lights",
	"Tidings of Joy", "Winter's Glow", "Yuletide Wish", "Santa’s Sleighbells", "Merry & Bright",
	"In the Snowlight", "Holly and Cheer", "Frosty Footsteps", "Carols at Midnight", "Snow Angel",
	"A Winter’s Star", "Candle Glow", "North Pole Nights", "The Carol of Hope", "On Christmas Eve",
	"Peace and Pine", "A Star in the Sky", "The First Frost", "Sleigh Ride Song", "Jolly and Warm",
	"On Christmas Morning", "Tidings and Cheer", "December Dream", "Under the Stars", "The Sparkling Night",
	"Holiday Heart", "A Mistletoe Wish", "The Christmas Waltz", "Carols by Firelight", "Snowman Serenade",
	"Gather Around", "Angel's Whisper", "December Moonlight", "Silver Spark", "Candy Cane Lane",
	"Merry Melody", "Winter’s Embrace", "Frozen Footsteps", "Yuletide Love", "Snowfall Song",
	"Season of Joy", "In the Frosty Air", "Sparkling December", "The Snowman’s Song", "Fireside Heart",
	"Peaceful Pines", "Wrapped in Wonder", "Beneath the Lights", "December Song", "Caroling By the Fire",
	"The Brightest Night", "Northern Skies", "Winter Wind", "Starry Christmas", "Holly Crown",
	"Glistening Pines", "A Silent Night", "The Reindeer’s Waltz", "Candy Cane Wishes", "Snowfall Symphony",
	"Golden Glow", "At Winter’s Door", "The Cheerful Light", "By the Tree", "Frosty Path",
	"Midnight Snowfall", "The Cozy Hearth", "Dream of Christmas", "Pinecone Melody", "In the Glow",
	"The First Light", "Icicle Song", "Red and Green", "A Candle's Warmth", "Sweet Noel",
	"Under a Snowy Sky", "The Cheer of Winter", "Mistletoe Dance", "Winter in Bloom", "Dreaming of Snow",
	"Snowfall Waltz", "By Starlight", "Snowbound", "Season’s Whisper", "Twinkling Pines",
	"Starry Bells", "The Little Reindeer", "Holiday Serenade", "December’s Promise", "With Love and Light",
	"The Warmth of Winter", "Frosted Window", "December's Light", "Peppermint Path", "Evergreen Waltz"
]

real_christmas_songs = [
	"All I Want for Christmas Is You", "Jingle Bell Rock", "Silent Night", "White Christmas",
	"Winter Wonderland", "Rockin' Around the Christmas Tree", "It's Beginning to Look a Lot Like Christmas",
	"The Christmas Song (Chestnuts Roasting on an Open Fire)", "Last Christmas", "Santa Claus Is Coming to Town",
	"O Holy Night", "Have Yourself a Merry Little Christmas", "Frosty the Snowman", "Holly Jolly Christmas",
	"Do You Hear What I Hear?", "Sleigh Ride", "Blue Christmas", "Let It Snow! Let It Snow! Let It Snow!",
	"Rudolph the Red-Nosed Reindeer", "Little Drummer Boy", "O Come, All Ye Faithful", "Joy to the World",
	"I'll Be Home for Christmas", "Silver Bells", "Carol of the Bells", "Deck the Halls", "Mary, Did You Know?",
	"We Wish You a Merry Christmas", "Baby, It's Cold Outside", "God Rest Ye Merry, Gentlemen",
	"Hark! The Herald Angels Sing", "Wonderful Christmastime", "Run Rudolph Run", "Merry Christmas Darling",
	"Feliz Navidad", "Happy Xmas (War Is Over)", "Please Come Home for Christmas", "Christmas (Baby Please Come Home)",
	"Here Comes Santa Claus", "Angels We Have Heard on High", "O Little Town of Bethlehem", "Do They Know It's Christmas?",
	"Santa Baby", "O Christmas Tree", "I Saw Mommy Kissing Santa Claus", "Jingle Bells", "Go Tell It on the Mountain",
	"Where Are You Christmas?", "Ave Maria", "What Child Is This?", "Peace on Earth/Little Drummer Boy"
]

real_christmas_artists = [
	"Mariah Carey", "Michael Bublé", "Bing Crosby", "Nat King Cole", "Pentatonix",
	"Frank Sinatra", "Wham!", "Brenda Lee", "Elvis Presley", "Trans-Siberian Orchestra",
	"Ariana Grande", "John Legend", "Kelly Clarkson", "Josh Groban", "Samantha Smith",
	"Harry Connick Jr.", "Faith Hill", "Celine Dion", "The Jackson 5", "Dean Martin",
	"Andrea Bocelli", "Diana Krall", "Lady A", "Barbra Streisand", "James Taylor",
	"LeAnn Rimes", "Rascall Flatts", "Gwen Stefani", "Michael W. Smith", "The Carpenters",
	"Celtic Woman", "Alabama", "The Beach Boys", "Jewel", "Kenny G",
	"The Robertsons", "Lindsey Stirling", "Sheryl Crow", "Annie Lennox", "Darius Rucker",
	"Luther Vandross", "Willie Nelson", "Rosanne Cash", "Carrie Underwood", "Mannheim Steamroller",
	"The Piano Guys", "Billie Eilish", "Norah Jones", "Sara Bareilles", "Josh Turner"
];


function getData() {
	fetch(`/api/get-game-info/`).then(response => response.json()).then(data => {
		console.log(data);
		real_artist_names = data.artists;
		real_song_titles = data.tracks;
	});
}
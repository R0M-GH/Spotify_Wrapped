/**
 * Boolean flag to toggle Christmas mode.
 * @type {boolean}
 */
let christmas = false;

/**
 * The highest score achieved in the game.
 * @type {number}
 */
let highScore = 0;

/**
 * Game status flag indicating whether the game is over.
 * @type {boolean}
 */
let isOver = false;

/**
 * The current score, tracks successful clicks during the game.
 * @type {number}
 */
let points = 0;

/**
 * The count of missed clicks during the game.
 * @type {number}
 */
let missed = 0;

/**
 * The number of successful hits during the game.
 * @type {number}
 */
let hits = 0;

/**
 * Total number of circles displayed in the game.
 * @type {number}
 */
let totalCircles = 0;

/**
 * The initial size of each circle in pixels.
 * @type {number}
 */
const size = 150;

/**
 * Duration of the game in milliseconds (20 seconds).
 * @type {number}
 */
const duration = 20000;

/**
 * The frequency at which circles appear in milliseconds (333ms = ~1 second).
 * @type {number}
 */
const frequency = 333;

/**
 * The start button element to begin the game.
 * @type {HTMLElement}
 */
const play = document.getElementById('t-play');

/**
 * The replay button element to restart the game.
 * @type {HTMLElement}
 */
const replay = document.getElementById('r-play');

/**
 * The full play button element (also serves as replay button).
 * @type {HTMLElement}
 */
const fullplay = document.getElementById('play');

/**
 * The header element to be hidden during gameplay.
 * @type {HTMLElement}
 */
const header = document.querySelector('.header');

/**
 * The container element where circles are displayed.
 * @type {HTMLElement}
 */
const container = document.getElementById('button-array');

/**
 * The Christmas mode switch element.
 * @type {HTMLElement}
 */
const christmasSwitch = document.getElementById('christmas-switch');

/**
 * The scores display element.
 * @type {HTMLElement}
 */
const sco = document.getElementById('scores');

/**
 * The options element to manage game settings.
 * @type {HTMLElement}
 */
const options = document.getElementById('options');

/**
 * The currently selected game mode (default is 'classic').
 * @type {string}
 */
let selectedMode = 'classic';

/**
 * Image element representing a sleigh, displayed when Christmas mode is active.
 * @type {HTMLImageElement}
 */
const sleigh = new Image();

/**
 * The image source for the sleigh.
 * @type {string}
 */
sleigh.src = '/static/Images/sleigh.png';

/**
 * Sets the position of the sleigh image.
 * @type {string}
 */
sleigh.style.position = 'absolute';

/**
 * Sets the visibility of the sleigh image.
 * @type {string}
 */
sleigh.style.display = 'none';

/**
 * Appends the sleigh image to the body of the document.
 */
document.body.appendChild(sleigh);

/**
 * The vertical position of the sleigh image, placed off-screen initially.
 * @type {string}
 */
sleigh.style.top = '-50px';


/**
 * The height of the browser window (viewport height).
 * @type {number}
 */
const screenHeight = window.innerHeight;

/**
 * The width of the browser window (viewport width).
 * @type {number}
 */
const screenWidth = window.innerWidth;

/**
 * The starting horizontal position for the circles.
 * @type {number}
 */
leftC = 50;

/**
 * Array to store references to the circles created during the game.
 * @type {Array<HTMLElement>}
 */
let circles = [];

/**
 * The amount by which each circle shrinks during each interval, in pixels.
 * @type {number}
 */
const shrinkAmount = 15;

/**
 * Time interval between each shrinking step of the circles, in milliseconds.
 * @type {number}
 */
const shrinkIntervalDuration = 100;

/**
 * Generates a random percentage value between 10% and 90%.
 * @returns {string} The randomly generated percentage as a string (e.g., "35%").
 */
function getRandomPercentage() {
    return 10 + (Math.random() * 80) + '%';
}

/**
 * Generates a random vertical position value (top) between 10% and 30% of the viewport height.
 * @returns {string} The randomly generated top value as a percentage (e.g., "25%").
 */
function getRandomTop() {
    return 10 + (Math.random() * 20) + '%';
}

/**
 * Updates the high score if the current points exceed the existing high score.
 * Updates the high score display in the DOM.
 */
function updateHighScore() {
    if (points > highScore) {
        highScore = points;
        document.querySelector('.h-score').textContent = `High Score: ${highScore}`;
    }
}


/**
 * Generates a random position for an element, either 'top' or 'left' based on the axis passed as an argument.
 * @param {string} axis - The axis to generate the position for ('top' or 'left').
 * @returns {string} A random position value in pixels (e.g., "150px").
 */
function getRandomPosition(axis) {
    if (axis === 'top') {
        return Math.floor(Math.random() * window.innerHeight) + 'px'; // Vertical position based on viewport height
    } else if (axis === 'left') {
        return Math.floor(Math.random() * window.innerWidth) + 'px'; // Horizontal position based on viewport width
    }
}

/**
 * Updates the left position of a circle, ensuring it stays within the viewport width.
 * The position is incremented by a random value between 20px and 220px.
 * If the circle exceeds the viewport width, the position is reset to 50px.
 * @returns {string} The updated left position in 'px' format (e.g., "120px").
 */
function getLeftC() {
    leftC += 20 + (Math.random() * 200); // Increment by a random value between 0 and 200
    if (leftC + 80 > window.innerWidth) { // If the circle goes out of bounds
        leftC = 50; // Reset left position to 50px
    }
    return leftC + 'px'; // Return the position in 'px' format
}

/**
 * Updates the score display, including accuracy, hits, and points.
 * Also updates the high score if necessary.
 */
function updateScoreDisplay() {
    const accuracyElement = document.querySelector('.accuracy');
    const hitElement = document.querySelector('.hit');
    const scoreElement = document.querySelector('.score');

    const accuracy = (hits / (hits + missed) * 100 || 0).toFixed(2);
    accuracyElement.textContent = `${accuracy}%`; // Display accuracy as percentage
    hitElement.textContent = `${hits} Hits`; // Display updated hits count
    scoreElement.textContent = `${points} Points`; // Display points
    updateHighScore(); // Call the function to update the high score
}

/**
 * Hides a circle when clicked, updates the score, and plays a sound effect.
 * The points are incremented for successful clicks and decremented for misses.
 *
 * @param {boolean} isReal - A flag indicating whether the click was on a real circle (`true` for real, `false` for miss).
 * @this {HTMLElement} The circle element that was clicked.
 */
function killButtons(isReal) {
    if (isReal) {
        points += 2; // Increment points for successful click
    } else {
        points -= 1; // Decrement points for miss
    }
    this.style.display = 'none'; // Hide the clicked circle
    hits += 1; // Increment hits count on successful click
    const sound = new Audio('/static/Images/laser-zap-90575.mp3');
    sound.play(); // Play sound effect
    updateScoreDisplay(); // Update the score display
}

/**
 * Generates a random item (either a fake or real artist/song) and returns it along with a flag indicating if it is fake.
 * The function selects an item from predefined arrays of fake and real artist names or song titles.
 * The probability distribution is:
 * - 25% chance for a fake artist name
 * - 25% chance for a fake song title
 * - 25% chance for a real artist name
 * - 25% chance for a real song title
 *
 * @returns {Object} An object containing:
 *   - {string} name - The name of the selected artist or song.
 *   - {boolean} isFake - A flag indicating if the item is fake (`true` for fake, `false` for real).
 */
function getRandomItem() {
    const realFake = Math.random(); // Random value to determine if item is fake or real
    let arr;
    let fake = true; // Default to fake item

    // Determine whether to use fake or real data based on the random value
    if (realFake < 0.25) {
        arr = fake_artist_names;
    } else if (realFake < 0.5) {
        arr = fake_song_titles;
    } else if (realFake < 0.75) {
        arr = real_artist_names;
        fake = false; // Mark as real
    } else {
        arr = real_song_titles;
        fake = false; // Mark as real
    }

    const randomIndex = Math.floor(Math.random() * arr.length); // Get random index from the chosen array
    return {
        name: arr[randomIndex], // Return the item name
        isFake: fake // Indicates whether the item is fake or real
    };
}

/**
 * Generates a random position for an element on either the 'top' or 'left' axis based on the viewport size.
 *
 * @param {string} axis - The axis for which the position is generated. It can either be 'top' for vertical positioning or 'left' for horizontal positioning.
 * @returns {string} A random position value in pixels (e.g., "150px") based on the specified axis.
 * @throws {Error} Throws an error if the provided axis is not 'top' or 'left'.
 */
function getRandomPosition(axis) {
    if (axis === 'top') {
        return Math.floor(Math.random() * window.innerHeight) + 'px'; // Vertical position based on viewport height
    } else if (axis === 'left') {
        return Math.floor(Math.random() * window.innerWidth) + 'px'; // Horizontal position based on viewport width
    }
}

/**
 * Creates and manages circles on the screen, including game setup, timer, and handling different modes.
 * The function sets up the game, generates circles at intervals, and handles the game duration, modes, and UI updates.
 * It also manages the game over state and updates the UI accordingly.
 *
 * The function supports various modes for the circles, including:
 * - Classic mode
 * - Bouncing mode
 * - Shooting mode
 * - Gliding mode
 *
 * When the game ends, it clears the circles, stops the interval, and updates the high score.
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
    setTimeout(function() {
        isOver = true; // Mark game as over after the duration
    }, duration);

    const interval = setInterval(function() {
        if (isOver) {
            clearInterval(interval); // Stop the interval when game is over
            header.style.display = 'flex';
            fullplay.style.display = 'none';
            options.style.display = 'flex';
            instructions.style.display = 'flex';
            sleigh.style.display = 'none';

            circles = []; // Reset the circles array
            container.innerHTML = ""; // Clear previous circles from the container
            createSleigh(10000); // Reset sleigh creation
            updateHighScore(); // Update high score
            sleigh.style.display = 'none';
            return;
        }

        // Create the circle element
        const circle = document.createElement('button'); // Create a button element for accessibility
        circle.className += 'circle';
        circle.style.width = `${size}px`;
        circle.style.height = `${size}px`;
        circle.style.position = 'absolute';
        const itemName = getRandomItem(); // Get a random item (artist or song)
        circle.textContent = itemName.name; // Set the text to the item name
        circle.style.color = 'white';
        circle.style.borderRadius = '50%'; // Make it circular
        circle.style.transition = 'width 0.1s, height 0.1s'; // Smooth transition for shrinking
        circle.style.fontSize = `${20}px`;

        // Add click event to the circle, which kills the button and shrinks it
        circle.addEventListener('click', function() {
                killButtons.call(this, itemName.isFake); // Call killButtons on click
                shrinkCircle(this); // Shrink the clicked circle
            });

        // Set behavior based on selected mode
        if (selectedMode === 'classic') {
            applyClassicMode(circle);
        } else if (selectedMode === 'bouncing') {
            applyBouncingMode(circle);
        } else if (selectedMode === 'shooting') {
            applyShootingMode(circle);
        } else if (selectedMode === 'gliding') {
            applyGlidingMode(circle);
        }

        circles.push(circle); // Add the circle to the circles array
        container.appendChild(circle); // Add the circle to the container
        totalCircles += 1; // Increment the total circles counter
    }, frequency); // Create a circle every 'frequency' milliseconds
}


/**
 * Applies 'classic' mode behavior to the circle, including setting a random position and shrinking the circle.
 * In classic mode, the circle is positioned randomly on the screen and shrunk.
 *
 * @param {HTMLElement} circle - The circle element to which the classic mode behavior will be applied.
 */
function applyClassicMode(circle) {
    sleigh.style.display = 'none'; // Hide sleigh in classic mode
    shrinkCircles(); // Shrink circles in classic mode
    circle.style.top = getRandomPosition('top'); // Random vertical position
    circle.style.left = getRandomPosition('left'); // Random horizontal position
}

/**
 * Applies 'bouncing' mode behavior to the circle, enabling it to bounce around the screen.
 * In bouncing mode, the circle is positioned randomly and enabled to bounce.
 *
 * @param {HTMLElement} circle - The circle element to which the bouncing mode behavior will be applied.
 */
function applyBouncingMode(circle) {
    sleigh.style.display = 'none'; // Hide sleigh in bouncing mode
    enableBouncing(circle); // Enable bouncing for the circle
    circle.style.top = getRandomPosition('top'); // Random vertical position
    circle.style.left = getRandomPosition('left'); // Random horizontal position
}

/**
 * Applies 'shooting' mode behavior to the circle, enabling shooting functionality and setting a random position.
 * In shooting mode, the circle is positioned randomly and shooting behavior is enabled.
 *
 * @param {HTMLElement} circle - The circle element to which the shooting mode behavior will be applied.
 */
function applyShootingMode(circle) {
    sleigh.style.display = 'none'; // Hide sleigh in shooting mode
    circle.style.top = getRandomTop(); // Random vertical position
    circle.style.left = getRandomTop(); // Random horizontal position
    enableShooting(circle); // Enable shooting behavior
}


/**
 * Applies 'gliding' mode behavior to the circle, creating a gliding effect.
 * In gliding mode, the circle is positioned with a fixed vertical position and a dynamic horizontal position.
 * A sleigh is also shown during this mode.
 *
 * @param {HTMLElement} circle - The circle element to which the gliding mode behavior will be applied.
 */
function applyGlidingMode(circle) {
    sleigh.style.display = 'flex'; // Show sleigh in gliding mode
    createGlidingBall(circle); // Create a gliding ball effect
    circle.style.left = getLeftC(); // Set the left position with a gliding offset
    circle.style.top = '130px'; // Set a fixed top position for gliding
}

/**
 * Shrinks the circle by reducing its width, height, and font size.
 * The circle shrinks in size until it reaches a point where it is hidden and counted as missed.
 *
 * @param {HTMLElement} circle - The circle element that will be shrunk.
 */
function shrinkCircle(circle) {
    let currentWidth = parseInt(circle.style.width);
    let currentHeight = parseInt(circle.style.height);
    let currentFontSize = parseInt(window.getComputedStyle(circle).fontSize);

    // Decrease the width, height by 30 and font size by 5 each time
    currentWidth -= 30;
    currentHeight -= 30;
    currentFontSize -= 5;

    // Hide the circle if it shrinks to zero, and update the missed count
    if ((currentWidth <= 0 || currentHeight <= 0 || currentFontSize <= 0) && circle.style.display !== "none") {
        circle.style.display = 'none';  // Hide the circle
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
 * Shrinks all the circles in the `circles` array.
 * This function iterates over each circle in the array and calls `shrinkCircle` to reduce its size.
 */
function shrinkCircles() {
    circles.forEach(circle => {
        shrinkCircle(circle);
    });
}

/**
 * Starts the game by resetting the scores and creating new circles.
 * It initializes the points, missed, and hits counters, updates the accuracy, hit, and score elements,
 * and begins the process of creating circles for the game.
 */
function startPlay() {
    console.log("start play!");
    points = 0;
    missed = 0;
    hits = 0;

    // Update the accuracy, hit, and score elements on the page
    const accuracyElement = document.querySelector('.accuracy');
    const hitElement = document.querySelector('.hit');
    const scoreElement = document.querySelector('.score');
    accuracyElement.textContent = "0%";
    hitElement.textContent = "0 Hits";
    scoreElement.textContent = "0 Points";
    const scoresDiv = document.querySelector('.scores');

    makeCircles(); // Start making circles
}


/**
 * Event listener for the "play" button that starts the game when clicked.
 * This function listens for a click event on the `play` button and calls `startPlay` to initialize the game.
 */
play.addEventListener("click", function() {
    startPlay();
});

/**
 * Handles the selection of the game mode by adding an event listener to each game mode option.
 * When an option is clicked:
 * - It unchecks all other options.
 * - Sets the clicked option as checked.
 * - Retrieves the value of the selected game mode.
 * - Logs a message and performs actions based on the selected game mode.
 */
document.querySelectorAll('.game-mode-option').forEach(option => {
    option.addEventListener('click', () => {
        // Uncheck all other options except the one that was clicked
        document.querySelectorAll('.game-mode-option').forEach(otherOption => {
            otherOption.checked = false;
        });
        // Set the clicked option to true
        option.checked = true;

        // Get the selected game mode
        selectedMode = document.querySelector('.game-mode-option:checked').value;

        // Perform actions based on the selected game mode
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
 * Enables the shooting behavior for a circle by making it move randomly on the screen.
 * The circle continuously moves in a random direction with a fixed speed and hides when it moves off-screen.
 * It also increments the missed counter and updates the score when the circle is hidden.
 *
 * @param {HTMLElement} circle - The circle element to which the shooting behavior will be applied.
 *
 * @returns {void} This function does not return any value.
 */
function enableShooting(circle) {
    let dx = (Math.random() + 0.2) * 3; // Random horizontal speed
    let dy = (Math.random() + 0.2) * 3; // Random vertical speed

    // Moves the circle continuously across the screen
    function moveCircle() {
        const rect = fullplay.getBoundingClientRect();
        const circleRect = circle.getBoundingClientRect();

        // Update position of the circle
        circle.style.left = `${circle.offsetLeft + dx}px`;
        circle.style.top = `${circle.offsetTop + dy}px`;

        // Continue moving the circle by calling moveCircle on the next frame
        requestAnimationFrame(moveCircle);

        // Hide the circle if it moves off-screen
        if ((circleRect.top > screenHeight * 1.2 || // Below the screen
            circleRect.left > screenWidth * 1.2 || // Right of the screen
            circleRect.right < -screenWidth * 0.2 || // Left of the screen
            circleRect.bottom < -screenHeight * 0.2) // Above the screen
            && circle.style.display !== "none" // Make sure the circle is not already hidden
        ) {
            circle.style.display = "none"; // Hide the circle
            missed++; // Increment the missed counter
            console.log(missed); // Log the missed count
            updateScoreDisplay(); // Update the score display
        }
    }

    // Start the movement animation
    requestAnimationFrame(moveCircle);
}

/**
 * Enables the bouncing behavior for a circle on the screen.
 * The circle moves with random velocities, bouncing off the edges of the screen and other balls.
 * The speed of the circle increases with each bounce, and it will be removed if it exceeds a certain speed.
 * The circle is also removed after a random timeout if not already removed due to high speed.
 *
 * @param {HTMLElement} circle - The circle element that will exhibit the bouncing behavior.
 *
 * @returns {void} This function does not return any value.
 */
function enableBouncing(circle) {
    let dx, dy;

    // Generate initial random speeds for the ball, avoiding values between -1 and 1
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
    balls.push({ circle, dx, dy });

    // Detect collision between two balls
    function checkCollisions() {
        balls.forEach((otherBall) => {
            if (circle === circle) return; // Got rid of bouncing functionality

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

    // Function to move the circle
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
        missed++; // Increment missing counter
        updateScoreDisplay();
    }, timeoutDuration);

    // Start the animation
    requestAnimationFrame(moveCircle);
}


/**
 * Function to create the sleigh at a specific horizontal position.
 *
 * @param {number} initialLeft - The initial horizontal position (in pixels) of the sleigh.
 * @returns {void}
 */
function createSleigh(initialLeft) {
    sleigh.style.left = `${initialLeft}px`; // Initial horizontal position
}

/**
 * Function to create and glide a ball along with the sleigh.
 * The ball will move downward and the sleigh will follow it horizontally.
 * If the ball goes off-screen, it will be hidden and the missed counter will be incremented.
 *
 * @param {HTMLElement} circle - The HTML element representing the ball (circle) to be glided.
 * @returns {void}
 */
function createGlidingBall(circle) {
    let dy = 2 + (Math.random() * 3); // Set an initial downward speed

    /**
     * Function to move the circle and update the sleigh position.
     * It continuously moves the ball downward and adjusts the sleigh's position
     * horizontally to follow the ball. If the ball goes off-screen, it is hidden.
     *
     * @returns {void}
     */
    function moveCircle() {
        const circleRect = circle.getBoundingClientRect(); // Get the circle's bounding rectangle

        // Update the circle's position
        circle.style.top = `${circle.offsetTop + dy}px`;

        // Update the sleigh's position to follow the circle horizontally
        sleigh.style.left = `${circle.offsetLeft}px`;

        // If the game is not over, continue moving the circle and sleigh
        if (!isOver) {
            requestAnimationFrame(moveCircle);
        }

        // Check if the ball is out of bounds (off-screen) in any direction
        if ((circleRect.top > screenHeight * 1.2 || // Below the screen
            circleRect.left > screenWidth * 1.2 || // Right of the screen
            circleRect.right < -screenWidth * 0.2 || // Left of the screen
            circleRect.bottom < -screenHeight * 0.2) // Above the screen
            && circle.style.display !== "none" // Make sure the circle is not already hidden
        ) {
            circle.style.display = "none"; // Hide the circle
            missed++; // Increment the missed counter
            console.log(missed); // Log the missed count
            updateScoreDisplay(); // Update the score display
        }
    }

    // Start the motion
    requestAnimationFrame(moveCircle);

    // Hide the sleigh if the game is over
    if (isOver) {
        sleigh.style.display = 'none';
    }
}


/**
 * Toggles the Christmas theme when the switch is toggled.
 * When the switch is checked, it applies the 'christmas-theme' class to the <body> tag
 * and updates the song and artist data to Christmas-themed values. It also makes
 * certain elements (like the 'chio' and sleigh) visible.
 * When the switch is unchecked, it removes the 'christmas-theme' class and restores
 * the original values for song and artist data while hiding the 'chio' and sleigh elements.
 *
 * @param {Event} event - The change event triggered when the christmasSwitch is toggled.
 * @returns {void}
 */
christmasSwitch.addEventListener('change', () => {
    const chioElement = document.getElementById('chio'); // Get the element with id 'chio'

    // Apply Christmas theme if the switch is checked
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

        // Restore original values when switch is unchecked
        fake_artist_names = original_fake_artist_names;
        fake_song_titles = original_fake_song_titles;
        real_artist_names = real_artist_names;
        real_song_titles = real_song_titles;
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
//real christmas songs


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

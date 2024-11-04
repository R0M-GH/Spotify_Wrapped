let christmas = false; // Christmas mode
let highScore = 0;
let isOver = false;    // Game status
let points = 0;        // Tracks successful clicks
let missed = 0;        // Tracks missed clicks
const size = 100;      // Initial size of each circle in pixels
const duration = 15000; // Duration in milliseconds (15 seconds)
const frequency = 500; // Frequency of circle appearance (every 1 second)
const play = document.getElementById('t-play'); // Start button element
const replay = document.getElementById('r-play'); // Replay button element
const fullplay = document.getElementById('play'); // Replay button element
const header = document.querySelector('.header'); // Header element to be hidden during gameplay
const container = document.getElementById('button-array'); // Container for the circles
const christmasSwitch = document.getElementById('christmas-switch'); // Christmas mode switch
const sco = document.getElementById('scores');

let circles = []; // Array to store references to circles
const shrinkAmount = 15; // Define how much each circle shrinks per interval
const shrinkIntervalDuration = 100; // Time between shrink intervals in milliseconds

function getRandomPercentage() {
    return 10 + (Math.random() * 80) + '%';
}

function updateHighScore() {
    if (points > highScore) {
        highScore = points;
        document.querySelector('.h-score').textContent = `High Score: ${highScore}`;
    }
}


function updateScoreDisplay() {
    const accuracyElement = document.querySelector('.accuracy');
    const hitElement = document.querySelector('.hit');
    const scoreElement = document.querySelector('.score');

    accuracyElement.textContent = `${((points / (points + missed)) * 100 || 0).toFixed(2)}%`; // Accuracy calculation
    hitElement.textContent = `${points} Hits`; // Updated to show actual hits
    scoreElement.textContent = `${points} Points`; // Display points
}

function killButtons(isReal) {
    if (isReal) {
        points += 2;
    } else {
        points -= 1;
    }
    this.style.display = 'none'; // Hide the clicked circle
    new Audio('path/to/sound.mp3').play(); // Play sound effect
    updateScoreDisplay(); // Update the score display
}

function getRandomItem() {
    const realFake = Math.random();
    let arr;
    let fake = true;

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

function makeCircles() {
    header.style.display = 'none';
    fullplay.style.display = 'flex';
    isOver = false;

    // Clear previous circles if any
    circles = []; // Reset the circles array
    container.innerHTML = ""; // Clear previous circles from the container

    setTimeout(function() {
        isOver = true;
        shrinkAllCircles(); // Call to shrink all circles after game is over
    }, duration);

    const interval = setInterval(function() {
        if (isOver) {
            clearInterval(interval);
            header.style.display = 'flex';
            fullplay.style.display = 'none';

            circles = []; // Reset the circles array
            container.innerHTML = ""; // Clear previous circles from the container

            updateHighScore();

            return;
        }

        const circle = document.createElement('button'); // Create a button element for accessibility
        circle.classList.add('class-container');
        circle.style.width = `${size}px`;
        circle.style.height = `${size}px`;
        circle.style.position = 'absolute';
        circle.style.top = getRandomPercentage();
        circle.style.left = getRandomPercentage();
        const itemName = getRandomItem();
        circle.textContent = itemName.name;
        circle.style.borderRadius = '50%'; // Make it circular
        circle.style.transition = 'width 0.1s, height 0.1s'; // Smooth transition for shrinking

        // Add an event listener to the circle for clicking
        circle.addEventListener('click', function() {
            const isReal = itemName.isFake === false; // Check if the item is real or fake
            killButtons.call(this, isReal);
            shrinkCircle(this); // Call the shrink function on click
        });


        circles.push(circle); // Store reference to the circle
        container.appendChild(circle);
        console.log("circle added");

        shrinkCircles();

    }, frequency); // Set interval time based on frequency
}

function shrinkCircle(circle) {
    // Get the current size of the circle
    const currentSize = parseInt(circle.style.width);

    // Calculate the new size after shrinking
    const newSize = Math.max(0, currentSize - shrinkAmount);
    circle.style.width = `${newSize}px`;
    circle.style.height = `${newSize}px`;

    // Set a smaller font size relative to the circle's size
    const newFontSize = Math.max(0, newSize / 3); // Adjust the divisor to control text size
    circle.style.fontSize = `${newFontSize}px`;

    // Update the displayed text
    circle.textContent = `${newSize}px`;

    // Hide the circle if it shrinks to 0
    if (newSize <= 0) {
        circle.style.display = 'none';
    }
}


function shrinkCircles() {
    circles.forEach(circle => {
        const currentSize = parseInt(circle.style.width);
        circle.style.width = `${Math.max(0, currentSize - shrinkAmount)}px`; // Shrink by a fixed amount
        circle.style.height = `${Math.max(0, currentSize - shrinkAmount)}px`; // Shrink by a fixed amount

        if (currentSize - shrinkAmount <= 0) {
            circle.style.display = 'none'; // Hide the circle if it shrinks to 0
        }
        console.log("shrunk");
    });
}

function startPlay() {
    console.log("start play!");
    points = 0;
    missed = 0;

    const accuracyElement = document.querySelector('.accuracy');
    const hitElement = document.querySelector('.hit');
    const scoreElement = document.querySelector('.score');
    accuracyElement.textContent = "0%";
    hitElement.textContent = "0 Hits";
    scoreElement.textContent = "0 Points";
    const scoresDiv = document.querySelector('.scores');

    makeCircles(); // Start making circles
}

play.addEventListener("click", function() {
    startPlay();
});


christmasSwitch.addEventListener('change', function() {
    christmas = this.checked;
    if (christmas) {
        fake_artist_names = fake_christmas_artists;
        fake_song_titles = fake_christmas_songs;
        real_artist_names = real_christmas_artists;
        real_song_titles = real_christmas_songs;
    } else {
        // Reset original names here
        fake_artist_names = original_fake_artist_names;
        fake_song_titles = original_fake_song_titles;
        real_artist_names = original_real_artist_names;
        real_song_titles = original_real_song_titles;
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
]
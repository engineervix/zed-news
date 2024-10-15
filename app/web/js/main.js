import "../css/main.scss";

import * as bootstrap from "bootstrap";
import AOS from "aos";
import Plyr from "plyr";
import UAParser from "ua-parser-js";
import sharer from "sharer.js";
import { format } from "timeago.js";
import "aos/dist/aos.css";
import "@fortawesome/fontawesome-free/css/all.min.css";

/* ***** ----------------------------------------------- ***** **
/* ***** https://getbootstrap.com/docs/5.3/components/tooltips/#enable-tooltips
/* ***** ----------------------------------------------- ***** */
const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"]'
);
const tooltipList = [...tooltipTriggerList].map(
  (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
);

/* ***** ----------------------------------------------- ***** **
/* ***** AOS
/* ***** ----------------------------------------------- ***** */

AOS.init();

/* ***** ----------------------------------------------- ***** **
/* ***** Plyr
/* ***** ----------------------------------------------- ***** */

const controls = [
  "play-large", // The large play button in the center
  "restart", // Restart playback
  "rewind", // Rewind by the seek time (default 10 seconds)
  "play", // Play/pause playback
  "fast-forward", // Fast forward by the seek time (default 10 seconds)
  "progress", // The progress bar and scrubber for playback and buffering
  "current-time", // The current time of playback
  "duration", // The full duration of the media
  "mute", // Toggle mute
  "volume", // Volume control
  "settings", // Settings menu
  "pip", // Picture-in-picture (currently Safari only)
  "airplay", // Airplay (currently Safari only)
  "download", // Show a download button
];

const tooltips = { controls: true };

// const players = Plyr.setup(".podcast-player", { controls, tooltips });
Plyr.setup(".podcast-player", { controls, tooltips });

document.querySelectorAll(".podcast-player").forEach((playPodcast) => {
  playPodcast.addEventListener("play", () => {
    const activated = playPodcast;
    document.querySelectorAll(".podcast-player").forEach((element) => {
      if (element !== activated) {
        element.pause();
      }
    });
  });
});

/* ***** ----------------------------------------------- ***** **
/* ***** Podcast Listen Buttons
/* ***** ----------------------------------------------- ***** */

/**
 * @param {String} HTML representing a single element
 * @return {Element}
 */
function htmlToElement(html) {
  // https://stackoverflow.com/a/35385518
  var template = document.createElement("template");
  html = html.trim(); // Never return a text node of whitespace as the result
  template.innerHTML = html;
  return template.content.firstChild;
}

function generatePodcastListenButton() {
  const parser = new UAParser();
  const result = parser.getResult();

  const platform = result.os.name.toLowerCase();
  let buttonHTML = "";

  if (platform === "mac os" || platform === "ios") {
    buttonHTML = `
      <a class="podcast-listen-btn" href="https://podcasts.apple.com/us/podcast/zed-news-podcast/id1690709989">
        <img src="/img/apple-podcasts-badge.svg" alt="Listen on Apple Podcasts" height="40" />
      </a>
    `;
  } else {
    buttonHTML = `
      <a class="podcast-listen-btn" href="https://open.spotify.com/show/14vv6liB2y2EWgJGRsNWVa">
        <img src="/img/spotify-podcast-badge.svg" alt="Listen on Spotify" height="40" />
      </a>
    `;
  }

  return buttonHTML;
}

const podcastListenButton = generatePodcastListenButton();
const container = document.querySelector(".podcast-listen-btn-container");
if (container) {
  container.replaceWith(htmlToElement(podcastListenButton));
}

/* ***** ----------------------------------------------- ***** **
/* ***** Format Build Date to Timeago
/* ***** ----------------------------------------------- ***** */

const buildDateElement = document.getElementById("build-date");
const buildDate = buildDateElement.textContent;
buildDateElement.textContent = format(buildDate);

/* ***** ----------------------------------------------- ***** **
/* ***** Trigger Play Button on Home Page
/* ***** ----------------------------------------------- ***** */

const homePlayButton = document.getElementById("home-play-btn");
const audioPlayer = document.querySelector("#audio-player .podcast-player");

if (homePlayButton && audioPlayer) {
  homePlayButton.addEventListener("click", () => {
    toggleAudio();
  });

  audioPlayer.addEventListener("play", () => {
    updateButtonState(true);
  });

  audioPlayer.addEventListener("pause", () => {
    updateButtonState(false);
  });
}

function toggleAudio() {
  if (audioPlayer.paused) {
    audioPlayer.play();
  } else {
    audioPlayer.pause();
  }

  updateButtonState(!audioPlayer.paused); // Update button state based on the audio player's current paused state
}

function updateButtonState(isPlaying) {
  if (isPlaying) {
    homePlayButton.classList.add("playing");
    homePlayButton.innerHTML = `<i class="fa-solid fa-circle-pause me-2"></i>Pause`;
  } else {
    homePlayButton.classList.remove("playing");
    homePlayButton.innerHTML = `<i class="fa-solid fa-circle-play me-2"></i>Play`;
  }
}

// Dark mode toggle functionality
function initDarkMode() {
  const darkModeToggles = document.querySelectorAll(
    "#dark-mode-toggle, #dark-mode-toggle-lg"
  );
  const body = document.body;
  const isDarkMode = localStorage.getItem("darkMode") === "enabled";

  if (isDarkMode) {
    body.classList.add("dark-mode");
    darkModeToggles.forEach(
      (toggle) => (toggle.innerHTML = '<i class="fa-solid fa-sun"></i>')
    );
  }

  function toggleDarkMode() {
    body.classList.toggle("dark-mode");
    const isDark = body.classList.contains("dark-mode");
    localStorage.setItem("darkMode", isDark ? "enabled" : "disabled");
    darkModeToggles.forEach((toggle) => {
      toggle.innerHTML = isDark
        ? '<i class="fa-solid fa-sun"></i>'
        : '<i class="fa-solid fa-moon"></i>';
    });
  }

  darkModeToggles.forEach((toggle) => {
    toggle.addEventListener("click", toggleDarkMode);
  });
}

// Call the function to initialize dark mode
initDarkMode();

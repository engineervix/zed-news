import "../css/main.scss";

import * as bootstrap from "bootstrap";
import AOS from "aos";
import Plyr from "plyr";
import UAParser from "ua-parser-js";
import sharer from "sharer.js";
import { format } from "timeago.js";
import "aos/dist/aos.css";
import "animate.css/animate.min.css";
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
/* ***** Custom
/* ***** ----------------------------------------------- ***** */

function generatePodcastListenButton() {
  const parser = new UAParser();
  const result = parser.getResult();

  const platform = result.os.name.toLowerCase();
  let buttonHTML = "";

  if (platform === "mac os" || platform === "ios") {
    buttonHTML = `
      <a class="podcast-listen-btn px-4 me-sm-3" href="#">
        <img src="/img/apple-podcasts-badge.svg" alt="Listen on Apple Podcasts" height="40" />
      </a>
    `;
  } else {
    buttonHTML = `
      <a class="podcast-listen-btn px-4 me-sm-3" href="#">
        <img src="/img/google-podcasts-badge.svg" alt="Listen on Google Podcasts" height="38" />
      </a>
    `;
  }

  return buttonHTML;
}

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

const podcastListenButton = generatePodcastListenButton();
const container = document.querySelector(".podcast-listen-btn-container");
if (container) {
  container.replaceWith(htmlToElement(podcastListenButton));
}

const buildDateElement = document.getElementById("build-date");
const buildDate = buildDateElement.textContent;
buildDateElement.textContent = format(buildDate);

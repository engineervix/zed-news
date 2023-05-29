import "../css/main.scss";

import * as bootstrap from "bootstrap";
import AOS from "aos";
import Plyr from "plyr";
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

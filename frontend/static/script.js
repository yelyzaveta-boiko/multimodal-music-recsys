const API_BASE_URL = "http://127.0.0.1:5000/api";

async function fetchSongs() {
    try {
        const response = await fetch(`${API_BASE_URL}/random-songs`);
        const songs = await response.json();
        console.log("Fetched Songs:", songs); 

        const songsContainer = document.getElementById("songs");
        songsContainer.innerHTML = ""; 

        songs.forEach(song => {
            const songItem = document.createElement("div");
            songItem.className = "song-item";
            songItem.innerHTML = `
                <p class="song-title">${song.name} by ${song.artists}</p>
                <div class="song-content">
                    <iframe 
                            class="spotify-embed-small"
                            src="https://open.spotify.com/embed/track/${song.spotify_uri?.split(':')[2]}" 
                            width="100%" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media">
                    </iframe>
                    <div class="slider-container">
                        <input type="range" min="0" max="10" value="5" data-id="${song.id}" class="slider">
                        <span class="slider-value">5</span>
                    </div>
                </div>
            `;
            songsContainer.appendChild(songItem);

            const slider = songItem.querySelector(".slider");
            const sliderValue = songItem.querySelector(".slider-value");

            slider.addEventListener("input", () => {
                // Update slider value dynamically
                sliderValue.textContent = slider.value; 
            });
        });
    } catch (error) {
        console.error("Error fetching songs:", error);
        alert("Failed to fetch songs. Please try again later.");
    }
}

document.getElementById("recommendButton").addEventListener("click", async () => {
    try {
        const sliders = document.querySelectorAll(".slider");
        // Send the user’s ratings for the random songs to the backend
        const ratings = Array.from(sliders).map(slider => ({
            id: slider.dataset.id,
            score: parseInt(slider.value)
        }));

        console.log("User Ratings:", ratings); 

        const response = await fetch(`${API_BASE_URL}/save-ratings`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ratings })
        });

        const saveRatingsData = await response.json();
        console.log("Save Ratings Response:", saveRatingsData); 

        // Fetch recommendations
        const recommendationsResponse = await fetch(`${API_BASE_URL}/recommendations`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });

        const recommendations = await recommendationsResponse.json();
        console.log("Recommendations:", recommendations); 

        const recommendationsContainer = document.getElementById("recommendations");
        recommendationsContainer.innerHTML = "<h2>Recommended Songs</h2>";

        recommendations.forEach(song => {
            if (!song.spotify_uri) {
                console.warn("Missing Spotify URI for song:", song);
                return;
            }

            const recommendationItem = document.createElement("div");
            recommendationItem.className = "song-item";
            recommendationItem.innerHTML = `
                <p class="song-title">${song.name} by ${song.artists}</p>
                <iframe src="https://open.spotify.com/embed/track/${song.spotify_uri.split(':')[2]}" 
                        width="100%" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media">
                </iframe>
            `;
            recommendationsContainer.appendChild(recommendationItem);
        });

        // Feedback button
        const feedbackButton = document.getElementById("openFeedbackButton");
        feedbackButton.style.display = "block";
    } catch (error) {
        console.error("Error fetching recommendations:", error);
        alert("An error occurred while fetching recommendations. Please try again.");
    }
});

// Modal logic
const feedbackModal = document.getElementById("feedbackModal");
const feedbackButton = document.getElementById("openFeedbackButton");
const closeModal = document.getElementById("closeModal");

// Open modal
feedbackButton.addEventListener("click", () => {
    feedbackModal.style.display = "block";
});

// Close modal when close button is clicked
closeModal.addEventListener("click", () => {
    feedbackModal.style.display = "none";
});

// Close modal when clicking outside the modal content
window.addEventListener("click", (event) => {
    if (event.target === feedbackModal) {
        feedbackModal.style.display = "none";
    }
});


document.addEventListener("DOMContentLoaded", fetchSongs);

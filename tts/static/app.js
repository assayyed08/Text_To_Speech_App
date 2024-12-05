document.addEventListener("DOMContentLoaded", () => {
    const elements = {
        textInput: document.getElementById("text-input"),
        highlightBox: document.getElementById("highlight-box"),
        fileInput: document.getElementById("file-upload"),
        submitButton: document.getElementById("submit-btn"),
        resetButton: document.getElementById("reset-btn"),
        startButton: document.getElementById("start-btn"),
        pauseButton: document.getElementById("pause-btn"),
        stopButton: document.getElementById("stop-btn"),
        voiceDropdown: document.getElementById("voice-select"),
        speedSlider: document.getElementById("speed-slider"),
        speedValue: document.getElementById("speed-display"),
        feedback: document.getElementById("feedback-message"),
        visitorCount: document.getElementById("visitorCount"),
    };

    let utterance = null;
    let isPaused = false;

    // Load voices dynamically and populate the dropdown
    const loadVoices = () => {
        const voices = speechSynthesis.getVoices();
        if (!voices.length) {
            console.warn("No voices found. Ensure your browser supports speech synthesis.");
            return;
        }

        elements.voiceDropdown.innerHTML = voices
            .map((voice, index) => `<option value="${index}">${voice.name} (${voice.lang})</option>`)
            .join("");

        console.log("Voices loaded:", voices);
    };

    speechSynthesis.onvoiceschanged = loadVoices;
    loadVoices(); // Initial call to ensure voices are loaded

    // Function to update feedback messages
    const updateFeedback = (message, type = "info") => {
        elements.feedback.textContent = message;
        elements.feedback.className = `alert alert-${type}`;
        elements.feedback.classList.remove("d-none");
    };

    // Hide feedback messages
    const hideFeedback = () => {
        elements.feedback.textContent = "";
        elements.feedback.classList.add("d-none");
    };

    // Fetch visitor count
    fetch("/get-visitor-count/")
        .then(response => response.json())
        .then(data => {
            elements.visitorCount.textContent = `Visitors today: ${data.visitor_count}`;
        })
        .catch(err => {
            console.error("Error fetching visitor count:", err);
            elements.visitorCount.textContent = "Unable to fetch visitor count.";
        });

    // Handle user details submission
    const userDetailsForm = document.getElementById("userDetailsForm");
    userDetailsForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const formData = new FormData(userDetailsForm);

        fetch("/save-user-details/", {
            method: "POST",
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    const modal = bootstrap.Modal.getInstance(document.getElementById("userDetailsModal"));
                    modal.hide();
                } else {
                    alert(data.message);
                }
            })
            .catch(err => console.error("Error saving user details:", err));
    });

    // Submit button: Process text or file
    elements.submitButton.addEventListener("click", async () => {
        const text = elements.textInput.value.trim();
        const file = elements.fileInput.files[0];

        if (!text && !file) {
            updateFeedback("Please provide text or upload a file.", "danger");
            return;
        }

        updateFeedback("Processing...", "info");

        try {
            if (file) {
                const formData = new FormData();
                formData.append("file", file);

                const response = await fetch("/process-file/", {
                    method: "POST",
                    body: formData,
                });

                const data = await response.json();
                if (data.success) {
                    elements.textInput.value = data.text; // Populate extracted text
                    updateFeedback("File processed successfully.", "success");
                } else {
                    updateFeedback(data.message || "File processing failed.", "danger");
                }
            } else if (text) {
                const response = await fetch("/process-text/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text }),
                });

                const data = await response.json();
                if (data.success) {
                    elements.textInput.value = data.text;
                    updateFeedback("Text processed successfully.", "success");
                } else {
                    updateFeedback(data.message || "Text processing failed.", "danger");
                }
            }
        } catch (error) {
            console.error("Error processing request:", error);
            updateFeedback("An error occurred during processing.", "danger");
        }
    });

    // Reset button: Clear inputs and cancel ongoing speech
    elements.resetButton.addEventListener("click", () => {
        elements.textInput.value = "";
        elements.fileInput.value = "";
        elements.speedSlider.value = "200";
        elements.speedValue.textContent = "200";
        elements.highlightBox.textContent = ""; // Clear the highlight box
        hideFeedback();
        speechSynthesis.cancel(); // Cancel any ongoing speech
    });

    // Start button: Begin speech synthesis
    elements.startButton.addEventListener("click", () => {
        const text = elements.textInput.value.trim();
        if (!text) {
            updateFeedback("Please provide text to read.", "danger");
            return;
        }

        speechSynthesis.cancel(); // Cancel any ongoing speech

        utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = elements.speedSlider.value / 100;

        const selectedVoiceIndex = elements.voiceDropdown.value;
        const voices = speechSynthesis.getVoices();
        if (voices[selectedVoiceIndex]) {
            utterance.voice = voices[selectedVoiceIndex];
        }

        utterance.onboundary = (event) => {
            const charIndex = event.charIndex;
            const textAfter = text.slice(charIndex);
            const sentences = textAfter.split(/[.!?]/);
            elements.highlightBox.textContent = sentences[0]?.trim() || "";
        };

        utterance.onend = () => {
            elements.highlightBox.textContent = "Speech completed.";
            updateFeedback("Speech completed.", "success");
        };

        speechSynthesis.speak(utterance);
    });

    // Pause button: Pause or resume speech synthesis
    elements.pauseButton.addEventListener("click", () => {
        if (speechSynthesis.speaking && !isPaused) {
            speechSynthesis.pause();
            isPaused = true;
            updateFeedback("Speech paused.", "warning");
        } else if (isPaused) {
            speechSynthesis.resume();
            isPaused = false;
            updateFeedback("Speech resumed.", "info");
        }
    });

    // Stop button: Stop speech synthesis
    elements.stopButton.addEventListener("click", () => {
        speechSynthesis.cancel();
        elements.highlightBox.textContent = ""; // Clear highlight box
        updateFeedback("Speech stopped.", "info");
    });

    // Speed slider: Update speech rate
    elements.speedSlider.addEventListener("input", () => {
        elements.speedValue.textContent = elements.speedSlider.value;
    });
});

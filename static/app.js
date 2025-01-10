document.addEventListener("DOMContentLoaded", () => {
    const rouletteFeed = document.getElementById("roulette-feed");
    const predictionFeed = document.getElementById("prediction-feed");

    const maxNumbers = 12; // Maximum numbers to display in the live feed

    // Connect to the Socket.IO server
    const socket = io("http://localhost:3000",{
        transports: ["websocket", "polling"],
        reconnection: true,
        reconnectionAttempts: 10,
        reconnectionDelay: 1000,
        timeout: 20000,
        autoConnect: true
    });

    // Listen for updates from the server
    socket.on("rouletteUpdate", (data) => {
        console.log("Received data from server:", data,
            
        ); // Debug log

        const { numbers, predictions } = data;

        // Update the roulette feed with the last 12 numbers
        if (numbers && numbers.length > 0) {
            updateFeed(rouletteFeed, numbers, "");
        }

        // Update the prediction feed with the predicted 3 numbers
        if (predictions && predictions.length > 0) {
            console.log("Updating prediction feed with:", predictions);
            updateFeed(predictionFeed, predictions, "Prediction (Neighbours)", true);
        } else {
            console.log("No predictions received.");
        }
    });

    /**
     * Function to update a feed (e.g., roulette feed or prediction feed).
     * @param {HTMLElement} feedElement - The element to update.
     * @param {Array} items - The numbers or predictions to display.
     * @param {String} title - The title to display for the section.
     * @param {Boolean} isPrediction - Whether this is the prediction feed (for styling).
     */
    function updateFeed(feedElement, items, title, isPrediction = false) {
        // Clear the current feed
        feedElement.innerHTML = "";

        // Display a title for the section
        const titleElement = document.createElement("h3");
        titleElement.textContent = title;
        titleElement.style.textAlign = "center";
        feedElement.appendChild(titleElement);

        // Create a container for the items
        const container = document.createElement("div");
        container.style.display = "flex";
        container.style.justifyContent = "center";
        container.style.gap = "10px";
        container.style.flexWrap = "wrap";

        // Add items as styled elements
        items.forEach((item) => {
            const listItem = document.createElement("div");
            listItem.textContent = item;

            // Apply styling for feed numbers
            if ([1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36].includes(item)) {
                listItem.classList.add("red"); // Red background, white font
            } else if ([2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35].includes(item)) {
                listItem.classList.add("black"); // Black background, white font
            } else if ([0].includes(item)) {
                listItem.classList.add("green");
            }

            // Additional styling for prediction feed
            if (isPrediction) {
                listItem.style.background = "black";
                listItem.style.width = "";
                listItem.style.height = "";
                listItem.style.textAlign = "center"; // Green border for predictions
            }

            listItem.style.padding = "10px";
            listItem.style.borderRadius = "5px";
            listItem.style.fontSize = "1.2em";
            listItem.style.textAlign = "center";

            container.appendChild(listItem);
        });

        feedElement.appendChild(container);
    }
});

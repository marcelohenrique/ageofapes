// Relic data (can be replaced with an API or database)
const relics = [
    {
        id: 1,
        name: "Relic 1",
        image: "antiagingdrink.webp",
        level: 3,
        unit: "Hitter",
        quality: "Rare",
        buff: {
            name: "Attack of Hitters",
            values: [5, 10, 15, 20, 25] // Values for 1 to 5 stars
        },
        displayBuffs: [
            {
                name: "Damage of Hitters",
                values: [1, 3, 5, 7, 10] // Values for 1 to 5 stars
            },
            {
                name: "Attack of Hitters",
                values: [2, 4, 6, 8, 12] // Values for 1 to 5 stars
            }
        ]
    },
    {
        id: 2,
        name: "Relic 2",
        image: "antiagingdrink.webp", // Same image as the first relic
        level: 5,
        unit: "Shooter",
        quality: "Epic",
        buff: {
            name: "Defense of Shooters",
            values: [10, 20, 30, 40, 50] // Values for 1 to 5 stars
        },
        displayBuffs: [
            {
                name: "Damage of Shooters",
                values: [2, 4, 6, 8, 10] // Values for 1 to 5 stars
            },
            {
                name: "Attack of Shooters",
                values: [3, 6, 9, 12, 15] // Values for 1 to 5 stars
            }
        ]
    },
    // Add more relics as needed...
];

// Function to get color based on relic quality
function getQualityColor(quality) {
    switch (quality) {
        case "Rare": return "#d4eaf7"; // Very light blue
        case "Epic": return "#e0d4f7"; // Very light purple
        case "Legendary": return "#faf3d1"; // Very light yellow
        case "Super": return "#f7d4d4"; // Very light red
        default: return "#f9f9f9"; // Default color (light gray)
    }
}

// Function to update stars based on the selected level
function updateStars(starsContainer, level, isHover = false) {
    if (!starsContainer) return;

    starsContainer.innerHTML = ""; // Clear existing stars
    for (let i = 1; i <= 5; i++) {
        const star = document.createElement("i");
        star.classList.add("fas", "fa-star"); // Default to filled star
        if (i > level) {
            star.classList.remove("fas"); // Remove filled star class
            star.classList.add("far"); // Add empty star class
        }
        starsContainer.appendChild(star);
    }
    if (isHover) starsContainer.classList.add("hover-effect");
    else starsContainer.classList.remove("hover-effect");
}

// Function to save the selected level to localStorage
function saveLevelToLocalStorage(relicId, level) {
    localStorage.setItem(`relic-${relicId}-level`, level);
}

// Function to load the selected level from localStorage
function loadLevelFromLocalStorage(relicId) {
    const level = localStorage.getItem(`relic-${relicId}-level`);
    return level ? parseInt(level) : null;
}

// Function to create relic elements
function createRelic(relic, grid) {
    if (!grid) return;

    const relicElement = document.createElement("div");
    relicElement.classList.add("col-md-4", "relic");
    relicElement.style.backgroundColor = getQualityColor(relic.quality);
    relicElement.dataset.id = relic.id; // Add an ID for filtering

    // Add image
    const img = document.createElement("img");
    img.src = relic.image;
    img.alt = relic.name;
    img.classList.add("img-fluid");
    relicElement.appendChild(img);

    // Add stars container
    const starsContainer = document.createElement("div");
    starsContainer.classList.add("stars");
    let currentLevel = loadLevelFromLocalStorage(relic.id) ?? relic.level; // Use saved level or initial level
    updateStars(starsContainer, currentLevel);
    relicElement.appendChild(starsContainer);

    // Add name
    const title = document.createElement("h3");
    title.textContent = relic.name;
    relicElement.appendChild(title);

    // Add unit
    const unit = document.createElement("p");
    unit.textContent = relic.unit;
    relicElement.appendChild(unit);

    // Add buff label
    const buffLabel = document.createElement("p");
    buffLabel.textContent = "Buff:";
    buffLabel.classList.add("buff-label");
    relicElement.appendChild(buffLabel);

    // Add buff information
    const buff = document.createElement("p");
    const buffValue = relic.buff.values[currentLevel - 1] ?? 0;
    buff.innerHTML = `${relic.buff.name} <span class="buff-green">${buffValue}%</span>`;
    buff.classList.add("buff-value");
    relicElement.appendChild(buff);

    // Add Display Buffs
    const displayBuffsLabel = document.createElement("p");
    displayBuffsLabel.textContent = "Display Buffs:";
    displayBuffsLabel.classList.add("buff-label");
    relicElement.appendChild(displayBuffsLabel);

    relic.displayBuffs.forEach(displayBuff => {
        const displayBuffElement = document.createElement("p");
        const displayBuffValue = displayBuff.values[currentLevel - 1] ?? 0;
        displayBuffElement.innerHTML = `${displayBuff.name} <span class="buff-green">${displayBuffValue}%</span>`;
        displayBuffElement.classList.add("buff-value");
        relicElement.appendChild(displayBuffElement);
    });

    // Add hover and click events for star selection
    starsContainer.addEventListener("mouseover", (event) => {
        if (event.target.tagName === "I") {
            const hoveredStar = event.target;
            const stars = Array.from(starsContainer.children);
            const hoveredIndex = stars.indexOf(hoveredStar);
            updateStars(starsContainer, hoveredIndex + 1, true); // Temporary preview
        }
    });

    starsContainer.addEventListener("mouseout", () => {
        updateStars(starsContainer, currentLevel); // Revert to selected level
    });

    starsContainer.addEventListener("click", (event) => {
        if (event.target.tagName === "I") {
            const clickedStar = event.target;
            const stars = Array.from(starsContainer.children);
            const clickedIndex = stars.indexOf(clickedStar);
            let newLevel = clickedIndex + 1;

            // Toggle the first star: if clicked again, set level to 0
            if (newLevel === 1 && currentLevel === 1) {
                newLevel = 0;
            }

            // Update the level and save to localStorage
            currentLevel = newLevel;
            updateStars(starsContainer, currentLevel);
            saveLevelToLocalStorage(relic.id, currentLevel);

            // Update the buff value
            const buffValue = relic.buff.values[currentLevel - 1] ?? 0;
            buff.innerHTML = `${relic.buff.name} <span class="buff-green">${buffValue}%</span>`;

            // Update the display buffs
            relic.displayBuffs.forEach((displayBuff, index) => {
                const displayBuffValue = displayBuff.values[currentLevel - 1] ?? 0;
                relicElement.querySelectorAll(".buff-value")[index + 1].innerHTML = `${displayBuff.name} <span class="buff-green">${displayBuffValue}%</span>`;
            });
        }
    });

    // Add click event to move the relic
    relicElement.addEventListener("click", (event) => {
        // Prevent moving the relic if the click is on the stars
        if (!event.target.classList.contains("stars")) {
            // Check the current grid of the relic
            const currentGrid = relicElement.parentElement;

            // Set the target grid based on the current grid
            const targetGrid = currentGrid.id === "available-relics-grid" ? selectedRelicsGrid : availableRelicsGrid;

            // Move the relic to the target grid
            moveRelic(relicElement, targetGrid);
        }
    });

    grid.appendChild(relicElement);
}

// Function to create a placeholder card
function createPlaceholder() {
    const placeholder = document.createElement("div");
    placeholder.classList.add("col-md-4", "placeholder-card");

    const relicElement = document.createElement("div");
    relicElement.classList.add("relic", "placeholder");

    // Circle with plus symbol
    const placeholderCircle = document.createElement("div");
    placeholderCircle.classList.add("placeholder-circle");
    const plusIcon = document.createElement("i");
    plusIcon.classList.add("fas", "fa-plus");
    placeholderCircle.appendChild(plusIcon);
    relicElement.appendChild(placeholderCircle);

    // Stars
    const starsContainer = document.createElement("div");
    starsContainer.classList.add("stars", "placeholder-stars");
    for (let i = 0; i < 5; i++) {
        const star = document.createElement("i");
        star.classList.add("far", "fa-star");
        starsContainer.appendChild(star);
    }
    relicElement.appendChild(starsContainer);

    // Placeholder text
    const title = document.createElement("h3");
    title.textContent = "No Relic Selected";
    title.classList.add("placeholder-text");
    relicElement.appendChild(title);

    const unit = document.createElement("p");
    unit.textContent = "Unit: ---";
    unit.classList.add("placeholder-text");
    relicElement.appendChild(unit);

    const buffLabel = document.createElement("p");
    buffLabel.textContent = "Buff:";
    buffLabel.classList.add("buff-label", "placeholder-text");
    relicElement.appendChild(buffLabel);

    const buff = document.createElement("p");
    buff.innerHTML = `<span class="buff-green">---</span>`;
    buff.classList.add("buff-value", "placeholder-text");
    relicElement.appendChild(buff);

    const displayBuffsLabel = document.createElement("p");
    displayBuffsLabel.textContent = "Display Buffs:";
    displayBuffsLabel.classList.add("buff-label", "placeholder-text");
    relicElement.appendChild(displayBuffsLabel);

    const displayBuff = document.createElement("p");
    displayBuff.innerHTML = `<span class="buff-green">---</span>`;
    displayBuff.classList.add("buff-value", "placeholder-text");
    relicElement.appendChild(displayBuff);

    placeholder.appendChild(relicElement);
    return placeholder;
}

// Function to initialize placeholders
function initializePlaceholders() {
    const selectedRelicsGrid = document.getElementById("selected-relics-grid");
    for (let i = 0; i < 18; i++) {
        const placeholder = createPlaceholder();
        selectedRelicsGrid.appendChild(placeholder);
    }
}

// Function to move a relic from one grid to another
function moveRelic(relic, targetGrid) {
    if (!relic || !targetGrid) return;

    const sourceGrid = relic.parentElement;
    if (sourceGrid === targetGrid) return; // Avoid moving to the same grid

    // Find the first placeholder in the target grid
    const placeholder = targetGrid.querySelector(".placeholder-card");

    if (placeholder) {
        // Replace the placeholder with the relic
        targetGrid.replaceChild(relic, placeholder);
    } else {
        // Add the relic to the target grid
        targetGrid.appendChild(relic);
    }

    // If the relic was moved from the selected relics grid to the available relics grid,
    // we need to add a new placeholder to the selected relics grid.
    if (sourceGrid.id === "selected-relics-grid" && targetGrid.id === "available-relics-grid") {
        const newPlaceholder = createPlaceholder();
        sourceGrid.appendChild(newPlaceholder);
    }
}

// Function to filter relics based on selected unit and quality
function filterRelics() {
    const unitFilter = document.getElementById("unit-filter").value;
    const qualityFilter = document.getElementById("quality-filter").value;

    const availableRelicsGrid = document.getElementById("available-relics-grid");
    const selectedRelicsGrid = document.getElementById("selected-relics-grid");

    // Clear the available relics grid before applying filters
    availableRelicsGrid.innerHTML = "";

    // Filter relics based on selected criteria
    relics.forEach(relic => {
        const matchesUnit = unitFilter === "all" || relic.unit === unitFilter;
        const matchesQuality = qualityFilter === "all" || relic.quality === qualityFilter;

        if (matchesUnit && matchesQuality) {
            // Check if the relic is already in the selected relics grid
            const isSelected = Array.from(selectedRelicsGrid.children).some(child => child.dataset.id === relic.id.toString());

            if (!isSelected) {
                createRelic(relic, availableRelicsGrid);
            }
        }
    });
}

// Add change events to filters
document.getElementById("unit-filter").addEventListener("change", filterRelics);
document.getElementById("quality-filter").addEventListener("change", filterRelics);

// Add reset button functionality
document.getElementById("reset-button").addEventListener("click", () => {
    localStorage.clear();
    const selectedRelicsGrid = document.getElementById("selected-relics-grid");
    selectedRelicsGrid.innerHTML = "";
    initializePlaceholders(); // Reinitialize placeholders
    filterRelics();
});

// Initialize grids when the page loads
const availableRelicsGrid = document.getElementById("available-relics-grid");
const selectedRelicsGrid = document.getElementById("selected-relics-grid");

function initializeGrids() {
    initializePlaceholders(); // Initialize placeholders
    filterRelics(); // Apply filters when the page loads
}

window.onload = initializeGrids;
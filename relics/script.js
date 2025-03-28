// Load relics data from external JSON file
let relics = [];

async function loadRelics() {
    try {
        const response = await fetch('converted_relics.json');
        relics = await response.json();
        filterRelics();
    } catch (error) {
        console.error("Error loading relics:", error);
    }
}

function getQualityColor(quality) {
    switch (quality) {
        case "Basic": return "#d4f7e2";  // Light green
        case "Rare": return "#d4eaf7";   // Light blue (unchanged)
        case "Epic": return "#e0d4f7";   // Light purple (unchanged)
        case "Legendary": return "#faf3d1"; // Light yellow (unchanged)
        case "Super": return "#f7d4d4";  // Light red (unchanged)
        default: return "#f9f9f9";       // Default light gray (unchanged)
    }
}

function updateStars(starsContainer, currentLevel, maxLevel = 5, isHover = false) {
    if (!starsContainer) return;
    
    starsContainer.innerHTML = "";
    for (let i = 1; i <= maxLevel; i++) {
        const star = document.createElement("i");
        star.classList.add(i <= currentLevel ? "fas" : "far", "fa-star");
        starsContainer.appendChild(star);
    }
    if (isHover) starsContainer.classList.add("hover-effect");
    else starsContainer.classList.remove("hover-effect");
}

function saveLevelToLocalStorage(relicId, level) {
    localStorage.setItem(`relic-${relicId}-level`, level);
}

function loadLevelFromLocalStorage(relic) {
    const storedLevel = localStorage.getItem(`relic-${relic.id}-level`);
    if (storedLevel !== null) return parseInt(storedLevel);
    
    // Default levels based on quality
    switch (relic.quality) {
        case "Basic": return 3;
        case "Rare": return 4;
        default: return 5; // Epic, Legendary, Super
    }
}

function createRelic(relic, grid) {
    if (!grid) return;

    const relicElement = document.createElement("div");
    relicElement.classList.add("col-md-4", "relic");
    relicElement.style.backgroundColor = getQualityColor(relic.quality);
    relicElement.dataset.id = relic.id;

    const img = document.createElement("img");
    img.src = relic.image;
    img.alt = relic.name;
    img.classList.add("img-fluid");
    relicElement.appendChild(img);

    const starsContainer = document.createElement("div");
    starsContainer.classList.add("stars");
    
    // Determine max level based on quality
    const maxLevel = relic.quality === "Basic" ? 3 : 
                     relic.quality === "Rare" ? 4 : 5;
    
    let currentLevel = loadLevelFromLocalStorage(relic);
    updateStars(starsContainer, currentLevel, maxLevel);
    relicElement.appendChild(starsContainer);

    const title = document.createElement("h3");
    title.textContent = relic.name;
    relicElement.appendChild(title);

    const unit = document.createElement("p");
    unit.textContent = relic.unit;
    relicElement.appendChild(unit);

    // Display Buffs only
    if (relic.displayBuffs && relic.displayBuffs.length > 0) {
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
    }

    starsContainer.addEventListener("mouseover", (event) => {
        if (event.target.tagName === "I") {
            const hoveredStar = event.target;
            const stars = Array.from(starsContainer.children);
            const hoveredIndex = stars.indexOf(hoveredStar);
            updateStars(starsContainer, hoveredIndex + 1, maxLevel, true);
        }
    });
    
    starsContainer.addEventListener("mouseout", () => {
        updateStars(starsContainer, currentLevel, maxLevel);
    });

    starsContainer.addEventListener("click", (event) => {
        if (event.target.tagName === "I") {
            const clickedStar = event.target;
            const stars = Array.from(starsContainer.children);
            const clickedIndex = stars.indexOf(clickedStar);
            let newLevel = clickedIndex + 1;
    
            // Toggle off if clicking current level
            if (newLevel === currentLevel) {
                newLevel = 0;
            }
            // Don't exceed max level
            else if (newLevel > maxLevel) {
                newLevel = maxLevel;
            }
    
            currentLevel = newLevel;
            updateStars(starsContainer, currentLevel, maxLevel);
            saveLevelToLocalStorage(relic.id, currentLevel);
    
            // Update display buffs
            if (relic.displayBuffs && relic.displayBuffs.length > 0) {
                relic.displayBuffs.forEach((displayBuff, index) => {
                    const displayBuffValue = currentLevel > 0 ? (displayBuff.values[currentLevel - 1] ?? 0) : 0;
                    relicElement.querySelectorAll(".buff-value")[index].innerHTML = 
                        `${displayBuff.name} <span class="buff-green">${displayBuffValue}%</span>`;
                });
            }
        }
    });

    relicElement.addEventListener("click", (event) => {
        if (!event.target.classList.contains("stars")) {
            const currentGrid = relicElement.parentElement;
            const targetGrid = currentGrid.id === "available-relics-grid" ? 
                selectedRelicsGrid : availableRelicsGrid;
            moveRelic(relicElement, targetGrid);
        }
    });

    grid.appendChild(relicElement);
}

function createPlaceholder() {
    const placeholder = document.createElement("div");
    placeholder.classList.add("col-md-4", "placeholder-card");

    const relicElement = document.createElement("div");
    relicElement.classList.add("relic", "placeholder");

    const placeholderCircle = document.createElement("div");
    placeholderCircle.classList.add("placeholder-circle");
    const plusIcon = document.createElement("i");
    plusIcon.classList.add("fas", "fa-plus");
    placeholderCircle.appendChild(plusIcon);
    relicElement.appendChild(placeholderCircle);

    const starsContainer = document.createElement("div");
    starsContainer.classList.add("stars", "placeholder-stars");
    for (let i = 0; i < 5; i++) {
        const star = document.createElement("i");
        star.classList.add("far", "fa-star");
        starsContainer.appendChild(star);
    }
    relicElement.appendChild(starsContainer);

    const title = document.createElement("h3");
    title.textContent = "No Relic Selected";
    title.classList.add("placeholder-text");
    relicElement.appendChild(title);

    const unit = document.createElement("p");
    unit.textContent = "Unit: ---";
    unit.classList.add("placeholder-text");
    relicElement.appendChild(unit);

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

function initializePlaceholders() {
    const selectedRelicsGrid = document.getElementById("selected-relics-grid");
    for (let i = 0; i < 18; i++) {
        const placeholder = createPlaceholder();
        selectedRelicsGrid.appendChild(placeholder);
    }
}

function moveRelic(relic, targetGrid) {
    if (!relic || !targetGrid) return;

    const sourceGrid = relic.parentElement;
    if (sourceGrid === targetGrid) return;

    const placeholder = targetGrid.querySelector(".placeholder-card");

    if (placeholder) {
        targetGrid.replaceChild(relic, placeholder);
    } else {
        targetGrid.appendChild(relic);
    }

    if (sourceGrid.id === "selected-relics-grid" && targetGrid.id === "available-relics-grid") {
        const newPlaceholder = createPlaceholder();
        sourceGrid.appendChild(newPlaceholder);
    }

    updateBuffSummary();
}

function filterRelics() {
    const menuUnitFilter = document.getElementById("menu-unit-filter").value;
    const menuQualityFilter = document.getElementById("menu-quality-filter").value;

    const availableRelicsGrid = document.getElementById("available-relics-grid");
    const selectedRelicsGrid = document.getElementById("selected-relics-grid");

    availableRelicsGrid.innerHTML = "";

    relics.forEach(relic => {
        const matchesUnit = menuUnitFilter === "all" || relic.unit === menuUnitFilter;
        const matchesQuality = menuQualityFilter === "all" || relic.quality === menuQualityFilter;

        if (matchesUnit && matchesQuality) {
            const isSelected = Array.from(selectedRelicsGrid.children).some(child => 
                child.dataset.id === relic.id.toString());
            if (!isSelected) {
                createRelic(relic, availableRelicsGrid);
            }
        }
    });
}

function calculateTotalBuffs() {
    const selectedRelicsGrid = document.getElementById("selected-relics-grid");
    const buffs = {};

    Array.from(selectedRelicsGrid.children).forEach(relicElement => {
        if (!relicElement.classList.contains("placeholder-card") && relicElement.dataset.id) {
            const relicId = parseInt(relicElement.dataset.id);
            const relic = relics.find(r => r.id === relicId);
            const level = loadLevelFromLocalStorage(relicId) || relic.level;

            if (relic.buff) {
                const buffValue = relic.buff.values[level - 1] || 0;
                buffs[relic.buff.name] = (buffs[relic.buff.name] || 0) + buffValue;
            }

            relic.displayBuffs?.forEach(displayBuff => {
                const displayBuffValue = displayBuff.values[level - 1] || 0;
                buffs[displayBuff.name] = (buffs[displayBuff.name] || 0) + displayBuffValue;
            });
        }
    });

    return buffs;
}

function updateBuffSummary() {
    const buffSummary = document.getElementById("buff-summary");
    const buffs = calculateTotalBuffs();

    buffSummary.innerHTML = '';

    if (Object.keys(buffs).length === 0) {
        buffSummary.innerHTML = '<p class="text-muted">No relics selected.</p>';
        return;
    }

    const sortedBuffs = Object.keys(buffs).sort();

    sortedBuffs.forEach(buffName => {
        const buffItem = document.createElement("div");
        buffItem.classList.add("buff-summary-item");

        const nameSpan = document.createElement("span");
        nameSpan.classList.add("buff-summary-name");
        nameSpan.textContent = buffName;

        const valueSpan = document.createElement("span");
        valueSpan.classList.add("buff-summary-value");
        valueSpan.textContent = `${buffs[buffName]}%`;

        buffItem.appendChild(nameSpan);
        buffItem.appendChild(valueSpan);
        buffSummary.appendChild(buffItem);
    });
}

// Floating Filter Functionality
const floatingFilterButton = document.getElementById('floating-filter-button');
const filterMenu = document.getElementById('filter-menu');
const menuUnitFilter = document.getElementById('menu-unit-filter');
const menuQualityFilter = document.getElementById('menu-quality-filter');
const menuResetButton = document.getElementById('menu-reset-button');

// Toggle filter menu
floatingFilterButton.addEventListener('click', (e) => {
    e.stopPropagation();
    filterMenu.classList.toggle('show');
});

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    if (!filterMenu.contains(e.target)) {
        filterMenu.classList.remove('show');
    }
});

// Sync filters with main filters
menuUnitFilter.addEventListener('change', () => {
    // document.getElementById('unit-filter').value = menuUnitFilter.value;
    filterRelics();
    filterMenu.classList.remove('show');
});

menuQualityFilter.addEventListener('change', () => {
    // document.getElementById('quality-filter').value = menuQualityFilter.value;
    filterRelics();
    filterMenu.classList.remove('show');
});

menuResetButton.addEventListener('click', () => {
    // document.getElementById('unit-filter').value = 'all';
    // document.getElementById('quality-filter').value = 'all';
    menuUnitFilter.value = 'all';
    menuQualityFilter.value = 'all';
    filterRelics();
    filterMenu.classList.remove('show');
});

// // Initialize menu filters to match main filters
// function syncMenuFilters() {
//     menuUnitFilter.value = document.getElementById('unit-filter').value;
//     menuQualityFilter.value = document.getElementById('quality-filter').value;
// }

const availableRelicsGrid = document.getElementById("available-relics-grid");
const selectedRelicsGrid = document.getElementById("selected-relics-grid");

function initializeGrids() {
    loadRelics();
    initializePlaceholders();
    filterRelics();
    // syncMenuFilters();
}

window.onload = initializeGrids;
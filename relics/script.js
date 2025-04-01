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
        case "Basic": return "#d4f7e2";
        case "Rare": return "#d4eaf7";
        case "Epic": return "#e0d4f7";
        case "Legendary": return "#faf3d1";
        case "Super": return "#f7d4d4";
        default: return "#f9f9f9";
    }
}

function saveLevelToLocalStorage(relicId, level) {
    localStorage.setItem(`relic-${relicId}-level`, level);
}

function loadLevelFromLocalStorage(relic) {
    const storedLevel = localStorage.getItem(`relic-${relic.id}-level`);
    if (storedLevel !== null) return parseInt(storedLevel);
    
    switch (relic.quality) {
        case "Basic": return 3;
        case "Rare": return 4;
        default: return 5;
    }
}

function updateRelicBuffs(relicElement, relic, level) {
    if (!relic.displayBuffs) return;
    
    const buffElements = relicElement.querySelectorAll('.buff-value');
    relic.displayBuffs.forEach((buff, index) => {
        if (buffElements[index]) {
            const value = level > 0 ? (buff.values[level - 1] ?? 0) : 0;
            const uomDisplay = buff.uom === '%' ? buff.uom : '';
            buffElements[index].innerHTML = `
                ${buff.name} <span class="buff-green">${value}${uomDisplay}</span>
            `;
        }
    });
}

function createRelic(relic, grid) {
    if (!grid) return;

    const relicElement = document.createElement("div");
    relicElement.classList.add("col-md-4", "relic");
    relicElement.style.backgroundColor = getQualityColor(relic.quality);
    relicElement.dataset.id = relic.id;

    // Create relic image
    const img = document.createElement("img");
    img.src = relic.image;
    img.alt = relic.name;
    img.classList.add("img-fluid");
    relicElement.appendChild(img);

    // Create stars container
    const starsContainer = document.createElement("div");
    starsContainer.classList.add("stars");
    
    const maxLevel = relic.quality === "Basic" ? 3 : 
                     relic.quality === "Rare" ? 4 : 5;
    let currentLevel = loadLevelFromLocalStorage(relic);

    // Create stars
    for (let i = 1; i <= maxLevel; i++) {
        const star = document.createElement("i");
        star.classList.add(i <= currentLevel ? "fas" : "far", "fa-star");
        starsContainer.appendChild(star);
    }
    relicElement.appendChild(starsContainer);

    // Add click handlers to each star
    starsContainer.querySelectorAll('i').forEach((star, index) => {
        star.addEventListener('click', (event) => {
            event.stopPropagation();
            event.stopImmediatePropagation();
            
            const clickedLevel = index + 1;
            currentLevel = clickedLevel === currentLevel ? 0 : clickedLevel;
            
            // Update star display
            starsContainer.querySelectorAll('i').forEach((s, i) => {
                s.classList.toggle('fas', i < currentLevel);
                s.classList.toggle('far', i >= currentLevel);
            });
            
            // Save and update
            saveLevelToLocalStorage(relic.id, currentLevel);
            updateRelicBuffs(relicElement, relic, currentLevel);
            updateBuffSummary();
        });
    });

    // Create relic title
    const title = document.createElement("h3");
    title.textContent = relic.name;
    relicElement.appendChild(title);

    // Create unit type display
    const unit = document.createElement("p");
    unit.textContent = relic.unit;
    relicElement.appendChild(unit);

    // Create display buffs
    if (relic.displayBuffs && relic.displayBuffs.length > 0) {
        const displayBuffsLabel = document.createElement("p");
        displayBuffsLabel.textContent = "Display Buffs:";
        displayBuffsLabel.classList.add("buff-label");
        relicElement.appendChild(displayBuffsLabel);

        relic.displayBuffs.forEach(displayBuff => {
            const displayBuffElement = document.createElement("p");
            displayBuffElement.classList.add("buff-value");
            relicElement.appendChild(displayBuffElement);
        });
        
        // Initialize buffs
        updateRelicBuffs(relicElement, relic, currentLevel);
    }

    // Relic click handler (excluding stars)
    relicElement.addEventListener('click', (event) => {
        if (event.target.closest('.stars')) return;
        
        const currentGrid = relicElement.parentElement;
        const targetGrid = currentGrid.id === "available-relics-grid" 
            ? document.getElementById("selected-relics-grid") 
            : document.getElementById("available-relics-grid");
        
        moveRelic(relicElement, targetGrid);
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
            const level = loadLevelFromLocalStorage(relic);

            relic.displayBuffs?.forEach(displayBuff => {
                const buffKey = `${displayBuff.name}${displayBuff.uom ? ` (${displayBuff.uom})` : ''}`;
                const displayBuffValue = displayBuff.values[level - 1] || 0;
                buffs[buffKey] = (buffs[buffKey] || 0) + displayBuffValue;
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
        
        // Check if the buff name ends with a unit of measure
        const hasUOM = /\(([^)]+)\)$/.test(buffName);
        valueSpan.textContent = buffs[buffName] + (hasUOM ? '' : '%');

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

floatingFilterButton.addEventListener('click', (e) => {
    e.stopPropagation();
    filterMenu.classList.toggle('show');
});

document.addEventListener('click', (e) => {
    if (!filterMenu.contains(e.target)) {
        filterMenu.classList.remove('show');
    }
});

menuUnitFilter.addEventListener('change', () => {
    filterRelics();
    filterMenu.classList.remove('show');
});

menuQualityFilter.addEventListener('change', () => {
    filterRelics();
    filterMenu.classList.remove('show');
});

menuResetButton.addEventListener('click', () => {
    menuUnitFilter.value = 'all';
    menuQualityFilter.value = 'all';
    filterRelics();
    filterMenu.classList.remove('show');
});

function initializeGrids() {
    loadRelics();
    initializePlaceholders();
    filterRelics();
}

window.onload = initializeGrids;
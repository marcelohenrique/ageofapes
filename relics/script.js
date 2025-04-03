let relics = [];

async function loadRelics() {
    try {
        const response = await fetch('converted_relics.json');
        relics = await response.json();
        return relics;
    } catch (error) {
        console.error("Error loading relics:", error);
        return [];
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

            // Only process displayBuffs (ignore main relic.buff)
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
        
        // Extract base buff name (remove parenthesized units if they exist)
        const baseName = buffName.replace(/\s*\([^)]*\)$/, '');
        nameSpan.textContent = baseName;

        const valueSpan = document.createElement("span");
        valueSpan.classList.add("buff-summary-value");
        
        // Check if buffName ends with "(%)" to determine if we should show % symbol
        const shouldShowPercent = buffName.endsWith("(%)");
        // Or check if it has any parenthesized unit (for backward compatibility)
        const hasUOM = /\(([^)]+)\)$/.test(buffName);
        
        // Show unit only if it's % or if there are no parentheses (matching card behavior)
        if (shouldShowPercent) {
            valueSpan.textContent = buffs[buffName] + '%';
        } else if (!hasUOM) {
            // If no parentheses, show raw value (matching card behavior)
            valueSpan.textContent = buffs[buffName];
        } else {
            // If has parentheses but not %, show raw value (matching card behavior)
            valueSpan.textContent = buffs[buffName];
        }

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
    if (filterMenu.classList.contains('show')) {
        buffMenu.classList.remove('show');
    }
});

// Buff Summary Floating Button Functionality
const floatingBuffButton = document.getElementById('floating-buff-button');
const buffMenu = document.getElementById('buff-menu');

floatingBuffButton.addEventListener('click', (e) => {
    e.stopPropagation();
    buffMenu.classList.toggle('show');
    if (buffMenu.classList.contains('show')) {
        filterMenu.classList.remove('show');
    }
});

document.addEventListener('click', (e) => {
    if (!filterMenu.contains(e.target)) {
        filterMenu.classList.remove('show');
    }
    if (!buffMenu.contains(e.target)) {
        buffMenu.classList.remove('show');
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

// Share functionality
function setupShareButton() {
    const shareButton = document.getElementById('floating-share-button');
    const shareMenu = document.getElementById('share-menu');
    const copyButton = document.getElementById('copy-share-link');
    const closeButton = document.getElementById('close-share-menu');
    const shareUrlInput = document.querySelector('.share-url');

    shareButton.addEventListener('click', (e) => {
        e.stopPropagation();
        shareMenu.classList.toggle('show');
        document.getElementById('filter-menu').classList.remove('show');
        document.getElementById('buff-menu').classList.remove('show');
        
        // Get all relic IDs in their original order
        const allRelicIds = relics.map(relic => relic.id);
        const maxId = Math.max(...allRelicIds);
        
        // Create a binary representation
        const selectedRelics = Array.from(document.getElementById('selected-relics-grid').children)
            .filter(el => !el.classList.contains('placeholder-card'))
            .map(el => parseInt(el.dataset.id));
        
        // Create binary mask (1 for selected, 0 for not selected)
        let binaryValue = 0;
        for (let i = 0; i < allRelicIds.length; i++) {
            if (selectedRelics.includes(allRelicIds[i])) {
                binaryValue |= (1 << i); // Set the bit at position i
            }
        }
        
        const shareUrl = `${window.location.origin}${window.location.pathname}?s=${binaryValue}`;
        shareUrlInput.value = shareUrl;
    });

    copyButton.addEventListener('click', () => {
        shareUrlInput.select();
        document.execCommand('copy');
        alert('Link copied to clipboard!');
    });

    closeButton.addEventListener('click', () => {
        shareMenu.classList.remove('show');
    });
}

function loadStateFromURL() {
    const params = new URLSearchParams(window.location.search);
    const stateParam = params.get('s');
    
    if (stateParam) {
        try {
            const binaryValue = parseInt(stateParam);
            const allRelicIds = relics.map(relic => relic.id);
            
            // Clear current selections
            const selectedGrid = document.getElementById('selected-relics-grid');
            selectedGrid.innerHTML = '';
            
            // Find which relics are selected
            const selectedRelics = [];
            for (let i = 0; i < allRelicIds.length; i++) {
                if (binaryValue & (1 << i)) {
                    selectedRelics.push(allRelicIds[i]);
                }
            }
            
            // Load selected relics
            selectedRelics.forEach(relicId => {
                const relicData = relics.find(r => r.id === relicId);
                if (relicData) {
                    createRelic(relicData, selectedGrid);
                }
            });
            
            // Fill with placeholders if needed
            while (selectedGrid.children.length < 18) {
                selectedGrid.appendChild(createPlaceholder());
            }
            
            updateBuffSummary();
        } catch (e) {
            console.error('Error loading state:', e);
        }
    }
}

function setRelicLevel(element, level) {
    const stars = element.querySelectorAll('.stars i');
    stars.forEach((star, i) => {
        star.classList.toggle('fas', i < level);
        star.classList.toggle('far', i >= level);
    });
    
    const relic = relics.find(r => r.id.toString() === element.dataset.id);
    if (relic) {
        saveLevelToLocalStorage(relic.id, level);
        updateRelicBuffs(element, relic, level);
    }
}

function initializeGrids() {
    loadRelics().then(() => {
        initializePlaceholders();
        filterRelics();
        loadStateFromURL();
        setupShareButton();
    });
}

window.onload = initializeGrids;
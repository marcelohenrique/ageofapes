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
    const selectedGrid = document.getElementById('selected-relics-grid');
    const availableGrid = document.getElementById('available-relics-grid');
    
    // Verifica se está tentando adicionar além do limite
    if (targetGrid === selectedGrid) {
        const currentCount = selectedGrid.querySelectorAll('.relic[data-id]').length;
        
        if (currentCount >= 18) {  // 
            // Feedback visualAlterado aqui
            relic.classList.add('relic-shake');
            setTimeout(() => relic.classList.remove('relic-shake'), 500);
            
            // Mostra alerta
            showLimitAlert();
            return;
        }
    }
    
    // Lógica de mover relíquia
    const sourceGrid = relic.parentElement;
    if (sourceGrid === targetGrid) return;

    // Remove da grade de origem
    sourceGrid.removeChild(relic);
    
    // Adiciona na grade de destino (substituindo placeholder se existir)
    const placeholder = targetGrid.querySelector(".placeholder-card");

    if (placeholder) {
        targetGrid.replaceChild(relic, placeholder);
    } else {
        targetGrid.appendChild(relic);
    }
    
    // Recria placeholder na grade de origem SE estiver saindo da grade selecionada
    if (sourceGrid === selectedGrid) {
        const newPlaceholder = createPlaceholder();
        sourceGrid.appendChild(newPlaceholder);
    }
    
    // Atualizações necessárias
    updateBuffSummary();
    updatePlaceholders();
}

// ========== NOVAS FUNÇÕES ADICIONADAS ========== //
function showLimitAlert() {
    const existingAlert = document.querySelector('.limit-alert');
    if (existingAlert) existingAlert.remove();
    
    const alert = document.createElement('div');
    alert.className = 'limit-alert alert alert-warning';
    alert.textContent = 'Limite de 18 relíquias atingido!';
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 2500);
}

function updatePlaceholders() {
    const selectedCount = document.getElementById('selected-relics-grid')
        .querySelectorAll('.relic[data-id]').length;
    
    document.querySelectorAll('.placeholder-card').forEach(ph => {
        ph.style.opacity = selectedCount >= 18 ? '0.3' : '0.7';
        ph.style.pointerEvents = selectedCount >= 18 ? 'none' : 'auto';
    });
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
    
    // Atualiza o contador
    const count = document.getElementById('selected-relics-grid')
        .querySelectorAll('.relic[data-id]').length;
    
    const counter = document.getElementById('selected-count');
    counter.textContent = count;
    counter.style.color = count >= 18 ? '#dc3545' : '#28a745';
    
    updatePlaceholders();
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

// Função para codificar as relíquias selecionadas
function encodeSelectedRelics(selectedIds) {
    // Converter para JSON e depois para Base64
    const jsonString = JSON.stringify(selectedIds);
    return btoa(unescape(encodeURIComponent(jsonString)));
}

// Função para decodificar
function decodeSelectedRelics(base64) {
    try {
        const jsonString = decodeURIComponent(escape(atob(base64)));
        return JSON.parse(jsonString);
    } catch (e) {
        console.error("Decoding error:", e);
        return [];
    }
}

// Função para codificar todos os níveis
function encodeAllLevels(relics) {
    // Criar array de níveis (índice = ID da relíquia)
    const maxId = Math.max(...relics.map(r => r.id));
    const levelsArray = new Array(maxId + 1).fill(0);
    
    relics.forEach(relic => {
        levelsArray[relic.id] = loadLevelFromLocalStorage(relic);
    });

    // Converter para string binária (3 bits por nível)
    let binaryString = '';
    levelsArray.forEach(level => {
        binaryString += level.toString(2).padStart(3, '0');
    });

    // Converter para Base64
    const bytes = [];
    for (let i = 0; i < binaryString.length; i += 8) {
        bytes.push(parseInt(binaryString.substr(i, 8), 2));
    }
    return btoa(String.fromCharCode(...bytes));
}

// Função para decodificar
function decodeAllLevels(base64, relics) {
    try {
        // Converter Base64 para string binária
        const binaryString = atob(base64).split('')
            .map(char => char.charCodeAt(0).toString(2).padStart(8, '0'))
            .join('');

        // Extrair níveis (3 bits cada)
        const levels = {};
        for (let i = 0; i < binaryString.length; i += 3) {
            const levelBits = binaryString.substr(i, 3);
            if (levelBits.length === 3) {
                const level = parseInt(levelBits, 2);
                const relicId = Math.floor(i / 3);
                levels[relicId] = level;
            }
        }

        return levels;
    } catch (e) {
        console.error("Erro ao decodificar níveis:", e);
        return {};
    }
}

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
        
        // Obter IDs das relíquias selecionadas EM ORDEM
        const selectedRelics = Array.from(document.getElementById('selected-relics-grid').children)
            .filter(el => !el.classList.contains('placeholder-card'))
            .map(el => parseInt(el.dataset.id));
        
        // Codificar para Base64
        const params = new URLSearchParams();
        if (selectedRelics.length > 0) {
            params.set('s', encodeSelectedRelics(selectedRelics));
        }
        params.set('l', encodeAllLevels(relics));
        
        shareUrlInput.value = `${window.location.origin}${window.location.pathname}?${params.toString()}`;
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
    
    // Carregar níveis primeiro
    const levelsParam = params.get('l');
    if (levelsParam) {
        const levels = decodeAllLevels(levelsParam, relics);
        relics.forEach(relic => {
            if (levels[relic.id] !== undefined) {
                saveLevelToLocalStorage(relic.id, levels[relic.id]);
            }
        });
    }

    // Depois carregar seleções (código anterior)
    const stateParam = params.get('s');
    
    if (stateParam) {
        try {
            // Decodificar a string Base64
            const selectedIds = decodeSelectedRelics(stateParam);
            
            // Limpar seleções atuais
            const selectedGrid = document.getElementById('selected-relics-grid');
            selectedGrid.innerHTML = '';
            
            // Carregar relíquias selecionadas NA ORDEM CORRETA
            selectedIds.forEach(relicId => {
                const relicData = relics.find(r => r.id === relicId);
                if (relicData) {
                    createRelic(relicData, selectedGrid);
                }
            });
            
            // Preencher com placeholders se necessário
            while (selectedGrid.children.length < 18) { // 16 seleções + 2 de buffer
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
        updateBuffSummary(); // Inicializa o contador
    });
}

window.onload = initializeGrids;
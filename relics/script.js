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

    const col = document.createElement("div");
    col.className = "col-4";
    grid.appendChild(col);

    const relicElement = document.createElement("div");
    relicElement.classList.add("relic");
    relicElement.style.backgroundColor = getQualityColor(relic.quality);
    relicElement.dataset.id = relic.id;
    col.appendChild(relicElement);

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
        
        const currentGrid = relicElement.parentElement.parentElement;
        const targetGrid = currentGrid.id === "available-relics-grid" 
            ? document.getElementById("selected-relics-grid") 
            : document.getElementById("available-relics-grid");
        
        moveRelic(relicElement, targetGrid);
    });

    if (window.innerWidth < 768) {
        relicElement.style.minHeight = '110px';
        relicElement.style.padding = '6px';
        const title = relicElement.querySelector('h3');
        title.style.whiteSpace = 'nowrap';
        title.style.overflow = 'hidden';
        title.style.textOverflow = 'ellipsis';
    }

    // grid.appendChild(relicElement);
}

function createPlaceholder() {
    const placeholder = document.createElement("div");
    placeholder.classList.add("placeholder-card");

    const relicElement = document.createElement("div");
    relicElement.classList.add("relic", "placeholder-relic");
    
    // Adicionar botão de bloqueio
    const lockButton = document.createElement("button");
    lockButton.classList.add("lock-button", "btn", "btn-sm");
    lockButton.innerHTML = '<i class="fas fa-lock-open"></i>';
    lockButton.addEventListener('click', (e) => {
        e.stopPropagation();
        placeholder.classList.toggle('locked');
        lockButton.querySelector('i').classList.toggle('fa-lock');
        lockButton.querySelector('i').classList.toggle('fa-lock-open');
        saveLockState(placeholder.dataset.slotId, placeholder.classList.contains('locked'));
        updatePlaceholders(); // Atualiza o contador quando o estado muda
    });
    relicElement.appendChild(lockButton);

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
    const selectedGrid = document.getElementById("selected-relics-grid");
    selectedGrid.innerHTML = '';
    
    const labels = ['6F', '5F', '4F', '3F', '2F', '1F'];
    
    labels.forEach((label, rowIndex) => {
        const row = document.createElement('div');
        row.className = 'row';
        selectedGrid.appendChild(row);
        
        const labelDiv = document.createElement('div');
        labelDiv.className = 'col-1';
        labelDiv.textContent = label;
        row.appendChild(labelDiv);

        const relicsDiv = document.createElement('div');
        relicsDiv.className = 'col-11';
        row.appendChild(relicsDiv);

        const relicRow = document.createElement('div');
        relicRow.className = 'row';
        relicsDiv.appendChild(relicRow);
       
        for (let i = 0; i < 3; i++) {
            const slot = document.createElement('div');
            slot.className = 'col-4 relic-slot';
            const placeholder = createPlaceholder();
            placeholder.dataset.slotId = `slot-${rowIndex}-${i}`; // ID único para cada slot
            if (loadLockState(placeholder.dataset.slotId)) {
                placeholder.classList.add('locked');
                placeholder.querySelector('.lock-button i').classList.remove('fa-lock-open');
                placeholder.querySelector('.lock-button i').classList.add('fa-lock');
            }
            slot.appendChild(placeholder);
            relicRow.appendChild(slot);
        }
    });

    updatePlaceholders(); // Atualiza o contador com os valores iniciais
}

function moveRelic(relic, targetGrid) {
    const selectedGrid = document.getElementById('selected-relics-grid');
    const availableGrid = document.getElementById('available-relics-grid');

    if (targetGrid === selectedGrid) {
        const availableSlots = countAvailableSlots();
        const selectedCount = document.querySelectorAll('#selected-relics-grid .relic-slot .relic[data-id]').length;
        
        if (selectedCount >= availableSlots) {
            relic.classList.add('relic-shake');
            setTimeout(() => relic.classList.remove('relic-shake'), 500);
            showLimitAlert();
            return;
        }
        
        const emptySlot = selectedGrid.querySelector('.relic-slot .placeholder-card:not(.locked)');
        if (emptySlot) {
            // Remove a col-4 vazia da grade disponível
            const emptyCol = relic.parentElement;
            if (emptyCol && emptyCol.classList.contains('col-4')) {
                emptyCol.remove();
            }
            
            emptySlot.parentElement.replaceChild(relic, emptySlot);
        } else {
            // Visual feedback for no available slots
            relic.classList.add('relic-shake');
            setTimeout(() => relic.classList.remove('relic-shake'), 500);
            showLimitAlert();
            return;
        }
    } else {
        const availableGridEmptyCol = relic.parentElement;
        availableGridEmptyCol.appendChild(createPlaceholder());

        // Moving back to available grid
        // Criamos uma nova col-4 para a relíquia
        const col = document.createElement("div");
        col.className = "col-4";
        col.appendChild(relic);
        availableGrid.appendChild(col);
    }
    
    updateBuffSummary();
    updatePlaceholders();
}

function saveLockState(slotId, isLocked) {
    localStorage.setItem(`slot-${slotId}-locked`, isLocked);
}

function loadLockState(slotId) {
    return localStorage.getItem(`slot-${slotId}-locked`) === 'true';
}

function countAvailableSlots() {
    const totalSlots = 18;
    const lockedSlots = document.querySelectorAll('.placeholder-card.locked').length;
    return totalSlots - lockedSlots;
}

function updatePlaceholders() {
    const selectedCount = document.querySelectorAll('#selected-relics-grid .relic-slot .relic[data-id]').length;
    const availableSlots = countAvailableSlots();
    
    document.querySelectorAll('.placeholder-card').forEach(ph => {
        ph.style.opacity = selectedCount >= availableSlots ? '0.3' : '0.7';
        ph.style.pointerEvents = selectedCount >= availableSlots ? 'none' : 'auto';
    });
    
    const counter = document.getElementById('selected-count');
    const maxSlots = document.getElementById('max-slots');
    
    counter.textContent = selectedCount;
    maxSlots.textContent = availableSlots;
    
    counter.style.color = selectedCount >= availableSlots ? '#dc3545' : '#28a745';
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

    // Percorre todos os slots de relíquias selecionadas
    selectedRelicsGrid.querySelectorAll('.relic-slot .relic[data-id]').forEach(relicElement => {
        const relicId = parseInt(relicElement.dataset.id);
        const relic = relics.find(r => r.id === relicId);
        
        if (relic) {
            const level = loadLevelFromLocalStorage(relic);
            
            // Processa os displayBuffs
            if (relic.displayBuffs) {
                relic.displayBuffs.forEach(displayBuff => {
                    const buffKey = displayBuff.name + (displayBuff.uom ? ` (${displayBuff.uom})` : '');
                    const buffValue = level > 0 ? (displayBuff.values[level - 1] || 0) : 0;
                    
                    if (buffValue !== 0) {
                        if (buffs[buffKey]) {
                            buffs[buffKey] += buffValue;
                        } else {
                            buffs[buffKey] = buffValue;
                        }
                    }
                });
            }
        }
    });

    return buffs;
}

function updateBuffSummary() {
    const count = document.querySelectorAll('#selected-relics-grid .relic-slot .relic[data-id]').length;
    
    const counter = document.getElementById('selected-count');
    counter.textContent = count;
    counter.style.color = count >= 18 ? '#dc3545' : '#28a745';

    const buffSummary = document.getElementById("buff-summary");
    const buffs = calculateTotalBuffs();

    buffSummary.innerHTML = '';

    if (Object.keys(buffs).length === 0) {
        buffSummary.innerHTML = '<p class="text-muted">No relics selected.</p>';
        return;
    }

    // Ordena os buffs por nome
    const sortedBuffNames = Object.keys(buffs).sort();

    sortedBuffNames.forEach(buffName => {
        const buffItem = document.createElement("div");
        buffItem.classList.add("buff-summary-item");

        const nameSpan = document.createElement("span");
        nameSpan.classList.add("buff-summary-name");
        nameSpan.textContent = buffName.replace(/ \(.*\)$/, ''); // Remove a unidade do nome

        const valueSpan = document.createElement("span");
        valueSpan.classList.add("buff-summary-value");
        
        // Verifica se é um buff com porcentagem
        const isPercentage = buffName.includes('(%)');
        valueSpan.textContent = isPercentage ? `${buffs[buffName]}%` : buffs[buffName];

        buffItem.appendChild(nameSpan);
        buffItem.appendChild(valueSpan);
        buffSummary.appendChild(buffItem);
    });
    
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
    updateMenuPositions();
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
    updateMenuPositions();
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
function encodeSelectedRelics() {
    const selectedGrid = document.getElementById('selected-relics-grid');
    const slots = selectedGrid.querySelectorAll('.relic-slot');
    const selectedIds = [];
    
    slots.forEach(slot => {
        const placeholder = slot.querySelector('.placeholder-card');
        const relic = slot.querySelector('.relic[data-id]');
        
        if (placeholder && placeholder.classList.contains('locked')) {
            // Slot bloqueado vazio - ID 0
            selectedIds.push(0);
        } else if (relic) {
            // Relíquia selecionada - ID normal
            selectedIds.push(parseInt(relic.dataset.id));
        } else {
            // Slot não bloqueado vazio - null (será tratado como vazio)
            selectedIds.push(null);
        }
    });
    
    return btoa(unescape(encodeURIComponent(JSON.stringify(selectedIds))));
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
function encodeAllLevels() {
    const levels = {};
    
    // Percorrer todas as relíquias e verificar se o nível foi alterado
    relics.forEach(relic => {
        const storedLevel = localStorage.getItem(`relic-${relic.id}-level`);
        if (storedLevel !== null) {
            levels[relic.id] = parseInt(storedLevel);
        }
    });

    // Converter para JSON e depois para Base64
    const jsonString = JSON.stringify(levels);
    return btoa(unescape(encodeURIComponent(jsonString)));
}

// Função para decodificar
function decodeAllLevels(base64) {
    try {
        const jsonString = decodeURIComponent(escape(atob(base64)));
        return JSON.parse(jsonString);
    } catch (e) {
        console.error("Error decoding levels:", e);
        return {};
    }
}

// Share functionality
const floatingShareButton = document.getElementById('floating-share-button');
const shareMenu = document.getElementById('share-menu');
function setupShareButton() {
    const copyButton = document.getElementById('copy-share-link');
    const closeButton = document.getElementById('close-share-menu');
    const shareUrlInput = document.querySelector('.share-url');

    floatingShareButton.addEventListener('click', (e) => {
        e.stopPropagation();
        shareMenu.classList.toggle('show');
        document.getElementById('filter-menu').classList.remove('show');
        document.getElementById('buff-menu').classList.remove('show');

        updateMenuPositions();
        
        const params = new URLSearchParams();
        params.set('s', encodeSelectedRelics());
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
    
    // Carregar níveis
    const levelsParam = params.get('l');
    if (levelsParam) {
        const levels = decodeAllLevels(levelsParam);
        
        // Aplicar apenas os níveis que estão na URL (não resetar os outros)
        for (const [relicId, level] of Object.entries(levels)) {
            saveLevelToLocalStorage(parseInt(relicId), level);
            
            // Atualizar visualmente as estrelas
            const relicElement = document.querySelector(`.relic[data-id="${relicId}"]`);
            if (relicElement) {
                setRelicLevel(relicElement, level);
            }
        }
    }

    // Carregar seleções
    const stateParam = params.get('s');
    if (stateParam) {
        try {
            const selectedIds = decodeSelectedRelics(stateParam);
            const selectedGrid = document.getElementById('selected-relics-grid');
            const slots = selectedGrid.querySelectorAll('.relic-slot');
            
            // Reset all slots to unlocked and empty first
            slots.forEach(slot => {
                const placeholder = slot.querySelector('.placeholder-card');
                if (placeholder) {
                    placeholder.classList.remove('locked');
                    placeholder.querySelector('.lock-button i').classList.remove('fa-lock');
                    placeholder.querySelector('.lock-button i').classList.add('fa-lock-open');
                }
                
                // Remove any existing relics
                const existingRelic = slot.querySelector('.relic[data-id]');
                if (existingRelic) {
                    const availableGrid = document.getElementById('available-relics-grid');
                    moveRelic(existingRelic, availableGrid);
                }
            });
            
            // Process each slot from the URL
            selectedIds.forEach((relicId, index) => {
                if (index >= slots.length) return;
                
                const slot = slots[index];
                const placeholder = slot.querySelector('.placeholder-card');
                
                if (relicId === 0) {
                    // Slot bloqueado
                    if (placeholder) {
                        placeholder.classList.add('locked');
                        placeholder.querySelector('.lock-button i').classList.remove('fa-lock-open');
                        placeholder.querySelector('.lock-button i').classList.add('fa-lock');
                        saveLockState(placeholder.dataset.slotId, true);
                    }
                } else if (relicId) {
                    // Relíquia normal
                    const relicElement = document.querySelector(`.relic[data-id="${relicId}"]`);
                    if (relicElement) {
                        moveRelic(relicElement, selectedGrid);
                    }
                }
            });
            
            updateBuffSummary();
            updatePlaceholders();
        } catch (e) {
            console.error('Error loading state:', e);
        }
    }
}

function setRelicLevel(element, level) {
    const stars = element.querySelectorAll('.stars i');
    const maxStars = stars.length;
    
    // Garantir que o nível não exceda o máximo de estrelas
    level = Math.min(level, maxStars);
    
    stars.forEach((star, i) => {
        star.classList.toggle('fas', i < level);
        star.classList.toggle('far', i >= level);
    });
    
    const relicId = parseInt(element.dataset.id);
    const relic = relics.find(r => r.id === relicId);
    if (relic) {
        saveLevelToLocalStorage(relicId, level);
        updateRelicBuffs(element, relic, level);
    }
}

function initializeGrids() {
    loadRelics().then(() => {
        initializePlaceholders();
        filterRelics();
        loadStateFromURL();
        setupShareButton();
        setupSectionToggles(); // Adicione esta linha
        updateBuffSummary(); // Inicializa o contador
    });
    window.addEventListener('scroll', updateMenuPositions);
    window.addEventListener('resize', updateMenuPositions);
}

function setupSectionToggles() {
    document.querySelectorAll('.toggle-section').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const section = document.getElementById(targetId);
            const icon = this.querySelector('i');
            
            section.classList.toggle('collapsed-section');
            icon.classList.toggle('fa-chevron-up');
            icon.classList.toggle('fa-chevron-down');
            
            // Salvar o estado no localStorage
            localStorage.setItem(`section-${targetId}-collapsed`, section.classList.contains('collapsed-section'));
        });
    });
    
    // Carregar estados salvos
    ['selected-section', 'available-section'].forEach(sectionId => {
        const isCollapsed = localStorage.getItem(`section-${sectionId}-collapsed`) === 'true';
        const section = document.getElementById(sectionId);
        const button = document.querySelector(`.toggle-section[data-target="${sectionId}"]`);
        const icon = button?.querySelector('i');
        
        if (isCollapsed && section && button && icon) {
            section.classList.add('collapsed-section');
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
        }
    });
}

function updateMenuPositions() {
    const menus = [filterMenu, buffMenu, shareMenu];
    const buttons = [floatingFilterButton, floatingBuffButton, floatingShareButton];
    
    menus.forEach((menu, index) => {
        if (menu.classList.contains('show')) {
            const buttonRect = buttons[index].getBoundingClientRect();
            menu.style.bottom = `${window.innerHeight - buttonRect.top}px`;
            menu.style.right = `${window.innerWidth - buttonRect.right + 60}px`;
        }
    });
}

window.onload = initializeGrids;
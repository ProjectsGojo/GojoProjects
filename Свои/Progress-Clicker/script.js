
let percent = 0;
let totalPercent = 0;
let percentPerSecond = 0;
let clickPower = 1;
let money = 0;


const linearUpgrades = [
    {
        id: 1,
        name: "Автокликер",
        description: "Автоматически добавляет 1% каждые 5 секунд",
        baseCost: 100,
        unlocked: false,
        bought: false,
        effect: () => { percentPerSecond += 0.2; }
    },
    {
        id: 2,
        name: "Улучшенный автокликер",
        description: "Увеличивает автокликер до 2% каждые 5 секунд",
        baseCost: 500,
        unlocked: false,
        bought: false,
        effect: () => { percentPerSecond += 0.4; }
    },
    {
        id: 3,
        name: "Мега кликер",
        description: "Увеличивает силу клика в 2 раза",
        baseCost: 2000,
        unlocked: false,
        bought: false,
        effect: () => { clickPower *= 2; }
    },
    {
        id: 4,
        name: "Гига кликер",
        description: "Увеличивает силу клика еще в 2 раза",
        baseCost: 10000,
        unlocked: false,
        bought: false,
        effect: () => { clickPower *= 2; }
    }
];


const boostUpgrades = [
    {
        id: 1,
        name: "Увеличение клика",
        description: "Увеличивает силу каждого клика",
        baseCost: 50,
        costGrowth: 1.5,
        level: 0,
        maxLevel: 100,
        effect: () => { clickPower += 1; }
    },
    {
        id: 2,
        name: "Скорость автокликера",
        description: "Увеличивает процент в секунду",
        baseCost: 200,
        costGrowth: 1.8,
        level: 0,
        maxLevel: 50,
        effect: () => { percentPerSecond += 0.1; }
    },
    {
        id: 3,
        name: "Критический клик",
        description: "Шанс нанести двойной урон",
        baseCost: 500,
        costGrowth: 2,
        level: 0,
        maxLevel: 20,
        effect: () => { /* Логика критического удара в функции клика */ }
    }
];


const clickArea = document.getElementById('click-area');
const progressFill = document.getElementById('progress-fill');
const currentPercentElement = document.getElementById('current-percent');
const totalPercentElement = document.getElementById('total-percent');
const percentPerSecondElement = document.getElementById('percent-per-second');
const clickPowerElement = document.getElementById('click-power');
const linearUpgradesContainer = document.getElementById('linear-upgrades');
const boostUpgradesContainer = document.getElementById('boost-upgrades');
const particlesContainer = document.getElementById('particles');
const clickEffect = document.getElementById('click-effect');


function initGame() {

    loadGame();
    

    setupClickArea();
    

    renderUpgrades();
    

    gameLoop();
    

    checkUnlockedUpgrades();
}


function setupClickArea() {
    // Клик мышью
    clickArea.addEventListener('click', (e) => {
        handleClick(e);
    });
    
    // Колесо мыши
    clickArea.addEventListener('wheel', (e) => {
        e.preventDefault();
        handleClick(e);
    });
    
    // Касание на мобильных устройствах
    clickArea.addEventListener('touchstart', (e) => {
        handleClick(e);
    });
}

// Обработка клика
function handleClick(event) {
    // Позиция клика
    const rect = clickArea.getBoundingClientRect();
    const x = (event.clientX || event.touches[0].clientX) - rect.left;
    const y = (event.clientY || event.touches[0].clientY) - rect.top;
    
    // Эффект клика
    createClickEffect(x, y);
    
    // Создаем частицы
    createParticles(x, y);
    
    // Проверяем критический удар
    const isCritical = Math.random() < (0.05 * boostUpgrades[2].level);
    const power = isCritical ? clickPower * 2 : clickPower;
    
    // Добавляем проценты
    addPercent(power);
    
    // Показываем всплывающий текст
    createFloatingText(x, y, isCritical ? `+${power}%!` : `+${power}%`, isCritical ? '#ff0000' : '#ffffff');
}

// Эффект при клике
function createClickEffect(x, y) {
    clickEffect.style.left = `${x}px`;
    clickEffect.style.top = `${y}px`;
    clickEffect.style.transform = 'scale(1)';
    clickEffect.style.opacity = '1';
    
    setTimeout(() => {
        clickEffect.style.transform = 'scale(3)';
        clickEffect.style.opacity = '0';
    }, 10);
}

// Добавление процентов
function addPercent(amount) {
    percent += amount;
    totalPercent += amount;
    
    // Обновляем отображение
    updateProgressBar();
    updateStats();
    
    // Проверяем, нужно ли разблокировать новые улучшения
    checkUnlockedUpgrades();
}

// Создание частиц
function createParticles(x, y) {
    const particleCount = 5 + Math.floor(Math.random() * 10);
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Размер и цвет
        const size = 2 + Math.random() * 5;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        // Позиция
        particle.style.left = `${x}px`;
        particle.style.top = `${y}px`;
        
        // Цвет
        const hue = 270 + Math.random() * 60; // Фиолетовые/розовые оттенки
        particle.style.backgroundColor = `hsl(${hue}, 100%, 70%)`;
        
        // Анимация
        const angle = Math.random() * Math.PI * 2;
        const speed = 1 + Math.random() * 3;
        const lifetime = 500 + Math.random() * 1000;
        
        particlesContainer.appendChild(particle);
        
        // Анимируем частицу
        let startTime = Date.now();
        
        function animateParticle() {
            const elapsed = Date.now() - startTime;
            const progress = elapsed / lifetime;
            
            if (progress >= 1) {
                particle.remove();
                return;
            }
            
            const distance = speed * elapsed / 10;
            const currentX = x + Math.cos(angle) * distance;
            const currentY = y + Math.sin(angle) * distance;
            const opacity = 1 - progress;
            
            particle.style.left = `${currentX}px`;
            particle.style.top = `${currentY}px`;
            particle.style.opacity = opacity;
            
            requestAnimationFrame(animateParticle);
        }
        
        requestAnimationFrame(animateParticle);
    }
}

// Создание всплывающего текста
function createFloatingText(x, y, text, color) {
    const floatingText = document.createElement('div');
    floatingText.textContent = text;
    floatingText.style.position = 'absolute';
    floatingText.style.left = `${x}px`;
    floatingText.style.top = `${y}px`;
    floatingText.style.color = color;
    floatingText.style.fontWeight = 'bold';
    floatingText.style.pointerEvents = 'none';
    floatingText.style.transition = 'all 0.5s';
    floatingText.style.transform = 'translate(-50%, -50%)';
    
    clickArea.appendChild(floatingText);
    
    setTimeout(() => {
        floatingText.style.top = `${y - 50}px`;
        floatingText.style.opacity = '0';
    }, 10);
    
    setTimeout(() => {
        floatingText.remove();
    }, 1000);
}

// Обновление прогресс бара
function updateProgressBar() {
    const progress = (percent / 1000000) * 100;
    progressFill.style.width = `${progress}%`;
    currentPercentElement.textContent = `${Math.floor(percent)}%`;
}

// Обновление статистики
function updateStats() {
    totalPercentElement.textContent = Math.floor(totalPercent);
    percentPerSecondElement.textContent = percentPerSecond.toFixed(1);
    clickPowerElement.textContent = clickPower;
}

// Рендер улучшений
function renderUpgrades() {
    // Линейные улучшения
    linearUpgradesContainer.innerHTML = '';
    linearUpgrades.forEach(upgrade => {
        const upgradeElement = document.createElement('div');
        upgradeElement.className = `upgrade ${!upgrade.unlocked ? 'locked' : ''}`;
        upgradeElement.innerHTML = `
            <div class="upgrade-name">${upgrade.name}</div>
            <div class="upgrade-description">${upgrade.description}</div>
            <div class="upgrade-cost">Цена: ${upgrade.baseCost}%</div>
            ${upgrade.bought ? '<div class="upgrade-level">Куплено!</div>' : ''}
        `;
        
        if (upgrade.unlocked && !upgrade.bought) {
            upgradeElement.addEventListener('click', () => buyLinearUpgrade(upgrade.id));
        }
        
        linearUpgradesContainer.appendChild(upgradeElement);
    });
    

    boostUpgradesContainer.innerHTML = '';
    boostUpgrades.forEach(upgrade => {
        const cost = Math.floor(upgrade.baseCost * Math.pow(upgrade.costGrowth, upgrade.level));
        
        const upgradeElement = document.createElement('div');
        upgradeElement.className = 'upgrade';
        upgradeElement.innerHTML = `
            <div class="upgrade-name">${upgrade.name}</div>
            <div class="upgrade-description">${upgrade.description}</div>
            <div class="upgrade-cost">Цена: ${cost}%</div>
            <div class="upgrade-level">Уровень: ${upgrade.level}/${upgrade.maxLevel}</div>
        `;
        
        if (upgrade.level < upgrade.maxLevel) {
            upgradeElement.addEventListener('click', () => buyBoostUpgrade(upgrade.id));
        } else {
            upgradeElement.classList.add('locked');
            upgradeElement.innerHTML += '<div class="upgrade-level">Макс. уровень!</div>';
        }
        
        boostUpgradesContainer.appendChild(upgradeElement);
    });
}


function buyLinearUpgrade(id) {
    const upgrade = linearUpgrades.find(u => u.id === id);
    
    if (!upgrade || upgrade.bought || !upgrade.unlocked) return;
    
    if (totalPercent >= upgrade.baseCost) {
        totalPercent -= upgrade.baseCost;
        upgrade.bought = true;
        upgrade.effect();
        
        
        const nextUpgrade = linearUpgrades.find(u => u.id === id + 1);
        if (nextUpgrade) {
            nextUpgrade.unlocked = true;
        }
        
        updateStats();
        renderUpgrades();
    }
}


function buyBoostUpgrade(id) {
    const upgrade = boostUpgrades.find(u => u.id === id);
    
    if (!upgrade || upgrade.level >= upgrade.maxLevel) return;
    
    const cost = Math.floor(upgrade.baseCost * Math.pow(upgrade.costGrowth, upgrade.level));
    
    if (totalPercent >= cost) {
        totalPercent -= cost;
        upgrade.level++;
        upgrade.effect();
        
        updateStats();
        renderUpgrades();
    }
}


function checkUnlockedUpgrades() {
    let changed = false;
    
  
    if (!linearUpgrades[0].unlocked && totalPercent >= linearUpgrades[0].baseCost / 2) {
        linearUpgrades[0].unlocked = true;
        changed = true;
    }
    

    for (let i = 1; i < linearUpgrades.length; i++) {
        if (!linearUpgrades[i].unlocked && linearUpgrades[i-1].bought) {
            linearUpgrades[i].unlocked = true;
            changed = true;
        }
    }
    
    if (changed) {
        renderUpgrades();
    }
}


function gameLoop() {

    if (percentPerSecond > 0) {
        addPercent(percentPerSecond / 60);
    }
    

    if (Date.now() - lastSaveTime > 5000) {
        saveGame();
        lastSaveTime = Date.now();
    }
    
    requestAnimationFrame(gameLoop);
}


function saveGame() {
    const gameData = {
        percent,
        totalPercent,
        percentPerSecond,
        clickPower,
        linearUpgrades,
        boostUpgrades,
        version: 1
    };
    
    localStorage.setItem('megaClickerSave', JSON.stringify(gameData));
}


function loadGame() {
    const savedData = localStorage.getItem('megaClickerSave');
    
    if (savedData) {
        try {
            const gameData = JSON.parse(savedData);
            
            percent = gameData.percent || 0;
            totalPercent = gameData.totalPercent || 0;
            percentPerSecond = gameData.percentPerSecond || 0;
            clickPower = gameData.clickPower || 1;
            
            if (gameData.linearUpgrades) {
                linearUpgrades.forEach((upgrade, index) => {
                    if (gameData.linearUpgrades[index]) {
                        upgrade.unlocked = gameData.linearUpgrades[index].unlocked;
                        upgrade.bought = gameData.linearUpgrades[index].bought;
                    }
                });
            }
            
            if (gameData.boostUpgrades) {
                boostUpgrades.forEach((upgrade, index) => {
                    if (gameData.boostUpgrades[index]) {
                        upgrade.level = gameData.boostUpgrades[index].level;
                    }
                });
            }
            
            updateProgressBar();
            updateStats();
        } catch (e) {
            console.error('Ошибка загрузки сохранения:', e);
        }
    }
}

let lastSaveTime = Date.now();


window.addEventListener('load', initGame);

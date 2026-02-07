const gameState = {
    commits: 0,
    cps: 0, // commits per second
    upgrades: [
        { id: 'mechanical_keyboard', name: 'Mechanical Keyboard', baseCost: 15, cpsMatch: 0.1, count: 0, desc: 'Clack clack clack.' },
        { id: 'coffee', name: 'Fresh Coffee', baseCost: 100, cpsMatch: 1, count: 0, desc: 'Caffeine boost.' },
        { id: 'stackoverflow', name: 'Stack Overflow Account', baseCost: 500, cpsMatch: 5, count: 0, desc: 'Copy-paste master.' },
        { id: 'copilot', name: 'AI Assistant', baseCost: 1500, cpsMatch: 15, count: 0, desc: 'Code writes itself.' },
        { id: 'server_farm', name: 'Server Farm', baseCost: 5000, cpsMatch: 50, count: 0, desc: 'Scale to infinity.' }
    ]
};

// Load saved game
const savedGame = localStorage.getItem('commitClickerSave');
if (savedGame) {
    const parsedSave = JSON.parse(savedGame);
    gameState.commits = parsedSave.commits || 0;
    
    // Restore upgrade counts
    if (parsedSave.upgrades) {
        gameState.upgrades.forEach((upgrade, index) => {
            if (parsedSave.upgrades[index]) {
                upgrade.count = parsedSave.upgrades[index].count;
            }
        });
    }
}

const elements = {
    commits: document.getElementById('commits'),
    cps: document.getElementById('cps'),
    btn: document.getElementById('commit-btn'),
    upgradesList: document.getElementById('upgrades-list')
};

function updateDisplay() {
    elements.commits.textContent = Math.floor(gameState.commits).toLocaleString();
    elements.cps.textContent = gameState.cps.toFixed(1);
    
    // Check upgrade availability
    document.querySelectorAll('.upgrade-item').forEach(item => {
        const cost = parseInt(item.dataset.cost);
        if (gameState.commits >= cost) {
            item.classList.remove('disabled');
        } else {
            item.classList.add('disabled');
        }
    });
}

function calculateCPS() {
    let cps = 0;
    gameState.upgrades.forEach(u => {
        cps += u.count * u.cpsMatch;
    });
    gameState.cps = cps;
}

function saveGame() {
    localStorage.setItem('commitClickerSave', JSON.stringify(gameState));
}

// Game Loop
setInterval(() => {
    calculateCPS();
    gameState.commits += gameState.cps / 10; // Run 10 times a second
    updateDisplay();
    saveGame();
}, 100);

// Click Handler
elements.btn.addEventListener('click', () => {
    gameState.commits++;
    updateDisplay();
    
    // Click animation
    const btn = elements.btn;
    btn.style.transform = 'scale(0.95)';
    setTimeout(() => btn.style.transform = 'scale(1)', 50);
});

// Render Upgrades
function renderUpgrades() {
    elements.upgradesList.innerHTML = '';
    gameState.upgrades.forEach(upgrade => {
        const cost = Math.floor(upgrade.baseCost * Math.pow(1.15, upgrade.count));
        
        const div = document.createElement('div');
        div.className = 'upgrade-item disabled';
        div.dataset.id = upgrade.id;
        div.dataset.cost = cost;
        
        div.innerHTML = `
            <div class="upgrade-info">
                <strong>${upgrade.name} (${upgrade.count})</strong>
                <span>${upgrade.desc} (+${upgrade.cpsMatch} cps)</span>
            </div>
            <div class="upgrade-cost">
                ${cost} commits
            </div>
        `;
        
        div.addEventListener('click', () => {
            const currentCost = Math.floor(upgrade.baseCost * Math.pow(1.15, upgrade.count));
            if (gameState.commits >= currentCost) {
                gameState.commits -= currentCost;
                upgrade.count++;
                renderUpgrades(); // Re-render to update cost/count
                calculateCPS();
                updateDisplay();
            }
        });
        
        elements.upgradesList.appendChild(div);
    });
}

renderUpgrades();
calculateCPS();
updateDisplay();

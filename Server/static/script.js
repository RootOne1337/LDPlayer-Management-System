const API_BASE = 'http://127.0.0.1:8001/api';
let authToken = null;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await initializeAuth();
    setupNavigation();
    setupModals();
    loadData();
    setInterval(loadData, 5000); // Refresh every 5 seconds
});

// Auth Initialization
async function initializeAuth() {
    try {
        // Try to get token from localStorage
        const savedToken = localStorage.getItem('auth_token');
        if (savedToken) {
            authToken = savedToken;
            return;
        }

        // Login with default credentials
        const response = await fetch('http://127.0.0.1:8001/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: 'admin',
                password: 'admin'
            })
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('auth_token', authToken);
        } else {
            console.error('Failed to authenticate');
        }
    } catch (error) {
        console.error('Auth error:', error);
    }
}

// Navigation Setup
function setupNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = link.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // Show selected tab
    const selectedTab = document.getElementById(`${tabName}-tab`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }

    const selectedLink = document.querySelector(`[data-tab="${tabName}"]`);
    if (selectedLink) {
        selectedLink.classList.add('active');
    }
}

// Modal Management
function setupModals() {
    // Close buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) closeModal(modal.id);
        });
    });

    // Close on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) closeModal(modal.id);
        });
    });

    // Prevent close when clicking modal content
    document.querySelectorAll('.modal-content').forEach(content => {
        content.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Helper function for API calls
async function apiCall(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    return fetch(url, {
        ...options,
        headers
    });
}

// Load Data
async function loadData() {
    if (!authToken) return; // Wait for auth
    
    try {
        // Load dashboard stats
        const workstationsResponse = await apiCall(`${API_BASE}/workstations`);
        if (!workstationsResponse.ok) throw new Error('Failed to load workstations');
        const workstations = await workstationsResponse.json();
        document.getElementById('stat-workstations').textContent = workstations.length;

        const emulatorsResponse = await apiCall(`${API_BASE}/emulators`);
        if (!emulatorsResponse.ok) throw new Error('Failed to load emulators');
        const emulators = await emulatorsResponse.json();
        document.getElementById('stat-emulators').textContent = emulators.length;

        const activeCount = emulators.filter(e => e.status === 'running').length;
        document.getElementById('stat-active').textContent = activeCount;

        // Update server status
        try {
            await apiCall(`${API_BASE}/health`);
            document.getElementById('stat-server').textContent = 'Online';
        } catch {
            document.getElementById('stat-server').textContent = 'Offline';
        }

        // Load sections
        displayWorkstations(workstations);
        displayEmulators(emulators);
        displayOperations();
        updateEmulatorWorkstationSelect(workstations);
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Display Workstations
function displayWorkstations(workstations) {
    const container = document.getElementById('workstations-list');
    
    if (!workstations || workstations.length === 0) {
        container.innerHTML = '<div class="loading">No workstations yet</div>';
        return;
    }

    container.innerHTML = workstations.map(ws => `
        <div class="item-card">
            <div class="item-header">
                <div class="item-title">${escapeHtml(ws.hostname)}</div>
                <span class="item-badge">${ws.status}</span>
            </div>
            <div class="item-body">
                <div class="item-info">
                    <div class="info-label">Path</div>
                    <div class="info-value">${escapeHtml(ws.ldplayer_path)}</div>
                </div>
                <div class="item-info">
                    <div class="info-label">Emulators Count</div>
                    <div class="info-value">${ws.emulator_count || 0}</div>
                </div>
                <div class="item-actions">
                    <button class="btn btn-secondary" onclick="editWorkstation(${ws.id})">Edit</button>
                    <button class="btn btn-danger" onclick="deleteWorkstation(${ws.id})">Delete</button>
                </div>
            </div>
        </div>
    `).join('');
}

// Display Emulators
function displayEmulators(emulators) {
    const container = document.getElementById('emulators-list');
    
    if (!emulators || emulators.length === 0) {
        container.innerHTML = '<div class="loading">No emulators yet</div>';
        return;
    }

    container.innerHTML = emulators.map(emu => `
        <div class="item-card">
            <div class="item-header">
                <div class="item-title">${escapeHtml(emu.name || emu.id)}</div>
                <span class="item-badge">${emu.status}</span>
            </div>
            <div class="item-body">
                <div class="item-info">
                    <div class="info-label">Workstation ID</div>
                    <div class="info-value">${emu.workstation_id}</div>
                </div>
                <div class="item-info">
                    <div class="info-label">Resolution</div>
                    <div class="info-value">${emu.resolution || 'N/A'}</div>
                </div>
                <div class="item-actions">
                    ${emu.status === 'running' 
                        ? `<button class="btn btn-warning" onclick="stopEmulator(${emu.id})"><i class="fas fa-stop"></i> Stop</button>` 
                        : `<button class="btn btn-success" onclick="startEmulator(${emu.id})"><i class="fas fa-play"></i> Start</button>`
                    }
                    <button class="btn btn-danger" onclick="deleteEmulator(${emu.id})">Delete</button>
                </div>
            </div>
        </div>
    `).join('');
}

// Display Operations
function displayOperations() {
    const container = document.getElementById('operations-list');
    
    // Placeholder - operations would be loaded from API
    const operations = [];
    
    if (!operations || operations.length === 0) {
        container.innerHTML = '<div class="loading">No operations yet</div>';
        return;
    }

    container.innerHTML = `<div class="operations-table">
        ${operations.map(op => `
            <div class="operation-row">
                <div>${escapeHtml(op.operation_type)}</div>
                <div>${escapeHtml(op.target || 'N/A')}</div>
                <div>${op.status}</div>
                <div>${new Date(op.timestamp).toLocaleString()}</div>
            </div>
        `).join('')}
    </div>`;
}

// Utility function
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Modal Functions
function showCreateWorkstationModal() {
    openModal('create-workstation-modal');
}

function showCreateEmulatorModal() {
    openModal('create-emulator-modal');
}

function updateEmulatorWorkstationSelect(workstations) {
    const select = document.getElementById('emu-workstation');
    if (select) {
        select.innerHTML = '<option value="">-- Select Workstation --</option>' + 
            (workstations || []).map(ws => 
                `<option value="${ws.id}">${escapeHtml(ws.hostname || ws.id)}</option>`
            ).join('');
    }
}

// Create Functions
async function createWorkstation(event) {
    event.preventDefault();
    
    const hostname = document.getElementById('ws-hostname').value;
    const path = document.getElementById('ws-path').value;

    try {
        const response = await apiCall(`${API_BASE}/workstations`, {
            method: 'POST',
            body: JSON.stringify({
                hostname,
                ldplayer_path: path
            })
        });

        if (response.ok) {
            showToast('Workstation created!', 'success');
            closeModal('create-workstation-modal');
            event.target.reset();
            loadData();
        } else {
            showToast('Error creating workstation', 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

async function createEmulator(event) {
    event.preventDefault();
    
    const workstationId = document.getElementById('emu-workstation').value;
    const name = document.getElementById('emu-name').value;
    const resolution = document.getElementById('emu-resolution').value;

    try {
        const response = await apiCall(`${API_BASE}/emulators`, {
            method: 'POST',
            body: JSON.stringify({
                workstation_id: parseInt(workstationId),
                name,
                resolution
            })
        });

        if (response.ok) {
            showToast('Emulator created!', 'success');
            closeModal('create-emulator-modal');
            event.target.reset();
            loadData();
        } else {
            showToast('Error creating emulator', 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

// Action Functions
async function startEmulator(emuId) {
    try {
        const response = await apiCall(`${API_BASE}/emulators/${emuId}/start`, {
            method: 'POST'
        });

        if (response.ok) {
            showToast('Emulator started!', 'success');
            loadData();
        } else {
            showToast('Error starting emulator', 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

async function stopEmulator(emuId) {
    try {
        const response = await apiCall(`${API_BASE}/emulators/${emuId}/stop`, {
            method: 'POST'
        });

        if (response.ok) {
            showToast('Emulator stopped!', 'success');
            loadData();
        } else {
            showToast('Error stopping emulator', 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

async function deleteWorkstation(wsId) {
    if (!confirm('Are you sure?')) return;

    try {
        const response = await apiCall(`${API_BASE}/workstations/${wsId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Workstation deleted!', 'success');
            loadData();
        } else {
            showToast('Error deleting', 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

async function deleteEmulator(emuId) {
    if (!confirm('Are you sure?')) return;

    try {
        const response = await apiCall(`${API_BASE}/emulators/${emuId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Emulator deleted!', 'success');
            loadData();
        } else {
            showToast('Error deleting', 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

function editWorkstation(wsId) {
    showToast('Edit feature coming soon', 'warning');
}

// Toast Notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    toast.textContent = message;
    toast.className = `toast ${type} active`;

    setTimeout(() => {
        toast.classList.remove('active');
    }, 3000);
}

let map;
let hospitalMarkers = [];
let surgeCircles = [];

const API_BASE = '';

document.addEventListener('DOMContentLoaded', function() {
    initMap();
    loadData();
    setupEventListeners();
});

function initMap() {
    map = L.map('map').setView([28.6139, 77.2090], 11);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);
}

function setupEventListeners() {
    document.getElementById('refreshBtn').addEventListener('click', loadData);
    document.getElementById('balanceBtn').addEventListener('click', loadBalance);
}

async function loadData() {
    showLoading(true);
    try {
        const [hospitalsRes, surgeRes] = await Promise.all([
            fetch(`${API_BASE}/hospitals`),
            fetch(`${API_BASE}/surge`)
        ]);
        
        const hospitals = await hospitalsRes.json();
        const surgeData = await surgeRes.json();
        
        updateMap(hospitals, surgeData);
        updateHospitalsList(surgeData.predictions || []);
        updateSummary(surgeData.city_summary || {});
        updateLastUpdated();
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Failed to load hospital data');
    } finally {
        showLoading(false);
    }
}

async function loadBalance() {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/balance`);
        const balanceData = await response.json();
        
        updateRecommendations(balanceData);
        updateLastUpdated();
    } catch (error) {
        console.error('Error loading balance data:', error);
        showError('Failed to load balance recommendations');
    } finally {
        showLoading(false);
    }
}

function updateMap(hospitals, surgeData) {
    hospitalMarkers.forEach(marker => map.removeLayer(marker));
    surgeCircles.forEach(circle => map.removeLayer(circle));
    hospitalMarkers = [];
    surgeCircles = [];
    
    const predictions = surgeData.predictions || [];
    const predictionMap = {};
    predictions.forEach(p => {
        predictionMap[p.hospital_id] = p;
    });
    
    hospitals.forEach(hospital => {
        const prediction = predictionMap[hospital.id] || {};
        const load = prediction.predicted_surge || ((hospital.current_patients / hospital.capacity) * 100);
        const riskLevel = prediction.risk_level || getRiskLevel(load);
        const color = getLoadColor(riskLevel);
        
        const surgeCircle = L.circle([hospital.location.lat, hospital.location.lng], {
            radius: 800 + (load * 5),
            fillColor: color,
            fillOpacity: 0.3,
            color: color,
            weight: 2,
            opacity: 0.6
        }).addTo(map);
        surgeCircles.push(surgeCircle);
        
        const icon = L.divIcon({
            className: 'hospital-marker',
            html: `<div style="
                background-color: ${color};
                width: 30px;
                height: 30px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 14px;
                font-weight: bold;
            ">🏥</div>`,
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
        
        const marker = L.marker([hospital.location.lat, hospital.location.lng], { icon })
            .addTo(map);
        
        const popupContent = `
            <div class="popup-content">
                <h3>${hospital.name}</h3>
                <div class="popup-stat">
                    <label>Type:</label>
                    <value>${hospital.type}</value>
                </div>
                <div class="popup-stat">
                    <label>Capacity:</label>
                    <value>${hospital.capacity} beds</value>
                </div>
                <div class="popup-stat">
                    <label>Current Patients:</label>
                    <value>${hospital.current_patients}</value>
                </div>
                <div class="popup-stat">
                    <label>Current Load:</label>
                    <value style="color: ${color}; font-weight: bold;">
                        ${load.toFixed(1)}%
                    </value>
                </div>
                <div class="popup-stat">
                    <label>ICU Beds:</label>
                    <value>${hospital.icu_occupied}/${hospital.icu_beds}</value>
                </div>
                <div class="popup-stat">
                    <label>Ventilators:</label>
                    <value>${hospital.ventilators_in_use}/${hospital.ventilators}</value>
                </div>
                <div class="popup-stat">
                    <label>Risk Level:</label>
                    <value style="color: ${color}; text-transform: uppercase;">
                        ${riskLevel}
                    </value>
                </div>
            </div>
        `;
        
        marker.bindPopup(popupContent);
        hospitalMarkers.push(marker);
    });
}

function updateHospitalsList(predictions) {
    const container = document.getElementById('hospitalsContent');
    document.getElementById('hospitalCount').textContent = predictions.length;
    
    if (!predictions.length) {
        container.innerHTML = '<div class="loading">No hospital data available</div>';
        return;
    }
    
    predictions.sort((a, b) => b.predicted_surge - a.predicted_surge);
    
    container.innerHTML = predictions.map(p => {
        const riskLevel = p.risk_level || getRiskLevel(p.predicted_surge);
        return `
            <div class="hospital-card ${riskLevel}">
                <div class="hospital-info">
                    <h3>${p.hospital_name}</h3>
                    <p>Factors: ${(p.surge_factors || []).join(', ') || 'Normal'}</p>
                </div>
                <div class="hospital-load">
                    <div class="load-value ${riskLevel}">${p.predicted_surge.toFixed(0)}%</div>
                    <div class="load-label">Predicted Load</div>
                </div>
            </div>
        `;
    }).join('');
}

function updateSummary(summary) {
    const container = document.getElementById('summaryContent');
    
    const riskClass = `risk-${summary.overall_risk || 'medium'}`;
    
    container.innerHTML = `
        <div class="summary-stats">
            <div class="stat-card ${riskClass}">
                <div class="stat-value">${(summary.overall_risk || 'N/A').toUpperCase()}</div>
                <div class="stat-label">City Risk Level</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${summary.overall_occupancy?.toFixed(0) || 0}%</div>
                <div class="stat-label">Overall Occupancy</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${summary.total_capacity || 0}</div>
                <div class="stat-label">Total Capacity</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${summary.total_occupied || 0}</div>
                <div class="stat-label">Total Occupied</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${summary.average_aqi || 0}</div>
                <div class="stat-label">Average AQI</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${summary.active_events || 0}</div>
                <div class="stat-label">Active Events</div>
            </div>
        </div>
        ${summary.recommendations?.length ? `
            <div class="action-items">
                ${summary.recommendations.map(r => `
                    <div class="action-item">
                        <span class="action-icon">⚠️</span>
                        <span>${r}</span>
                    </div>
                `).join('')}
            </div>
        ` : ''}
    `;
}

function updateRecommendations(balanceData) {
    const container = document.getElementById('recommendationsContent');
    const alertCount = (balanceData.alerts?.length || 0) + (balanceData.transfer_recommendations?.length || 0);
    document.getElementById('alertCount').textContent = alertCount;
    
    let html = '';
    
    if (balanceData.alerts?.length) {
        html += balanceData.alerts.map(alert => {
            const alertClass = alert.level === 'critical' ? 'critical' : 
                               alert.level === 'warning' ? 'warning' : 'info';
            const icon = alert.level === 'critical' ? '🚨' : 
                        alert.level === 'warning' ? '⚠️' : 'ℹ️';
            return `
                <div class="alert-card ${alertClass}">
                    <div class="alert-header">${icon} ${alert.title}</div>
                    <div class="alert-message">${alert.message}</div>
                </div>
            `;
        }).join('');
    }
    
    if (balanceData.transfer_recommendations?.length) {
        html += '<h4 style="margin: 1rem 0 0.5rem; font-size: 0.875rem;">Patient Transfers</h4>';
        html += balanceData.transfer_recommendations.map(t => `
            <div class="transfer-card">
                <div class="transfer-header">
                    ${t.priority === 'urgent' ? '🚑' : '➡️'} 
                    ${t.priority.toUpperCase()} Transfer
                </div>
                <div class="transfer-details">
                    <div class="transfer-from">
                        <strong>From:</strong> ${t.from_hospital.name}<br>
                        <small>Load: ${t.from_hospital.predicted_surge?.toFixed(0) || t.from_hospital.current_load?.toFixed(0)}%</small>
                    </div>
                    <div class="transfer-arrow">→</div>
                    <div class="transfer-to">
                        <strong>To:</strong> ${t.to_hospital.name}<br>
                        <small>${t.to_hospital.available_beds} beds available</small>
                    </div>
                </div>
                <div style="margin-top: 0.5rem;">
                    <span class="transfer-count">${t.patients_to_transfer} patients</span>
                    <small style="margin-left: 0.5rem; color: #64748b;">${t.distance_km} km</small>
                </div>
            </div>
        `).join('');
    }
    
    if (balanceData.action_items?.length) {
        html += '<h4 style="margin: 1rem 0 0.5rem; font-size: 0.875rem;">Action Items</h4>';
        html += '<div class="action-items">';
        html += balanceData.action_items.map(item => `
            <div class="action-item">
                <span class="action-icon">✅</span>
                <span>${item}</span>
            </div>
        `).join('');
        html += '</div>';
    }
    
    if (!html) {
        html = `
            <div style="text-align: center; padding: 2rem; color: #22c55e;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">✓</div>
                <p>All hospitals are operating within normal parameters.</p>
                <p style="font-size: 0.8rem; color: #64748b; margin-top: 0.5rem;">
                    No transfers or interventions recommended at this time.
                </p>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function getLoadColor(riskLevel) {
    switch(riskLevel) {
        case 'critical': return '#dc2626';
        case 'high': return '#ef4444';
        case 'medium': return '#f59e0b';
        case 'low': return '#22c55e';
        default: return '#64748b';
    }
}

function getRiskLevel(load) {
    if (load >= 90) return 'critical';
    if (load >= 70) return 'high';
    if (load >= 50) return 'medium';
    return 'low';
}

function updateLastUpdated() {
    const now = new Date();
    document.getElementById('lastUpdated').textContent = now.toLocaleString();
}

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

function showError(message) {
    console.error(message);
    alert(message);
}

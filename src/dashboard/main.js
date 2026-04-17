let map, markers = [];
let currentCase = null;
let focusMarker = null;

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    initTabs();
    initMap();
    initCharts();
    renderTable(APP_DATA.cases);
    updateStats();
    
    // Global Event Listeners
    document.querySelector('.close-drawer').addEventListener('click', closeDrawer);
    document.getElementById('search-input').addEventListener('input', redoFilter);
    document.getElementById('month-filter').addEventListener('change', redoFilter);
    document.getElementById('severity-filter').addEventListener('change', redoFilter);
}

function initTabs() {
    const tabs = document.querySelectorAll('.nav-item');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            const target = tab.getAttribute('data-tab');
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(target).classList.add('active');
            
            if(target === 'map-tab') {
                setTimeout(() => map.invalidateSize(), 100);
            } else if (target === 'stats-tab') {
                setTimeout(() => {
                    if(hotspotChart) hotspotChart.resize();
                    if(trendChart) trendChart.resize();
                    if(districtChart) districtChart.resize();
                    if(deptChart) deptChart.resize();
                }, 100);
            }
        });
    });
}

function initMap() {
    map = L.map('map', {
        zoomControl: false
    }).setView([22.6273, 120.3014], 13);
    
    L.control.zoom({ position: 'topright' }).addTo(map);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO'
    }).addTo(map);

    renderMarkers(APP_DATA.cases);
}

function renderMarkers(cases) {
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    // Use pre-calculated hotspots from the Analytics Engine
    // If cases are filtered, we'll map them back to their clusters
    const filteredIds = new Set(cases.map(c => c.case_id));
    
    APP_DATA.hotspots.forEach(h => {
        // Find cases in this hotspot that are part of the current filtered set
        const idsInCluster = h.case_ids.split(',');
        const clusterCases = APP_DATA.cases.filter(c => idsInCluster.includes(c.case_id) && filteredIds.has(c.case_id));
        
        if (clusterCases.length === 0) return; // Skip empty clusters in filter

        const count = clusterCases.length;
        const primary = clusterCases[0];
        
        // Final Safeguard: Single cases should NOT be Extreme Red unless truly severe
        let color = '#22d3ee';
        let radius = 6;
        if (count >= 3 || (h.severity >= 5.0 && count > 1)) {
            color = '#ef4444'; radius = 12;
        } else if (count >= 2 || (h.severity >= 2.5 && count > 1)) {
            color = '#f59e0b'; radius = 9;
        }

        const marker = L.circleMarker([h.lat, h.lng], {
            radius: radius,
            fillColor: color,
            color: '#fff',
            weight: 1.5,
            opacity: 0.8,
            fillOpacity: 0.8
        }).addTo(map);

        if (count > 1) {
            marker.bindTooltip(`🔥 ${h.primary_address} (${count}筆案件)`, { permanent: false, direction: 'top' });
        }

        marker.on('click', () => showDetails(clusterCases));
        markers.push(marker);
    });
}

let trendChart, districtChart, deptChart, hotspotChart;
let currentTrendUnit = 'month';

function initCharts() {
    const hotspotDom = document.getElementById('hotspot-chart');
    const trendDom = document.getElementById('trend-chart');
    const districtDom = document.getElementById('district-chart');
    const deptDom = document.getElementById('dept-chart');
    
    if (hotspotChart) hotspotChart.dispose();
    if (trendChart) trendChart.dispose();
    if (districtChart) districtChart.dispose();
    if (deptChart) deptChart.dispose();

    hotspotChart = echarts.init(hotspotDom, 'dark');
    trendChart = echarts.init(trendDom, 'dark');
    districtChart = echarts.init(districtDom, 'dark');
    deptChart = echarts.init(deptDom, 'dark');

    updateChartsData(APP_DATA.cases);
    
    // Toggle Event
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTrendUnit = btn.getAttribute('data-unit');
            updateChartsData(lastFilteredData || APP_DATA.cases);
        });
    });

    window.addEventListener('resize', () => {
        if(hotspotChart) hotspotChart.resize();
        if(trendChart) trendChart.resize();
        if(districtChart) districtChart.resize();
        if(deptChart) deptChart.resize();
    });
}

let lastFilteredData = null;

function updateChartsData(cases) {
    if (!trendChart) return;
    lastFilteredData = cases;

    // 1. Hotspot Ranking (Using Pre-calculated Analysis Table)
    const filteredIds = new Set(cases.map(c => c.case_id));
    const sortedHotspots = APP_DATA.hotspots
        .map(h => {
            const currentCount = h.case_ids.split(',').filter(id => filteredIds.has(id)).length;
            return { name: h.primary_address, value: currentCount };
        })
        .filter(item => item.value > 0)
        .sort((a, b) => b.value - a.value)
        .slice(0, 10);

    hotspotChart.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value' },
        yAxis: { 
            type: 'category', 
            data: sortedHotspots.map(a => a.name.substring(0, 15)),
            inverse: true
        },
        series: [{
            name: '密度',
            type: 'bar',
            data: sortedHotspots.map(a => a.value),
            itemStyle: { color: (params) => params.data >= 3 ? '#ef4444' : '#22d3ee' }
        }]
    });

    // 1. Trend Analysis (Month/Week)
    const timeCounts = {};
    cases.forEach(c => {
        if(c.suggestion_date) {
            let key = c.suggestion_date.substring(0, 7);
            if (currentTrendUnit === 'week') {
                const date = new Date(c.suggestion_date);
                const week = Math.ceil(date.getDate() / 7);
                key = `${c.suggestion_date.substring(0, 7)}-W${week}`;
            }
            timeCounts[key] = (timeCounts[key] || 0) + 1;
        }
    });
    const sortedTimeline = Object.entries(timeCounts).sort();

    trendChart.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: sortedTimeline.map(t => t[0]) },
        yAxis: { type: 'value' },
        series: [{
            name: '案件量',
            type: 'line',
            smooth: true,
            data: sortedTimeline.map(t => t[1]),
            areaStyle: { opacity: 0.2, color: '#22d3ee' },
            itemStyle: { color: '#22d3ee' }
        }]
    });

    // 2. District Analysis
    const distCounts = {};
    cases.forEach(c => {
        const d = c.district || '未知';
        distCounts[d] = (distCounts[d] || 0) + 1;
    });
    const sortedDist = Object.entries(distCounts).sort((a,b) => b[1] - a[1]).slice(0, 10);

    districtChart.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'value' },
        yAxis: { type: 'category', data: sortedDist.map(d => d[0]), inverse: true },
        series: [{
            name: '量',
            type: 'bar',
            data: sortedDist.map(d => d[1]),
            itemStyle: { color: '#8b5cf6' }
        }]
    });

    // 3. Dept Analysis
    const deptCounts = {};
    cases.forEach(c => {
        const d = c.dept || '未分類';
        deptCounts[d] = (deptCounts[d] || 0) + 1;
    });

    deptChart.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'item' },
        series: [{
            name: '負責課室',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: { borderRadius: 10, borderColor: '#020617', borderWidth: 2 },
            label: { show: false },
            data: Object.entries(deptCounts).map(([k, v]) => ({ name: k, value: v }))
        }]
    });
}

function renderTable(cases) {
    const tbody = document.querySelector('#case-table tbody');
    tbody.innerHTML = '';
    
    cases.forEach(c => {
        const tr = document.createElement('tr');
        const sevTag = c.severity >= 5.0 ? '🔴' : (c.severity >= 2.5 ? '🟡' : '🟢');
        
        tr.innerHTML = `
            <td>${c.case_id}</td>
            <td>${c.suggestion_date || c.date_suggested.substring(0, 10)}</td>
            <td>
                <div class="content-cell">
                    <div class="raw-content">${c.content}</div>
                    <div class="expand-toggle-box" onclick="toggleExpand(this)">
                        <span class="btn-text">📖 點擊展開全文</span>
                    </div>
                </div>
            </td>
            <td>
                <span class="badge" style="background:#475569">${c.district || '未知'}</span>
                <span class="badge" style="background:${getDeptColor(c.dept)}">${c.dept || '未分類'}</span>
                <br>
                <strong>${sevTag}</strong> ${c.address || '-'}
            </td>
            <td><button class="view-btn">🎯 定位</button></td>
        `;
        tr.querySelector('.view-btn').addEventListener('click', () => {
            const sameLocation = APP_DATA.cases.filter(x => x.latitude === c.latitude && x.longitude === c.longitude);
            jumpToMap(c, sameLocation);
        });
        tbody.appendChild(tr);
    });
}

function getDeptColor(dept) {
    const colors = {
        '交通工程科': '#3b82f6',
        '停車管理中心': '#10b981',
        '交通管制工程處': '#ef4444',
        '運輸規劃科': '#f59e0b'
    };
    return colors[dept] || '#888';
}

function redoFilter() {
    const searchVal = document.getElementById('search-input').value.toLowerCase();
    const monthVal = document.getElementById('month-filter').value;
    const severityMin = parseFloat(document.getElementById('severity-filter').value);

    const filtered = APP_DATA.cases.filter(c => {
        const matchSearch = c.case_id.toLowerCase().includes(searchVal) || 
                          c.content.toLowerCase().includes(searchVal) || 
                          (c.address && c.address.toLowerCase().includes(searchVal));
        
        const matchMonth = monthVal === 'all' || (c.date_suggested && c.date_suggested.startsWith(monthVal));
        const matchSeverity = (c.severity || 0) >= severityMin;

        return matchSearch && matchMonth && matchSeverity;
    });

    renderTable(filtered);
    renderMarkers(filtered);
    updateChartsData(filtered);
    updateStats(filtered.length);
}

function showDetails(clusterCases, activeCaseId = null) {
    const drawer = document.getElementById('detail-drawer');
    const drawerContent = drawer.querySelector('.drawer-content');
    
    // Clear dynamic parts but keep structure
    const primary = activeCaseId ? clusterCases.find(x => x.case_id === activeCaseId) : clusterCases[0];
    currentCase = primary;

    // Reset drawer view
    renderCaseSelector(clusterCases, primary.case_id);
    updateDrawerFields(primary, clusterCases.length);
    
    // Highlights
    if (focusMarker) map.removeLayer(focusMarker);
    focusMarker = L.circle([primary.latitude, primary.longitude], {
        radius: 40,
        color: '#22d3ee',
        fillOpacity: 0.2,
        className: 'focus-ring'
    }).addTo(map);

    drawer.classList.add('open');
}

function updateDrawerFields(c, clusterCount = 1) {
    document.getElementById('case-id-title').innerText = c.case_id;
    document.getElementById('case-date').innerText = c.date_suggested;
    document.getElementById('case-content').innerText = c.content;
    document.getElementById('case-reply').innerText = c.reply_content || '尚未回覆';
    document.getElementById('case-address').innerText = c.address || '無法辨識';
    document.getElementById('case-coords').innerText = c.latitude ? `${c.latitude}, ${c.longitude}` : '無座標';
    
    // UI Label logic synced with map clusters
    let sevText = '熱度: 一般';
    let sevColor = '#8b5cf6';

    if (clusterCount >= 3 || (c.severity >= 5.0 && clusterCount > 1)) {
        sevText = '熱度: 極高 (多次提及)';
        sevColor = '#ef4444';
    } else if (clusterCount >= 2 || (c.severity >= 2.5 && clusterCount > 1)) {
        sevText = '熱度: 中度';
        sevColor = '#f59e0b';
    }

    const sourceEl = document.getElementById('case-source');
    sourceEl.innerText = `${sevText} | 來源: ${c.geocode_source || '待查'}`;
    sourceEl.style.background = sevColor;
}

function renderCaseSelector(cluster, activeId) {
    let selector = document.getElementById('group-selector');
    if (!selector) {
        selector = document.createElement('div');
        selector.id = 'group-selector';
        selector.className = 'case-selector';
        const title = document.getElementById('case-id-title');
        title.parentNode.insertBefore(selector, title.nextSibling);
    }

    if (cluster.length <= 1) {
        selector.style.display = 'none';
        return;
    }

    selector.style.display = 'block';
    selector.innerHTML = `
        <label>此區域有 ${cluster.length} 筆案件：</label>
        <div class="case-list">
            ${cluster.map(x => `
                <div class="case-chip ${x.case_id === activeId ? 'active' : ''}" onclick="switchCase('${x.case_id}')">
                    ${x.case_id.split('-').pop()}
                </div>
            `).join('')}
        </div>
    `;
    
    // Attach selection logic helper to window for simplicity in onclick
    window.switchCase = (id) => {
        const c = cluster.find(x => x.case_id === id);
        updateDrawerFields(c, cluster.length);
        renderCaseSelector(cluster, id);
    };
}

function closeDrawer() {
    document.getElementById('detail-drawer').classList.remove('open');
    if (focusMarker) {
        map.removeLayer(focusMarker);
        focusMarker = null;
    }
}

function jumpToMap(c, cluster = null) {
    document.querySelector('[data-tab="map-tab"]').click();
    map.setView([c.latitude, c.longitude], 16);
    showDetails(cluster || [c], c.case_id);
}

function toggleExpand(btn) {
    const cell = btn.closest('.content-cell');
    const isExpanded = cell.classList.toggle('expanded');
    btn.querySelector('.btn-text').innerText = isExpanded ? '🔼 收合內容' : '📖 點擊展開全文';
}

function updateStats(count) {
    const total = count !== undefined ? count : APP_DATA.cases.length;
    document.getElementById('total-count').innerText = total;
}



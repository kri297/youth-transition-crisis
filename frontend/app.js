// API Base URL - Render deployment
const API_BASE = 'https://youth-transition-crisis.onrender.com/api';

// Global data storage
let globalData = {};

// Color scheme
const COLORS = {
    exemplary: '#27ae60',
    good: '#26a69a',
    moderate: '#f39c12',
    at_risk: '#e67e22',
    critical: '#e74c3c',
    primary: '#00695c',
    secondary: '#00897b'
};

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    setupNavigation();
    await loadAllData();
    hideLoading();
});

// Setup navigation
function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.content-section');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetSection = btn.dataset.section;

            // Update active button
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Show target section
            sections.forEach(s => s.classList.remove('active'));
            document.getElementById(targetSection).classList.add('active');

            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });
}

// Load all data from API
async function loadAllData() {
    try {
        // Fetch all data in parallel
        const [overview, states, monthly, riskDist] = await Promise.all([
            fetch(`${API_BASE}/overview`).then(r => r.json()),
            fetch(`${API_BASE}/states`).then(r => r.json()),
            fetch(`${API_BASE}/monthly`).then(r => r.json()),
            fetch(`${API_BASE}/risk-distribution`).then(r => r.json())
        ]);

        globalData = { overview, states, monthly, riskDist };

        // Populate UI
        populateOverview(overview, states);
        populateResearchQuestion(overview);
        createAllCharts();

    } catch (error) {
        console.error('Error loading data:', error);
        alert('Failed to load data. Make sure the backend server is running at ' + API_BASE);
    }
}

// Populate overview section
function populateOverview(overview, states) {
    // Stats grid
    const statsGrid = document.getElementById('stats-grid');
    statsGrid.innerHTML = `
        <div class="stat-card">
            <div class="stat-label">Best Performer</div>
            <div class="stat-value">${overview.best_percentage}%</div>
            <div class="stat-desc">${overview.best_state}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Worst Performer</div>
            <div class="stat-value">${overview.worst_percentage}%</div>
            <div class="stat-desc">${overview.worst_state}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Gap Ratio</div>
            <div class="stat-value">${overview.gap}X</div>
            <div class="stat-desc">Disparity</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">National Average</div>
            <div class="stat-value">${overview.national_avg}%</div>
            <div class="stat-desc">${overview.num_states} States/UTs</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Total Records</div>
            <div class="stat-value">${(overview.total_records / 1000000).toFixed(1)}M</div>
            <div class="stat-desc">${overview.num_districts} Districts</div>
        </div>
    `;

    // Critical alert
    const criticalAlert = document.getElementById('critical-alert');
    criticalAlert.innerHTML = `
        <h3>⚠️ CRITICAL ALERT</h3>
        <p>
            <strong>${overview.critical_states + overview.at_risk_states} states</strong> require immediate intervention. 
            The best performer (<strong>${overview.best_state}</strong> at ${overview.best_percentage}%) 
            is <strong>${overview.gap}X better</strong> than the worst performer 
            (<strong>${overview.worst_state}</strong> at ${overview.worst_percentage}%).
        </p>
    `;

    // Footer date
    document.getElementById('footer-date').textContent = `Analysis Date: ${overview.analysis_date}`;

    // Update gap titles
    document.getElementById('gap-title').textContent = `The ${overview.gap}X Gap - Best vs Worst Performers`;
    document.getElementById('fig2-title').textContent = `Figure 2: The ${overview.gap}X Gap`;
}

// Populate research question
function populateResearchQuestion(overview) {
    document.getElementById('research-question').innerHTML = `
        <strong>Why do some Indian states achieve youth biometric engagement rates ${overview.gap}X higher than others, 
        and what does this disparity reveal about systemic barriers to accessing education, healthcare, and social welfare services?</strong>
    `;
}

// Create all charts
function createAllCharts() {
    const { overview, states, monthly, riskDist } = globalData;

    // Top 15 chart
    createTop15Chart(states.slice(0, 15), 'chart-top15');
    createTop15Chart(states.slice(0, 15), 'chart-fig1');

    // Gap chart
    createGapChart(overview, 'chart-gap');
    createGapChart(overview, 'chart-fig2');

    // Scatter chart
    createScatterChart(states, 'chart-scatter');
    createScatterChart(states, 'chart-fig3');

    // Monthly trends
    createMonthlyChart(monthly, 'chart-monthly');
    createMonthlyChart(monthly, 'chart-fig4');

    // Risk distribution
    createRiskChart(riskDist, 'chart-risk');
    createRiskChart(riskDist, 'chart-fig5');
}

// Create Top 15 chart
function createTop15Chart(top15, elementId) {
    const data = [{
        type: 'bar',
        x: top15.map(s => s.youth_bio_pct).reverse(),
        y: top15.map(s => s.state).reverse(),
        orientation: 'h',
        marker: {
            color: top15.map(s => s.youth_bio_pct).reverse(),
            colorscale: [[0, COLORS.critical], [0.5, COLORS.moderate], [1, COLORS.exemplary]],
            line: { color: 'white', width: 1 }
        },
        text: top15.map(s => `${s.youth_bio_pct.toFixed(1)}%`).reverse(),
        textposition: 'outside',
        textfont: { size: 12, color: '#2c3e50', family: 'Inter' }
    }];

    const layout = {
        title: {
            text: '<b>Top 15 States by Youth Biometric Engagement</b>',
            font: { size: 18, color: '#2c3e50', family: 'Inter' }
        },
        xaxis: {
            title: 'Youth Biometric Engagement (%)',
            titlefont: { size: 14, color: '#2c3e50' },
            tickfont: { size: 12, color: '#2c3e50' },
            gridcolor: '#e0e0e0'
        },
        yaxis: {
            titlefont: { size: 14, color: '#2c3e50' },
            tickfont: { size: 12, color: '#2c3e50' }
        },
        height: 600,
        margin: { l: 150, r: 80, t: 60, b: 80 },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: 'white'
    };

    Plotly.newPlot(elementId, data, layout, { displayModeBar: false, responsive: true });
}

// Create Gap chart
function createGapChart(overview, elementId) {
    const data = [{
        type: 'bar',
        x: [overview.best_state, overview.worst_state],
        y: [overview.best_percentage, overview.worst_percentage],
        marker: {
            color: [COLORS.exemplary, COLORS.critical],
            line: { color: 'white', width: 2 }
        },
        text: [`${overview.best_percentage}%`, `${overview.worst_percentage}%`],
        textposition: 'outside',
        textfont: { size: 16, color: '#2c3e50', family: 'Inter' }
    }];

    const layout = {
        title: {
            text: '<b>Best vs Worst Performers - The Engagement Gap</b>',
            font: { size: 18, color: '#2c3e50', family: 'Inter' }
        },
        annotations: [{
            x: 0.5,
            y: (overview.best_percentage + overview.worst_percentage) / 2,
            text: `<b>${overview.gap}X GAP</b>`,
            showarrow: false,
            font: { size: 24, color: 'white', family: 'Inter' },
            bgcolor: COLORS.critical,
            borderpad: 10,
            bordercolor: '#c0392b',
            borderwidth: 3
        }],
        xaxis: {
            titlefont: { size: 14, color: '#2c3e50' },
            tickfont: { size: 13, color: '#2c3e50' }
        },
        yaxis: {
            title: 'Youth Biometric Engagement (%)',
            titlefont: { size: 14, color: '#2c3e50' },
            tickfont: { size: 12, color: '#2c3e50' },
            gridcolor: '#e0e0e0'
        },
        height: 500,
        margin: { l: 80, r: 80, t: 60, b: 80 },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: 'white'
    };

    Plotly.newPlot(elementId, data, layout, { displayModeBar: false, responsive: true });
}

// Create Scatter chart
function createScatterChart(states, elementId) {
    const categories = ['Exemplary', 'Good', 'Moderate', 'At Risk', 'Critical'];
    const traces = categories.map(cat => {
        const filtered = states.filter(s => s.risk_category === cat);
        return {
            type: 'scatter',
            mode: 'markers',
            name: cat,
            x: filtered.map(s => s.youth_demo_pct),
            y: filtered.map(s => s.youth_bio_pct),
            text: filtered.map(s => s.state),
            marker: {
                size: 12,
                color: COLORS[cat.toLowerCase().replace(' ', '_')],
                line: { width: 2, color: 'white' },
                opacity: 0.8
            }
        };
    });

    // Add diagonal line
    const maxVal = Math.max(...states.map(s => Math.max(s.youth_bio_pct, s.youth_demo_pct)));
    traces.push({
        type: 'scatter',
        mode: 'lines',
        name: 'Equal Line',
        x: [0, maxVal],
        y: [0, maxVal],
        line: { dash: 'dash', color: COLORS.critical, width: 2 },
        showlegend: false
    });

    const layout = {
        title: {
            text: '<b>Biometric vs Demographic Youth Engagement</b>',
            font: { size: 18, color: '#2c3e50', family: 'Inter' }
        },
        xaxis: {
            title: 'Youth Demographic Engagement (%)',
            titlefont: { size: 14, color: '#2c3e50' },
            tickfont: { size: 12, color: '#2c3e50' },
            gridcolor: '#e0e0e0'
        },
        yaxis: {
            title: 'Youth Biometric Engagement (%)',
            titlefont: { size: 14, color: '#2c3e50' },
            tickfont: { size: 12, color: '#2c3e50' },
            gridcolor: '#e0e0e0'
        },
        height: 600,
        margin: { l: 80, r: 80, t: 60, b: 80 },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: 'white',
        legend: {
            bgcolor: 'rgba(255,255,255,0.9)',
            bordercolor: '#e0e0e0',
            borderwidth: 1
        }
    };

    Plotly.newPlot(elementId, traces, layout, { displayModeBar: false, responsive: true });
}

// Create Monthly chart
function createMonthlyChart(monthly, elementId) {
    const data = [{
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Youth Bio %',
        x: monthly.map(m => m.month_str),
        y: monthly.map(m => m.youth_bio_pct),
        line: { color: COLORS.good, width: 4 },
        marker: { size: 12, color: COLORS.good, line: { width: 2, color: 'white' } },
        text: monthly.map(m => `${m.youth_bio_pct.toFixed(1)}%`),
        textposition: 'top center',
        textfont: { size: 11, color: '#2c3e50' }
    }];

    const layout = {
        title: {
            text: '<b>Monthly Youth Biometric Engagement</b>',
            font: { size: 18, color: '#2c3e50', family: 'Inter' }
        },
        xaxis: {
            title: 'Month',
            titlefont: { size: 14, color: '#2c3e50' },
            tickfont: { size: 11, color: '#2c3e50' },
            tickangle: -45
        },
        yaxis: {
            title: 'Youth Biometric Engagement (%)',
            titlefont: { size: 14, color: '#2c3e50' },
            tickfont: { size: 12, color: '#2c3e50' },
            gridcolor: '#e0e0e0'
        },
        height: 500,
        margin: { l: 80, r: 80, t: 60, b: 100 },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: 'white'
    };

    Plotly.newPlot(elementId, data, layout, { displayModeBar: false, responsive: true });
}

// Create Risk distribution chart
function createRiskChart(riskDist, elementId) {
    const categories = ['Exemplary', 'Good', 'Moderate', 'At Risk', 'Critical'];
    const counts = categories.map(cat => riskDist[cat] || 0);
    const colors = categories.map(cat => COLORS[cat.toLowerCase().replace(' ', '_')]);

    const data = [{
        type: 'bar',
        x: categories,
        y: counts,
        marker: {
            color: colors,
            line: { color: 'white', width: 2 }
        },
        text: counts.map(c => `${c} states`),
        textposition: 'outside',
        textfont: { size: 14, color: '#2c3e50', family: 'Inter' }
    }];

    const layout = {
        title: {
            text: '<b>State Distribution by Risk Category</b>',
            font: { size: 18, color: '#2c3e50', family: 'Inter' }
        },
        xaxis: {
            title: 'Risk Category',
            titlefont: { size: 14, color: '#2c3e50' },
            tickfont: { size: 13, color: '#2c3e50' }
        },
        yaxis: {
            title: 'Number of States',
            titlefont: { size: 14, color: '#2c3e50' },
            tickfont: { size: 12, color: '#2c3e50' },
            gridcolor: '#e0e0e0'
        },
        height: 500,
        margin: { l: 80, r: 80, t: 60, b: 80 },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: 'white'
    };

    Plotly.newPlot(elementId, data, layout, { displayModeBar: false, responsive: true });
}

// Hide loading screen
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

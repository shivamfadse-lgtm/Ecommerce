// SmartDeliver AI Frontend Application

let appState = {
  token: localStorage.getItem('token') || '',
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  priority: 'Balanced',
  k: 4,
  currentView: 'dashboard',
  analysisData: null,
  authModalOpen: false,
  authTab: 'login', // 'login' or 'signup'
  authError: ''
};

async function fetchAnalysis() {
  const container = document.getElementById('app');
  if (container && !appState.analysisData) {
    container.innerHTML = '<div class="loading">⚡ Running geospatial clustering & demand analysis for Nanded...</div>';
  }

  const headers = {};
  if (appState.token) {
    headers['Authorization'] = `Bearer ${appState.token}`;
  }

  try {
    const res = await fetch(`/api/analyze?priority=${encodeURIComponent(appState.priority)}&k=${appState.k}`, { headers });
    if (res.ok) {
      appState.analysisData = await res.json();
      renderCurrentView();
    } else {
      if (container) container.innerHTML = `<div class="card" style="color:#ef4444">Failed to fetch analysis (${res.status}).</div>`;
    }
  } catch (err) {
    if (container) container.innerHTML = `<div class="card" style="color:#ef4444">Network error connecting to backend: ${err.message}</div>`;
  }
}

function renderUserProfile() {
  const profileDiv = document.getElementById('user-profile');
  const logoutBtn = document.getElementById('logout-button');
  const topbarActions = document.querySelector('.topbar-right');

  if (!topbarActions) return;

  // Render Login or User Profile badge
  if (appState.token && appState.user) {
    if (profileDiv) {
      profileDiv.style.display = 'flex';
      profileDiv.innerHTML = `<div><b>${appState.user.name}</b></div><small>${appState.user.role || 'Logistics Specialist'}</small>`;
    }
    if (logoutBtn) {
      logoutBtn.innerText = 'Log out';
      logoutBtn.className = 'logout-button';
      logoutBtn.onclick = handleLogout;
    }
  } else {
    if (profileDiv) {
      profileDiv.style.display = 'none';
    }
    if (logoutBtn) {
      logoutBtn.innerText = 'Log In / Register';
      logoutBtn.className = 'login-btn';
      logoutBtn.onclick = () => openAuthModal('login');
    }
  }
}

function openAuthModal(tab = 'login') {
  appState.authModalOpen = true;
  appState.authTab = tab;
  appState.authError = '';
  renderAuthModal();
}

function closeAuthModal() {
  appState.authModalOpen = false;
  const modal = document.getElementById('auth-modal-root');
  if (modal) modal.remove();
}
window.closeAuthModal = closeAuthModal;

function renderAuthModal() {
  let modalRoot = document.getElementById('auth-modal-root');
  if (!modalRoot) {
    modalRoot = document.createElement('div');
    modalRoot.id = 'auth-modal-root';
    document.body.appendChild(modalRoot);
  }

  if (!appState.authModalOpen) {
    modalRoot.innerHTML = '';
    return;
  }

  const isLogin = appState.authTab === 'login';

  modalRoot.innerHTML = `
    <div class="modal-overlay" onclick="if(event.target === this) closeAuthModal()">
      <div class="modal-card">
        <div style="display:flex; justify-between; align-items:center; margin-bottom: 12px;">
          <div class="modal-title">${isLogin ? 'Log In to SmartDeliver AI' : 'Create an Account'}</div>
          <button onclick="closeAuthModal()" style="background:transparent; border:none; color:#94a3b8; font-size:18px; cursor:pointer;">✕</button>
        </div>
        <div class="modal-sub">Nanded Delivery Intelligence Workspace</div>

        <div class="auth-tabs">
          <button class="auth-tab ${isLogin ? 'active' : ''}" onclick="switchAuthTab('login')">Log In</button>
          <button class="auth-tab ${!isLogin ? 'active' : ''}" onclick="switchAuthTab('signup')">Create Account</button>
        </div>

        ${appState.authError ? `<div class="auth-error">${appState.authError}</div>` : ''}

        <form id="auth-form" onsubmit="handleAuthSubmit(event)">
          ${!isLogin ? `
            <div class="form-group">
              <label>Full Name</label>
              <input type="text" id="auth-name" class="form-input" placeholder="e.g. Ramesh Patil" required />
            </div>
          ` : ''}

          <div class="form-group">
            <label>Email Address</label>
            <input type="email" id="auth-email" class="form-input" placeholder="name@company.com" value="${isLogin ? 'demo@smartdeliver.ai' : ''}" required />
          </div>

          <div class="form-group">
            <label>Password</label>
            <input type="password" id="auth-password" class="form-input" placeholder="••••••••" value="${isLogin ? 'Password123!' : ''}" required />
          </div>

          ${!isLogin ? `
            <div class="form-group">
              <label>Confirm Password</label>
              <input type="password" id="auth-confirm" class="form-input" placeholder="••••••••" required />
            </div>
          ` : ''}

          <button type="submit" class="submit-btn" id="auth-submit-btn">
            ${isLogin ? 'Log In' : 'Register Account'}
          </button>
        </form>
      </div>
    </div>
  `;
}

window.switchAuthTab = function(tab) {
  appState.authTab = tab;
  appState.authError = '';
  renderAuthModal();
};

window.handleAuthSubmit = async function(e) {
  e.preventDefault();
  appState.authError = '';
  const btn = document.getElementById('auth-submit-btn');
  if (btn) btn.innerText = 'Processing...';

  const email = document.getElementById('auth-email')?.value.trim();
  const password = document.getElementById('auth-password')?.value;

  try {
    if (appState.authTab === 'login') {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (res.ok && data.access_token) {
        appState.token = data.access_token;
        appState.user = data.user;
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        closeAuthModal();
        renderUserProfile();
        appState.analysisData = null;
        fetchAnalysis();
      } else {
        appState.authError = data.detail || 'Login failed. Please check your credentials.';
        renderAuthModal();
      }
    } else {
      const name = document.getElementById('auth-name')?.value.trim();
      const confirm_password = document.getElementById('auth-confirm')?.value;

      if (password !== confirm_password) {
        appState.authError = 'Passwords do not match.';
        renderAuthModal();
        return;
      }

      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password, confirm_password })
      });
      const data = await res.json();
      if (res.ok && data.created) {
        // Auto Login after registration
        const loginRes = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const loginData = await loginRes.json();
        if (loginRes.ok && loginData.access_token) {
          appState.token = loginData.access_token;
          appState.user = loginData.user;
          localStorage.setItem('token', loginData.access_token);
          localStorage.setItem('user', JSON.stringify(loginData.user));
        }
        closeAuthModal();
        renderUserProfile();
        appState.analysisData = null;
        fetchAnalysis();
      } else {
        appState.authError = data.detail || 'Registration failed. Please check form fields.';
        renderAuthModal();
      }
    }
  } catch (err) {
    appState.authError = 'Network error: ' + err.message;
    renderAuthModal();
  }
};

async function handleLogout() {
  if (appState.token) {
    try {
      await fetch('/api/logout', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${appState.token}` }
      });
    } catch (e) {
      console.warn('Logout notification error:', e);
    }
  }
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  appState.token = '';
  appState.user = null;
  renderUserProfile();
  appState.analysisData = null;
  fetchAnalysis();
}

let activeCharts = {};

function destroyActiveCharts() {
  Object.keys(activeCharts).forEach(key => {
    try {
      if (activeCharts[key] && typeof activeCharts[key].destroy === 'function') {
        activeCharts[key].destroy();
      }
    } catch (e) {
      console.warn('Error destroying chart:', key, e);
    }
  });
  activeCharts = {};
}

function renderCurrentView() {
  destroyActiveCharts();
  const container = document.getElementById('app');
  if (!container || !appState.analysisData) return;

  renderUserProfile();
  const d = appState.analysisData;

  if (appState.currentView === 'dashboard') {
    renderDashboard(container, d);
  } else if (appState.currentView === 'recommendations') {
    renderRecommendations(container, d);
  } else if (appState.currentView === 'analytics') {
    renderAnalytics(container, d);
  } else if (appState.currentView === 'network-map') {
    renderNetworkMap(container, d);
  } else if (appState.currentView === 'data-management') {
    renderDataManagement(container, d);
  } else if (appState.currentView === 'scenario') {
    renderScenarioSimulator(container, d);
  } else if (appState.currentView === 'impact') {
    renderImpact(container, d);
  } else if (appState.currentView === 'methodology') {
    renderMethodology(container, d);
  }
}

function renderDashboard(container, d) {
  const rec = d.recommendation || {};
  container.innerHTML = `
    <div class="kpi-grid">
      <div class="card">
        <div class="card-title">Total Customers</div>
        <div class="card-value">${d.demand.total_customers.toLocaleString()}</div>
        <div class="card-sub">Nanded City Area</div>
      </div>
      <div class="card">
        <div class="card-title">Total Daily Orders</div>
        <div class="card-value">${d.demand.total_orders.toLocaleString()}</div>
        <div class="card-sub">Demand Density</div>
      </div>
      <div class="card">
        <div class="card-title">Avg Order Value</div>
        <div class="card-value">₹${Math.round(d.demand.avg_order_value)}</div>
        <div class="card-sub">Per Customer Order</div>
      </div>
      <div class="card" style="border-color: #10b981;">
        <div class="card-title">AI Recommended Location</div>
        <div class="card-value" style="color: #10b981; font-size: 20px; line-height: 1.2;">${rec.area || 'N/A'}</div>
        <div class="card-sub">Score: <b>${rec.ai_score || 0}/100</b></div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-top: 20px;">
      <div class="card">
        <div class="card-title">Top Delivery Center Candidates</div>
        <div class="table-container" style="margin-top: 12px;">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Location / Area</th>
                <th>AI Score</th>
                <th>Avg Distance</th>
                <th>Road Score</th>
                <th>Operating Cost</th>
              </tr>
            </thead>
            <tbody>
              ${d.candidates.slice(0, 5).map(c => `
                <tr style="${c.rank === 1 ? 'background: rgba(16,185,129,0.1); font-weight: 600;' : ''}">
                  <td>#${c.rank}</td>
                  <td>${c.area} ${c.rank === 1 ? '<span class="badge badge-rec">AI RECOMMENDED</span>' : ''}</td>
                  <td><b style="color:${c.rank === 1 ? '#10b981' : '#f8fafc'}">${c.ai_score}</b>/100</td>
                  <td>${c.average_delivery_distance} km</td>
                  <td>${c.road_connectivity}/100</td>
                  <td>₹${c.operating_cost.toLocaleString()}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Why This Location?</div>
        <p style="font-size: 13px; color: #cbd5e1; margin-top: 10px; line-height: 1.5;">${d.explanation.summary}</p>
        <div style="margin-top: 16px;">
          <div style="font-size: 12px; font-weight: 700; color: #10b981; margin-bottom: 6px;">POSITIVE FACTORS</div>
          <ul style="font-size: 12px; color: #94a3b8; padding-left: 18px; line-height: 1.6;">
            ${(d.explanation.positive_factors || []).map(f => `<li>${f}</li>`).join('')}
          </ul>
        </div>
        ${d.explanation.risks && d.explanation.risks.length > 0 ? `
          <div style="margin-top: 16px;">
            <div style="font-size: 12px; font-weight: 700; color: #ef4444; margin-bottom: 6px;">POTENTIAL RISKS</div>
            <ul style="font-size: 12px; color: #94a3b8; padding-left: 18px; line-height: 1.6;">
              ${d.explanation.risks.map(r => `<li>${r}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

function renderRecommendations(container, d) {
  container.innerHTML = `
    <div class="card">
      <div style="display:flex; justify-between; align-items:center; margin-bottom: 16px;">
        <div class="card-title">All Candidate Locations Ranked</div>
        <div style="font-size:12px; color:#94a3b8;">Active Priority: <b>${d.weights.priority}</b></div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Location</th>
              <th>AI Score</th>
              <th>Demand Score</th>
              <th>Avg Distance</th>
              <th>Coverage (5km)</th>
              <th>Road Connectivity</th>
              <th>Traffic Score</th>
              <th>Monthly Cost</th>
            </tr>
          </thead>
          <tbody>
            ${d.candidates.map(c => `
              <tr style="${c.rank === 1 ? 'background: rgba(16,185,129,0.15); font-weight: 600;' : ''}">
                <td>#${c.rank}</td>
                <td>${c.area} ${c.rank === 1 ? '<span class="badge badge-rec">#1 BEST CHOICE</span>' : ''}</td>
                <td><b style="color:#10b981; font-size: 16px;">${c.ai_score}</b></td>
                <td>${c.demand_score}/100</td>
                <td>${c.average_delivery_distance} km</td>
                <td>${c.coverage_percentage}%</td>
                <td>${c.road_connectivity}/100</td>
                <td>${c.traffic_score}/100</td>
                <td>₹${c.operating_cost.toLocaleString()}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function renderAnalytics(container, d) {
  if (!d || !d.analytics || !d.demand) {
    container.innerHTML = `<div class="card" style="padding: 24px; text-align: center; color: #6B7772;">Analytics data unavailable.</div>`;
    return;
  }

  const elbow = d.analytics.elbow || [];
  const sil = d.analytics.silhouette || [];
  const optK = d.analytics.optimal_k;
  const silItem = sil.find(item => item.k === optK);
  const optSilScore = silItem ? silItem.silhouette_score : 'N/A';
  const areaSummary = d.demand.area_summary || [];
  const dailyDemand = d.demand.daily_demand || [];

  container.innerHTML = `
    <!-- Top Row: K-Means Diagnostics (Elbow + Silhouette) -->
    <div class="charts-grid">
      <div class="card chart-card">
        <div class="chart-header">
          <div>
            <div class="card-title" style="margin-bottom:2px;">Elbow Method (WCSS / Inertia)</div>
            <div style="font-size: 11px; color: #6B7772;">WCSS curve across K=2..8 to detect curvature elbow</div>
          </div>
          <span class="chart-badge">Optimal K = ${optK}</span>
        </div>
        <div class="chart-container">
          <canvas id="chart-elbow"></canvas>
        </div>
      </div>

      <div class="card chart-card">
        <div class="chart-header">
          <div>
            <div class="card-title" style="margin-bottom:2px;">Silhouette Score Analysis</div>
            <div style="font-size: 11px; color: #6B7772;">Cluster tightness & separation efficiency</div>
          </div>
          <span class="chart-badge">Authoritative K = ${optK} (${optSilScore})</span>
        </div>
        <div class="chart-container">
          <canvas id="chart-silhouette"></canvas>
        </div>
      </div>
    </div>

    <!-- Second Row: Customer Demand Dynamics (Area Demand + Daily Trend) -->
    <div class="charts-grid">
      <div class="card chart-card">
        <div class="chart-header">
          <div>
            <div class="card-title" style="margin-bottom:2px;">Demand by Area</div>
            <div style="font-size: 11px; color: #6B7772;">Total order distribution across Nanded localities</div>
          </div>
          <span class="chart-badge">${areaSummary.length} Localities</span>
        </div>
        <div class="chart-container">
          <canvas id="chart-area-demand"></canvas>
        </div>
      </div>

      <div class="card chart-card">
        <div class="chart-header">
          <div>
            <div class="card-title" style="margin-bottom:2px;">Daily Order Trend</div>
            <div style="font-size: 11px; color: #6B7772;">Time-series order volume trajectory</div>
          </div>
          <span class="chart-badge">${dailyDemand.length} Days Tracked</span>
        </div>
        <div class="chart-container">
          <canvas id="chart-daily-trend"></canvas>
        </div>
      </div>
    </div>

    <!-- Bottom Row: Discovered Customer Clusters Table -->
    <div class="card" style="margin-top: 4px;">
      <div class="chart-header" style="margin-bottom:8px;">
        <div class="card-title" style="margin-bottom:0;">Discovered Customer Clusters (K=${d.clusters.length})</div>
        <span class="chart-badge">Model: scikit-learn KMeans</span>
      </div>
      <div class="table-container" style="margin-top: 10px;">
        <table>
          <thead>
            <tr>
              <th>Cluster ID</th>
              <th>Zone Label</th>
              <th>Customer Count</th>
              <th>Total Demand</th>
              <th>Avg Order Value</th>
              <th>Centroid Lat / Lon</th>
            </tr>
          </thead>
          <tbody>
            ${d.clusters.map(c => `
              <tr>
                <td>#${c.cluster_id + 1}</td>
                <td><span class="badge ${c.label.includes('High') ? 'badge-rec' : 'badge-info'}">${c.label}</span></td>
                <td>${c.customer_count}</td>
                <td>₹${c.total_order_value.toLocaleString()} (${c.demand_pct}%)</td>
                <td>₹${Math.round(c.avg_order_value)}</td>
                <td>${c.centroid_latitude}, ${c.centroid_longitude}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;

  setTimeout(() => initAnalyticsCharts(d), 0);
}

function initAnalyticsCharts(d) {
  if (typeof Chart === 'undefined') {
    console.error('Chart.js library is not loaded');
    return;
  }

  // Set global Chart.js styling
  Chart.defaults.font.family = "'Plus Jakarta Sans', -apple-system, sans-serif";
  Chart.defaults.color = "#6B7772";

  const optK = d.analytics?.optimal_k;

  // 1. Elbow / WCSS Chart
  const elbowData = d.analytics?.elbow || [];
  const elbowCanvas = document.getElementById('chart-elbow');
  if (elbowCanvas && elbowData.length > 0) {
    activeCharts['elbow'] = new Chart(elbowCanvas.getContext('2d'), {
      type: 'line',
      data: {
        labels: elbowData.map(item => `K=${item.k}`),
        datasets: [{
          label: 'WCSS (Inertia)',
          data: elbowData.map(item => item.wcss),
          borderColor: '#17644F',
          backgroundColor: 'rgba(23, 100, 79, 0.08)',
          borderWidth: 2.5,
          tension: 0.25,
          fill: true,
          pointBackgroundColor: elbowData.map(item => item.k === optK ? '#D8E86A' : '#17644F'),
          pointBorderColor: elbowData.map(item => item.k === optK ? '#10231D' : '#FFFFFF'),
          pointBorderWidth: elbowData.map(item => item.k === optK ? 2.5 : 1.5),
          pointRadius: elbowData.map(item => item.k === optK ? 7 : 4),
          pointHoverRadius: elbowData.map(item => item.k === optK ? 9 : 6),
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#18231F',
            titleColor: '#F8FAF7',
            bodyColor: '#F8FAF7',
            padding: 10,
            cornerRadius: 4,
            callbacks: {
              label: (context) => {
                const kVal = elbowData[context.dataIndex]?.k;
                const isOpt = kVal === optK ? ' ★ Authoritative Optimal K' : '';
                return ` WCSS: ${Number(context.raw).toLocaleString()}${isOpt}`;
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: 'Number of Clusters (K)', color: '#6B7772', font: { weight: '600', size: 11 } },
            grid: { color: 'rgba(221, 216, 204, 0.4)' },
            ticks: { color: '#6B7772' }
          },
          y: {
            title: { display: true, text: 'WCSS / Inertia', color: '#6B7772', font: { weight: '600', size: 11 } },
            grid: { color: 'rgba(221, 216, 204, 0.4)' },
            ticks: { color: '#6B7772' }
          }
        }
      }
    });
  }

  // 2. Silhouette Score Chart
  const silData = d.analytics?.silhouette || [];
  const silCanvas = document.getElementById('chart-silhouette');
  if (silCanvas && silData.length > 0) {
    activeCharts['silhouette'] = new Chart(silCanvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: silData.map(item => `K=${item.k}`),
        datasets: [{
          label: 'Silhouette Score',
          data: silData.map(item => item.silhouette_score),
          backgroundColor: silData.map(item => item.k === optK ? '#17644F' : 'rgba(23, 100, 79, 0.3)'),
          borderColor: silData.map(item => item.k === optK ? '#D8E86A' : '#17644F'),
          borderWidth: silData.map(item => item.k === optK ? 2 : 1),
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#18231F',
            titleColor: '#F8FAF7',
            bodyColor: '#F8FAF7',
            padding: 10,
            cornerRadius: 4,
            callbacks: {
              label: (context) => {
                const kVal = silData[context.dataIndex]?.k;
                const isOpt = kVal === optK ? ' ★ Authoritative Optimal K' : '';
                return ` Silhouette Score: ${context.raw}${isOpt}`;
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: 'Number of Clusters (K)', color: '#6B7772', font: { weight: '600', size: 11 } },
            grid: { display: false },
            ticks: { color: '#6B7772' }
          },
          y: {
            title: { display: true, text: 'Silhouette Score', color: '#6B7772', font: { weight: '600', size: 11 } },
            grid: { color: 'rgba(221, 216, 204, 0.4)' },
            ticks: { color: '#6B7772' },
            suggestedMin: 0
          }
        }
      }
    });
  }

  // 3. Demand by Area (Horizontal Bar Chart)
  const areaData = [...(d.demand?.area_summary || [])].sort((a, b) => b.total_orders - a.total_orders);
  const areaCanvas = document.getElementById('chart-area-demand');
  if (areaCanvas && areaData.length > 0) {
    activeCharts['areaDemand'] = new Chart(areaCanvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: areaData.map(a => a.area),
        datasets: [{
          label: 'Total Orders',
          data: areaData.map(a => a.total_orders),
          backgroundColor: areaData.map(a => a.zone_type?.includes('High') ? '#17644F' : 'rgba(23, 100, 79, 0.5)'),
          borderColor: '#17644F',
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#18231F',
            titleColor: '#F8FAF7',
            bodyColor: '#F8FAF7',
            padding: 10,
            cornerRadius: 4,
            callbacks: {
              label: (context) => {
                const item = areaData[context.dataIndex];
                return ` Orders: ${item.total_orders.toLocaleString()} (${item.demand_pct}% demand · ${item.customer_count} customers)`;
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: 'Total Orders', color: '#6B7772', font: { weight: '600', size: 11 } },
            grid: { color: 'rgba(221, 216, 204, 0.4)' },
            ticks: { color: '#6B7772' }
          },
          y: {
            title: { display: true, text: 'Area / Locality', color: '#6B7772', font: { weight: '600', size: 11 } },
            grid: { display: false },
            ticks: { color: '#18231F', font: { size: 11, weight: '500' } }
          }
        }
      }
    });
  }

  // 4. Daily Order Trend (Time Series Line Chart)
  const dailyData = d.demand?.daily_demand || [];
  const dailyCanvas = document.getElementById('chart-daily-trend');
  if (dailyCanvas && dailyData.length > 0) {
    activeCharts['dailyTrend'] = new Chart(dailyCanvas.getContext('2d'), {
      type: 'line',
      data: {
        labels: dailyData.map(item => item.date),
        datasets: [{
          label: 'Daily Orders',
          data: dailyData.map(item => item.orders),
          borderColor: '#17644F',
          backgroundColor: 'rgba(23, 100, 79, 0.12)',
          borderWidth: 2,
          tension: 0.25,
          fill: true,
          pointRadius: 2,
          pointHoverRadius: 5,
          pointBackgroundColor: '#17644F'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#18231F',
            titleColor: '#F8FAF7',
            bodyColor: '#F8FAF7',
            padding: 10,
            cornerRadius: 4,
            callbacks: {
              label: (context) => {
                const item = dailyData[context.dataIndex];
                const rev = item?.revenue != null ? ` · Revenue: ₹${Math.round(item.revenue).toLocaleString()}` : '';
                return ` Orders: ${context.raw}${rev}`;
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: 'Order Date', color: '#6B7772', font: { weight: '600', size: 11 } },
            grid: { color: 'rgba(221, 216, 204, 0.4)' },
            ticks: {
              color: '#6B7772',
              maxTicksLimit: 10,
              maxRotation: 0
            }
          },
          y: {
            title: { display: true, text: 'Orders', color: '#6B7772', font: { weight: '600', size: 11 } },
            grid: { color: 'rgba(221, 216, 204, 0.4)' },
            ticks: { color: '#6B7772' }
          }
        }
      }
    });
  }
}

function renderNetworkMap(container, d) {
  container.innerHTML = `
    <div class="card">
      <div style="display:flex; justify-between; align-items:center; margin-bottom: 12px;">
        <div class="card-title">Interactive Geospatial Map — Nanded</div>
        <div style="font-size:12px; color:#94a3b8;">Showing ${d.customers.length} customer locations & candidate sites</div>
      </div>
      <div id="map-box"></div>
    </div>
  `;

  setTimeout(() => {
    if (typeof L !== 'undefined') {
      const map = L.map('map-box').setView([19.155, 77.31], 12);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '© OpenStreetMap'
      }).addTo(map);

      // Plot Customers
      d.customers.forEach(c => {
        L.circleMarker([c.latitude, c.longitude], {
          radius: 3,
          color: '#3b82f6',
          fillColor: '#60a5fa',
          fillOpacity: 0.6,
          weight: 1
        }).bindPopup(`<b>Customer ${c.customer_id}</b><br>Area: ${c.area}<br>Order Value: ₹${c.order_value}`).addTo(map);
      });

      // Plot Candidates
      d.candidates.forEach(cand => {
        const isBest = cand.rank === 1;
        const marker = L.circleMarker([cand.latitude, cand.longitude], {
          radius: isBest ? 10 : 7,
          color: isBest ? '#10b981' : '#f59e0b',
          fillColor: isBest ? '#10b981' : '#f59e0b',
          fillOpacity: 0.9,
          weight: isBest ? 3 : 2
        }).addTo(map);

        marker.bindPopup(`
          <div style="color:#000;">
            <b>${isBest ? '⭐ #1 AI RECOMMENDED' : `Rank #${cand.rank}`}</b><br>
            <b>${cand.area}</b><br>
            AI Score: <b>${cand.ai_score}/100</b><br>
            Avg Delivery Dist: ${cand.average_delivery_distance} km<br>
            Monthly Cost: ₹${cand.operating_cost.toLocaleString()}
          </div>
        `);
      });
    }
  }, 100);
}

function renderDataManagement(container, d) {
  container.innerHTML = `
    <div class="card">
      <div class="card-title">Upload Customer Order CSV Dataset</div>
      <p style="font-size: 13px; color: #94a3b8; margin: 10px 0;">Upload your e-commerce order records CSV file to dynamically clean data and re-run K-Means geospatial clustering.</p>
      <input type="file" id="csv-input" accept=".csv,.xlsx" style="background:#1e293b; padding:10px; border-radius:6px; color:#fff;" />
      <button id="upload-btn" style="background:#10b981; color:#fff; border:none; padding:10px 20px; font-weight:bold; border-radius:6px; cursor:pointer; margin-left:10px;">Upload & Analyze</button>
    </div>
    <div class="card" style="margin-top: 20px;">
      <div class="card-title">Current Dataset Quality Summary</div>
      <div class="table-container" style="margin-top:12px;">
        <table>
          <tr><th>Total Uploaded Rows</th><td>${d.quality.total_rows}</td></tr>
          <tr><th>Valid Clean Rows</th><td>${d.quality.valid_rows}</td></tr>
          <tr><th>Duplicates Removed</th><td>${d.quality.duplicates_removed}</td></tr>
          <tr><th>Invalid Coordinates Filtered</th><td>${d.quality.invalid_coordinates_removed}</td></tr>
        </table>
      </div>
    </div>
  `;

  document.getElementById('upload-btn')?.addEventListener('click', async () => {
    const fileInput = document.getElementById('csv-input');
    if (!fileInput.files.length) return alert('Select a CSV file first.');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const headers = {};
    if (appState.token) {
      headers['Authorization'] = `Bearer ${appState.token}`;
    }

    try {
      const res = await fetch(`/api/upload?priority=${appState.priority}&k=${appState.k}`, {
        method: 'POST',
        headers,
        body: formData
      });
      if (res.ok) {
        appState.analysisData = await res.json();
        alert('Dataset uploaded and analyzed successfully!');
        appState.currentView = 'dashboard';
        renderCurrentView();
      } else {
        alert('Upload failed: ' + (await res.text()));
      }
    } catch (e) {
      alert('Error uploading file: ' + e.message);
    }
  });
}

function renderScenarioSimulator(container, d) {
  container.innerHTML = `
    <div class="card">
      <div class="card-title">Business Priority & Cluster Simulator</div>
      <p style="font-size: 13px; color: #94a3b8; margin: 10px 0;">Test how changing optimization priorities or cluster count affects the recommended delivery center.</p>
      <div style="display:flex; gap:20px; align-items:center; margin-top:16px;">
        <div>
          <label style="font-size:12px; color:#94a3b8; display:block; margin-bottom:4px;">Cluster Count K (2-8):</label>
          <select id="sim-k" style="background:#1e293b; color:#fff; border:1px solid #334155; padding:8px 12px; border-radius:6px;">
            ${[2,3,4,5,6,7,8].map(kv => `<option value="${kv}" ${kv === appState.k ? 'selected' : ''}>K = ${kv}</option>`).join('')}
          </select>
        </div>
        <button id="run-sim" style="background:#3b82f6; color:#fff; border:none; padding:10px 20px; font-weight:bold; border-radius:6px; cursor:pointer;">Run Simulation</button>
      </div>
    </div>
  `;

  document.getElementById('run-sim')?.addEventListener('click', () => {
    appState.k = parseInt(document.getElementById('sim-k').value);
    appState.analysisData = null;
    fetchAnalysis();
  });
}

function renderImpact(container, d) {
  const rec = d.recommendation || {};
  const avgDist = rec.average_delivery_distance != null ? `${rec.average_delivery_distance} km` : 'N/A';
  const coverage = rec.coverage_percentage != null ? `${rec.coverage_percentage}%` : 'N/A';
  const cost = rec.operating_cost != null ? `₹${Number(rec.operating_cost).toLocaleString()}` : 'N/A';
  container.innerHTML = `
    <div class="card">
      <div class="card-title">Estimated Business Impact Summary</div>
      <div class="kpi-grid" style="margin-top:16px;">
        <div class="card" style="background:#0f172a;">
          <div class="card-title">Avg Delivery Distance Reduction</div>
          <div class="card-value" style="color:#94a3b8; font-size:18px;">Not Calculated</div>
          <div class="card-sub">Dynamic baseline pending Phase 4 (Current: ${avgDist})</div>
        </div>
        <div class="card" style="background:#0f172a;">
          <div class="card-title">Customer 5km Coverage</div>
          <div class="card-value" style="color:#3b82f6;">${coverage}</div>
          <div class="card-sub">Direct reach</div>
        </div>
        <div class="card" style="background:#0f172a;">
          <div class="card-title">Estimated Monthly Operating Cost</div>
          <div class="card-value">${cost}</div>
          <div class="card-sub">Projected hub cost</div>
        </div>
      </div>
    </div>
  `;
}

function renderMethodology(container, d) {
  container.innerHTML = `
    <div class="card">
      <div class="card-title">Research Methodology & Workflow</div>
      <div style="font-size:13px; color:#cbd5e1; line-height:1.8; margin-top:12px;">
        <ol style="padding-left: 20px;">
          <li><b>Spatial Data Collection</b>: Customer locations, orders, and road metrics for Nanded.</li>
          <li><b>Data Cleaning</b>: Filtering bad coordinates, duplicates, and missing values via Pandas.</li>
          <li><b>K-Means Clustering</b>: Clustering customer coordinates using Scikit-Learn.</li>
          <li><b>Elbow Method & WCSS</b>: Calculating inertia across K=2..8 to detect knee curvature.</li>
          <li><b>Silhouette Analysis</b>: Measuring separation tightness of customer demand clusters.</li>
          <li><b>Candidate Location Generation</b>: Centroid synthesis + commercial nodes.</li>
          <li><b>Multi-Criteria Location Scoring</b>: Weighted formula combining Demand, Distance, Road Connectivity, Cost, and Coverage.</li>
        </ol>
      </div>
    </div>
  `;
}

// Event Listeners Initialization
document.addEventListener('DOMContentLoaded', () => {
  // Priority selector
  const prioritySelect = document.getElementById('priority');
  if (prioritySelect) {
    prioritySelect.value = appState.priority;
    prioritySelect.addEventListener('change', (e) => {
      appState.priority = e.target.value;
      appState.analysisData = null;
      fetchAnalysis();
    });
  }

  // Sidebar Nav buttons
  document.querySelectorAll('.sidebar .nav').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.sidebar .nav').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      appState.currentView = btn.getAttribute('data-view');
      renderCurrentView();
    });
  });

  // Render initial auth button / profile badge
  renderUserProfile();

  // Initial Fetch
  fetchAnalysis();
});

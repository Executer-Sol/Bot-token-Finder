// ============================================
// CORREÇÕES E MELHORIAS DO DASHBOARD
// ============================================

// Variáveis globais que estavam faltando
let realtimeMonitoringActive = false;
let allActiveTrades = [];
let activeTradesData = [];
let currentSort = { field: null, direction: 'asc' };

// ============================================
// FUNÇÕES DE MONITORAMENTO TEMPO REAL
// ============================================
async function startAlchemyRealtimeMonitoring() {
    try {
        const response = await fetch('/api/alchemy/realtime/start', {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            realtimeMonitoringActive = true;
            showToast('✅ Monitoramento em tempo real iniciado', 'success');
            startRealtimePolling();
        } else {
            showToast('❌ ' + (result.error || 'Erro ao iniciar monitoramento'), 'error');
        }
    } catch (error) {
        console.error('Erro ao iniciar monitoramento:', error);
        showToast('❌ Erro ao iniciar monitoramento', 'error');
    }
}

async function stopAlchemyRealtimeMonitoring() {
    try {
        const response = await fetch('/api/alchemy/realtime/stop', {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            realtimeMonitoringActive = false;
            showToast('⏸️ Monitoramento em tempo real parado', 'info');
            stopRealtimePolling();
        } else {
            showToast('❌ ' + (result.error || 'Erro ao parar monitoramento'), 'error');
        }
    } catch (error) {
        console.error('Erro ao parar monitoramento:', error);
        showToast('❌ Erro ao parar monitoramento', 'error');
    }
}

function startRealtimePolling() {
    // Polling para atualizar dados em tempo real
    if (window.realtimePollingInterval) {
        clearInterval(window.realtimePollingInterval);
    }
    
    window.realtimePollingInterval = setInterval(async () => {
        if (realtimeMonitoringActive) {
            try {
                await loadData();
            } catch (error) {
                console.error('Erro no polling:', error);
            }
        }
    }, 5000); // Atualiza a cada 5 segundos
}

function stopRealtimePolling() {
    if (window.realtimePollingInterval) {
        clearInterval(window.realtimePollingInterval);
        window.realtimePollingInterval = null;
    }
}

// ============================================
// FUNÇÃO ÚNICA PARA CONFIGURAÇÃO ALCHEMY
// ============================================
function openAlchemyConfig() {
    const modal = document.getElementById('alchemyConfigModal');
    const apiKeyInput = document.getElementById('alchemyApiKey');
    
    if (!modal || !apiKeyInput) {
        console.error('Modal ou input não encontrado');
        return;
    }
    
    const savedKey = localStorage.getItem('alchemy_api_key') || '';
    apiKeyInput.value = savedKey;
    modal.style.display = 'flex';
}

// ============================================
// CARREGAMENTO PROGRESSIVO
// ============================================
async function loadProgressive() {
    // Fase 1: Crítico (0s)
    await loadEssential();
    
    // Fase 2: Importante (1s)
    setTimeout(loadImportant, 1000);
    
    // Fase 3: Secundário (2s)
    setTimeout(loadSecondary, 2000);
}

async function loadEssential() {
    try {
        // KPIs + trades ativos (crítico)
        const [statsResponse, tradesResponse] = await Promise.all([
            fetch('/api/stats'),
            fetch('/api/trades/active')
        ]);
        
        const stats = await statsResponse.json();
        const trades = await tradesResponse.json();
        
        // Renderizar imediatamente
        if (typeof renderKPIs === 'function') {
            renderKPIs(stats);
        }
        if (typeof updateActiveTrades === 'function') {
            updateActiveTrades(trades);
        }
    } catch (error) {
        console.error('Erro ao carregar dados essenciais:', error);
    }
}

async function loadImportant() {
    try {
        // Wallet + bot state
        await Promise.all([
            fetch('/api/wallet-balance').then(r => r.json()).then(data => {
                if (typeof loadWalletBalance === 'function') {
                    loadWalletBalance();
                }
            }),
            fetch('/api/bot/state').then(r => r.json()).then(data => {
                if (typeof loadBotState === 'function') {
                    loadBotState();
                }
            })
        ]);
    } catch (error) {
        console.error('Erro ao carregar dados importantes:', error);
    }
}

async function loadSecondary() {
    try {
        // Histórico + estatísticas do dia
        await Promise.all([
            fetch('/api/trades/sold').then(r => r.json()).then(data => {
                if (typeof loadSoldTrades === 'function') {
                    loadSoldTrades();
                }
            }),
            fetch('/api/daily-stats').then(r => r.json()).then(data => {
                if (typeof loadDailyStats === 'function') {
                    loadDailyStats();
                }
            })
        ]);
    } catch (error) {
        console.error('Erro ao carregar dados secundários:', error);
    }
}

// ============================================
// INICIALIZAÇÃO
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Verifica status do monitoramento
    if (typeof checkRealtimeStatus === 'function') {
        checkRealtimeStatus();
    }
    
    // Carrega dados progressivamente
    loadProgressive();
    
    // Esconde loading overlay após carregar dados essenciais
    setTimeout(() => {
        const loader = document.getElementById('initialLoader');
        if (loader) {
            loader.classList.add('hidden');
        }
    }, 1500);
});

// Exporta funções para uso global
window.realtimeMonitoringActive = realtimeMonitoringActive;
window.startAlchemyRealtimeMonitoring = startAlchemyRealtimeMonitoring;
window.stopAlchemyRealtimeMonitoring = stopAlchemyRealtimeMonitoring;
window.openAlchemyConfig = openAlchemyConfig;
window.loadProgressive = loadProgressive;











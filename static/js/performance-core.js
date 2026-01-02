// ============================================
// CORE DE PERFORMANCE - Otimizações Críticas
// ============================================

// ============================================
// 1. REQUEST DEDUPLICATOR
// ============================================
class RequestDeduplicator {
    constructor() {
        this.pending = new Map();
    }
    
    async fetch(url, options = {}) {
        const key = url + JSON.stringify(options);
        
        // Se já tem requisição em andamento, retorna a mesma Promise
        if (this.pending.has(key)) {
            console.log('♻️ Reusando request:', url);
            return this.pending.get(key);
        }
        
        const promise = fetch(url, options)
            .then(r => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                return r.json();
            })
            .finally(() => {
                // Remove após 100ms para permitir cache
                setTimeout(() => this.pending.delete(key), 100);
            });
        
        this.pending.set(key, promise);
        return promise;
    }
    
    clear() {
        this.pending.clear();
    }
}

// ============================================
// 2. SMART CACHE
// ============================================
class SmartCache {
    constructor() {
        this.cache = new Map();
        this.ttls = {
            '/api/stats': 30000,           // 30s
            '/api/trades/active': 15000,   // 15s
            '/api/trades/sold': 60000,      // 60s (não muda rápido)
            '/api/wallet-balance': 45000,   // 45s
            '/api/last-token': 10000,       // 10s (mais importante)
            '/api/bot/state': 30000,        // 30s
            '/api/sol-price': 120000,       // 2min (preço muda devagar)
            '/api/daily-stats': 60000,      // 60s
            '/api/consolidated': 10000      // 10s
        };
    }
    
    get(url) {
        const item = this.cache.get(url);
        if (!item) return null;
        
        const ttl = this.ttls[url] || 30000;
        const isExpired = Date.now() - item.timestamp > ttl;
        
        if (isExpired) {
            this.cache.delete(url);
            return null;
        }
        
        console.log('💾 Cache hit:', url);
        return item.data;
    }
    
    set(url, data) {
        this.cache.set(url, {
            data,
            timestamp: Date.now()
        });
        console.log('💾 Cache set:', url);
    }
    
    clear(url = null) {
        if (url) {
            this.cache.delete(url);
            console.log('🗑️ Cache cleared:', url);
        } else {
            this.cache.clear();
            console.log('🗑️ All cache cleared');
        }
    }
    
    has(url) {
        const item = this.cache.get(url);
        if (!item) return false;
        const ttl = this.ttls[url] || 30000;
        return Date.now() - item.timestamp <= ttl;
    }
}

// ============================================
// 3. UPDATE SCHEDULER (Polling Inteligente)
// ============================================
class UpdateScheduler {
    constructor() {
        this.lastUpdate = {};
        this.intervals = {
            critical: 10000,    // 10s - Trades ativos e último token
            normal: 30000,      // 30s - Stats gerais
            slow: 60000         // 60s - Wallet, config, histórico
        };
        this.isRunning = false;
        this.tickInterval = null;
    }
    
    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        
        // Verifica a cada 5s se precisa atualizar
        this.tickInterval = setInterval(() => this.tick(), 5000);
        console.log('🔄 UpdateScheduler iniciado');
    }
    
    stop() {
        if (this.tickInterval) {
            clearInterval(this.tickInterval);
            this.tickInterval = null;
        }
        this.isRunning = false;
        console.log('⏸️ UpdateScheduler parado');
    }
    
    tick() {
        if (!window.dashboard) return;
        
        const now = Date.now();
        
        // Atualiza apenas se passou tempo suficiente
        if (now - (this.lastUpdate.critical || 0) >= this.intervals.critical) {
            this.updateCritical();
            this.lastUpdate.critical = now;
        }
        
        if (now - (this.lastUpdate.normal || 0) >= this.intervals.normal) {
            this.updateNormal();
            this.lastUpdate.normal = now;
        }
        
        if (now - (this.lastUpdate.slow || 0) >= this.intervals.slow) {
            this.updateSlow();
            this.lastUpdate.slow = now;
        }
    }
    
    async updateCritical() {
        // Apenas trades ativos e último token (mais importante)
        if (window.dashboard && typeof window.dashboard.loadActiveTrades === 'function') {
            window.dashboard.loadActiveTrades().catch(err => console.error('Erro ao atualizar trades:', err));
        }
        if (window.dashboard && typeof window.dashboard.loadLastToken === 'function') {
            window.dashboard.loadLastToken().catch(err => console.error('Erro ao atualizar último token:', err));
        }
    }
    
    async updateNormal() {
        // Stats gerais
        if (window.dashboard && typeof window.dashboard.loadStats === 'function') {
            window.dashboard.loadStats().catch(err => console.error('Erro ao atualizar stats:', err));
        }
    }
    
    async updateSlow() {
        // Wallet, bot state, histórico
        if (window.dashboard && typeof window.dashboard.loadWalletBalance === 'function') {
            window.dashboard.loadWalletBalance().catch(err => console.error('Erro ao atualizar wallet:', err));
        }
        if (window.dashboard && typeof window.dashboard.loadBotState === 'function') {
            window.dashboard.loadBotState().catch(err => console.error('Erro ao atualizar bot state:', err));
        }
    }
}

// ============================================
// 4. DASHBOARD CORE (Consolidado)
// ============================================
class DashboardCore {
    constructor() {
        this.cache = new SmartCache();
        this.requestDedupe = new RequestDeduplicator();
        this.scheduler = new UpdateScheduler();
        this.isInitialized = false;
    }
    
    // Fetch com cache e deduplicação
    async fetch(url, options = {}, forceRefresh = false) {
        // Verifica cache primeiro
        if (!forceRefresh) {
            const cached = this.cache.get(url);
            if (cached) {
                return cached;
            }
        }
        
        // Usa deduplicator para evitar requisições duplicadas
        const data = await this.requestDedupe.fetch(url, options);
        
        // Salva no cache
        this.cache.set(url, data);
        
        return data;
    }
    
    // Load Active Trades (consolidado)
    async loadActiveTrades(forceRefresh = false) {
        try {
            const data = await this.fetch('/api/trades/active', {}, forceRefresh);
            
            if (typeof this.renderActiveTrades === 'function') {
                this.renderActiveTrades(data);
            } else if (typeof window.renderActiveTradesTable === 'function') {
                window.renderActiveTradesTable(data);
            }
            
            return data;
        } catch (error) {
            console.error('Erro ao carregar trades ativos:', error);
            throw error;
        }
    }
    
    // Load Stats (consolidado)
    async loadStats(forceRefresh = false) {
        try {
            const data = await this.fetch('/api/stats', {}, forceRefresh);
            
            // Tenta renderizar usando função global se disponível
            if (typeof window.loadStats === 'function' && window.loadStats !== this.loadStats) {
                // Chama função global que já tem lógica de renderização
                await window.loadStats(forceRefresh);
                return data;
            } else if (typeof this.renderStats === 'function') {
                this.renderStats(data);
            }
            
            return data;
        } catch (error) {
            console.error('Erro ao carregar stats:', error);
            throw error;
        }
    }
    
    // Load Last Token (consolidado)
    async loadLastToken(forceRefresh = false) {
        try {
            const data = await this.fetch('/api/last-token', {}, forceRefresh);
            
            // Tenta usar função global se disponível
            if (typeof window.loadLastToken === 'function' && window.loadLastToken !== this.loadLastToken) {
                await window.loadLastToken(forceRefresh);
                return data;
            } else if (typeof this.renderLastToken === 'function') {
                this.renderLastToken(data);
            }
            
            return data;
        } catch (error) {
            console.error('Erro ao carregar último token:', error);
            throw error;
        }
    }
    
    // Load Wallet Balance
    async loadWalletBalance(forceRefresh = false) {
        try {
            const data = await this.fetch('/api/wallet-balance', {}, forceRefresh);
            
            if (typeof this.renderWalletBalance === 'function') {
                this.renderWalletBalance(data);
            }
            
            return data;
        } catch (error) {
            console.error('Erro ao carregar wallet:', error);
            throw error;
        }
    }
    
    // Load Bot State
    async loadBotState(forceRefresh = false) {
        try {
            const data = await this.fetch('/api/bot/state', {}, forceRefresh);
            
            if (typeof this.renderBotState === 'function') {
                this.renderBotState(data);
            }
            
            return data;
        } catch (error) {
            console.error('Erro ao carregar bot state:', error);
            throw error;
        }
    }
    
    // Load Sold Trades
    async loadSoldTrades(forceRefresh = false) {
        try {
            const data = await this.fetch('/api/trades/sold', {}, forceRefresh);
            
            if (typeof this.renderSoldTrades === 'function') {
                this.renderSoldTrades(data);
            }
            
            return data;
        } catch (error) {
            console.error('Erro ao carregar trades vendidos:', error);
            throw error;
        }
    }
    
    // Carregamento essencial (para primeira renderização)
    async loadEssential(forceRefresh = false) {
        try {
            // Carrega dados críticos em paralelo
            const [stats, trades, lastToken] = await Promise.all([
                this.loadStats(forceRefresh),
                this.loadActiveTrades(forceRefresh),
                this.loadLastToken(forceRefresh)
            ]);
            
            return { stats, trades, lastToken };
        } catch (error) {
            console.error('Erro ao carregar dados essenciais:', error);
            throw error;
        }
    }
    
    // Inicialização
    async init() {
        if (this.isInitialized) return;
        
        console.log('🚀 DashboardCore inicializando...');
        
        // Carrega dados essenciais
        await this.loadEssential();
        
        // Inicia scheduler
        this.scheduler.start();
        
        this.isInitialized = true;
        console.log('✅ DashboardCore inicializado');
    }
    
    // Limpa cache
    clearCache(url = null) {
        this.cache.clear(url);
    }
    
    // Força refresh de tudo
    async refreshAll() {
        console.log('🔄 Forçando refresh de todos os dados...');
        this.cache.clear();
        await this.loadEssential(true);
    }
}

// ============================================
// 5. INICIALIZAÇÃO GLOBAL
// ============================================
window.requestDedupe = new RequestDeduplicator();
window.smartCache = new SmartCache();
window.dashboard = new DashboardCore();

// Inicializa quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.dashboard.init();
    });
} else {
    window.dashboard.init();
}

console.log('✅ Performance Core carregado');


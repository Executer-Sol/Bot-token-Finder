// ============================================
// DASHBOARD PRINCIPAL - CLASSE ORGANIZADA
// ============================================

class TradingDashboard {
  constructor() {
    this.cache = new Map();
    this.cacheTTL = 30000; // 30 segundos
    this.apiQueue = [];
    this.isProcessing = false;
    this.updateIntervals = {
      active: null,
      stats: null,
      bot: null
    };
    this.solPriceUSD = 150.0;
    this.previousSolPrice = 150.0;
    this.charts = {
      profitLoss: null,
      scorePerformance: null,
      profitLossPie: null,
      hourlyProfit: null
    };
    this.allActiveTrades = [];
    this.allSoldTrades = [];
    this.isDarkMode = localStorage.getItem('darkMode') === 'true';
    
    this.init();
  }
  
  async init() {
    this.Logger.log('Inicializando dashboard...');
    await this.loadDependencies();
    this.setupEventListeners();
    this.setupDarkMode();
    await this.loadInitialData();
    this.startOptimizedIntervals();
    this.Logger.log('Dashboard inicializado!');
  }
  
  // ============================================
  // LOGGER
  // ============================================
  Logger = {
    log: (...args) => console.log('[Dashboard]', ...args),
    error: (...args) => console.error('[Dashboard]', ...args),
    warn: (...args) => console.warn('[Dashboard]', ...args),
    info: (...args) => console.info('[Dashboard]', ...args)
  };
  
  // ============================================
  // CARREGAMENTO DE DEPENDÊNCIAS
  // ============================================
  async loadDependencies() {
    // Chart.js lazy loading
    if (typeof Chart === 'undefined') {
      await this.loadScript('https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js');
      this.Logger.log('Chart.js carregado');
    }
  }
  
  loadScript(url) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = url;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }
  
  // ============================================
  // CACHE E RATE LIMITING
  // ============================================
  async fetchWithCache(url, options = {}, forceRefresh = false) {
    const cacheKey = `${url}_${JSON.stringify(options)}`;
    
    // Se forceRefresh, ignora cache
    if (!forceRefresh) {
      const cached = this.cache.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
        this.Logger.log('Cache hit:', url);
        return cached.data;
      }
    }
    
    const data = await this.queueRequest(async () => {
      const response = await fetch(url, options);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    });
    
    // Atualiza cache mesmo se forceRefresh
    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now()
    });
    
    return data;
  }
  
  // Limpa cache de URLs específicas
  clearCache(urlPattern = null) {
    if (urlPattern) {
      // Remove apenas entradas que correspondem ao padrão
      for (const [key] of this.cache.entries()) {
        if (key.includes(urlPattern)) {
          this.cache.delete(key);
        }
      }
    } else {
      // Limpa todo o cache
      this.cache.clear();
    }
    this.Logger.log('Cache limpo:', urlPattern || 'tudo');
  }
  
  async queueRequest(fn) {
    return new Promise((resolve, reject) => {
      this.apiQueue.push({ fn, resolve, reject });
      if (!this.isProcessing) this.processQueue();
    });
  }
  
  async processQueue() {
    if (this.isProcessing || this.apiQueue.length === 0) return;
    this.isProcessing = true;
    
    const { fn, resolve, reject } = this.apiQueue.shift();
    try {
      const result = await fn();
      resolve(result);
    } catch (error) {
      this.Logger.error('Queue error:', error);
      reject(error);
    }
    
    this.isProcessing = false;
    setTimeout(() => this.processQueue(), 100); // Rate limit: 10 req/s
  }
  
  // ============================================
  // ALCHEMY DATA APIs
  // ============================================
  async getAlchemyPortfolio(walletAddress) {
    try {
      // Se tiver API key do Alchemy configurada
      const apiKey = this.getAlchemyApiKey();
      if (!apiKey) {
        // Só mostra aviso uma vez por sessão
        if (!this._alchemyWarningShown) {
          this.Logger.warn('Alchemy API key não configurada, usando RPC padrão. Clique no botão "🔑 Alchemy" para configurar.');
          this._alchemyWarningShown = true;
        }
        return null;
      }
      
      // Usa endpoint do backend que gerencia a API key
      const url = '/api/alchemy/portfolio';
      const headers = { 
        'X-Alchemy-API-Key': apiKey,
        'Content-Type': 'application/json'
      };
      
      return await this.fetchWithCache(url, { headers });
    } catch (error) {
      this.Logger.error('Erro ao buscar portfolio Alchemy:', error);
      return null;
    }
  }
  
  async getAlchemyTransfers(walletAddress, limit = 50) {
    try {
      const apiKey = this.getAlchemyApiKey();
      if (!apiKey) return null;
      
      const url = `https://solana-mainnet.g.alchemy.com/v0/accounts/${walletAddress}/transfers`;
      const headers = { 'X-Alchemy-Token': apiKey };
      const params = { limit };
      
      const queryString = new URLSearchParams(params).toString();
      return await this.fetchWithCache(`${url}?${queryString}`, { headers });
    } catch (error) {
      this.Logger.error('Erro ao buscar transfers Alchemy:', error);
      return null;
    }
  }
  
  async getAlchemyTokenPrice(tokenAddress) {
    try {
      const apiKey = this.getAlchemyApiKey();
      if (!apiKey) return null;
      
      const url = `https://solana-mainnet.g.alchemy.com/v0/prices/token/${tokenAddress}`;
      const headers = { 'X-Alchemy-Token': apiKey };
      
      const data = await this.fetchWithCache(url, { headers });
      return data?.price || null;
    } catch (error) {
      this.Logger.error('Erro ao buscar preço Alchemy:', error);
      return null;
    }
  }
  
  getAlchemyApiKey() {
    // Busca do localStorage primeiro
    let apiKey = localStorage.getItem('alchemy_api_key');
    
    // Se não tiver no localStorage, tenta extrair do RPC_URL se for Alchemy
    if (!apiKey) {
      // Verifica se há uma API key padrão do Alchemy no RPC_URL
      // Isso é útil se a mesma API key for usada para RPC e Data APIs
      const rpcUrl = window.location.origin; // Não temos acesso direto ao RPC_URL do backend
      // Mas podemos tentar buscar do servidor
      // Por enquanto, retorna null e deixa o backend extrair do RPC_URL
    }
    
    return apiKey || null;
  }
  
  // ============================================
  // DETECÇÃO AUTOMÁTICA DE VENDAS (ALCHEMY)
  // ============================================
  async detectSellsFromAlchemy(walletAddress) {
    try {
      const transfers = await this.getAlchemyTransfers(walletAddress, 100);
      if (!transfers || !transfers.transfers) return [];
      
      // Filtra apenas transferências que receberam SOL (vendas)
      const sells = transfers.transfers.filter(t => {
        return t.to === walletAddress && 
               t.category === 'external' && 
               t.value > 0;
      });
      
      return sells.map(transfer => ({
        signature: transfer.hash,
        timestamp: transfer.block_timestamp,
        sol_received: transfer.value,
        token_mint: transfer.token_address || null,
        token_symbol: transfer.token_symbol || 'UNKNOWN'
      }));
    } catch (error) {
      this.Logger.error('Erro ao detectar vendas:', error);
      return [];
    }
  }
  
  // ============================================
  // CARREGAMENTO DE DADOS
  // ============================================
  async loadInitialData() {
    const start = performance.now();
    
    try {
      await Promise.all([
        this.loadStats(),
        this.loadActiveTrades(),
        this.loadSoldTrades(),
        this.loadLastToken(),
        this.loadWalletBalance(),
        this.loadDailyStats(),
        this.loadBlacklist(),
        this.loadDailyTokens(),
        this.fetchSOLPrice()
      ]);
      
      const end = performance.now();
      this.Logger.log(`Dados carregados em ${(end - start).toFixed(2)}ms`);
    } catch (error) {
      this.Logger.error('Erro ao carregar dados iniciais:', error);
    }
  }
  
  async loadStats() {
    try {
      const stats = await this.fetchWithCache('/api/stats');
      this.renderStats(stats);
      this.renderScoreAnalysis(stats.score_analysis);
      this.renderActiveAnalysis(stats.active_analysis);
      this.renderPerformanceAnalysis(stats.performance_analysis);
    } catch (error) {
      this.Logger.error('Erro ao carregar stats:', error);
    }
  }
  
  async loadActiveTrades() {
    try {
      const trades = await this.fetchWithCache('/api/trades/active');
      this.allActiveTrades = trades;
      this.renderActiveTrades(trades);
    } catch (error) {
      this.Logger.error('Erro ao carregar trades ativos:', error);
    }
  }
  
  async loadSoldTrades(forceRefresh = false) {
    try {
      const trades = await this.fetchWithCache('/api/trades/sold', {}, forceRefresh);
      this.allSoldTrades = trades;
      this.renderSoldTrades(trades);
    } catch (error) {
      this.Logger.error('Erro ao carregar trades vendidos:', error);
    }
  }
  
  async loadWalletBalance() {
    try {
      const balance = await this.fetchWithCache('/api/wallet-balance');
      this.renderWalletBalance(balance);
      
      // Tenta usar Alchemy Portfolio API se disponível
      if (balance.wallet_address) {
        const portfolio = await this.getAlchemyPortfolio(balance.wallet_address);
        if (portfolio) {
          this.renderAlchemyPortfolio(portfolio);
        }
      }
    } catch (error) {
      this.Logger.error('Erro ao carregar saldo:', error);
    }
  }
  
  // ============================================
  // INTERVALOS OTIMIZADOS
  // ============================================
  startOptimizedIntervals() {
    // Se monitoramento em tempo real estiver ativo, usa intervalos mais frequentes
    const isRealtimeActive = window.realtimeMonitoringActive || false;
    const activeInterval = isRealtimeActive ? 2000 : 3000; // 2s se tempo real, 3s normal
    const otherInterval = isRealtimeActive ? 5000 : 10000; // 5s se tempo real, 10s normal
    
    // Consolidar intervalos em um único
    setInterval(() => {
      Promise.all([
        this.loadActiveTrades(),
        this.loadStats()
      ]).catch(err => this.Logger.error('Erro no intervalo:', err));
    }, activeInterval);
    
    // Intervalo menos frequente para outros dados
    setInterval(() => {
      Promise.all([
        this.loadBotState(),
        this.loadLastToken(),
        this.loadWalletBalance(),
        this.fetchSOLPrice()
      ]).catch(err => this.Logger.error('Erro no intervalo:', err));
    }, otherInterval);
  }
  
  // ============================================
  // BUSCA EM TEMPO REAL
  // ============================================
  setupSearch() {
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = '🔍 Buscar tokens...';
    searchInput.className = 'search-input';
    searchInput.setAttribute('aria-label', 'Buscar tokens');
    
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        this.filterTrades(e.target.value.toLowerCase());
      }, 300); // Debounce
    });
    
    // Adiciona ao header das abas
    const resumoHeader = document.querySelector('#tab-resumo .trades-panel h2');
    if (resumoHeader) {
      resumoHeader.appendChild(searchInput);
    }
  }
  
  filterTrades(searchTerm) {
    if (!searchTerm) {
      this.renderActiveTrades(this.allActiveTrades);
      this.renderSoldTrades(this.allSoldTrades);
      return;
    }
    
    const filteredActive = this.allActiveTrades.filter(trade => 
      trade.symbol.toLowerCase().includes(searchTerm) ||
      trade.contract_address.toLowerCase().includes(searchTerm)
    );
    
    const filteredSold = this.allSoldTrades.filter(trade => 
      trade.symbol.toLowerCase().includes(searchTerm) ||
      trade.contract_address.toLowerCase().includes(searchTerm)
    );
    
    this.renderActiveTrades(filteredActive);
    this.renderSoldTrades(filteredSold);
  }
  
  // ============================================
  // EXPORTAÇÃO CSV
  // ============================================
  exportToCSV(data, filename) {
    if (!data || data.length === 0) {
      this.showToast('Nenhum dado para exportar', 'error');
      return;
    }
    
    const headers = Object.keys(data[0]);
    const csv = [
      headers.join(','),
      ...data.map(row => 
        headers.map(h => {
          const value = row[h] || '';
          // Escapa vírgulas e aspas
          return `"${String(value).replace(/"/g, '""')}"`;
        }).join(',')
      )
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    
    this.showToast('✅ Dados exportados!', 'success');
  }
  
  // ============================================
  // VALIDAÇÃO
  // ============================================
  isValidSolanaAddress(address) {
    return /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(address);
  }
  
  sanitizeInput(input) {
    return input.trim().replace(/[<>]/g, '');
  }
  
  // ============================================
  // EVENT LISTENERS
  // ============================================
  setupEventListeners() {
    // Atalhos de teclado
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'r') {
          e.preventDefault();
          this.loadInitialData();
          this.showToast('🔄 Dados atualizados!', 'info');
        }
        if (e.key === 'e') {
          e.preventDefault();
          this.exportToCSV(this.allSoldTrades, 'trades_vendidos');
        }
      }
      if (e.key === 'Escape') {
        this.closeModals();
      }
      if (e.key === 'd' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.toggleDarkMode();
      }
    });
    
    // Setup busca
    this.setupSearch();
  }
  
  // ============================================
  // DARK MODE
  // ============================================
  setupDarkMode() {
    if (this.isDarkMode) {
      document.body.classList.add('dark-mode');
      const toggle = document.querySelector('.dark-mode-toggle');
      if (toggle) toggle.textContent = '☀️';
    }
  }
  
  toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    this.isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', this.isDarkMode);
    const toggle = document.querySelector('.dark-mode-toggle');
    if (toggle) {
      toggle.textContent = this.isDarkMode ? '☀️' : '🌙';
    }
  }
  
  // ============================================
  // TOAST NOTIFICATIONS
  // ============================================
  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toast.setAttribute('role', 'alert');
    document.getElementById('toastContainer').appendChild(toast);
    
    setTimeout(() => {
      toast.style.animation = 'slideIn 0.3s ease reverse';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }
  
  // ============================================
  // RENDERIZAÇÃO (métodos simplificados)
  // ============================================
  renderStats(stats) {
    if (!stats) return;
    
    const activeCountEl = document.getElementById('activeCount');
    const soldCountEl = document.getElementById('soldCount');
    if (activeCountEl) activeCountEl.textContent = stats.active_count || 0;
    if (soldCountEl) soldCountEl.textContent = stats.sold_count || 0;
    
    // Profit/Loss
    const activeProfitEl = document.getElementById('activeProfit');
    if (activeProfitEl) {
      activeProfitEl.innerHTML = this.formatSOLWithUSD(stats.total_active_profit_loss || 0);
      activeProfitEl.className = 'value ' + this.getProfitClass(stats.total_active_profit_loss || 0);
    }
    
    const soldProfitEl = document.getElementById('soldProfit');
    if (soldProfitEl) {
      soldProfitEl.innerHTML = this.formatSOLWithUSD(stats.total_sold_profit_loss || 0);
      soldProfitEl.className = 'value ' + this.getProfitClass(stats.total_sold_profit_loss || 0);
    }
    
    const overallProfitEl = document.getElementById('overallProfit');
    if (overallProfitEl) {
      overallProfitEl.innerHTML = this.formatSOLWithUSD(stats.overall_profit_loss || 0);
      overallProfitEl.className = 'value ' + this.getProfitClass(stats.overall_profit_loss || 0);
    }
    
    const overallCard = document.getElementById('overallCard');
    if (overallCard) {
      overallCard.className = 'stat-card ' + this.getProfitClass(stats.overall_profit_loss || 0);
    }
    
    // Win Rate
    const winRateEl = document.getElementById('winRate');
    const winRateDetailsEl = document.getElementById('winRateDetails');
    if (winRateEl && stats.win_rate !== undefined) {
      winRateEl.textContent = this.formatNumber(stats.win_rate) + '%';
      if (winRateDetailsEl) {
        winRateDetailsEl.textContent = `${stats.profitable_trades || 0} ganhos / ${stats.losing_trades || 0} perdas`;
      }
    }
    
    // ROI Médio
    const avgROIEl = document.getElementById('avgROI');
    if (avgROIEl && stats.avg_roi !== undefined) {
      avgROIEl.textContent = this.formatPercent(stats.avg_roi);
      avgROIEl.className = 'value ' + this.getProfitClass(stats.avg_roi);
    }
    
    // Tokens comprados
    if (stats.today_tokens_bought !== undefined) {
      const todayEl = document.getElementById('todayTokens');
      if (todayEl) todayEl.textContent = stats.today_tokens_bought;
    }
    if (stats.total_tokens_bought !== undefined) {
      const totalEl = document.getElementById('totalTokens');
      if (totalEl) totalEl.textContent = stats.total_tokens_bought;
    }
    
    // Renderiza análises se disponíveis
    if (stats.score_analysis) {
      this.renderScoreAnalysis(stats.score_analysis);
    }
    if (stats.active_analysis) {
      this.renderActiveAnalysis(stats.active_analysis);
    }
    if (stats.performance_analysis) {
      this.renderPerformanceAnalysis(stats.performance_analysis);
    }
  }
  
  formatSOLWithUSD(solValue) {
    if (solValue === null || solValue === undefined || isNaN(solValue)) return '';
    const usdValue = solValue * this.solPriceUSD;
    const sign = usdValue >= 0 ? '+' : '';
    const color = usdValue >= 0 ? '#10b981' : '#ef4444';
    return `
      <div style="display: flex; flex-direction: column; align-items: flex-start;">
        <div>${this.formatNumber(solValue)} SOL</div>
        <div style="font-size: 0.75em; color: ${color}; margin-top: 2px; opacity: 0.85;">${sign}$${this.formatNumber(Math.abs(usdValue))} USD</div>
      </div>
    `;
  }
  
  formatPercent(num) {
    const sign = num >= 0 ? '+' : '';
    return `${sign}${this.formatNumber(num)}%`;
  }
  
  getProfitClass(profit) {
    if (profit > 0) return 'profit';
    if (profit < 0) return 'loss';
    return '';
  }
  
  renderScoreAnalysis(scoreAnalysis) {
    const container = document.getElementById('scoreAnalysis');
    if (!container || !scoreAnalysis || Object.keys(scoreAnalysis).length === 0) {
      if (container) container.innerHTML = '<div style="padding: 15px; text-align: center; color: #999;">Nenhum dado disponível</div>';
      return;
    }
    
    let html = '';
    for (const [score, data] of Object.entries(scoreAnalysis)) {
      const winRate = data.count > 0 ? (data.profitable / data.count * 100) : 0;
      html += `
        <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; margin-bottom: 10px;">
          <div style="font-weight: bold; margin-bottom: 8px;">Score ${score}</div>
          <div style="font-size: 0.9em; color: #666;">Tokens: ${data.count} | Lucrativos: ${data.profitable} (${this.formatNumber(winRate)}%)</div>
        </div>
      `;
    }
    container.innerHTML = html;
  }
  
  renderActiveAnalysis(activeAnalysis) {
    const container = document.getElementById('activeAnalysis');
    if (!container || !activeAnalysis || activeAnalysis.length === 0) {
      if (container) container.innerHTML = '<div style="padding: 15px; text-align: center; color: #999;">Nenhum token ativo</div>';
      return;
    }
    
    let html = '';
    for (const token of activeAnalysis) {
      html += `
        <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; margin-bottom: 10px;">
          <div style="font-weight: bold; margin-bottom: 8px;">${this.sanitizeInput(token.symbol)}</div>
          <div style="font-size: 0.9em; color: #666;">Score: ${token.score} | Múltiplo: ${this.formatNumber(token.multiple)}x</div>
        </div>
      `;
    }
    container.innerHTML = html;
  }
  
  renderPerformanceAnalysis(performance) {
    if (!performance) return;
    
    // Métricas básicas
    const avgTimeToPeakEl = document.getElementById('avgTimeToPeak');
    if (avgTimeToPeakEl && performance.avg_time_to_peak !== null) {
      avgTimeToPeakEl.textContent = this.formatNumber(performance.avg_time_to_peak) + ' min';
    }
    
    const avgTimeToSellEl = document.getElementById('avgTimeToSell');
    if (avgTimeToSellEl && performance.avg_time_to_sell !== null) {
      avgTimeToSellEl.textContent = this.formatNumber(performance.avg_time_to_sell) + ' min';
    }
    
    const avgPeakMultipleEl = document.getElementById('avgPeakMultiple');
    if (avgPeakMultipleEl && performance.avg_peak_multiple !== null) {
      avgPeakMultipleEl.textContent = this.formatNumber(performance.avg_peak_multiple) + 'x';
    }
  }
  
  renderActiveTrades(trades) {
    const container = document.getElementById('activeTrades');
    if (!container) return;
    
    if (trades.length === 0) {
      container.innerHTML = '<div class="no-trades">Nenhum token ativo no momento</div>';
      return;
    }
    
    // Renderização similar à anterior
    container.innerHTML = trades.map(trade => this.renderTradeItem(trade, 'active')).join('');
  }
  
  renderSoldTrades(trades) {
    const container = document.getElementById('soldTrades');
    if (!container) return;
    
    if (trades.length === 0) {
      container.innerHTML = '<div class="no-trades">Nenhum token vendido ainda</div>';
      return;
    }
    
    trades.sort((a, b) => new Date(b.sold_at) - new Date(a.sold_at));
    container.innerHTML = trades.map(trade => this.renderTradeItem(trade, 'sold')).join('');
  }
  
  renderTradeItem(trade, type) {
    // Renderização simplificada
    return `
      <div class="trade-item ${type}">
        <div class="trade-header">
          <div class="trade-symbol">${this.sanitizeInput(trade.symbol)}</div>
          <div class="trade-score">Score: ${trade.score}</div>
        </div>
        <!-- Resto do HTML -->
      </div>
    `;
  }
  
  renderWalletBalance(balance) {
    // Renderização do saldo
    const container = document.getElementById('walletBalanceContent');
    if (!container) return;
    
    container.innerHTML = `
      <div style="text-align: center;">
        <div style="font-size: 0.9em; opacity: 0.9; margin-bottom: 8px;">SOL</div>
        <div style="font-size: 2em; font-weight: bold;">${this.formatNumber(balance.sol)}</div>
      </div>
      <!-- Resto -->
    `;
  }
  
  renderAlchemyPortfolio(portfolio) {
    // Renderiza dados do Alchemy Portfolio API
    this.Logger.log('Portfolio Alchemy:', portfolio);
    // Implementar renderização específica
  }
  
  // ============================================
  // UTILITÁRIOS
  // ============================================
  formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) return '0';
    return new Intl.NumberFormat('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 8
    }).format(num);
  }
  
  formatPrice(num) {
    if (num === null || num === undefined || isNaN(num) || num === 0) return '$0,00';
    
    if (Math.abs(num) < 0.0001) {
      const formatted = num.toFixed(10).replace(/\.?0+$/, '');
      return '$' + formatted.replace('.', ',');
    } else if (Math.abs(num) < 0.01) {
      const formatted = num.toFixed(8).replace(/\.?0+$/, '');
      return '$' + formatted.replace('.', ',');
    } else {
      const formatted = num.toFixed(4).replace(/\.?0+$/, '');
      return '$' + formatted.replace('.', ',');
    }
  }
  
  async fetchSOLPrice() {
    try {
      const data = await this.fetchWithCache('/api/sol-price');
      if (data.price && data.price > 0) {
        this.previousSolPrice = this.solPriceUSD;
        this.solPriceUSD = data.price;
      }
    } catch (error) {
      this.Logger.error('Erro ao buscar preço SOL:', error);
    }
  }
  
  closeModals() {
    // Fecha todos os modais abertos
    document.querySelectorAll('[id$="Modal"]').forEach(modal => {
      if (modal.style.display !== 'none') {
        modal.style.display = 'none';
      }
    });
  }
  
  // ============================================
  // MÉTODOS ADICIONAIS
  // ============================================
  async loadLastToken() {
    try {
      const token = await this.fetchWithCache('/api/last-token');
      const container = document.getElementById('lastTokenContent');
      if (!container) return;
      
      if (!token || !token.symbol) {
        container.innerHTML = '<div class="no-trades">Nenhum token detectado ainda</div>';
        return;
      }
      
      const date = new Date(token.detected_at);
      const timeAgo = Math.floor((Date.now() - date.getTime()) / 1000 / 60);
      let timeDisplay = timeAgo + ' minutos atrás';
      if (timeAgo < 1) timeDisplay = 'Agora mesmo';
      else if (timeAgo === 1) timeDisplay = '1 minuto atrás';
      
      container.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
          <div><div style="font-size: 0.9em; color: #666;">Símbolo</div><div style="font-size: 1.5em; font-weight: bold;">${this.sanitizeInput(token.symbol)}</div></div>
          <div><div style="font-size: 0.9em; color: #666;">Score</div><div style="font-size: 1.5em; font-weight: bold; color: #667eea;">${token.score}</div></div>
          <div><div style="font-size: 0.9em; color: #666;">Preço</div><div style="font-size: 1.5em; font-weight: bold;">$${this.formatNumber(token.price)}</div></div>
          <div><div style="font-size: 0.9em; color: #666;">Tempo</div><div style="font-size: 1.2em; font-weight: bold;">${timeDisplay}</div></div>
        </div>
      `;
    } catch (error) {
      this.Logger.error('Erro ao carregar último token:', error);
    }
  }
  
  async loadDailyStats() {
    try {
      const stats = await this.fetchWithCache('/api/daily-stats');
      const dailyTradesEl = document.getElementById('dailyTradesCount');
      if (dailyTradesEl) dailyTradesEl.textContent = stats.trades_count || 0;
    } catch (error) {
      this.Logger.error('Erro ao carregar stats diários:', error);
    }
  }
  
  async loadBlacklist() {
    try {
      const data = await this.fetchWithCache('/api/blacklist');
      const container = document.getElementById('blacklistContent');
      if (!container) return;
      
      if (data.addresses && data.addresses.length > 0) {
        container.innerHTML = data.addresses.map(address => `
          <div style="display: flex; justify-content: space-between; padding: 10px; margin-bottom: 5px; background: #f5f5f5; border-radius: 8px;">
            <span style="font-family: monospace; font-size: 0.9em;">${address}</span>
          </div>
        `).join('');
      } else {
        container.innerHTML = '<div style="color: #999; text-align: center; padding: 20px;">Nenhum token na blacklist</div>';
      }
    } catch (error) {
      this.Logger.error('Erro ao carregar blacklist:', error);
    }
  }
  
  async loadDailyTokens() {
    try {
      const data = await this.fetchWithCache('/api/daily-tokens');
      const container = document.getElementById('dailyTokensList');
      if (!container) return;
      
      if (data.error) {
        container.innerHTML = `<div style="color: #ef4444; padding: 20px; text-align: center;">Erro: ${data.error}</div>`;
        return;
      }
      
      if (document.getElementById('dailyTotal')) {
        document.getElementById('dailyTotal').textContent = data.total || 0;
        document.getElementById('dailyProfitable').textContent = data.profitable || 0;
        document.getElementById('dailyLosing').textContent = data.losing || 0;
        document.getElementById('dailyActive').textContent = data.active || 0;
      }
      
      if (!data.tokens || data.tokens.length === 0) {
        container.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;">Nenhum token detectado hoje ainda</div>';
        return;
      }
      
      container.innerHTML = data.tokens.map(token => {
        const profitClass = token.profit_loss_sol >= 0 ? 'profit' : 'loss';
        return `
          <div style="background: white; border-radius: 12px; padding: 20px; border-left: 4px solid ${token.profit_loss_sol >= 0 ? '#10b981' : '#ef4444'};">
            <div style="display: flex; justify-content: space-between; align-items: start;">
              <div>
                <div style="font-size: 1.5em; font-weight: bold; margin-bottom: 8px;">${this.sanitizeInput(token.symbol)}</div>
                <div style="font-size: 0.9em; color: #666;">Score: ${token.score} | Preço: $${this.formatNumber(token.entry_price)}</div>
              </div>
              <div style="text-align: right;">
                <div style="font-size: 1.8em; font-weight: bold; color: ${token.profit_loss_sol >= 0 ? '#10b981' : '#ef4444'};">
                  ${token.percent_change >= 0 ? '+' : ''}${this.formatNumber(token.percent_change)}%
                </div>
              </div>
            </div>
          </div>
        `;
      }).join('');
    } catch (error) {
      this.Logger.error('Erro ao carregar tokens diários:', error);
    }
  }
  
  async loadBotState() {
    try {
      const data = await this.fetchWithCache('/api/bot/state');
      const statusText = document.getElementById('botStatusText');
      const toggleBtn = document.getElementById('toggleBotBtn');
      
      if (statusText && toggleBtn) {
        if (data.enabled) {
          statusText.textContent = '✅ Bot ATIVO';
          statusText.style.color = '#10b981';
          toggleBtn.textContent = '⏸️ Desativar Bot';
          toggleBtn.style.background = '#ef4444';
        } else {
          statusText.textContent = '⏸️ Bot DESATIVADO';
          statusText.style.color = '#ef4444';
          toggleBtn.textContent = '▶️ Ativar Bot';
          toggleBtn.style.background = '#10b981';
        }
      }
    } catch (error) {
      this.Logger.error('Erro ao carregar estado do bot:', error);
    }
  }
  
  async loadTradingConfig() {
    try {
      const config = await this.fetchWithCache('/api/trading-config');
      // Implementação básica - pode ser expandida
      this.Logger.log('Config carregada:', config);
    } catch (error) {
      this.Logger.error('Erro ao carregar config:', error);
    }
  }
  
  async loadCharts() {
    try {
      if (typeof Chart === 'undefined') {
        await this.loadDependencies();
      }
      // Implementação básica - pode ser expandida
      this.Logger.log('Gráficos carregados');
    } catch (error) {
      this.Logger.error('Erro ao carregar gráficos:', error);
    }
  }
  
  async loadHourlyAnalysis() {
    try {
      const trades = await this.fetchWithCache('/api/trades/sold');
      if (trades.length === 0) {
        const content = document.getElementById('analiseContent');
        if (content) content.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">Nenhum dado disponível</p>';
        return;
      }
      // Implementação básica - pode ser expandida
      this.Logger.log('Análise horária carregada');
    } catch (error) {
      this.Logger.error('Erro ao carregar análise:', error);
    }
  }
  
  async performHealthCheck() {
    try {
      const data = await this.fetchWithCache('/api/health-check');
      // Implementação básica - pode ser expandida
      this.Logger.log('Health check realizado');
    } catch (error) {
      this.Logger.error('Erro no health check:', error);
    }
  }
}

// ============================================
// INICIALIZAÇÃO
// ============================================
let dashboard;

document.addEventListener('DOMContentLoaded', () => {
  dashboard = new TradingDashboard();
  
  // Expor globalmente para compatibilidade
  window.dashboard = dashboard;
  
  // Funções globais para compatibilidade com HTML
  window.loadData = () => dashboard.loadInitialData();
  window.toggleDarkMode = () => dashboard.toggleDarkMode();
  window.exportData = () => dashboard.exportToCSV(dashboard.allSoldTrades, 'trades');
  
  // Funções que precisam acessar métodos do dashboard
  window.loadStats = (forceRefresh = false) => dashboard.loadStats(forceRefresh);
  window.loadActiveTrades = () => dashboard.loadActiveTrades();
  window.loadSoldTrades = (forceRefresh = false) => dashboard.loadSoldTrades(forceRefresh);
  window.loadLastToken = () => dashboard.loadLastToken();
  window.loadWalletBalance = () => dashboard.loadWalletBalance();
  window.loadDailyStats = () => dashboard.loadDailyStats();
  window.loadBlacklist = () => dashboard.loadBlacklist();
  window.loadDailyTokens = () => dashboard.loadDailyTokens();
  window.loadBotState = () => dashboard.loadBotState();
  window.loadTradingConfig = () => dashboard.loadTradingConfig();
  window.loadCharts = () => dashboard.loadCharts();
  window.loadHourlyAnalysis = () => dashboard.loadHourlyAnalysis();
  window.performHealthCheck = () => dashboard.performHealthCheck();
});


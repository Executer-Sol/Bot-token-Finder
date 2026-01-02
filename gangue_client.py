"""
Cliente para buscar tokens do site da Gangue (gangue.macaco.club)
Substitui o Telegram como fonte de informações
"""
import aiohttp
import asyncio
import json
import re
import os
from typing import Optional, List
from datetime import datetime, timezone
from message_parser import TokenInfo, parse_price_with_subscript

class GangueClient:
    def __init__(self, session_cookie: str = None, ga_cookie: str = None, cookies_file: str = 'cookies.json'):
        """
        Inicializa cliente da Gangue
        Args:
            session_cookie: Cookie de sessão (ex: "s%3A1234567890abcdef...") - opcional se usar cookies_file
            ga_cookie: Cookie do Google Analytics (ex: "GA1.2.1234567890.1234567890") - opcional se usar cookies_file
            cookies_file: Caminho para arquivo JSON com cookies (padrão: cookies.json)
        """
        self.base_url = "https://gangue.macaco.club"
        self.cookies_file = cookies_file
        self.session_cookie = session_cookie
        self.ga_cookie = ga_cookie
        self.session = None
        
        # Tenta carregar cookies do arquivo se não foram fornecidos
        if not self.session_cookie and os.path.exists(cookies_file):
            self._load_cookies_from_file()
    
    def _get_headers(self):
        """Retorna headers para requisições"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': f'{self.base_url}/',
            'Origin': self.base_url
        }
        return headers
    
    def _load_cookies_from_file(self):
        """Carrega cookies do arquivo JSON"""
        try:
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # Formato esperado: [{"name": "session", "value": "...", ...}, ...]
            for cookie in cookies_data:
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                
                if name == 'session':
                    self.session_cookie = value
                elif name == '_ga':
                    self.ga_cookie = value
            
            if self.session_cookie:
                print(f"✅ Cookies carregados de {self.cookies_file} (session encontrado)")
            else:
                print(f"⚠️  Arquivo {self.cookies_file} não contém cookie 'session'")
        except FileNotFoundError:
            print(f"⚠️  Arquivo {self.cookies_file} não encontrado. Usando cookies das variáveis de ambiente (se configuradas)")
        except Exception as e:
            print(f"⚠️  Erro ao carregar cookies de {self.cookies_file}: {e}")
            print(f"   Usando cookies das variáveis de ambiente (se configuradas)")
    
    def _get_cookies(self):
        """Retorna cookies para requisições"""
        cookies = {}
        if self.session_cookie:
            cookies['session'] = self.session_cookie
        if self.ga_cookie:
            cookies['_ga'] = self.ga_cookie
        return cookies
    
    async def fetch_tokens(self, limit: int = 50) -> List[dict]:
        """
        Busca tokens do site da Gangue
        Retorna lista de tokens com informações
        """
        try:
            # Tenta diferentes endpoints possíveis
            endpoints = [
                '/api/tokens',
                '/api/tokens/recent',
                '/api/tokens/latest',
                '/tokens',
                '/api/v1/tokens',
                '/api/token-finder',  # Possível endpoint do Token Finder
                '/token-finder',  # Possível rota do Token Finder
                '/alphas',  # Possível rota de alphas/tokens
            ]
            
            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints:
                    try:
                        url = f"{self.base_url}{endpoint}"
                        cookies = self._get_cookies()
                        headers = self._get_headers()
                        
                        async with session.get(
                            url,
                            headers=headers,
                            cookies=cookies,
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                content_type = response.headers.get('Content-Type', '')
                                
                                if 'application/json' in content_type:
                                    data = await response.json()
                                    # Tenta diferentes estruturas de resposta
                                    if isinstance(data, list):
                                        return data
                                    elif isinstance(data, dict):
                                        # Pode estar em 'tokens', 'data', 'results', etc.
                                        for key in ['tokens', 'data', 'results', 'items']:
                                            if key in data:
                                                return data[key]
                                        return [data] if data else []
                                    return []
                                else:
                                    # Se for HTML, tenta parsear
                                    html = await response.text()
                                    return self._parse_html_tokens(html)
                    except Exception as e:
                        # Não imprime erro para cada endpoint (muito verbose)
                        # print(f"⚠️  Erro ao tentar endpoint {endpoint}: {e}")
                        continue
                
                # Se nenhum endpoint funcionou, tenta scraping HTML da página principal
                print("⚠️  Nenhum endpoint JSON funcionou, tentando scraping HTML...")
                # Tenta primeiro a página do Token Finder (onde os tokens são exibidos)
                tokens = await self._scrape_token_finder_page()
                if not tokens:
                    tokens = await self._scrape_main_page()
                return tokens
                
        except Exception as e:
            print(f"❌ Erro ao buscar tokens da Gangue: {e}")
            return []
    
    def _parse_html_tokens(self, html: str) -> List[dict]:
        """Parse tokens de HTML - melhorado para extrair dados de JavaScript e HTML"""
        tokens = []
        try:
            import re
            from html import unescape
            import json
            
            # MÉTODO 1: Procura por dados JSON em scripts JavaScript
            # Muitos sites SPA carregam dados iniciais em scripts
            script_patterns = [
                r'<script[^>]*>.*?(\{.*?"tokens".*?\}).*?</script>',
                r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
                r'window\.__DATA__\s*=\s*(\{.*?\});',
                r'const\s+tokens\s*=\s*(\[.*?\]);',
                r'var\s+tokens\s*=\s*(\[.*?\]);',
                r'"tokens"\s*:\s*(\[.*?\])',
                r'data-tokens=["\'](\[.*?\])["\']',
            ]
            
            for pattern in script_patterns:
                matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    try:
                        # Tenta parsear como JSON
                        data = json.loads(match)
                        if isinstance(data, list):
                            tokens.extend(data)
                        elif isinstance(data, dict):
                            # Procura por chaves comuns
                            for key in ['tokens', 'data', 'items', 'results', 'list']:
                                if key in data and isinstance(data[key], list):
                                    tokens.extend(data[key])
                                    break
                    except:
                        continue
            
            # Se encontrou tokens em scripts, retorna
            if tokens:
                print(f"✅ Encontrados {len(tokens)} tokens em scripts JavaScript")
                return tokens
            
            # MÉTODO 2: Usa BeautifulSoup para parsing mais robusto
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Procura por elementos com data-attributes
                data_elements = soup.find_all(attrs={'data-token': True}) + \
                               soup.find_all(attrs={'data-ca': True}) + \
                               soup.find_all(attrs={'data-contract': True})
                
                for elem in data_elements:
                    token_data = {}
                    # Extrai dados dos atributos data-*
                    for attr in elem.attrs:
                        if attr.startswith('data-'):
                            key = attr.replace('data-', '').replace('-', '_')
                            token_data[key] = elem.attrs[attr]
                    
                    # Tenta extrair texto do elemento
                    text = elem.get_text(strip=True)
                    
                    # Procura por contract address no texto ou atributos
                    ca_match = re.search(r'([A-Za-z0-9]{32,44})', text + str(elem.attrs))
                    if ca_match:
                        token_data['contract_address'] = ca_match.group(1)
                    
                    # Procura por score
                    score_match = re.search(r'(\d{1,2})', text)
                    if score_match:
                        try:
                            score = int(score_match.group(1))
                            if 10 <= score <= 21:
                                token_data['score'] = score
                        except:
                            pass
                    
                    if 'contract_address' in token_data and 'score' in token_data:
                        tokens.append(token_data)
                
                # MÉTODO PRINCIPAL: Procura por tabelas (como MemeBuyBot faz com Cheerio)
                # Estrutura esperada: <table> com <tr> contendo <td> com ticker, CA, score
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) < 2:
                            continue
                        
                        # Extrai texto de cada célula (mais preciso que juntar tudo)
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        row_text = ' '.join(cell_texts)
                        
                        # Procura contract address (string longa alfanumérica de 32-44 chars)
                        ca_match = re.search(r'([A-Za-z0-9]{32,44})', row_text)
                        if not ca_match:
                            continue
                        
                        contract_address = ca_match.group(1)
                        
                        # Procura score (número entre 10-21, mais específico)
                        score_match = re.search(r'\b(1[0-9]|2[01])\b', row_text)
                        if not score_match:
                            continue
                        
                        try:
                            score = int(score_match.group(1))
                            if not (10 <= score <= 21):
                                continue
                        except:
                            continue
                        
                        # Procura símbolo (primeira palavra curta alfanumérica)
                        # Estratégia: procura em cada célula individualmente
                        symbol = 'UNKNOWN'
                        for i, cell_text in enumerate(cell_texts):
                            # Se encontrou o CA nesta célula, símbolo provavelmente está antes
                            if contract_address in cell_text and i > 0:
                                # Tenta pegar da célula anterior
                                prev_text = cell_texts[i-1]
                                symbol_match = re.search(r'([A-Za-z0-9]{2,10})', prev_text)
                                if symbol_match:
                                    symbol = symbol_match.group(1).upper()
                                    break
                            # Ou procura diretamente no texto da célula (padrão: SYMBOL ... CA)
                            symbol_match = re.search(r'([A-Za-z0-9]{2,10})\s+[A-Za-z0-9]{32,44}', cell_text)
                            if symbol_match:
                                symbol = symbol_match.group(1).upper()
                                break
                        
                        # Se não encontrou símbolo, tenta padrão mais simples em toda a linha
                        if symbol == 'UNKNOWN':
                            symbol_match = re.search(r'([A-Za-z0-9]{2,10})', row_text)
                            if symbol_match:
                                symbol = symbol_match.group(1).upper()
                        
                        tokens.append({
                            'symbol': symbol,
                            'score': score,
                            'contract_address': contract_address,
                            'price': 0.0
                        })
                
                # Remove duplicatas baseado no contract address
                seen = set()
                unique_tokens = []
                for token in tokens:
                    ca = token.get('contract_address', '')
                    if ca and ca not in seen:
                        seen.add(ca)
                        unique_tokens.append(token)
                
                if unique_tokens:
                    print(f"✅ BeautifulSoup encontrou {len(unique_tokens)} tokens únicos")
                    return unique_tokens
            except ImportError:
                # BeautifulSoup não instalado, continua com regex
                pass
            except Exception as e:
                print(f"⚠️  Erro ao usar BeautifulSoup: {e}")
            
            # MÉTODO 3: Fallback para regex (método original melhorado)
            if not tokens:
                # Procura por linhas de tabela (tr) com dados
                table_rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
                
                for row in table_rows:
                    # Procura por contract address (longa string alfanumérica)
                    contract_match = re.search(r'([A-Za-z0-9]{32,44})', row)
                    if not contract_match:
                        continue
                    
                    contract_address = contract_match.group(1)
                    
                    # Procura por score (número após "Score" ou em coluna separada)
                    score_match = re.search(r'(?:Score[:\s]*)?(\d{1,2})', row, re.IGNORECASE)
                    if not score_match:
                        continue
                    
                    score = int(score_match.group(1))
                    
                    # Procura por símbolo/ticker (texto curto, geralmente antes do contract)
                    # Remove tags HTML primeiro
                    clean_row = re.sub(r'<[^>]+>', ' ', row)
                    clean_row = unescape(clean_row)
                    
                    # Procura por palavra curta (2-10 caracteres) antes do contract
                    symbol_match = re.search(r'([A-Za-z0-9]{2,10})\s+[A-Za-z0-9]{32,44}', clean_row)
                    if symbol_match:
                        symbol = symbol_match.group(1)
                    else:
                        # Fallback: procura por padrão #SYMBOL
                        symbol_match = re.search(r'#([A-Za-z0-9]{2,10})', clean_row)
                        symbol = symbol_match.group(1) if symbol_match else 'UNKNOWN'
                    
                    # Procura por preço (opcional)
                    price_match = re.search(r'\$?(\d+\.?\d*[₀₁₂₃₄₅₆₇₈₉]?\d*)', clean_row)
                    price = 0.0
                    if price_match:
                        try:
                            price_str = price_match.group(1)
                            price = parse_price_with_subscript(price_str)
                        except:
                            pass
                    
                    tokens.append({
                        'symbol': symbol.upper(),
                        'score': score,
                        'contract_address': contract_address,
                        'price': price,
                        'price_usd': price
                    })
            
            # Se não encontrou na tabela, tenta padrão mais simples
            if len(tokens) == 0:
                # Procura por padrões: símbolo, contract, score em qualquer ordem
                # Formato: SYMBOL ... CONTRACT ... SCORE
                patterns = [
                    r'([A-Za-z0-9]{2,10})\s+.*?([A-Za-z0-9]{32,44})\s+.*?(\d{1,2})',
                    r'([A-Za-z0-9]{32,44})\s+.*?(\d{1,2})\s+.*?([A-Za-z0-9]{2,10})',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    for match in matches:
                        # Tenta identificar qual é qual
                        for item in match:
                            if len(item) >= 32:  # Contract address
                                contract_address = item
                            elif item.isdigit() and 10 <= int(item) <= 21:  # Score
                                score = int(item)
                            elif len(item) >= 2:  # Symbol
                                symbol = item
                        
                        if 'contract_address' in locals() and 'score' in locals() and 'symbol' in locals():
                            tokens.append({
                                'symbol': symbol.upper(),
                                'score': score,
                                'contract_address': contract_address,
                                'price': 0.0
                            })
                            break
            
            # Remove duplicatas baseado no contract address
            seen = set()
            unique_tokens = []
            for token in tokens:
                ca = token.get('contract_address', '')
                if ca and ca not in seen:
                    seen.add(ca)
                    unique_tokens.append(token)
            
            return unique_tokens
            
        except Exception as e:
            print(f"⚠️  Erro ao parsear HTML: {e}")
            import traceback
            traceback.print_exc()
        
        return tokens
    
    async def _scrape_token_finder_page(self) -> List[dict]:
        """Faz scraping da página do Token Finder (onde os tokens são exibidos)"""
        try:
            # Tenta acessar a página do Token Finder
            token_finder_urls = [
                f"{self.base_url}/token-finder",
                f"{self.base_url}/alphas",
                f"{self.base_url}/tokens",
            ]
            
            async with aiohttp.ClientSession() as session:
                for url in token_finder_urls:
                    try:
                        cookies = self._get_cookies()
                        headers = self._get_headers()
                        
                        async with session.get(
                            url,
                            headers=headers,
                            cookies=cookies,
                            timeout=aiohttp.ClientTimeout(total=15)
                        ) as response:
                            if response.status == 200:
                                html = await response.text()
                                tokens = self._parse_html_tokens(html)
                                
                                if len(tokens) > 0:
                                    print(f"✅ Encontrados {len(tokens)} tokens na página {url}")
                                    return tokens
                    except Exception as e:
                        continue
            
            return []
        except Exception as e:
            print(f"⚠️  Erro ao fazer scraping do Token Finder: {e}")
            return []
    
    async def _scrape_main_page(self) -> List[dict]:
        """Faz scraping da página principal - melhorado com Selenium (se disponível)"""
        try:
            # TENTATIVA 1: Usar Selenium para renderizar JavaScript (como MemeBuyBot)
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.common.exceptions import TimeoutException, WebDriverException
                
                print("🔄 Tentando usar Selenium para renderizar JavaScript...")
                
                # Configura Chrome em modo headless
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument(f'user-agent={self._get_headers()["User-Agent"]}')
                
                # Tenta criar driver (pode falhar se ChromeDriver não estiver instalado)
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                except Exception as e:
                    print(f"⚠️  Selenium não disponível (ChromeDriver não encontrado): {e}")
                    print("   Continuando com método HTTP simples...")
                    driver = None
                
                if driver:
                    try:
                        # Tenta primeiro a página do Token Finder (onde os tokens são exibidos)
                        token_finder_urls = [
                            f"{self.base_url}/token-finder",
                            f"{self.base_url}/alphas",
                            f"{self.base_url}/tokens",
                            f"{self.base_url}/",
                        ]
                        
                        for url in token_finder_urls:
                            try:
                                driver.get(url)
                                
                                # Adiciona cookies se disponíveis
                                cookies = self._get_cookies()
                                if cookies:
                                    for name, value in cookies.items():
                                        try:
                                            driver.add_cookie({'name': name, 'value': value, 'domain': '.macaco.club'})
                                        except:
                                            pass
                                
                                # Recarrega página com cookies
                                driver.get(url)
                                
                                # Aguarda tabela ou elementos com tokens carregarem (até 15 segundos)
                                try:
                                    # Tenta encontrar tabela
                                    WebDriverWait(driver, 15).until(
                                        EC.any_of(
                                            EC.presence_of_element_located((By.TAG_NAME, "table")),
                                            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-token], [data-ca], tr"))
                                        )
                                    )
                                    # Aguarda mais um pouco para HTMX/JavaScript carregar dados
                                    import asyncio
                                    await asyncio.sleep(3)  # Aumentado para 3 segundos
                                except TimeoutException:
                                    print(f"⚠️  Elementos não encontrados em {url}, mas continuando...")
                                
                                # Obtém HTML renderizado
                                html = driver.page_source
                                
                                # Testa parsing
                                tokens = self._parse_html_tokens(html)
                                
                                if len(tokens) > 0:
                                    print(f"✅ Encontrados {len(tokens)} tokens via Selenium em {url}")
                                    driver.quit()
                                    return tokens
                            except Exception as e:
                                print(f"⚠️  Erro ao acessar {url}: {e}")
                                continue
                        
                        driver.quit()
                        
                        # Parse HTML renderizado
                        tokens = self._parse_html_tokens(html)
                        
                        if len(tokens) > 0:
                            print(f"✅ Encontrados {len(tokens)} tokens via Selenium")
                            return tokens
                        else:
                            print("⚠️  Selenium renderizou página mas não encontrou tokens")
                    except Exception as e:
                        print(f"⚠️  Erro ao usar Selenium: {e}")
                        if driver:
                            driver.quit()
            except ImportError:
                print("⚠️  Selenium não instalado. Instale com: pip install selenium")
            except Exception as e:
                print(f"⚠️  Erro ao tentar Selenium: {e}")
            
            # TENTATIVA 2: HTTP simples (fallback)
            print("🔄 Tentando método HTTP simples...")
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/"
                cookies = self._get_cookies()
                headers = self._get_headers()
                
                async with session.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        tokens = self._parse_html_tokens(html)
                        
                        if len(tokens) > 0:
                            print(f"✅ Encontrados {len(tokens)} tokens via scraping HTML")
                        else:
                            print(f"⚠️  Nenhum token encontrado no HTML. Status: {response.status}")
                            print(f"   💡 Dica: O site pode carregar dados via JavaScript.")
                            print(f"   💡 Instale Selenium: pip install selenium")
                            print(f"   💡 E baixe ChromeDriver: https://chromedriver.chromium.org/")
                        
                        return tokens
                    else:
                        print(f"⚠️  Erro ao acessar página: Status {response.status}")
        except Exception as e:
            print(f"❌ Erro ao fazer scraping: {e}")
            import traceback
            traceback.print_exc()
        
        return []
    
    def parse_token_data(self, token_data: dict) -> Optional[TokenInfo]:
        """
        Converte dados do token da Gangue para TokenInfo
        Args:
            token_data: Dicionário com dados do token (formato da API ou HTML parseado)
        """
        try:
            # Tenta diferentes formatos de dados
            symbol = token_data.get('symbol') or token_data.get('name') or token_data.get('token')
            if not symbol:
                return None
            
            # Preço pode estar em diferentes formatos
            price = token_data.get('price') or token_data.get('price_usd') or token_data.get('current_price')
            if price is None:
                # Tenta parsear de string
                price_str = token_data.get('price_str', '')
                if price_str:
                    price = parse_price_with_subscript(price_str.replace('$', ''))
                else:
                    price = 0.0
            
            # Score
            score = token_data.get('score') or token_data.get('gangue_score')
            if score is None:
                return None
            score = int(score)
            
            # Contract Address
            ca = token_data.get('contract_address') or token_data.get('ca') or token_data.get('address') or token_data.get('mint')
            if not ca:
                return None
            
            # FDV
            fdv = token_data.get('fdv') or token_data.get('market_cap') or '0'
            
            # Tempo desde detecção
            # Como o site da Gangue não fornece horário, usamos o horário atual (0 minutos)
            # O horário real será registrado quando o bot comprar o token
            minutes_detected = None
            if 'detected_at' in token_data:
                try:
                    detected_at = datetime.fromisoformat(token_data['detected_at'].replace('Z', '+00:00'))
                    now = datetime.now(timezone.utc)
                    minutes_detected = int((now - detected_at).total_seconds() / 60)
                except:
                    pass
            elif 'minutes_ago' in token_data:
                minutes_detected = int(token_data['minutes_ago'])
            elif 'time_detected' in token_data:
                minutes_detected = int(token_data['time_detected'])
            else:
                # Se não tem horário no site, assume que foi detectado agora (0 minutos)
                # Isso permite que o bot compre imediatamente se estiver dentro da janela de tempo
                minutes_detected = 0
            
            return TokenInfo(symbol, float(price), str(fdv), score, ca, minutes_detected)
            
        except Exception as e:
            print(f"⚠️  Erro ao parsear token da Gangue: {e}")
            return None
    
    async def get_latest_tokens(self, limit: int = 10) -> List[TokenInfo]:
        """
        Busca os tokens mais recentes e retorna como TokenInfo
        """
        tokens_data = await self.fetch_tokens(limit)
        tokens = []
        
        for token_data in tokens_data:
            token_info = self.parse_token_data(token_data)
            if token_info:
                tokens.append(token_info)
        
        return tokens
    
    async def close(self):
        """Fecha sessão"""
        if self.session:
            await self.session.close()


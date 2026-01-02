# Como Funciona a Compra/Venda no Bot

## 🔄 Fluxo Atual (Bot Principal)

### 1. **COMPRA de Tokens**
- **Moeda usada**: USDC (stablecoin)
- **Endereço USDC**: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- **Processo**:
  ```
  USDC → Token detectado no Telegram
  Exemplo: $5 USDC → 1.000.000 tokens de BONK
  ```

### 2. **VENDA de Tokens**
- **Vende de volta para**: USDC
- **Processo**:
  ```
  Token → USDC
  Exemplo: 1.000.000 tokens BONK → $10 USDC (lucro!)
  ```

## 📊 Endereços Importantes

| Moeda | Endereço (Mint) | Uso |
|-------|----------------|-----|
| **USDC** | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | ✅ Usado pelo bot |
| **SOL** | `So11111111111111111111111111111111111111112` | ⚠️ Usado apenas no teste |

## 💰 Valores Configurados (em USDC)

- Score 15-17: **$5 USDC** por token
- Score 18-19: **$3 USDC** por token  
- Score 20-21: **$2 USDC** por token
- Score <15: **$1 USDC** (se habilitado)

## ⚙️ Por que USDC e não SOL?

1. **Estabilidade**: USDC é uma stablecoin (1 USDC = $1 USD)
2. **Previsibilidade**: Valores fixos em dólares
3. **Controle de Risco**: Mais fácil calcular lucros/perdas
4. **Configuração**: Todas as configurações estão em USDC

## 🔄 Exemplo de Trade Completo

1. **Detecção**: Bot detecta token no Telegram
   - Símbolo: BONK
   - Score: 16
   - Preço: $0.00001

2. **Compra**: Usa $5 USDC → compra BONK
   - Quantidade: 500.000 BONK tokens
   - Preço entrada: $0.00001

3. **Monitoramento**: Bot monitora preço

4. **Take Profit**: Quando preço dobra (2x)
   - Preço atual: $0.00002
   - Vende 50% (250.000 tokens) → recebe $5 USDC
   - Mantém 50% (250.000 tokens) esperando mais alta

5. **Venda Final**: Quando atinge 8x
   - Preço: $0.00008
   - Vende resto → recebe $20 USDC
   - **Lucro Total**: $25 USDC (entrada foi $5 USDC)

## 🧪 Teste Atual

O arquivo `teste_solana_simples.py` usa SOL apenas para **testar** a conexão:
- Compra SOL com USDC
- Vende SOL de volta para USDC
- É só um teste de funcionalidade, não o bot real

## ⚠️ Importante

- **Você precisa ter USDC na carteira** para o bot funcionar
- Não precisa de SOL (exceto para pagar taxas de transação)
- Todas as compras/vendas são em USDC












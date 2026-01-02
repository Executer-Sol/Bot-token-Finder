# ✅ Como Verificar se o Dashboard Está Funcionando

## 🔍 Diagnóstico

### 1. **Servidor Flask está rodando?**
Abra o terminal e verifique se há um processo Python rodando na porta 5000:
```bash
# No Windows (PowerShell)
netstat -ano | findstr :5000
```

Ou verifique se você vê mensagens como:
```
 * Running on http://127.0.0.1:5000
```

### 2. **Dashboard carrega?**
Abra no navegador: http://localhost:5000

### 3. **Console do Navegador (F12)**
Pressione `F12` no navegador e vá na aba **Console**. 
- ❌ Se houver erros vermelhos, copie e me envie
- ✅ Se estiver vazio ou só avisos, está OK

### 4. **Rede/Network (F12)**
Pressione `F12` → aba **Network** → recarregue a página
- Veja se as requisições `/api/stats`, `/api/trades/active`, etc. aparecem
- Clique em cada uma e veja a resposta:
  - ✅ Status 200 = funcionando
  - ❌ Status 500 ou erro = problema

### 5. **Dados estão vazios?**
Isso é **NORMAL** se:
- Você ainda não comprou nenhum token
- O bot ainda não fez nenhum trade
- O arquivo `trades_history.json` está vazio

## 🎯 O Que Deve Aparecer Quando Funciona

### Com Dados Vazios (Normal):
- Tokens Ativos: **0**
- Tokens Vendidos: **0**
- Lucro Ativo: **0.0000 SOL**
- Lucro Vendido: **0.0000 SOL**
- Win Rate: **0%**
- ROI Médio: **0%**

### Quando o Bot Fizer Trades:
- Os números começam a aparecer automaticamente
- A cada 30 segundos atualiza sozinho
- Ou clique em "Atualizar" manualmente

## 🔧 Solução Rápida

### Se NADA aparece (nem zeros):

1. **Verifique se o servidor está rodando:**
```bash
python web_interface.py
# ou
python run_web.py
```

2. **Abra o navegador no console (F12) e veja os erros**

3. **Teste a API diretamente:**
```bash
# Abra no navegador:
http://localhost:5000/api/stats
http://localhost:5000/api/trades/active
```

Se aparecer JSON = API funcionando! ✅
Se der erro = servidor não está rodando ❌

## 📝 Resumo

✅ **Sistema funcionando corretamente se:**
- Dashboard carrega
- Console não tem erros vermelhos
- APIs retornam JSON (mesmo que vazio)
- Números aparecem (mesmo que zeros)

❌ **Problema se:**
- Dashboard não carrega
- Console tem erros
- APIs retornam erro 500
- Nada aparece na tela (nem zeros)






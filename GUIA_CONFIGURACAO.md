# 📋 GUIA DE CONFIGURAÇÃO - Luna Automation

## O que essa automação faz

1. **Lê** sua planilha do Google Sheets
2. **Filtra** pedidos por data e que contenham "card" na coluna de pagamento
3. **Acessa** a Luna Checkout e verifica se cada pedido está pago
4. **Envia** no WhatsApp: o link do pedido e o nome do produto
5. **Aguarda** você responder com o valor (respondendo ao link) e o email (respondendo ao produto)
6. **Grava** valor e email na planilha, na linha correta

---

## ✅ PRÉ-REQUISITOS

- Python 3.10 ou superior
- Node.js 18 ou superior
- Conta no Google Cloud (para API do Sheets)
- WhatsApp ativo no celular

---

## 🚀 INSTALAÇÃO (faça uma vez)

### 1. Instalar dependências Python
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Instalar dependências Node.js
```bash
npm install
```

---

## 🔑 CONFIGURAR GOOGLE SHEETS API

### Passo 1 - Criar projeto no Google Cloud
1. Acesse: https://console.cloud.google.com/
2. Clique em "Novo Projeto" → dê um nome → Criar
3. No menu lateral: **APIs e Serviços** → **Biblioteca**
4. Busque e ative: **Google Sheets API** e **Google Drive API**

### Passo 2 - Criar conta de serviço
1. Vá em **APIs e Serviços** → **Credenciais**
2. Clique em **+ Criar Credenciais** → **Conta de serviço**
3. Preencha o nome → Criar e Continuar → Concluir
4. Clique na conta de serviço criada
5. Aba **Chaves** → **Adicionar Chave** → **Criar nova chave** → JSON
6. Salve o arquivo JSON baixado como `config/google_credentials.json`

### Passo 3 - Compartilhar a planilha
1. Abra o arquivo JSON e copie o valor de `"client_email"` (algo como `nome@projeto.iam.gserviceaccount.com`)
2. Abra sua planilha no Google Sheets
3. Clique em **Compartilhar** → cole o email copiado → Permissão: **Editor** → Enviar

### Passo 4 - Configurar o config.py
Abra `config/config.py` e preencha:

```python
SPREADSHEET_ID = "ID_DA_SUA_PLANILHA"
# Pegue da URL: docs.google.com/spreadsheets/d/[ESTE_TRECHO]/edit

SHEET_NAME = "Página1"  # Nome da aba

# Letras das colunas da sua planilha:
COL_DATA         = "A"   # Coluna com data
COL_PAGAMENTO    = "B"   # Coluna com tipo de pagamento
COL_ID_PEDIDO    = "C"   # Coluna com ID do pedido
COL_LINK_PEDIDO  = "D"   # Coluna com link do pedido
COL_VALOR_PAGO   = "E"   # Onde gravar o valor
COL_EMAIL_COMPRA = "F"   # Onde gravar o email

DATA_MINIMA = "01/04/2025"  # Data de corte (DD/MM/AAAA)
```

---

## 📱 CONFIGURAR WHATSAPP

Preencha no `config/config.py`:
```python
WHATSAPP_GROUP = "Nome Exato do Grupo"  # Ou JID: "5511999999999@g.us"
```

> O login na Luna Checkout é feito **manualmente no navegador** — uma janela do Chrome abrirá na primeira execução. Após o login, a sessão fica salva em `sessions/luna_session.json`.

Dica: com o servidor WhatsApp rodando, acesse `http://localhost:3000/groups` para ver o nome exato dos grupos disponíveis.

---

## ▶️ COMO USAR (toda vez que rodar)

### Terminal 1 - Servidor WhatsApp
```bash
node whatsapp_server.js
```
**Primeira vez:** vai aparecer um QR Code. Escaneie com o WhatsApp do celular (Configurações → Aparelhos conectados → Conectar aparelho).

### Terminal 2 - Automação principal
```bash
python main.py
```

O script vai:
1. Perguntar a data de corte (Enter para usar a do config)
2. Listar pedidos encontrados
3. Pedir confirmação antes de processar
4. Para cada pedido pago:
   - Enviar link no WhatsApp
   - Enviar nome do produto no WhatsApp
   - **Você responde ao link com o VALOR**
   - **Você responde ao produto com o EMAIL**
   - Grava automaticamente na planilha

---

## 💡 DICAS

- **Grupos do WhatsApp:** para listar grupos disponíveis, acesse `http://localhost:3000/groups` após iniciar o servidor
- **Logs:** salvos na pasta `logs/` com data e hora
- **Headless:** para rodar sem abrir o Chrome visualmente, edite `luna_scraper.py` e mude `headless=False` para `headless=True`
- **Timeout:** se demorar para responder, ajuste `TIMEOUT_RESPOSTA_MINUTOS` no config

---

## ❓ PROBLEMAS COMUNS

| Problema | Solução |
|----------|---------|
| "Servidor WhatsApp não está rodando" | Execute `node whatsapp_server.js` no Terminal 1 |
| "Credenciais não encontradas" | Coloque o JSON em `config/google_credentials.json` |
| "Grupo não encontrado" | Acesse `http://localhost:3000/groups` e copie o nome exato |
| Login na Luna falhou | Verifique email/senha no `config.py` |
| Coluna errada na planilha | Ajuste as letras das colunas no `config.py` |

# Luna Automation

> Automação completa de pedidos de dropshipping: Google Sheets + Luna Checkout + WhatsApp

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933?style=flat&logo=node.js&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-browser%20automation-2EAD33?style=flat&logo=playwright&logoColor=white)
![WhatsApp](https://img.shields.io/badge/WhatsApp-Baileys-25D366?style=flat&logo=whatsapp&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat)

---

## Sobre o projeto

Luna Automation resolve um problema real no dropshipping: o processo manual de conferir pedidos pagos, enviar informações no WhatsApp e preencher planilhas é lento e sujeito a erros. Esta automação une três plataformas em um fluxo contínuo, eliminando o trabalho repetitivo.

```
Google Sheets → Luna Checkout → WhatsApp → Google Sheets
```

**O que ele faz, na prática:**

1. Lê pedidos do Google Sheets filtrando por data e tipo de pagamento (PIX ou cartão)
2. Acessa o painel Luna Checkout via automação de navegador e verifica se cada pedido está confirmado como **Pago**
3. Envia automaticamente o link do pedido e o nome do produto no grupo do WhatsApp
4. Aguarda você responder no grupo com o **valor pago** e o **e-mail do comprador**
5. Grava as respostas automaticamente na planilha, na linha e coluna corretas

---

## Arquitetura

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  Google Sheets  │────▶│      main.py          │────▶│  Luna Checkout  │
│  (leitura de    │     │  (orquestrador        │     │  (Playwright /  │
│   pedidos)      │     │   principal)          │     │  Chromium)      │
└─────────────────┘     └──────────┬───────────┘     └─────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  whatsapp_server.js   │
                        │  (Node.js + Baileys)  │
                        │  HTTP API local       │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐     ┌─────────────────┐
                        │  Grupo WhatsApp       │────▶│  Google Sheets  │
                        │  (envio + recepção    │     │  (gravação de   │
                        │   de mensagens)       │     │   valor e email) │
                        └──────────────────────┘     └─────────────────┘
```

O Python e o Node.js se comunicam via **HTTP local** — o `whatsapp_server.js` expõe uma API REST que o `main.py` consome. Isso permite usar o Baileys (biblioteca WhatsApp exclusiva de Node.js) junto com toda a lógica em Python.

---

## Estrutura do projeto

```
luna-automation/
├── main.py                        # Ponto de entrada da automação
├── app.py                         # Interface gráfica alternativa (tkinter)
├── whatsapp_server.js             # Servidor WhatsApp (Baileys + Express)
├── qr_window.py                   # Janela de QR Code para conexão WhatsApp
├── requirements.txt               # Dependências Python
├── package.json                   # Dependências Node.js
├── config/
│   ├── config.example.py          # Template de configuração (copie para config.py)
│   └── google_credentials.json    # Credenciais Google (não commitar — ver .gitignore)
├── modules/
│   ├── google_sheets.py           # Leitura e escrita no Google Sheets
│   ├── luna_scraper.py            # Automação do navegador (Playwright)
│   └── whatsapp.py                # Cliente HTTP para o servidor WhatsApp
├── sessions/                      # Sessões salvas (WhatsApp auth, navegador)
└── logs/                          # Logs com timestamp de cada execução
```

---

## Pré-requisitos

- Python 3.10+
- Node.js 18+
- Conta Google Cloud com Google Sheets API e Google Drive API habilitadas
- WhatsApp ativo no celular para escanear o QR Code

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/laitartlucas/Luna-Automation.git
cd luna-automation
```

### 2. Instale as dependências Python

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Instale as dependências Node.js

```bash
npm install
```

---

## Configuração

### Google Sheets API

1. Acesse [console.cloud.google.com](https://console.cloud.google.com/) e crie um projeto
2. Ative a **Google Sheets API** e a **Google Drive API**
3. Crie uma **Conta de Serviço** → gere uma chave JSON → salve como `config/google_credentials.json`
4. Compartilhe sua planilha com o `client_email` do JSON (permissão de Editor)

### Configuração da automação

```bash
cp config/config.example.py config/config.py
```

Edite `config/config.py` com seus dados:

```python
SPREADSHEET_ID   = "ID_DA_SUA_PLANILHA"   # da URL do Google Sheets
SHEET_NAME       = "Nome da Aba"

COL_DATA         = "I"   # Coluna da data do pedido
COL_PAGAMENTO    = "E"   # Coluna do tipo de pagamento
COL_ID_PEDIDO    = "J"   # Coluna do ID do pedido
COL_LINK_PEDIDO  = "Q"   # Coluna do link do pedido
COL_VALOR_PAGO   = "L"   # Onde gravar o valor pago
COL_EMAIL_COMPRA = "K"   # Onde gravar o e-mail

DATA_MINIMA      = "01/01/2025"
WHATSAPP_GROUP   = "Nome Exato do Grupo"
```

---

## Como usar

### Terminal 1 — Servidor WhatsApp

```bash
node whatsapp_server.js
```

Na primeira execução, um QR Code aparece no terminal. Escaneie com o WhatsApp do celular em **Configurações → Aparelhos conectados → Conectar aparelho**. A sessão fica salva para as próximas execuções.

### Terminal 2 — Automação principal

```bash
python main.py
```

O script:
1. Verifica se o servidor WhatsApp está online
2. Pergunta a data de corte e o tipo de pagamento a filtrar
3. Lista os pedidos encontrados e pede confirmação
4. Para cada pedido pago: envia link + produto no WhatsApp, aguarda suas respostas e grava na planilha

---

## Fluxo por pedido

```
Pedido encontrado na planilha (data e pagamento ok)
        ↓
Verifica status na Luna Checkout via Playwright
        ↓ (somente se status = "Pago")
Envia link do pedido no grupo WhatsApp
Envia nome do produto no grupo WhatsApp
        ↓
Aguarda resposta com o VALOR → grava na planilha
Aguarda resposta com o E-MAIL → grava na planilha
        ↓
Próximo pedido
```

---

## Dependências

| Tipo    | Biblioteca                    | Uso                                        |
|---------|-------------------------------|--------------------------------------------|
| Python  | `gspread`                     | Leitura e escrita no Google Sheets         |
| Python  | `google-auth`                 | Autenticação com a API Google              |
| Python  | `playwright`                  | Automação do navegador (Luna Checkout)     |
| Python  | `requests`                    | Comunicação HTTP com o servidor WhatsApp   |
| Node.js | `@whiskeysockets/baileys`     | Integração com WhatsApp Web                |
| Node.js | `express`                     | Servidor HTTP local                        |
| Node.js | `qrcode-terminal`             | Exibição do QR Code no terminal            |

---

## Dicas

- **Listar grupos disponíveis:** com o servidor rodando, acesse `http://localhost:3000/groups`
- **Modo headless:** edite `modules/luna_scraper.py` e mude `headless=False` para `headless=True` para ocultar o navegador
- **Logs:** cada execução gera um arquivo em `logs/automacao_YYYYMMDD_HHMMSS.log`
- **Resetar sessão WhatsApp:** delete a pasta `sessions/whatsapp/` e reinicie o servidor
- **Resetar sessão Luna:** delete `sessions/luna_session.json`

---

## Problemas comuns

| Problema | Solução |
|----------|---------|
| "Servidor WhatsApp não está rodando" | Execute `node whatsapp_server.js` no Terminal 1 |
| "Credenciais não encontradas" | Salve o JSON em `config/google_credentials.json` |
| "Grupo não encontrado" | Acesse `/groups` e use o nome exato retornado |
| Coluna errada na planilha | Revise as letras das colunas no `config.py` |
| QR Code expirou | Reinicie o `whatsapp_server.js` |

---

## Segurança

Os arquivos listados abaixo já estão no `.gitignore` e **não serão enviados ao repositório**:

```
config/config.py              # Seus IDs e configurações pessoais
config/google_credentials.json  # Credenciais da API Google
sessions/                     # Sessões de autenticação
logs/                         # Logs de execução
```

> Nunca remova esses itens do `.gitignore`. Credenciais expostas publicamente podem comprometer sua conta Google e sua sessão do WhatsApp.

---

## Licença

MIT

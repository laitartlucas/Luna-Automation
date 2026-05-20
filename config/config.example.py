# ============================================================
#   CONFIGURAÇÕES DA AUTOMAÇÃO - EDITE AQUI
#   Copie este arquivo para config.py e preencha seus dados:
#   cp config/config.example.py config/config.py
# ============================================================

import os as _os

# --- GOOGLE SHEETS ---
SPREADSHEET_ID = "ID_DA_SUA_PLANILHA"
# Pegue da URL: docs.google.com/spreadsheets/d/[ESTE_TRECHO]/edit

SHEET_NAME = "Nome da Aba"

# Colunas da planilha (letra da coluna)
COL_DATA         = "A"   # Coluna com data do pedido
COL_PAGAMENTO    = "B"   # Coluna com tipo de pagamento (card/pix)
COL_ID_PEDIDO    = "C"   # Coluna com ID do pedido
COL_LINK_PEDIDO  = "D"   # Coluna com link do pedido
COL_VALOR_PAGO   = "E"   # Coluna onde gravar o valor pago
COL_EMAIL_COMPRA = "F"   # Coluna onde gravar o e-mail do comprador

# Data mínima para filtrar pedidos (formato: DD/MM/AAAA)
DATA_MINIMA = "01/01/2025"

# Caminho do arquivo de credenciais do Google
GOOGLE_CREDENTIALS_FILE = "config/google_credentials.json"

# --- LUNA CHECKOUT ---
LUNA_URL        = "https://app.lunacheckout.com"
LUNA_EMAIL      = ""  # Login feito manualmente no navegador
LUNA_SENHA      = ""  # Login feito manualmente no navegador
LUNA_ORDERS_URL = "https://app.lunacheckout.com/vendas/pedidos"

# --- WHATSAPP ---
WHATSAPP_GROUP = "Nome Exato do Grupo"
# Dica: com o servidor rodando, acesse http://localhost:3000/groups para listar grupos
WHATSAPP_PORT  = 3000

# --- COMPORTAMENTO ---
TIMEOUT_RESPOSTA_MINUTOS = 60
INTERVALO_CHECK_SEGUNDOS = 10

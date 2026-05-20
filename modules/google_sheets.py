"""
Módulo de integração com Google Sheets
"""
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.config import (
    SPREADSHEET_ID, SHEET_NAME, GOOGLE_CREDENTIALS_FILE,
    COL_DATA, COL_PAGAMENTO, COL_ID_PEDIDO,
    COL_LINK_PEDIDO, COL_VALOR_PAGO, COL_EMAIL_COMPRA,
    DATA_MINIMA
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def col_letter_to_index(letter: str) -> int:
    """Converte letra de coluna (A, B, C...) para índice base 1."""
    letter = letter.upper()
    result = 0
    for char in letter:
        result = result * 26 + (ord(char) - ord('A') + 1)
    return result

def get_sheet():
    """Retorna a aba da planilha autenticada."""
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    sheet = spreadsheet.worksheet(SHEET_NAME)
    return sheet

def parse_date(date_str: str) -> datetime:
    """Tenta parsear data em vários formatos, com ou sem hora."""
    date_str = date_str.strip()
    formats = [
        "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
        "%d-%m-%Y %H:%M:%S", "%d-%m-%Y",
        "%d/%m/%y", "%m/%d/%Y",
        "%Y/%m/%d %H:%M:%S", "%Y/%m/%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(date_str.replace("Z", ""))
    except ValueError:
        pass
    return None

def get_pedidos_filtrados(data_minima_str: str = None, tipos_pagamento: list = None) -> list[dict]:
    """
    Busca linhas da planilha onde:
    - A data é maior que data_minima
    - A coluna de pagamento contém 'card' (case insensitive)
    
    Retorna lista de dicts com os dados de cada linha.
    """
    if data_minima_str is None:
        data_minima_str = DATA_MINIMA
    if tipos_pagamento is None:
        tipos_pagamento = ["card"]

    data_minima = parse_date(data_minima_str)
    if not data_minima:
        raise ValueError(f"Data inválida: {data_minima_str}. Use o formato DD/MM/AAAA")

    sheet = get_sheet()
    all_rows = sheet.get_all_values()

    if not all_rows:
        print("⚠️  Planilha vazia.")
        return []

    # Índices das colunas (base 0 para listas Python)
    idx_data      = col_letter_to_index(COL_DATA) - 1
    idx_pagamento = col_letter_to_index(COL_PAGAMENTO) - 1
    idx_id        = col_letter_to_index(COL_ID_PEDIDO) - 1
    idx_link      = col_letter_to_index(COL_LINK_PEDIDO) - 1

    resultados = []

    for row_num, row in enumerate(all_rows, start=1):
        # Pula linhas com colunas insuficientes
        max_idx = max(idx_data, idx_pagamento, idx_id, idx_link)
        if len(row) <= max_idx:
            continue

        data_cell      = row[idx_data].strip()
        pagamento_cell = row[idx_pagamento].strip()
        id_pedido      = row[idx_id].strip()
        link_pedido    = row[idx_link].strip()

        # Verifica tipo de pagamento
        if not any(t in pagamento_cell.lower() for t in tipos_pagamento):
            continue

        # Verifica a data
        data_row = parse_date(data_cell)
        if not data_row:
            continue

        if data_row <= data_minima:
            continue

        resultados.append({
            "row_num":    row_num,
            "data":       data_cell,
            "pagamento":  pagamento_cell,
            "id_pedido":  id_pedido,
            "link_pedido": link_pedido,
        })

    print(f"✅ Encontrados {len(resultados)} pedidos com {tipos_pagamento} após {data_minima_str}")
    return resultados

def atualizar_valor_pago(row_num: int, valor: str):
    """Atualiza a coluna de valor pago na linha especificada."""
    sheet = get_sheet()
    cell = f"{COL_VALOR_PAGO}{row_num}"
    sheet.update_acell(cell, valor)
    print(f"✅ Valor '{valor}' salvo em {cell}")

def atualizar_email_compra(row_num: int, email: str):
    """Atualiza a coluna de email de compra na linha especificada."""
    sheet = get_sheet()
    cell = f"{COL_EMAIL_COMPRA}{row_num}"
    sheet.update_acell(cell, email)
    print(f"✅ Email '{email}' salvo em {cell}")
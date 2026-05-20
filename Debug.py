"""
debug.py - Mostra exatamente o que está sendo lido da planilha
Execute: py -3.12 debug.py
"""
import sys
sys.path.insert(0, ".")

from modules.google_sheets import get_sheet, col_letter_to_index, parse_date
from config.config import (
    COL_DATA, COL_PAGAMENTO, COL_ID_PEDIDO,
    COL_LINK_PEDIDO, DATA_MINIMA
)

print("🔍 Conectando na planilha...")
sheet = get_sheet()
rows = sheet.get_all_values()
print(f"✅ Total de linhas encontradas: {len(rows)}\n")

idx_data      = col_letter_to_index(COL_DATA) - 1
idx_pagamento = col_letter_to_index(COL_PAGAMENTO) - 1
idx_id        = col_letter_to_index(COL_ID_PEDIDO) - 1
idx_link      = col_letter_to_index(COL_LINK_PEDIDO) - 1

print(f"📋 Colunas configuradas: Data={COL_DATA}({idx_data}) | Pagamento={COL_PAGAMENTO}({idx_pagamento}) | ID={COL_ID_PEDIDO}({idx_id}) | Link={COL_LINK_PEDIDO}({idx_link})")
print(f"📅 Data mínima: {DATA_MINIMA}\n")

from datetime import datetime
data_minima = parse_date(DATA_MINIMA)

print("=" * 70)
print("Primeiras 10 linhas com dados:")
print("=" * 70)

count = 0
for i, row in enumerate(rows[:50], start=1):
    max_idx = max(idx_data, idx_pagamento, idx_id)
    if len(row) <= max_idx:
        continue
    
    data_val  = row[idx_data] if idx_data < len(row) else "VAZIO"
    pag_val   = row[idx_pagamento] if idx_pagamento < len(row) else "VAZIO"
    id_val    = row[idx_id] if idx_id < len(row) else "VAZIO"

    if not any([data_val.strip(), pag_val.strip(), id_val.strip()]):
        continue

    data_parsed = parse_date(data_val)
    tem_card = "card" in pag_val.lower()
    data_ok = data_parsed and data_parsed > data_minima if data_parsed else False

    print(f"Linha {i:3} | Data: '{data_val[:20]}' (parseou: {data_parsed is not None}, maior: {data_ok}) | Pag: '{pag_val}' (card: {tem_card}) | ID: '{id_val[:20]}'")
    count += 1
    if count >= 10:
        break

print("=" * 70)
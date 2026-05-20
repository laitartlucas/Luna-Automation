import sys
sys.path.insert(0, ".")
from modules.google_sheets import get_pedidos_filtrados
 
print("Testando filtro PIX...")
pedidos = get_pedidos_filtrados("24/04/2026 14:20:00", ["pix"])
print(f"Encontrados: {len(pedidos)}")
for p in pedidos:
    print(f"  Linha {p['row_num']}: ID {p['id_pedido']} | Pag: {p['pagamento']}")
"""
============================================================
   LUNA AUTOMATION - Script Principal
============================================================
"""
import sys
import os
import time
import traceback
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from config.config import DATA_MINIMA
from modules.google_sheets import (
    get_pedidos_filtrados,
    atualizar_valor_pago,
    atualizar_email_compra,
)
from modules.luna_scraper import buscar_pedido_por_id, fechar_navegador
from modules.whatsapp import verificar_conexao, enviar_mensagem, aguardar_mensagem_sua

LOG_FILE = f"logs/automacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    linha = f"[{timestamp}] {msg}"
    print(linha)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

def verificar_prereqs():
    log("🔍 Verificando pré-requisitos...")

    if not verificar_conexao():
        log("❌ Servidor WhatsApp não está rodando!")
        log("   Execute em outro terminal: node whatsapp_server.js")
        return False
    log("✅ WhatsApp conectado")

    from config.config import GOOGLE_CREDENTIALS_FILE
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        log(f"❌ Arquivo de credenciais não encontrado: {GOOGLE_CREDENTIALS_FILE}")
        return False
    log("✅ Credenciais Google encontradas")

    return True

def processar_pedido(pedido: dict) -> bool:
    row_num   = pedido["row_num"]
    id_pedido = pedido["id_pedido"]
    link      = pedido["link_pedido"]

    log(f"\n{'='*50}")
    log(f"📦 Processando pedido #{id_pedido} (linha {row_num})")

    # 1. Busca na Luna e verifica se está Pago
    dados_luna = buscar_pedido_por_id(id_pedido)
    if not dados_luna:
        log(f"⏭️  Pedido {id_pedido} pulado (não pago ou não encontrado)")
        return False

    nome_produto = dados_luna["nome_produto"]

    # 2. Envia link da coluna Q no WhatsApp
    msg_link = f"🔗 *Link do pedido:*\n{link}"
    if not enviar_mensagem(msg_link):
        log(f"❌ Falha ao enviar link do pedido {id_pedido}")
        return False
    time.sleep(2)

    # 3. Envia nome do produto no WhatsApp
    msg_produto = f"📦 *Produto:*\n{nome_produto}"
    if not enviar_mensagem(msg_produto):
        log(f"❌ Falha ao enviar nome do produto")
        return False

    log(f"📲 Mensagens enviadas!")

    # 4. Aguarda você enviar o VALOR no grupo
    log(f"\n💬 Envie o VALOR no grupo do WhatsApp...")
    resposta_valor = aguardar_mensagem_sua()

    if resposta_valor:
        valor_limpo = resposta_valor.strip()
        atualizar_valor_pago(row_num, valor_limpo)
        log(f"✅ Valor '{valor_limpo}' gravado na planilha (linha {row_num}, coluna L)")
    else:
        log(f"⚠️  Nenhuma mensagem de valor recebida para pedido {id_pedido}")

    # 5. Aguarda você enviar o EMAIL no grupo
    log(f"\n💬 Agora envie o EMAIL no grupo do WhatsApp...")
    resposta_email = aguardar_mensagem_sua()

    if resposta_email:
        email_limpo = resposta_email.strip()
        atualizar_email_compra(row_num, email_limpo)
        log(f"✅ Email '{email_limpo}' gravado na planilha (linha {row_num}, coluna K)")
    else:
        log(f"⚠️  Nenhuma mensagem de email recebida para pedido {id_pedido}")

    log(f"✅ Pedido {id_pedido} processado com sucesso!\n")
    return True

def main():
    os.makedirs("logs", exist_ok=True)

    log("=" * 60)
    log("   LUNA AUTOMATION - Iniciando")
    log("=" * 60)

    if not verificar_prereqs():
        sys.exit(1)

    # Pergunta a data mínima
    print(f"\n📅 Data mínima configurada: {DATA_MINIMA}")
    usar_outra = input("   Usar outra data? (Enter para manter, ou digite DD/MM/AAAA HH:MM:SS): ").strip()
    data_filtro = usar_outra if usar_outra else DATA_MINIMA

    # Pergunta o tipo de pagamento
    print(f"\n💳 Filtrar por tipo de pagamento:")
    print(f"   1 - card")
    print(f"   2 - pix")
    print(f"   3 - ambos (card e pix)")
    opcao = input("   Escolha (1/2/3): ").strip()
    if opcao == "1":
        tipos_pagamento = ["card"]
    elif opcao == "2":
        tipos_pagamento = ["pix"]
    else:
        tipos_pagamento = ["card", "pix"]
    log(f"💳 Filtrando por: {tipos_pagamento}")

    # Busca pedidos na planilha
    log(f"\n📊 Buscando pedidos após {data_filtro} com pagamento {tipos_pagamento}...")
    try:
        pedidos = get_pedidos_filtrados(data_filtro, tipos_pagamento)
    except Exception as e:
        log(f"❌ Erro ao acessar planilha: {e}")
        traceback.print_exc()
        sys.exit(1)

    if not pedidos:
        log("ℹ️  Nenhum pedido encontrado com os critérios definidos.")
        sys.exit(0)

    log(f"📋 {len(pedidos)} pedido(s) encontrado(s):")
    for p in pedidos:
        log(f"   • Linha {p['row_num']}: ID {p['id_pedido']} | Data: {p['data']}")

    confirma = input(f"\n🚀 Iniciar processamento de {len(pedidos)} pedido(s)? (s/n): ").strip().lower()
    if confirma != "s":
        log("Cancelado pelo usuário.")
        sys.exit(0)

    # Processa cada pedido
    total = len(pedidos)
    sucesso = 0
    falha = 0

    for i, pedido in enumerate(pedidos, 1):
        log(f"\n[{i}/{total}] Processando pedido...")
        try:
            ok = processar_pedido(pedido)
            if ok:
                sucesso += 1
            else:
                falha += 1
        except KeyboardInterrupt:
            log("\n⚠️  Interrompido pelo usuário!")
            break
        except Exception as e:
            log(f"❌ Erro inesperado no pedido {pedido.get('id_pedido')}: {e}")
            traceback.print_exc()
            falha += 1

        if i < total:
            time.sleep(2)

    fechar_navegador()
    log(f"\n{'='*60}")
    log(f"   RESUMO FINAL")
    log(f"   ✅ Sucesso: {sucesso}/{total}")
    log(f"   ❌ Falhas:  {falha}/{total}")
    log(f"   📄 Log salvo em: {LOG_FILE}")
    log(f"{'='*60}")

if __name__ == "__main__":
    main()
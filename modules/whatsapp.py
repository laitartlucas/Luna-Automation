"""
Módulo de integração com WhatsApp via servidor Baileys local
"""
import requests
import time
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.config import (
    WHATSAPP_GROUP, WHATSAPP_PORT,
    TIMEOUT_RESPOSTA_MINUTOS, INTERVALO_CHECK_SEGUNDOS
)

BASE_URL = f"http://localhost:{WHATSAPP_PORT}"
JID_FILE = "sessions/group_jid.json"

def verificar_conexao() -> bool:
    try:
        resp = requests.get(f"{BASE_URL}/status", timeout=5)
        return resp.json().get("connected", False)
    except:
        return False

def salvar_jid(jid: str):
    """Salva o JID do grupo para usar no filtro."""
    os.makedirs("sessions", exist_ok=True)
    with open(JID_FILE, "w") as f:
        json.dump({"jid": jid}, f)

def carregar_jid() -> str | None:
    """Carrega o JID do grupo salvo."""
    if os.path.exists(JID_FILE):
        try:
            with open(JID_FILE) as f:
                return json.load(f).get("jid")
        except:
            pass
    return None

def enviar_mensagem(mensagem: str) -> dict | None:
    try:
        resp = requests.post(f"{BASE_URL}/send", json={
            "group": WHATSAPP_GROUP,
            "message": mensagem,
        }, timeout=10)
        data = resp.json()
        if data.get("success"):
            # Salva o JID do grupo retornado pelo servidor
            if data.get("jid"):
                salvar_jid(data["jid"])
            print(f"📤 Mensagem enviada: {mensagem[:60]}...")
            return data
        else:
            print(f"❌ Erro ao enviar mensagem: {data}")
            return None
    except Exception as e:
        print(f"❌ Erro na requisição WhatsApp: {e}")
        return None

def aguardar_mensagem_sua(descricao: str = "") -> str | None:
    """
    Aguarda uma mensagem no grupo 'Pedido teste'.
    Filtra pelo JID do grupo salvo.
    """
    timeout_segundos = TIMEOUT_RESPOSTA_MINUTOS * 60
    elapsed = 0
    group_jid = carregar_jid()

    if group_jid:
        print(f"\n⏳ Aguardando mensagem no grupo '{WHATSAPP_GROUP}' ({descricao})...")
    else:
        print(f"\n⏳ Aguardando mensagem no grupo '{WHATSAPP_GROUP}' ({descricao})...")
        print(f"   ⚠️  JID do grupo não encontrado ainda — será aprendido na primeira mensagem enviada")

    while elapsed < timeout_segundos:
        try:
            resp = requests.get(f"{BASE_URL}/messages/pending", timeout=5)
            mensagens = resp.json()

            for msg in mensagens:
                text     = msg.get("text", "").strip()
                from_jid = msg.get("from", "")
                is_group = "@g.us" in from_jid

                if not text or not is_group:
                    continue

                # Se temos o JID salvo, filtra pelo grupo correto
                if group_jid:
                    if from_jid != group_jid:
                        continue

                print(f"✅ Mensagem do grupo capturada: '{text}'")
                return text

        except Exception as e:
            print(f"⚠️  Erro ao verificar mensagens: {e}")

        time.sleep(INTERVALO_CHECK_SEGUNDOS)
        elapsed += INTERVALO_CHECK_SEGUNDOS

        if elapsed % 120 == 0:
            print(f"   ... ainda aguardando ({elapsed // 60} min / {TIMEOUT_RESPOSTA_MINUTOS} min)")

    print(f"⚠️  Timeout após {TIMEOUT_RESPOSTA_MINUTOS} minutos.")
    return None

def listar_grupos() -> list:
    try:
        resp = requests.get(f"{BASE_URL}/groups", timeout=10)
        return resp.json()
    except Exception as e:
        print(f"❌ Erro ao listar grupos: {e}")
        return []
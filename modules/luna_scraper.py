"""
Módulo de automação do navegador para Luna Checkout
"""
import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.config import LUNA_URL, LUNA_ORDERS_URL

SESSION_FILE = "sessions/luna_session.json"

_playwright = None
_browser    = None
_context    = None
_page       = None

def get_page():
    global _playwright, _browser, _context, _page
    if _page is None:
        from playwright.sync_api import sync_playwright
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=False)
        if os.path.exists(SESSION_FILE):
            print("📂 Carregando sessão salva da Luna...")
            with open(SESSION_FILE, "r") as f:
                storage = json.load(f)
            _context = _browser.new_context(storage_state=storage)
        else:
            _context = _browser.new_context()
        _page = _context.new_page()
    return _page

def salvar_sessao():
    if _context:
        os.makedirs("sessions", exist_ok=True)
        storage = _context.storage_state()
        with open(SESSION_FILE, "w") as f:
            json.dump(storage, f)
        print("💾 Sessão salva!")

def fazer_login():
    page = get_page()
    print("\n🌐 Abrindo página de login da Luna Checkout...")
    page.goto(f"{LUNA_URL}/login", wait_until="networkidle")
    print("👉 Faça o login no navegador que abriu.")
    input("✅ Após estar logado, pressione ENTER aqui para continuar...")
    salvar_sessao()
    print("💾 Sessão salva! Próximas execuções não precisarão de login.\n")
    return True

def garantir_login():
    page = get_page()
    page.goto(LUNA_ORDERS_URL, wait_until="networkidle")
    time.sleep(2)
    if "/login" in page.url:
        print("🔐 Sessão expirada ou primeiro acesso.")
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        fazer_login()
        page.goto(LUNA_ORDERS_URL, wait_until="networkidle")
        time.sleep(2)
    return True

def buscar_pedido_por_id(id_pedido: str) -> dict | None:
    page = get_page()
    try:
        print(f"\n🔍 Buscando pedido #{id_pedido} na Luna...")

        if not garantir_login():
            return None

        # Clica no botão da lupa para abrir a barra de busca
        try:
            page.locator('button[aria-label="Pesquisar"]').click(timeout=5000)
            time.sleep(1)
            print("   ✅ Lupa clicada")
        except Exception as e:
            print(f"   ⚠️  Erro ao clicar na lupa: {e}")
            return None

        # Digita o ID na barra de busca
        try:
            inp = page.locator("input.input-search-cancel-button-none").last
            inp.click()
            time.sleep(0.5)
            inp.type(id_pedido, delay=50)
            time.sleep(3)
            print(f"   ✅ ID digitado na busca")
        except Exception as e:
            print(f"   ⚠️  Erro ao digitar na busca: {e}")
            return None

        # Aguarda o pedido aparecer na lista e clica
        try:
            # Aguarda a linha com o número do pedido aparecer
            page.wait_for_selector(f'text=#{id_pedido}', timeout=8000)
            time.sleep(0.5)
            page.click(f'text=#{id_pedido}', timeout=5000)
            print(f"   ✅ Clicou no pedido #{id_pedido}")
        except:
            try:
                # Tenta clicar na linha da tabela
                page.locator("tr").filter(has_text=id_pedido).first.click(timeout=5000)
                print(f"   ✅ Clicou na linha da tabela")
            except Exception as e:
                print(f"   ⚠️  Erro ao clicar no pedido: {e}")

        # Aguarda navegação para a página do pedido
        try:
            page.wait_for_url(f"**/pedidos/**", timeout=8000)
            print(f"   ✅ Navegou para página do pedido")
        except:
            pass

        time.sleep(2)

        # Verifica se abriu o pedido pela URL
        current_url = page.url
        print(f"   URL atual: {current_url}")
        if "/pedidos/" not in current_url or len(current_url.split("/pedidos/")[-1]) < 5:
            print(f"⚠️  Pedido #{id_pedido} não abriu corretamente.")
            return None

        # ✅ Verifica status PAGO pelo span exato
        try:
            spans = page.locator("span.flex-1.text-inherit.font-normal.px-1").all()
            status_texts = [s.inner_text(timeout=2000).strip() for s in spans]
            print(f"   Status encontrados: {status_texts}")
        except:
            status_texts = []

        if "Pago" not in status_texts:
            print(f"⚠️  Pedido #{id_pedido} não está Pago. Status: {status_texts}. Pulando.")
            return None

        print(f"   ✅ Status PAGO confirmado!")

        # ✅ Captura nome do produto
        nome_produto = None
        try:
            el = page.locator("h3.font-medium.text-font-primary").first
            nome_produto = el.inner_text(timeout=3000).strip()
            print(f"   ✅ Produto: {nome_produto}")
        except:
            nome_produto = f"Produto do pedido #{id_pedido}"

        return {
            "id_pedido":    id_pedido,
            "nome_produto": nome_produto,
            "status":       "pago",
        }

    except Exception as e:
        print(f"❌ Erro ao buscar pedido #{id_pedido}: {e}")
        return None

def fechar_navegador():
    global _playwright, _browser, _context, _page
    salvar_sessao()
    if _browser:
        _browser.close()
        _browser = None
        _page    = None
        _context = None
    if _playwright:
        _playwright.stop()
        _playwright = None
"""
Luna Automation - Interface Gráfica
Execute: py -3.12 app.py
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import os
import time
import traceback
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

# Cores e estilos
BG_DARK      = "#0f1117"
BG_CARD      = "#1a1d2e"
BG_INPUT     = "#252836"
ACCENT       = "#6c63ff"
ACCENT_HOVER = "#574fd6"
GREEN        = "#00d4a0"
RED          = "#ff4757"
YELLOW       = "#ffa502"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#8b8fa8"
BORDER       = "#2d3045"

class LunaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Luna Automation")
        self.root.geometry("1100x700")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)
        self.root.minsize(900, 600)

        self.running = False
        self.thread = None

        self._setup_styles()
        self._build_ui()
        self._check_status_loop()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Card.TFrame", background=BG_CARD, relief="flat")
        style.configure("Dark.TFrame", background=BG_DARK)
        style.configure("TLabel", background=BG_CARD, foreground=TEXT_PRIMARY, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG_CARD, foreground=TEXT_PRIMARY, font=("Segoe UI", 13, "bold"))
        style.configure("Sub.TLabel", background=BG_CARD, foreground=TEXT_SECONDARY, font=("Segoe UI", 9))
        style.configure("Dark.TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=("Segoe UI", 18, "bold"))
        style.configure("Status.TLabel", background=BG_DARK, foreground=TEXT_SECONDARY, font=("Segoe UI", 9))
        style.configure("Treeview", background=BG_INPUT, foreground=TEXT_PRIMARY,
                        fieldbackground=BG_INPUT, rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background=BG_CARD, foreground=TEXT_SECONDARY,
                        font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", ACCENT)])
        style.configure("TEntry", fieldbackground=BG_INPUT, foreground=TEXT_PRIMARY,
                        insertcolor=TEXT_PRIMARY, borderwidth=0, relief="flat")
        style.configure("TCombobox", fieldbackground=BG_INPUT, foreground=TEXT_PRIMARY,
                        selectbackground=ACCENT, selectforeground=TEXT_PRIMARY)

    def _card(self, parent, padx=10, pady=10, fill="both", expand=False, side="top"):
        frame = tk.Frame(parent, bg=BG_CARD, bd=0, highlightthickness=1,
                         highlightbackground=BORDER)
        frame.pack(padx=padx, pady=pady, fill=fill, expand=expand, side=side)
        return frame

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG_DARK, height=60)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        tk.Label(header, text="🌙 Luna Automation", bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=20, pady=15)

        self.lbl_time = tk.Label(header, text="", bg=BG_DARK, fg=TEXT_SECONDARY,
                                  font=("Segoe UI", 9))
        self.lbl_time.pack(side="right", padx=20)
        self._update_clock()

        # Divisor
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        # Layout principal
        main = tk.Frame(self.root, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=0, pady=0)

        # Coluna esquerda
        left = tk.Frame(main, bg=BG_DARK, width=320)
        left.pack(side="left", fill="y", padx=10, pady=10)
        left.pack_propagate(False)

        # Status cards
        self._build_status_panel(left)
        self._build_config_panel(left)
        self._build_buttons(left)

        # Divisor vertical
        tk.Frame(main, bg=BORDER, width=1).pack(side="left", fill="y", pady=10)

        # Coluna direita
        right = tk.Frame(main, bg=BG_DARK)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self._build_pedidos_panel(right)
        self._build_log_panel(right)

    def _build_status_panel(self, parent):
        card = self._card(parent, padx=0, pady=(0,8))
        tk.Label(card, text="CONEXÕES", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(10,5))

        # WhatsApp
        row_wa = tk.Frame(card, bg=BG_CARD)
        row_wa.pack(fill="x", padx=12, pady=3)
        tk.Label(row_wa, text="WhatsApp", bg=BG_CARD, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 10)).pack(side="left")
        self.dot_wa = tk.Label(row_wa, text="●", bg=BG_CARD, fg=RED,
                                font=("Segoe UI", 12))
        self.dot_wa.pack(side="right")
        self.lbl_wa = tk.Label(row_wa, text="Desconectado", bg=BG_CARD, fg=RED,
                                font=("Segoe UI", 9))
        self.lbl_wa.pack(side="right", padx=5)

        # Luna
        row_luna = tk.Frame(card, bg=BG_CARD)
        row_luna.pack(fill="x", padx=12, pady=(3,10))
        tk.Label(row_luna, text="Luna Checkout", bg=BG_CARD, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 10)).pack(side="left")
        self.dot_luna = tk.Label(row_luna, text="●", bg=BG_CARD, fg=YELLOW,
                                  font=("Segoe UI", 12))
        self.dot_luna.pack(side="right")
        self.lbl_luna = tk.Label(row_luna, text="Aguardando", bg=BG_CARD, fg=YELLOW,
                                  font=("Segoe UI", 9))
        self.lbl_luna.pack(side="right", padx=5)

    def _build_config_panel(self, parent):
        card = self._card(parent, padx=0, pady=(0,8))
        tk.Label(card, text="CONFIGURAÇÕES", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(10,5))

        # Data
        tk.Label(card, text="Data mínima", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=12)
        self.entry_data = tk.Entry(card, bg=BG_INPUT, fg=TEXT_PRIMARY, bd=0,
                                    insertbackground=TEXT_PRIMARY, font=("Segoe UI", 10),
                                    relief="flat")
        self.entry_data.pack(fill="x", padx=12, pady=(2,8), ipady=6)
        self.entry_data.insert(0, "01/04/2025")

        # Tipo de pagamento
        tk.Label(card, text="Forma de pagamento", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=12)
        self.combo_pag = ttk.Combobox(card, values=["card", "pix", "card e pix"],
                                       state="readonly", font=("Segoe UI", 10))
        self.combo_pag.current(0)
        self.combo_pag.pack(fill="x", padx=12, pady=(2,8), ipady=3)

        # Grupo WhatsApp
        tk.Label(card, text="Grupo WhatsApp", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=12)
        self.entry_group = tk.Entry(card, bg=BG_INPUT, fg=TEXT_PRIMARY, bd=0,
                                     insertbackground=TEXT_PRIMARY, font=("Segoe UI", 10),
                                     relief="flat")
        self.entry_group.pack(fill="x", padx=12, pady=(2,12), ipady=6)

        # Carrega grupo do config
        try:
            from config.config import WHATSAPP_GROUP
            self.entry_group.insert(0, WHATSAPP_GROUP)
        except:
            self.entry_group.insert(0, "Pedido teste")

    def _build_buttons(self, parent):
        card = self._card(parent, padx=0, pady=(0,8))

        self.btn_start = tk.Button(
            card, text="▶  INICIAR AUTOMAÇÃO",
            bg=ACCENT, fg=TEXT_PRIMARY, bd=0, relief="flat",
            font=("Segoe UI", 10, "bold"), cursor="hand2",
            activebackground=ACCENT_HOVER, activeforeground=TEXT_PRIMARY,
            command=self._iniciar
        )
        self.btn_start.pack(fill="x", padx=12, pady=(10,5), ipady=10)

        self.btn_stop = tk.Button(
            card, text="⏹  PARAR",
            bg=BG_INPUT, fg=TEXT_SECONDARY, bd=0, relief="flat",
            font=("Segoe UI", 10), cursor="hand2",
            activebackground=RED, activeforeground=TEXT_PRIMARY,
            command=self._parar, state="disabled"
        )
        self.btn_stop.pack(fill="x", padx=12, pady=(0,5), ipady=8)

        btn_node = tk.Button(
            card, text="📱  Iniciar Servidor WhatsApp",
            bg=BG_INPUT, fg=TEXT_SECONDARY, bd=0, relief="flat",
            font=("Segoe UI", 9), cursor="hand2",
            command=self._iniciar_whatsapp
        )
        btn_node.pack(fill="x", padx=12, pady=(0,10), ipady=6)

        # Progresso
        self.lbl_progresso = tk.Label(card, text="Aguardando...", bg=BG_CARD,
                                       fg=TEXT_SECONDARY, font=("Segoe UI", 8))
        self.lbl_progresso.pack(pady=(0,5))

        self.progress = ttk.Progressbar(card, mode="determinate")
        self.progress.pack(fill="x", padx=12, pady=(0,10))

    def _build_pedidos_panel(self, parent):
        card = tk.Frame(parent, bg=BG_CARD, bd=0, highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(fill="x", pady=(0,8))

        tk.Label(card, text="PEDIDOS ENCONTRADOS", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(10,5))

        cols = ("linha", "id", "data", "pagamento", "status")
        self.tree = ttk.Treeview(card, columns=cols, show="headings", height=6)
        self.tree.heading("linha", text="Linha")
        self.tree.heading("id", text="ID Pedido")
        self.tree.heading("data", text="Data")
        self.tree.heading("pagamento", text="Pagamento")
        self.tree.heading("status", text="Status")
        self.tree.column("linha", width=50, anchor="center")
        self.tree.column("id", width=100, anchor="center")
        self.tree.column("data", width=150)
        self.tree.column("pagamento", width=80, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        scroll = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(12,0), pady=(0,12))
        scroll.pack(side="right", fill="y", pady=(0,12), padx=(0,12))

    def _build_log_panel(self, parent):
        card = tk.Frame(parent, bg=BG_CARD, bd=0, highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(fill="both", expand=True)

        header_log = tk.Frame(card, bg=BG_CARD)
        header_log.pack(fill="x", padx=12, pady=(10,5))
        tk.Label(header_log, text="LOG EM TEMPO REAL", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Button(header_log, text="Limpar", bg=BG_INPUT, fg=TEXT_SECONDARY,
                  bd=0, relief="flat", font=("Segoe UI", 8), cursor="hand2",
                  command=self._limpar_log).pack(side="right")

        self.log_text = tk.Text(card, bg=BG_INPUT, fg=TEXT_PRIMARY, bd=0,
                                 relief="flat", font=("Consolas", 9),
                                 wrap="word", state="disabled",
                                 insertbackground=TEXT_PRIMARY)
        self.log_text.pack(fill="both", expand=True, padx=12, pady=(0,12))

        # Tags de cor
        self.log_text.tag_config("success", foreground=GREEN)
        self.log_text.tag_config("error", foreground=RED)
        self.log_text.tag_config("warning", foreground=YELLOW)
        self.log_text.tag_config("info", foreground=ACCENT)
        self.log_text.tag_config("normal", foreground=TEXT_PRIMARY)

    def _update_clock(self):
        self.lbl_time.config(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.root.after(1000, self._update_clock)

    def _check_status_loop(self):
        """Verifica status do WhatsApp a cada 5 segundos."""
        try:
            resp = requests.get("http://localhost:3000/status", timeout=2)
            connected = resp.json().get("connected", False)
            if connected:
                self.dot_wa.config(fg=GREEN)
                self.lbl_wa.config(text="Conectado", fg=GREEN)
            else:
                self.dot_wa.config(fg=RED)
                self.lbl_wa.config(text="Desconectado", fg=RED)
        except:
            self.dot_wa.config(fg=RED)
            self.lbl_wa.config(text="Servidor offline", fg=RED)
        self.root.after(5000, self._check_status_loop)

    def _log(self, msg, tag="normal"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {msg}\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _limpar_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def _iniciar_whatsapp(self):
        try:
            from qr_window import QRWindow
            QRWindow(self.root)
        except Exception as e:
            self._log(f"❌ Erro ao abrir janela do WhatsApp: {e}", "error")

    def _iniciar(self):
        if self.running:
            return

        data_filtro = self.entry_data.get().strip()
        pag_escolha = self.combo_pag.get()
        grupo = self.entry_group.get().strip()

        if not data_filtro:
            messagebox.showerror("Erro", "Informe a data mínima!")
            return

        if pag_escolha == "card":
            tipos = ["card"]
        elif pag_escolha == "pix":
            tipos = ["pix"]
        else:
            tipos = ["card", "pix"]

        # Atualiza grupo no config em memória
        try:
            import config.config as cfg
            cfg.WHATSAPP_GROUP = grupo
        except:
            pass

        self.running = True
        self.btn_start.config(state="disabled", bg=BG_INPUT, fg=TEXT_SECONDARY)
        self.btn_stop.config(state="normal", bg=RED, fg=TEXT_PRIMARY)

        self.thread = threading.Thread(
            target=self._run_automacao,
            args=(data_filtro, tipos),
            daemon=True
        )
        self.thread.start()

    def _parar(self):
        self.running = False
        self._log("⚠️  Parando automação...", "warning")
        self.btn_start.config(state="normal", bg=ACCENT, fg=TEXT_PRIMARY)
        self.btn_stop.config(state="disabled", bg=BG_INPUT, fg=TEXT_SECONDARY)
        self.lbl_progresso.config(text="Parado pelo usuário")

    def _run_automacao(self, data_filtro, tipos_pagamento):
        try:
            from modules.google_sheets import get_pedidos_filtrados, atualizar_valor_pago, atualizar_email_compra
            from modules.luna_scraper import buscar_pedido_por_id, fechar_navegador
            from modules.whatsapp import enviar_mensagem, aguardar_mensagem_sua

            self._log("🚀 Iniciando automação...", "info")
            self._log(f"📅 Data: {data_filtro} | Pagamento: {tipos_pagamento}", "info")

            # Busca pedidos
            self._log("📊 Buscando pedidos na planilha...", "info")
            pedidos = get_pedidos_filtrados(data_filtro, tipos_pagamento)

            if not pedidos:
                self._log("ℹ️  Nenhum pedido encontrado.", "warning")
                self._finalizar()
                return

            self._log(f"✅ {len(pedidos)} pedido(s) encontrado(s)!", "success")

            # Popula tabela
            for item in self.tree.get_children():
                self.tree.delete(item)
            for p in pedidos:
                self.tree.insert("", "end", values=(
                    p["row_num"], p["id_pedido"], p["data"], p["pagamento"], "⏳ Aguardando"
                ))

            total = len(pedidos)
            sucesso = 0

            for i, pedido in enumerate(pedidos):
                if not self.running:
                    break

                row_num   = pedido["row_num"]
                id_pedido = pedido["id_pedido"]
                link      = pedido["link_pedido"]

                self.lbl_progresso.config(text=f"Pedido {i+1}/{total}: #{id_pedido}")
                self.progress["value"] = (i / total) * 100

                self._log(f"\n{'─'*40}", "normal")
                self._log(f"📦 Pedido #{id_pedido} (linha {row_num})", "info")

                # Atualiza status na tabela
                items = self.tree.get_children()
                if i < len(items):
                    self.tree.set(items[i], "status", "🔍 Verificando")

                # Busca na Luna
                self.dot_luna.config(fg=YELLOW)
                self.lbl_luna.config(text="Verificando", fg=YELLOW)

                dados = buscar_pedido_por_id(id_pedido)

                if not dados:
                    self._log(f"⏭️  Pedido #{id_pedido} não está pago. Pulando.", "warning")
                    if i < len(items):
                        self.tree.set(items[i], "status", "⏭️ Pulado")
                    continue

                self.dot_luna.config(fg=GREEN)
                self.lbl_luna.config(text="Conectado", fg=GREEN)

                nome_produto = dados["nome_produto"]
                self._log(f"✅ Produto: {nome_produto}", "success")

                if i < len(items):
                    self.tree.set(items[i], "status", "📤 Enviando")

                # Envia no WhatsApp
                enviar_mensagem(f"🔗 *Link do pedido:*\n{link}")
                time.sleep(2)
                enviar_mensagem(f"📦 *Produto:*\n{nome_produto}")
                self._log("📲 Mensagens enviadas no WhatsApp!", "success")

                if i < len(items):
                    self.tree.set(items[i], "status", "⏳ Ag. valor")

                # Aguarda valor
                self._log("💬 Aguardando você enviar o VALOR no grupo...", "info")
                valor = aguardar_mensagem_sua("VALOR")
                if valor:
                    atualizar_valor_pago(row_num, valor.strip())
                    self._log(f"✅ Valor '{valor}' gravado na coluna L!", "success")

                if i < len(items):
                    self.tree.set(items[i], "status", "⏳ Ag. email")

                # Aguarda email
                self._log("💬 Aguardando você enviar o EMAIL no grupo...", "info")
                email = aguardar_mensagem_sua("EMAIL")
                if email:
                    atualizar_email_compra(row_num, email.strip())
                    self._log(f"✅ Email '{email}' gravado na coluna K!", "success")

                if i < len(items):
                    self.tree.set(items[i], "status", "✅ Concluído")

                sucesso += 1
                time.sleep(2)

            fechar_navegador()
            self.progress["value"] = 100
            self._log(f"\n🏁 Finalizado! {sucesso}/{total} pedidos processados.", "success")

        except Exception as e:
            self._log(f"❌ Erro: {e}", "error")
            self._log(traceback.format_exc(), "error")
        finally:
            self._finalizar()

    def _finalizar(self):
        self.running = False
        self.root.after(0, lambda: self.btn_start.config(
            state="normal", bg=ACCENT, fg=TEXT_PRIMARY))
        self.root.after(0, lambda: self.btn_stop.config(
            state="disabled", bg=BG_INPUT, fg=TEXT_SECONDARY))
        self.root.after(0, lambda: self.lbl_progresso.config(text="Concluído"))
        self.root.after(0, lambda: self.dot_luna.config(fg=YELLOW))
        self.root.after(0, lambda: self.lbl_luna.config(text="Aguardando", fg=YELLOW))

def main():
    root = tk.Tk()
    app = LunaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
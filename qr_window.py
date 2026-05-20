"""
Janela popup para exibir QR Code do WhatsApp
"""
import tkinter as tk
from tkinter import ttk
import requests
import threading
import time
import qrcode
from PIL import Image, ImageTk
import subprocess
import os

BG_DARK  = "#0f1117"
BG_CARD  = "#1a1d2e"
ACCENT   = "#6c63ff"
GREEN    = "#00d4a0"
RED      = "#ff4757"
YELLOW   = "#ffa502"
TEXT_PRIMARY   = "#ffffff"
TEXT_SECONDARY = "#8b8fa8"
BORDER   = "#2d3045"

class QRWindow:
    def __init__(self, parent):
        self.parent = parent
        self.win = tk.Toplevel(parent)
        self.win.title("Conectar WhatsApp")
        self.win.geometry("400x520")
        self.win.configure(bg=BG_DARK)
        self.win.resizable(False, False)
        self.win.grab_set()  # Modal

        self.node_process = None
        self.checking = True
        self._build_ui()
        self._start_server()

        self.win.protocol("WM_DELETE_WINDOW", self._fechar)

    def _build_ui(self):
        # Título
        tk.Label(self.win, text="📱 Conectar WhatsApp",
                 bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 14, "bold")).pack(pady=(20,5))

        tk.Label(self.win, text="Escaneie o QR Code com seu celular",
                 bg=BG_DARK, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 9)).pack(pady=(0,15))

        # Área do QR Code
        self.qr_frame = tk.Frame(self.win, bg=BG_CARD, bd=0,
                                  highlightthickness=1, highlightbackground=BORDER)
        self.qr_frame.pack(padx=30, pady=0)

        self.qr_label = tk.Label(self.qr_frame, bg=BG_CARD,
                                  text="⏳ Iniciando servidor...",
                                  fg=TEXT_SECONDARY, font=("Segoe UI", 10),
                                  width=30, height=12)
        self.qr_label.pack(padx=20, pady=20)

        # Status
        self.lbl_status = tk.Label(self.win, text="Aguardando QR Code...",
                                    bg=BG_DARK, fg=YELLOW,
                                    font=("Segoe UI", 9))
        self.lbl_status.pack(pady=10)

        # Instruções
        inst = tk.Frame(self.win, bg=BG_DARK)
        inst.pack(padx=30, fill="x")
        for step in ["1. Abra o WhatsApp no celular",
                     "2. Toque em ⋮ → Aparelhos conectados",
                     "3. Toque em Conectar aparelho",
                     "4. Aponte a câmera para o QR Code"]:
            tk.Label(inst, text=step, bg=BG_DARK, fg=TEXT_SECONDARY,
                     font=("Segoe UI", 8), anchor="w").pack(fill="x", pady=1)

        # Botão fechar
        tk.Button(self.win, text="Fechar",
                  bg=BG_CARD, fg=TEXT_SECONDARY, bd=0, relief="flat",
                  font=("Segoe UI", 9), cursor="hand2",
                  command=self._fechar).pack(pady=15)

    def _start_server(self):
        """Inicia o servidor Node.js e monitora o QR Code."""
        try:
            self.node_process = subprocess.Popen(
                ["node", "whatsapp_server.js"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=os.getcwd()
            )
            # Thread para ler output e capturar QR
            threading.Thread(target=self._read_output, daemon=True).start()
            # Thread para verificar conexão
            threading.Thread(target=self._check_connected, daemon=True).start()
        except Exception as e:
            self.lbl_status.config(text=f"Erro: {e}", fg=RED)

    def _read_output(self):
        """Lê o output do servidor para capturar o QR Code via API."""
        time.sleep(3)  # Aguarda servidor iniciar
        self._fetch_qr()

    def _fetch_qr(self):
        """Busca o QR Code via endpoint do servidor."""
        # Aguarda servidor iniciar completamente
        self.win.after(0, lambda: self.lbl_status.config(
            text="⏳ Iniciando servidor...", fg=YELLOW))
        time.sleep(5)
        
        for i in range(60):  # Tenta por 60 segundos
            if not self.checking:
                return
            try:
                resp = requests.get("http://localhost:3000/qr", timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    qr_data = data.get("qr")
                    if qr_data:
                        self._show_qr(qr_data)
                        return
                    else:
                        self.win.after(0, lambda: self.lbl_status.config(
                            text=f"⏳ Aguardando QR Code...", fg=YELLOW))
                else:
                    self.win.after(0, lambda: self.lbl_status.config(
                        text=f"⏳ Aguardando servidor... ({i+1}s)", fg=YELLOW))
            except:
                self.win.after(0, lambda: self.lbl_status.config(
                    text=f"⏳ Conectando ao servidor... ({i+1}s)", fg=YELLOW))
            time.sleep(1)
        self.win.after(0, lambda: self.lbl_status.config(
            text="⚠️  QR não obtido. Verifique o servidor.", fg=YELLOW))

    def _show_qr(self, qr_data: str):
        """Gera e exibe o QR Code na janela."""
        try:
            qr = qrcode.QRCode(version=1, box_size=5, border=2)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((240, 240), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            def update():
                self.qr_label.config(image=photo, text="", width=240, height=240)
                self.qr_label.image = photo
                self.lbl_status.config(text="📷 Escaneie com o WhatsApp!", fg=YELLOW)
            self.win.after(0, update)
        except Exception as e:
            self.win.after(0, lambda: self.lbl_status.config(
                text=f"Erro ao gerar QR: {e}", fg=RED))

    def _check_connected(self):
        """Verifica se conectou e fecha a janela."""
        time.sleep(5)
        while self.checking:
            try:
                resp = requests.get("http://localhost:3000/status", timeout=2)
                if resp.json().get("connected"):
                    def on_connected():
                        self.lbl_status.config(text="✅ WhatsApp conectado!", fg=GREEN)
                        self.qr_label.config(image="", text="✅ Conectado!",
                                             fg=GREEN, font=("Segoe UI", 14, "bold"))
                        self.win.after(2000, self._fechar)
                    self.win.after(0, on_connected)
                    return
            except:
                pass
            time.sleep(2)

    def _fechar(self):
        self.checking = False
        self.win.destroy()
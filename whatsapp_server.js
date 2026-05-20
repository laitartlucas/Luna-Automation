import makeWASocket, { useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } from "@whiskeysockets/baileys";
import express from "express";
import bodyParser from "body-parser";
import pino from "pino";
import qrcode from "qrcode-terminal";
import { existsSync, mkdirSync, readFileSync, writeFileSync, rmSync } from "fs";

const app = express();
app.use(bodyParser.json());

const PORT = 3000;
const SESSION_DIR = "./sessions/whatsapp";
const PENDING_MESSAGES_FILE = "./sessions/pending_messages.json";

let sock = null;
let isConnected = false;
let lastQR = null;

if (!existsSync(SESSION_DIR)) mkdirSync(SESSION_DIR, { recursive: true });
if (!existsSync("./sessions")) mkdirSync("./sessions", { recursive: true });

function savePendingMessage(data) {
  let pending = [];
  if (existsSync(PENDING_MESSAGES_FILE)) {
    try { pending = JSON.parse(readFileSync(PENDING_MESSAGES_FILE)); } catch {}
  }
  pending.push(data);
  writeFileSync(PENDING_MESSAGES_FILE, JSON.stringify(pending, null, 2));
}

function getAndClearPending() {
  if (!existsSync(PENDING_MESSAGES_FILE)) return [];
  try {
    const data = JSON.parse(readFileSync(PENDING_MESSAGES_FILE));
    writeFileSync(PENDING_MESSAGES_FILE, JSON.stringify([]));
    return data;
  } catch { return []; }
}

async function connectWhatsApp() {
  const { state, saveCreds } = await useMultiFileAuthState(SESSION_DIR);
  const { version } = await fetchLatestBaileysVersion();

  sock = makeWASocket({
    version,
    auth: state,
    logger: pino({ level: "silent" }),
    browser: ["Luna Automation", "Chrome", "1.0.0"],
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", ({ connection, lastDisconnect, qr }) => {
    if (qr) {
      console.log("\n📱 Escaneie o QR Code abaixo com seu WhatsApp:\n");
      qrcode.generate(qr, { small: true });
      console.log("\n(WhatsApp > ⋮ Menu > Aparelhos conectados > Conectar aparelho)\n");
    }
    if (connection === "open") {
      isConnected = true;
      console.log("✅ WhatsApp conectado com sucesso!");
    }
    if (connection === "close") {
      isConnected = false;
      const reason = lastDisconnect?.error?.output?.statusCode;
      const shouldReconnect = reason !== DisconnectReason.loggedOut;
      console.log("❌ Conexão encerrada. Motivo:", reason);

      if (!shouldReconnect) {
        console.log("🗑️  Removendo sessão salva...");
        if (existsSync(SESSION_DIR)) {
          rmSync(SESSION_DIR, { recursive: true, force: true });
          console.log("✅ Sessão removida! Reinicie o servidor para conectar novamente.");
        }
      } else {
        setTimeout(connectWhatsApp, 3000);
      }
    }
  });

  sock.ev.on("messages.upsert", ({ messages, type }) => {
    if (type !== "notify") return;
    for (const msg of messages) {
      const text = msg.message?.conversation ||
                   msg.message?.extendedTextMessage?.text || "";
      const quoted = msg.message?.extendedTextMessage?.contextInfo?.quotedMessage;
      const quotedText = quoted?.conversation || quoted?.extendedTextMessage?.text || "";
      const from = msg.key.remoteJid;
      const sender = msg.pushName || msg.key.participant || from;

      const fromMe = msg.key.fromMe || false;
      if (fromMe) {
        console.log(`📤 Sua mensagem: ${text}`);
      } else {
        console.log(`📨 Mensagem de ${sender}: ${text}`);
      }

      savePendingMessage({
        from, sender,
        text: text.trim(),
        quotedText: quotedText.trim(),
        timestamp: Date.now(),
        messageId: msg.key.id,
        fromMe: fromMe,
      });
    }
  });
}

async function resolveGroupJid(groupName) {
  if (!sock) return null;
  if (groupName.includes("@g.us") || groupName.includes("@s.whatsapp.net")) return groupName;
  const groups = await sock.groupFetchAllParticipating();
  for (const [jid, info] of Object.entries(groups)) {
    if (info.subject.toLowerCase().includes(groupName.toLowerCase())) return jid;
  }
  return null;
}

app.get("/status", (_req, res) => res.json({ connected: isConnected }));

app.get("/qr", (_req, res) => {
  if (lastQR) {
    res.json({ qr: lastQR });
  } else {
    res.status(404).json({ error: "QR não disponível" });
  }
});

app.post("/send", async (req, res) => {
  const { group, message } = req.body;
  if (!sock || !isConnected) return res.status(503).json({ error: "WhatsApp não conectado" });
  if (!group || !message) return res.status(400).json({ error: "Campos 'group' e 'message' obrigatórios" });
  try {
    const jid = await resolveGroupJid(group);
    if (!jid) return res.status(404).json({ error: `Grupo "${group}" não encontrado` });
    const sent = await sock.sendMessage(jid, { text: message });
    console.log(`📤 Enviado para ${group}: "${message.substring(0, 50)}..."`);
    res.json({ success: true, messageId: sent.key.id, jid });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/groups", async (req, res) => {
  if (!sock || !isConnected) return res.status(503).json({ error: "WhatsApp não conectado" });
  try {
    const groups = await sock.groupFetchAllParticipating();
    const list = Object.entries(groups).map(([jid, info]) => ({ jid, name: info.subject }));
    res.json(list);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/messages/pending", (_req, res) => {
  res.json(getAndClearPending());
});

app.listen(PORT, () => {
  console.log(`\n🚀 Servidor WhatsApp rodando na porta ${PORT}`);
  connectWhatsApp();
});
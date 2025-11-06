// app/services/baileys_instance/index.js
import 'dotenv/config'
import makeWASocket, { useMultiFileAuthState, DisconnectReason } from '@whiskeysockets/baileys'
import fetch from 'node-fetch'
import pino from 'pino'
import express from 'express'
import { Boom } from '@hapi/boom'

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000'
const GROUP_ID = process.env.WHATS_GROUP_ID || '' // ex.: 120363420910776837@g.us
const PORT = process.env.BAILEYS_PORT || 3001

const app = express()
app.use(express.json())

let sock = null


// endpoint para o backend/diagnóstico enviar mensagens
app.post('/enviar-mensagem', async (req, res) => {
  try {
    const { numero, mensagem } = req.body
    if (!numero || !mensagem) return res.status(400).json({ status: 'erro', msg: 'faltam campos' })
    await sock.sendMessage(numero, { text: mensagem })
    console.log(`📤 Enviada mensagem para ${numero}: ${mensagem}`)
    res.json({ status: 'sucesso', enviado: true })
  } catch (e) {
    console.error('🚨 Erro /enviar-mensagem:', e)
    res.status(500).json({ status: 'erro', msg: String(e) })
  }
})

app.get('/', (_, res) => res.send('✅ Baileys ativo'))
app.listen(PORT, () => console.log(`🚀 Servidor Baileys rodando em http://127.0.0.1:${PORT}`))

async function iniciar() {
  const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys')
  sock = makeWASocket({
    auth: state,
    printQRInTerminal: true,
    logger: pino({ level: 'silent' }),
    browser: ['Veloce.IA', 'Chrome', '1.0.0']
  })

  sock.ev.on('creds.update', saveCreds)

  sock.ev.on('connection.update', ({ connection, lastDisconnect }) => {
    if (connection === 'close') {
      const shouldReconnect =
        (lastDisconnect?.error instanceof Boom
          ? lastDisconnect.error.output?.statusCode
          : 0) !== DisconnectReason.loggedOut
      console.log('❌ Conexão encerrada. Reconnecting...')
      if (shouldReconnect) iniciar()
    } else if (connection === 'open') {
      console.log('✅ Conectado ao WhatsApp com sucesso!')
    }
  })

  // ouvindo mensagens
  sock.ev.on('messages.upsert', async ({ messages }) => {
    const msg = messages?.[0]
    if (!msg?.message) return

    const from = msg.key.remoteJid
    const isFromMe = msg.key.fromMe
    const isGroup = from.endsWith('@g.us')

      // Evita duplicar resposta do comando "assumir lead"
    if (isFromMe) return


    // extrai texto
    const texto =
      msg.message?.conversation ||
      msg.message?.extendedTextMessage?.text ||
      msg.message?.imageMessage?.caption ||
      ''

      if (isGroup) {
  const lower = (texto || '').toLowerCase().trim()
  if (lower === 'assumir lead') {
    try {
      const corretorJid = msg.key.participant || msg.participant
      // apenas aciona o backend, sem enviar mensagem duplicada
      await fetch(`${BACKEND_URL}/assumir`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ corretor_jid: corretorJid, group_id: from })
      })
      console.log(`📩 Solicitação de assumir lead enviada ao backend por ${corretorJid}`)
    } catch (e) {
      console.error('🚨 Erro ao enviar comando "assumir lead" ao backend:', e)
    }
    return // garante que não continue o fluxo
  }
  return // não conversa no grupo
}



    // 2) PRIVADO: conversa normal
    if (isFromMe) return // ignora eco

    if (!texto?.trim()) {
      // evita disparar /webhook com vazio
      return
    }

    try {
      console.log(`💬 Mensagem recebida de ${from}: ${texto}`)
      // chama backend
      const resp = await fetch(`${BACKEND_URL}/webhook/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ remetente: from, text: texto })
      })
      const data = await resp.json()

      if (data?.resposta_gerada?.resposta) {
        await sock.sendMessage(from, { text: data.resposta_gerada.resposta })
        console.log(`🤖 IA respondeu: ${data.resposta_gerada.resposta}`)
      }

      // se backend sinalizou, dispara resumo no grupo
      if (data?.notify_group && data?.group_id && data?.group_message) {
        await sock.sendMessage(data.group_id, { text: data.group_message })
        console.log('📣 Resumo enviado ao grupo (lead completo).')
      }
    } catch (e) {
      console.error('🚨 Erro ao falar com backend:', e)
      await sock.sendMessage(from, { text: '⚠️ Tive um problema ao processar. Pode tentar de novo?' })
    }
  })
}

iniciar()

import subprocess
import time
import os

VENOM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venom_instance")

def iniciar_venom():
    """
    Inicia o Venom-Bot em segundo plano via Node.js.
    Se o Venom já estiver rodando, ignora.
    """
    if not os.path.exists(VENOM_DIR):
        os.makedirs(VENOM_DIR)

    node_file = os.path.join(VENOM_DIR, "venom.js")

    # Cria o arquivo venom.js (caso não exista)
    if not os.path.exists(node_file):
        with open(node_file, "w", encoding="utf-8") as f:
            f.write("""
const venom = require('venom-bot');
const fs = require('fs');
const express = require('express');
const app = express();
const port = 3001;

let clientInstance;

venom
  .create({
    session: 'veloce_ia',
    multidevice: true,
  })
  .then((client) => start(client))
  .catch((err) => console.log(err));

function start(client) {
  clientInstance = client;
  console.log('✅ Venom-Bot conectado à sessão WhatsApp.');

  // Endpoint para enviar mensagens via HTTP
  app.use(express.json());
  app.post('/send', async (req, res) => {
    const { number, message } = req.body;
    try {
      await client.sendText(number + '@c.us', message);
      console.log('📤 Mensagem enviada para', number);
      res.status(200).send({ status: 'success', number, message });
    } catch (error) {
      console.error('❌ Erro ao enviar mensagem:', error);
      res.status(500).send({ status: 'error', error });
    }
  });

  app.listen(port, () => console.log(`🚀 API Venom rodando em http://localhost:${port}`));
}
""")

    print("🚀 Iniciando Venom-Bot...")
    subprocess.Popen(["node", node_file], cwd=VENOM_DIR)
    time.sleep(5)
    print("✅ Venom-Bot inicializado. Aguardando conexão com WhatsApp...")


def enviar_mensagem_whatsapp(numero, mensagem):
    """
    Envia mensagem para o número especificado usando o Venom local.
    """
    import requests
    try:
        payload = {"number": numero, "message": mensagem}
        response = requests.post("http://localhost:3001/send", json=payload)
        if response.status_code == 200:
            print(f"📨 Mensagem enviada com sucesso para {numero}")
        else:
            print(f"❌ Falha ao enviar mensagem ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"⚠️ Erro ao conectar ao Venom: {e}")

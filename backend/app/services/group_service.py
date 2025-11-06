import json
import os
from datetime import datetime
from app.services.knowledge_service import carregar_conhecimento

# Caminho para armazenar logs simulados das notificações
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "group_notifications.json")

# Configuração: alterna entre modo simulado e Venom real
USE_VENOM = True

def gerar_resumo_lead(lead_data: dict) -> str:
    """
    Gera o texto resumido do lead para envio ao grupo de corretores.
    """
    return (
        f"🏡 *Novo Lead {lead_data['classificacao']}!*\n\n"
        f"📱 *Telefone:* {lead_data['remetente']}\n"
        f"🎯 *Intenção:* {lead_data['intencao']}\n"
        f"🏙️ *Cidade:* {lead_data['cidade']}\n"
        f"💬 *Mensagem:* {lead_data['ultima_mensagem']}\n\n"
        f"📆 *Data:* {lead_data['data_interacao']}\n\n"
        f"👉 Clique para assumir: https://assumirleads.netlify.app/{lead_data['remetente']}"
    )


def enviar_para_grupo(lead_data: dict):
    """
    Envia o resumo do lead ao grupo de corretores.
    No modo simulado, apenas imprime e salva log.
    No modo real, envia via Venom-Bot.
    """
    empresa = carregar_conhecimento()
    numero_grupo = empresa.get("whatsapp_grupo", "não configurado")
    mensagem = gerar_resumo_lead(lead_data)

    if USE_VENOM:
        try:
            from app.services.venom_client import enviar_mensagem_whatsapp
            enviar_mensagem_whatsapp(numero_grupo, mensagem)
            print(f"✅ Lead enviado ao grupo do WhatsApp ({numero_grupo}) via Venom.")
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem via Venom: {e}")
            salvar_log_envio(numero_grupo, mensagem, erro=str(e))
    else:
        print("\n📩 [SIMULAÇÃO] Enviando lead para o grupo de corretores:")
        print(f"Grupo: {numero_grupo}")
        print(mensagem)
        salvar_log_envio(numero_grupo, mensagem)


def salvar_log_envio(grupo, mensagem, erro=None):
    """
    Armazena logs dos envios simulados (para auditoria local).
    """
    log = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as file:
                log = json.load(file)
        except json.JSONDecodeError:
            log = []

    log.append({
        "grupo": grupo,
        "mensagem": mensagem,
        "data_envio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "erro" if erro else "sucesso",
        "detalhe": erro if erro else "enviado com sucesso"
    })

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(log, file, indent=4, ensure_ascii=False)

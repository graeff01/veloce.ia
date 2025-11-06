import json
import os
from datetime import datetime

# Caminho do arquivo onde os leads serão armazenados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_FILE = os.path.join(BASE_DIR, "leads_info.json")


def carregar_leads():
    """
    Retorna todos os leads já armazenados.
    """
    if not os.path.exists(LEADS_FILE):
        return {}
    try:
        with open(LEADS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}


def salvar_leads(leads_data):
    """
    Salva o dicionário completo de leads.
    """
    with open(LEADS_FILE, "w", encoding="utf-8") as file:
        json.dump(leads_data, file, indent=4, ensure_ascii=False)


def registrar_lead(remetente, classificacao, intencao, cidade, mensagem, resposta):
    """
    Registra ou atualiza um lead com as informações mais recentes.
    """
    leads = carregar_leads()

    leads[remetente] = {
        "remetente": remetente,
        "classificacao": classificacao,
        "intencao": intencao,
        "cidade": cidade,
        "ultima_mensagem": mensagem,
        "ultima_resposta": resposta,
        "data_interacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    salvar_leads(leads)
    return leads[remetente]


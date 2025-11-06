import json
import os

# Caminho para armazenar o histórico de conversas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "conversation_memory.json")


def carregar_historico(remetente: str):
    """
    Carrega o histórico de conversas de um remetente específico.
    Retorna uma lista de mensagens [{role, content}, ...]
    """
    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data.get(remetente, [])
    except json.JSONDecodeError:
        return []


def salvar_mensagem(remetente: str, role: str, content: str):
    """
    Salva uma nova mensagem no histórico do remetente.
    """
    data = {}
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            data = {}

    if remetente not in data:
        data[remetente] = []

    data[remetente].append({"role": role, "content": content})

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

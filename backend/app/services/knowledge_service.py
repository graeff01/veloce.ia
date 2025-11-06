import json
import os

# Caminho do arquivo que armazena as informações da empresa
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_FILE = os.path.join(BASE_DIR, "knowledge_base.json")


def carregar_conhecimento():
    """
    Carrega as informações institucionais da empresa (mente da IA).
    """
    if not os.path.exists(KNOWLEDGE_FILE):
        # Caso o arquivo ainda não exista, cria um modelo padrão
        conhecimento_base = {
            "empresa": "Auxiliadora Predial - Canoas",
            "descricao": "Imobiliária referência em Canoas, especializada em imóveis residenciais e comerciais.",
            "bairros_principais": ["Jardim do Lago", "Marechal Rondon", "Centro", "Harmonia"],
            "tom_de_voz": "profissional, acolhedor e resolutivo",
            "objetivo_ia": "ajudar o cliente a encontrar o imóvel ideal e gerar leads qualificados para a equipe de corretores.",
            "whatsapp_grupo": "5551994061787",
            "respostas_personalizadas": {
                "saudacao": "Olá! 👋 Sou a assistente virtual da Auxiliadora Predial de Canoas. Posso te ajudar a encontrar o imóvel perfeito?",
                "encerramento": "Agradeço o contato! Nossa equipe de especialistas vai te retornar em instantes 😊",
                "erro_padrao": "Desculpe, não consegui entender perfeitamente. Você poderia me explicar um pouco melhor o que procura?"
            }
        }

        with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as file:
            json.dump(conhecimento_base, file, indent=4, ensure_ascii=False)
        return conhecimento_base

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def obter_resposta_personalizada(chave: str):
    """
    Retorna uma resposta padrão configurada (ex: saudação, encerramento, erro).
    """
    data = carregar_conhecimento()
    return data.get("respostas_personalizadas", {}).get(chave, "")


def obter_contexto_empresa():
    """
    Retorna dados gerais da empresa que podem ser usados pela IA.
    """
    return carregar_conhecimento()

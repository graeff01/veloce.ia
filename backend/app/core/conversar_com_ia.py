# app/core/conversar_com_ia.py
import openai
import json
import os
from datetime import datetime

# 🔑 Define sua chave de API da OpenAI (pode vir de .env ou direto)
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🧠 Memória de conversa (simples, salva localmente)
DATA_DIR = "app/data"
os.makedirs(DATA_DIR, exist_ok=True)
HISTORICO_FILE = os.path.join(DATA_DIR, "historico_conversas.json")


def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def salvar_historico(historico):
    with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)


# === FUNÇÃO PRINCIPAL ===
async def gerar_resposta(remetente: str, mensagem: str):
    """
    Gera uma resposta natural e estratégica para o lead.
    A IA entende o contexto da conversa e responde como um humano.
    """

    historico = carregar_historico()
    conversa_usuario = historico.get(remetente, [])

    # adiciona a mensagem atual ao histórico
    conversa_usuario.append({"role": "user", "content": mensagem})

    # prompt base — guia o tom e comportamento da IA
    prompt_base = {
        "role": "system",
        "content": (
            "Você é uma assistente inteligente da Auxiliadora Predial, especialista em imóveis. "
            "Seu papel é conversar naturalmente com clientes interessados em comprar, alugar ou investir em imóveis. "
            "Fale de forma humana, empática e natural, como um corretor experiente, mas sem textos longos. "
            "Evite parecer robótico. Seja objetivo, simpático e claro. "
            "Seu objetivo é entender o que o cliente quer e coletar informações como: "
            "(1) cidade ou bairro, (2) tipo de imóvel, (3) faixa de valor e (4) finalidade (compra, aluguel, investimento). "
            "Depois, ofereça encaminhar o contato para um corretor especializado. "
            "Se o cliente disser 'sim', finalize educadamente. "
            "Nunca diga que é uma IA ou assistente virtual. "
            "Use linguagem do dia a dia, como se estivesse falando pelo WhatsApp."
        ),
    }

    mensagens_para_ia = [prompt_base] + conversa_usuario

    # === Geração da resposta ===
    try:
        resposta = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=mensagens_para_ia,
            temperature=0.7,
            max_tokens=220,
        )

        resposta_texto = resposta.choices[0].message["content"].strip()

    except Exception as e:
        resposta_texto = "Desculpe, estou com dificuldade para entender agora. Pode repetir?"
        print("🚨 Erro ao gerar resposta:", e)

    # Atualiza histórico com a resposta da IA
    conversa_usuario.append({"role": "assistant", "content": resposta_texto})
    historico[remetente] = conversa_usuario
    salvar_historico(historico)

    # === Análise básica do contexto (para o dashboard e o grupo) ===
    classificacao = (
        "Lead Quente"
        if any(palavra in mensagem.lower() for palavra in ["comprar", "investir", "comprar um imóvel", "procuro"])
        else "Lead Morno"
        if any(palavra in mensagem.lower() for palavra in ["olhar", "saber", "ver", "interesse"])
        else "Lead Frio"
    )

    intencao = (
        "compra"
        if "comprar" in mensagem.lower()
        else "aluguel"
        if "alugar" in mensagem.lower()
        else "investimento"
        if "investir" in mensagem.lower()
        else "dúvida"
    )

    cidade = None
    cidades_conhecidas = ["canoas", "porto alegre", "florianópolis", "santa catarina"]
    for c in cidades_conhecidas:
        if c in mensagem.lower():
            cidade = c.capitalize()
            break

    resultado = {
        "resposta": resposta_texto,
        "classificacao": classificacao,
        "intencao": intencao,
        "cidade": cidade or "não informado",
        "timestamp": datetime.now().isoformat(),
    }

    return resultado

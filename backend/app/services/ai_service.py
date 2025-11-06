from openai import OpenAI
from app.config import settings
from app.services.knowledge_service import obter_contexto_empresa
from app.services.memory_service import salvar_mensagem, carregar_historico
from app.services.leads_service import registrar_lead
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

contexto_empresa = obter_contexto_empresa()


def processar_mensagem(remetente: str, texto: str):
    """
    Processa a mensagem recebida e retorna uma resposta gerada pela IA
    com classificação automática do lead.
    """

    historico = carregar_historico(remetente)

    # f-string permite inserir variáveis dentro das chaves {}
    system_prompt = f"""
    Você é um assistente imobiliário inteligente da Veloce.IA.
    Seu papel é entender o que o cliente deseja e responder de forma natural, simpática e estratégica.
    Também classifique automaticamente o lead com base na intenção e urgência.

    Use o formato JSON abaixo SEM EXPLICAÇÕES:
    {{
      "resposta": "...texto natural...",
      "classificacao": "Lead Quente / Lead Morno / Lead Frio",
      "intencao": "compra / aluguel / dúvidas / outro",
      "cidade": "cidade mencionada ou 'não informado'"
    }}

    Você está representando a empresa {contexto_empresa['empresa']}.
    Ela é descrita como: "{contexto_empresa['descricao']}".
    Seu tom de voz deve ser {contexto_empresa['tom_de_voz']}.
    Bairros principais que a empresa atende: {', '.join(contexto_empresa['bairros_principais'])}.
    """

    mensagens = [{"role": "system", "content": system_prompt}]
    for msg in historico:
        mensagens.append({"role": msg["role"], "content": msg["content"]})
    mensagens.append({"role": "user", "content": texto})

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensagens,
        temperature=0.7
    )

    resposta_texto = resposta.choices[0].message.content.strip()

    try:
        resposta_json = json.loads(resposta_texto)
    except json.JSONDecodeError:
        resposta_json = {
            "resposta": resposta_texto,
            "classificacao": "Não identificado",
            "intencao": "Não identificado",
            "cidade": "Não informado"
        }

    salvar_mensagem(remetente, "user", texto)
    salvar_mensagem(remetente, "assistant", resposta_json["resposta"])

    registrar_lead(
        remetente=remetente,
        classificacao=resposta_json["classificacao"],
        intencao=resposta_json["intencao"],
        cidade=resposta_json["cidade"],
        mensagem=texto,
        resposta=resposta_json["resposta"]
    )

    return {
        "status": "ok",
        "mensagem_recebida": texto,
        "resposta_gerada": resposta_json
    }

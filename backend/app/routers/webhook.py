# app/routers/webhook.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.core.ai_engine import gerar_resposta
import os, json, httpx
from dotenv import load_dotenv

# Inicialização
router = APIRouter()
load_dotenv()

DATA_DIR = "app/data"
os.makedirs(DATA_DIR, exist_ok=True)

LEADS_FILE = os.path.join(DATA_DIR, "leads_info.json")
QUEUE_FILE = os.path.join(DATA_DIR, "queue.json")

GROUP_ID = os.getenv("WHATS_GROUP_ID")

if GROUP_ID:
    print(f"✅ Grupo configurado: {GROUP_ID}")
else:
    print("⚠️ Atenção: variável WHATS_GROUP_ID não definida. Leads não serão enviados ao grupo.")

# ========== FUNÇÕES AUXILIARES ==========

def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _salvar_lead(numero, info):
    base = _load_json(LEADS_FILE, {})
    cur = base.get(numero, {})
    cur.update(info)
    base[numero] = cur
    _save_json(LEADS_FILE, base)

def _ja_enviado_ao_grupo(numero):
    base = _load_json(LEADS_FILE, {})
    return base.get(numero, {}).get("enviado_grupo", False)

def _marca_enviado(numero):
    base = _load_json(LEADS_FILE, {})
    cur = base.get(numero, {})
    cur["enviado_grupo"] = True
    base[numero] = cur
    _save_json(LEADS_FILE, base)

def _push_pendente(item):
    data = _load_json(QUEUE_FILE, {"pendentes": []})
    data["pendentes"] = [x for x in data["pendentes"] if x.get("numero") != item.get("numero")]
    data["pendentes"].append(item)
    _save_json(QUEUE_FILE, data)

# ========== RECEBE MENSAGENS DO LEAD ==========

@router.post("/webhook/")
async def receber_mensagem(request: Request):
    try:
        body = await request.json()
        remetente = body.get("remetente")
        texto = (body.get("text") or "").strip()

        if not remetente or not texto:
            print(f"⚠️ Mensagem vazia recebida de {remetente}")
            return JSONResponse({"status": "ok", "ignorado": True})

        if remetente.endswith("@g.us"):
            return JSONResponse({"status": "ok", "ignorado": True})

        resultado = gerar_resposta(remetente, texto)

        print(f"\n💬 Mensagem recebida de {remetente}: {texto}")
        print(f"🧠 Classificação: {resultado['classificacao']} | Intenção: {resultado['intencao']} | Cidade: {resultado['cidade']} | Valor: {resultado['valor']}")

        _salvar_lead(remetente, {
            "numero": remetente,
            "ultima_mensagem": texto,
            "resposta": resultado["resposta"],
            "classificacao": resultado["classificacao"],
            "intencao": resultado["intencao"],
            "cidade": resultado["cidade"],
            "valor": resultado["valor"]
        })

        # --- SE O LEAD ESTÁ COMPLETO, PREPARA ENVIO ---
        notify_group = False
        group_message = None

        if resultado.get("lead_completo") and not _ja_enviado_ao_grupo(remetente):
            if GROUP_ID and len(GROUP_ID) > 10:
                try:
                    print("📋 Lead completo detectado — preparando envio para o grupo...")
                    notify_group = True
                    _marca_enviado(remetente)

                    resumo = (
                        f"📩 *Novo Lead Qualificado!*\n"
                        f"───────────────────────────────\n"
                        f"🏙️ *Cidade:* {resultado.get('cidade', 'não informado')}\n"
                        f"🎯 *Intenção:* {resultado.get('intencao', 'não informado')}\n"
                        f"💵 *Valor:* {resultado.get('valor', 'não informado')}\n"
                        f"───────────────────────────────\n"
                        f"Para assumir este lead, digite: *assumir lead*"
                    )

                    _push_pendente({
                        "numero": remetente,
                        "resumo": resumo,
                        "cidade": resultado.get("cidade"),
                        "intencao": resultado.get("intencao"),
                        "valor": resultado.get("valor")
                    })

                    group_message = resumo
                    print("✅ Lead pronto para envio ao grupo!")

                except Exception as e:
                    print("🚨 Erro ao preparar envio do lead:", e)
            else:
                print("⚠️ Nenhum ID de grupo válido definido. Lead não enviado.")

        return JSONResponse({
            "status": "ok",
            "resposta_gerada": {
                "resposta": resultado["resposta"],
                "classificacao": resultado["classificacao"],
                "intencao": resultado["intencao"],
                "cidade": resultado["cidade"],
                "valor": resultado["valor"]
            },
            "notify_group": notify_group,
            "group_id": GROUP_ID if notify_group else None,
            "group_message": group_message
        })

    except Exception as e:
        print("🚨 Erro no webhook:", e)
        return JSONResponse({"status": "erro", "mensagem": str(e)}, status_code=500)

# ========== ASSUMIR LEAD (GRUPO) ==========

@router.post("/assumir")
async def assumir_lead(request: Request):
    """
    Endpoint chamado pelo Baileys quando alguém digita 'assumir lead' no grupo.
    Envia os dados completos do lead para o corretor que assumiu.
    """
    try:
        body = await request.json()
        corretor_jid = body.get("corretor_jid")
        group_id = body.get("group_id")

        if not corretor_jid:
            return JSONResponse({"erro": "Número do corretor não informado"}, status_code=400)

        # Carregar fila de leads pendentes
        fila = _load_json(QUEUE_FILE, {"pendentes": []})
        if not fila["pendentes"]:
            print("⚠️ Nenhum lead pendente encontrado.")
            return JSONResponse({"status": "vazio", "mensagem": "Nenhum lead pendente."})

        # Pega o primeiro lead e remove da fila
        lead = fila["pendentes"].pop(0)
        _save_json(QUEUE_FILE, fila)

        resumo_privado = (
            "📋 *Lead Assumido com Sucesso!*\n"
            "───────────────────────────────\n"
            f"🏙️ *Cidade:* {lead.get('cidade', 'não informado')}\n"
            f"🎯 *Intenção:* {lead.get('intencao', 'não informado')}\n"
            f"💰 *Valor:* {lead.get('valor', 'não informado')}\n"
            "───────────────────────────────\n"
            "✅ Esse lead agora é seu! Um corretor já não poderá mais assumir.\n"
            "Entre em contato com o cliente para dar continuidade ao atendimento."
        )


        async with httpx.AsyncClient() as client:
            await client.post(
                "http://127.0.0.1:3001/enviar-mensagem",
                json={"numero": corretor_jid, "mensagem": resumo_privado},
            )

        print(f"✅ Lead assumido e enviado para {corretor_jid}")
        return JSONResponse({
            "status": "ok",
            "mensagem": "Lead assumido com sucesso!",
            "lead": {"resumo_privado": resumo_privado}
        })

    except Exception as e:
        print("🚨 Erro ao assumir lead:", e)
        return JSONResponse({"erro": str(e)}, status_code=500)

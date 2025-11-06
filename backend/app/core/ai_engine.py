# app/core/ai_engine.py
import os, json, re
from datetime import datetime

DATA_DIR = "app/data"
os.makedirs(DATA_DIR, exist_ok=True)
MEM_FILE = os.path.join(DATA_DIR, "memory.json")

INTENT_KEYWORDS = {
    "compra": ["comprar", "compra", "quero comprar"],
    "aluguel": ["alugar", "aluguel", "locar", "arrendar", "quero alugar"],
}

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

def _extract_valor(texto: str):
    """
    Extrai valor aproximado (R$) do texto.
    Suporta formatos como: 900 mil, 900.000, R$ 1.2 mi, etc.
    Retorna string normalizada ex.: 'R$ 900.000'
    """
    t = texto.lower().replace(".", "").replace(",", ".")
    # padrões comuns
    mi = re.search(r"(\d+(\.\d+)?)\s*m[ií]", t)
    mil = re.search(r"(\d+(\.\d+)?)\s*mil", t)
    num = re.search(r"r?\$?\s*(\d{3,})", t)

    if mi:
        valor = float(mi.group(1)) * 1_000_000
        return f"R$ {int(round(valor)):,.0f}".replace(",", ".")
    if mil:
        valor = float(mil.group(1)) * 1000
        return f"R$ {int(round(valor)):,.0f}".replace(",", ".")
        valor = min(valor, 9_000_000)  # trava para evitar exagero por erro de regex
    if num:
        raw = num.group(1)
        try:
            n = int(raw)
            return f"R$ {n:,.0f}".replace(",", ".")
        except Exception:
            pass
    return None

def _detect_intencao(texto: str):
    l = texto.lower()
    for intent, kws in INTENT_KEYWORDS.items():
        if any(kw in l for kw in kws):
            return intent
    # fallback: se mencionar “investir”
    if "invest" in l:
        return "investimento"
    return None

def _detect_cidade(texto: str):
    # Para MVP: pega nomes mais comuns. Pode evoluir com dicionário do cliente.
    cidades = ["canoas", "porto alegre", "gravataí", "sapucaia", "esteio", "nova santa rita"]
    l = texto.lower()
    for c in cidades:
        if c in l:
            return c.title()
    return None

def _normalize_city(city):
    if not city:
        return "não informado"
    return city.title()

def _load_mem():
    data = _load_json(MEM_FILE, {})
    # garantir formato correto (dict)
    if not isinstance(data, dict):
        data = {}
        _save_mem(data)
    return data


def _save_mem(mem):
    _save_json(MEM_FILE, mem)

def gerar_resposta(remetente: str, texto: str):
    """
    Gera resposta natural, atualiza memória e indica quando lead está 'completo'.
    Lead completo = intenção ('compra' ou 'aluguel') + cidade + valor.
    """
    mem = _load_mem()
    state = mem.get(remetente, {
        "intencao": None,
        "cidade": None,
        "valor": None,
        "historico": []
    })

    # atualiza histórico
    state["historico"].append({"quem": "user", "texto": texto, "ts": datetime.utcnow().isoformat()})

    # extrair sinais
    intencao = state["intencao"] or _detect_intencao(texto)
    cidade = state["cidade"] or _detect_cidade(texto)
    valor = state["valor"] or _extract_valor(texto)

    state["intencao"] = intencao
    state["cidade"] = cidade
    state["valor"] = valor

    # montar resposta natural (curta, humana)
    resposta = None
    if not intencao:
        resposta = "Olá! Está procurando comprar ou alugar?"
    elif intencao and not cidade:
        resposta = "Perfeito, e em qual cidade você pretende?"
    elif intencao and cidade and not valor:
        resposta = f"Ótimo, {cidade}! Qual a faixa de valor que você tem em mente?"
    else:
        # tudo que precisamos está preenchido
        resposta = (
            f"Perfeito! Vou te ajudar com opções em {cidade} dentro de {valor}. "
            f"Enquanto isso, prefere casa ou apartamento, ou está aberto(a) a sugestões?"
        )

        # gravar a resposta no histórico
    state["historico"].append({"quem": "ia", "texto": resposta, "ts": datetime.utcnow().isoformat()})

    mem[remetente] = state
    _save_mem(mem)

    # critérios de completude
    lead_completo = bool(
        (intencao in ["compra", "aluguel"]) and cidade and valor
    )

    return {
        "resposta": resposta,
        "classificacao": "Lead Quente" if lead_completo else ("Lead Morno" if intencao else "Lead Frio"),
        "intencao": intencao or "não informado",
        "cidade": _normalize_city(cidade),
        "valor": valor or "não informado",
        "lead_completo": lead_completo
    }
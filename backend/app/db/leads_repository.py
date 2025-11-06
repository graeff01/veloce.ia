# app/db/leads_repository.py
import json
from pathlib import Path
from app.models.lead import Lead

# Caminho do arquivo local onde os leads serão salvos
DATA_PATH = Path("app/db/leads.json")

def salvar_lead(lead: Lead):
    """Adiciona um novo lead ao arquivo JSON."""
    leads = carregar_leads()
    leads.append(lead.dict())

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=4)

def carregar_leads():
    """Carrega todos os leads salvos (ou retorna lista vazia)."""
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

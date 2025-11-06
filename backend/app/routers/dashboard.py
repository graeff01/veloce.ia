from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
import json
import os

router = APIRouter()

LEADS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../services/leads_info.json")


@router.get("/leads", response_class=JSONResponse)
def listar_leads():
    """
    Retorna o conteúdo do leads_info.json como JSON.
    """
    try:
        with open(LEADS_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {"erro": "Arquivo leads_info.json não encontrado"}
    except json.JSONDecodeError:
        return {"erro": "Erro ao ler leads_info.json"}


@router.get("/painel", response_class=HTMLResponse)
def exibir_painel():
    """
    Retorna o painel HTML com tabela dinâmica de leads.
    """
    html = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Painel de Leads | Veloce.IA</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f4f8; margin: 0; padding: 20px; }
            h1 { text-align: center; color: #5A33FF; }
            table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee; }
            th { background: #5A33FF; color: white; text-transform: uppercase; font-size: 14px; }
            tr:hover { background-color: #f9f9ff; }
            .lead-quente { color: #FF3B30; font-weight: bold; }
            .lead-morno { color: #FF9500; font-weight: bold; }
            .lead-frio { color: #34C759; font-weight: bold; }
            .footer { text-align: center; margin-top: 20px; color: #888; font-size: 12px; }
        </style>
    </head>
    <body>
        <h1>Painel de Leads — Veloce.IA</h1>
        <table id="tabelaLeads">
            <thead>
                <tr>
                    <th>Telefone</th>
                    <th>Classificação</th>
                    <th>Intenção</th>
                    <th>Cidade</th>
                    <th>Mensagem</th>
                    <th>Data</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>

        <div class="footer">Atualizado automaticamente a cada 10 segundos 🚀</div>

        <script>
            async function carregarLeads() {
                const response = await fetch('/dashboard/leads');
                const data = await response.json();
                const tbody = document.querySelector('#tabelaLeads tbody');
                tbody.innerHTML = '';

                for (const leadId in data) {
                    const lead = data[leadId];
                    const row = document.createElement('tr');

                    let classe = '';
                    if (lead.classificacao.toLowerCase().includes('quente')) classe = 'lead-quente';
                    else if (lead.classificacao.toLowerCase().includes('morno')) classe = 'lead-morno';
                    else classe = 'lead-frio';

                    row.innerHTML = `
                        <td>${lead.remetente}</td>
                        <td class="${classe}">${lead.classificacao}</td>
                        <td>${lead.intencao}</td>
                        <td>${lead.cidade}</td>
                        <td>${lead.ultima_mensagem}</td>
                        <td>${lead.data_interacao}</td>
                    `;
                    tbody.appendChild(row);
                }
            }

            carregarLeads();
            setInterval(carregarLeads, 10000); // Atualiza a cada 10 segundos
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

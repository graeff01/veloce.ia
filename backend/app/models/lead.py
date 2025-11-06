from datetime import datetime
from pydantic import BaseModel

class Lead(BaseModel):
    id: str
    nome: str | None = None
    mensagem: str
    classificacao: str
    resposta: str
    data: datetime = datetime.now().isoformat()

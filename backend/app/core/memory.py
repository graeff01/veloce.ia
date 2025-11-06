import json
import os

class MemoryManager:
    def __init__(self):
        self.memory_file = "app/data/memory.json"
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def obter_historico(self, remetente):
        """Retorna histórico de mensagens de um número."""
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get(remetente, [])
        except Exception:
            return []

    def salvar_historico(self, remetente, historico):
        """Salva histórico atualizado do remetente."""
        with open(self.memory_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data[remetente] = historico
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# === Instância global ===
memoria_conversa = MemoryManager()
